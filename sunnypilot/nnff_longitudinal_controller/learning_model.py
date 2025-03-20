import math

import numpy as np

from tinygrad.nn.optim import SGD, Adam
from tinygrad.tensor import Tensor


class TinyNeuralNetwork:
    """Neural network using tinygrad for machine learning."""

    def __init__(
            self,
            input_size: int = 8,
            hidden_size: int = 24,
            output_size: int = 5,
            lr: float = 0.01,
            optimizer_type: str = 'adam',
            activation: str = 'leakyrelu',
            weight_init: str = 'he',
            dropout_rate: float = 0.0
    ):
        """
        Initialize the neural network with the given parameters.

        Args:
            input_size: Number of input features
            hidden_size: Size of the hidden layers
            output_size: Number of output features
            lr: Learning rate
            optimizer_type: Type of optimizer ('sgd', 'adam')
            activation: Activation function ('relu', 'leakyrelu', 'sigmoid', 'tanh')
            weight_init: Weight initialization method ('he', 'xavier', 'normal')
            dropout_rate: Dropout rate (0.0 to 1.0) for regularization
        """
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.lr = lr
        self.dropout_rate = dropout_rate
        self.activation_name = activation

        # Initialize weights based on selected method
        if weight_init == 'he':
            scale1 = math.sqrt(2.0 / input_size)
            scale2 = math.sqrt(2.0 / hidden_size)
        elif weight_init == 'xavier':
            scale1 = math.sqrt(6.0 / (input_size + hidden_size))
            scale2 = math.sqrt(6.0 / (hidden_size + output_size))
        else:  # normal
            scale1, scale2 = 0.1, 0.1

        # Initialize parameters as tinygrad Tensors
        self.W1 = Tensor.randn(input_size, hidden_size) * scale1
        self.b1 = Tensor.zeros(hidden_size)
        self.W2 = Tensor.randn(hidden_size, hidden_size) * scale2
        self.b2 = Tensor.zeros(hidden_size)
        self.W3 = Tensor.randn(hidden_size, output_size) * scale2
        self.b3 = Tensor.zeros(output_size)

        # Set up optimizer
        if optimizer_type == 'adam':
            self.optimizer = Adam([self.W1, self.b1, self.W2, self.b2, self.W3, self.b3], lr=self.lr)
        else:
            self.optimizer = SGD([self.W1, self.b1, self.W2, self.b2, self.W3, self.b3], lr=self.lr)

        # For tracking training metrics
        self.training_loss_history: list[float] = []
        self.validation_loss_history: list[float] = []
        self.training_iterations = 0
        self.best_loss = float('inf')

        # Flag for compiled forward pass
        self._forward_compiled = False
        self._backward_compiled = False

    def activation(self, x: Tensor) -> Tensor:
        """Apply the selected activation function."""
        if self.activation_name == 'relu':
            return x.relu()
        elif self.activation_name == 'leakyrelu':
            return x.leakyrelu(0.01)
        elif self.activation_name == 'sigmoid':
            return x.sigmoid()
        elif self.activation_name == 'tanh':
            return x.tanh()
        else:
            return x.leakyrelu(0.01)  # Default to leaky ReLU

    def dropout(self, x: Tensor, training: bool = True) -> Tensor:
        """Apply dropout regularization if rate > 0 and in training mode."""
        if training and self.dropout_rate > 0:
            mask = Tensor.rand(x.shape) > self.dropout_rate
            return x * mask * (1 / (1 - self.dropout_rate))  # Scale to maintain expected value
        return x

    def forward(self, x: Tensor, training: bool = False) -> Tensor:
        """Forward pass through the network.

        Args:
          x: Input tensor
          training: Whether the network is in training mode (affects dropout)

        Returns:
          Output tensor after passing through the network
        """
        # First layer: linear + activation + dropout
        z1 = x.dot(self.W1) + self.b1
        a1 = self.activation(z1)
        a1 = self.dropout(a1, training)

        # Second layer: linear + activation + dropout
        z2 = a1.dot(self.W2) + self.b2
        a2 = self.activation(z2)
        a2 = self.dropout(a2, training)

        # Output layer: linear + sigmoid activation
        z3 = a2.dot(self.W3) + self.b3
        return z3.sigmoid()

    def backward_step(self, x: Tensor, y: Tensor) -> tuple[Tensor, Tensor]:
        """Perform backward propagation.

        Args:
            x: Input tensor
            y: Target tensor

        Returns:
            tuple of (loss, output)
        """
        # Forward pass with training=True (enables dropout)
        out = self.forward(x, training=True)

        # Calculate loss (Mean Squared Error)
        loss = ((out - y) ** 2).mean()

        # Backward pass
        loss.backward()

        return loss, out

    def train(self, x: Tensor | np.ndarray, y: Tensor | np.ndarray,
              iterations: int = 1, batch_size: int | None = None,
              validation_data: tuple[Tensor | np.ndarray, Tensor | np.ndarray] | None = None) -> float:
        """
        Train the network for a given number of iterations.

        Args:
            x: Input data (Tensor or numpy array)
            y: Target data (Tensor or numpy array)
            iterations: Number of training iterations
            batch_size: Batch size for mini-batch training (None for full batch)
            validation_data: Optional tuple of (val_x, val_y) for validation

        Returns:
            Average loss over the training iterations
        """
        # Convert inputs to Tensors if they're numpy arrays
        if not isinstance(x, Tensor):
            x = Tensor(x)
        if not isinstance(y, Tensor):
            y = Tensor(y)
        avg_loss = 0.0

        self.optimizer.params = [self.W1, self.b1, self.W2, self.b2, self.W3, self.b3]

        # Save the prev. training status
        previous_training_state = Tensor.training

        # Allow tinygrad training
        Tensor.training = True

        try:
            # Train for the specified number of iterations
            for _i in range(iterations):
                # Reset JIT compilation so new parameters are used
                self._forward_compiled = False
                self._backward_compiled = False
                if batch_size is None or batch_size >= x.shape[0]:
                    # Full batch training
                    loss, _ = self.backward_step(x, y)
                    self._ensure_all_gradients()
                    self.optimizer.step()
                    self.optimizer.zero_grad()
                    scalar_loss = float(loss.numpy())
                else:
                    # Mini-batch training
                    indices = np.random.permutation(x.shape[0])
                    scalar_loss = 0.0
                    for j in range(0, x.shape[0], batch_size):
                        batch_indices = indices[j:j + batch_size]
                        batch_x = x[batch_indices]
                        batch_y = y[batch_indices]

                        # Reset JIT flags for mini-batch step
                        self._forward_compiled = False
                        self._backward_compiled = False

                        loss, _ = self.backward_step(batch_x, batch_y)

                        # Ensure all parameters have gradients
                        self._ensure_all_gradients()
                        self.optimizer.step()
                        self.optimizer.zero_grad()
                        scalar_loss += float(loss.numpy()) * len(batch_indices) / x.shape[0]

                avg_loss += scalar_loss / iterations
                self.training_loss_history.append(scalar_loss)
                self.training_iterations += 1

            # Run validation if provided
            if validation_data is not None:
                val_x, val_y = validation_data
                if not isinstance(val_x, Tensor):
                    val_x = Tensor(val_x)
                if not isinstance(val_y, Tensor):
                    val_y = Tensor(val_y)

                with Tensor.no_grad():
                    val_out = self.forward(val_x)
                    val_loss = ((val_out - val_y) ** 2).mean().numpy()
                    self.validation_loss_history.append(float(val_loss))

                    # Save best model if validation loss improves
                    if val_loss < self.best_loss:
                        self.best_loss = val_loss

        finally:
            # Restore the previous training state
            Tensor.training = previous_training_state

        return avg_loss

    def _ensure_all_gradients(self) -> None:
        """Initialize gradients if they are None or not yet realized."""
        params = [self.W1, self.b1, self.W2, self.b2, self.W3, self.b3]
        for param in params:
            if param.grad is None or callable(param.grad):
                param.grad = Tensor(np.zeros(param.numpy().shape, dtype=param.numpy().dtype))
