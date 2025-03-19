import numpy as np

from sunnypilot.nnff_longitudinal_controller.longitudinal_nnff import TinyNeuralNetwork
from tinygrad.tensor import Tensor

nn_model = TinyNeuralNetwork(input_size=3, hidden_size=5, output_size=2, lr=0.01)

# Define the input and target tensors (ensure they are 2D)
x = Tensor(np.array([[0.1, 0.2, 0.3]], dtype=np.float32))  # Reshaped to keep it 2D
target = Tensor(np.array([[0.35, 0.9]], dtype=np.float32))  # Reshaped to keep it 2D

# Set weights and biases with proper shapes for a three-layer network:
nn_model.W1 = Tensor(np.random.randn(3, 5).astype(np.float32))  # shape: (3,5)
nn_model.b1 = Tensor(np.zeros(5, dtype=np.float32))  # shape: (5,)
nn_model.W2 = Tensor(np.random.randn(5, 5).astype(np.float32))  # shape: (5,5)
nn_model.b2 = Tensor(np.zeros(5, dtype=np.float32))  # shape: (5,)
nn_model.W3 = Tensor(np.random.randn(5, 2).astype(np.float32))  # shape: (5,2)
nn_model.b3 = Tensor(np.zeros(2, dtype=np.float32))  # shape: (2,)

# Print the initial output and loss
init_out = nn_model.forward(x)
print("Initial output:", init_out.numpy())
init_loss = ((init_out - target) ** 2).mean().numpy()
print("Initial loss:", init_loss)

# Train the network
num_iterations = 1000
print_interval = 200

for i in range(num_iterations):
  nn_model.train(x, target, iterations=1)

  # Print progress periodically
  if (i + 1) % print_interval == 0:
    current_out = nn_model.forward(x)
    current_loss = ((current_out - target) ** 2).mean().numpy()
    print(f"Iteration {i + 1}, output: {current_out.numpy()}, loss: {current_loss}")

# Print the final output and loss
final_out = nn_model.forward(x)
print("Final output:", final_out.numpy())
print("Target:", target.numpy())
print("Training iterations:", nn_model.training_iterations)
print("Recent loss history:", nn_model.training_loss_history[-5:])
