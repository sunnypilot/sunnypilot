import numpy as np

from sunnypilot.nnff_longitudinal_controller.learning_model import TinyNeuralNetwork
from tinygrad.tensor import Tensor

nn_model = TinyNeuralNetwork(input_size=3, hidden_size=5, output_size=2, lr=0.1, dropout_rate=0.0)

# Define the input and target tensors (ensure they are 2D)
x = Tensor(np.array([[0.1, 0.2, 0.3]], dtype=np.float32))
target = Tensor(np.array([[0.15, 0.9]], dtype=np.float32))

# Print the initial output and loss
init_out = nn_model.forward(x)
print("Initial output:", init_out.numpy())
init_loss = ((init_out - target) ** 2).mean().numpy()
print("Initial loss:", init_loss)

# Train the network
num_iterations = 1000
print_interval = 100

for i in range(num_iterations):
    nn_model.train(x, target, iterations=1)

    if (i + 1) % print_interval == 0:
        current_out = nn_model.forward(x)
        current_loss = ((current_out - target) ** 2).mean().numpy()
        print(f"Iteration {i + 1}, output: {current_out.numpy()}, loss: {current_loss}")

print("Final output:", nn_model.forward(x).numpy())
print("Target:", target.numpy())
print("Training iterations:", nn_model.training_iterations)
print("Recent loss history:", nn_model.training_loss_history[-5:])
