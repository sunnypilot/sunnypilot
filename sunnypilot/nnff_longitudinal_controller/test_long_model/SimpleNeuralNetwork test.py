import numpy as np

from sunnypilot.nnff_longitudinal_controller.longitudinal_nnff import TinyNeuralNetwork

nn_model = TinyNeuralNetwork(input_size=3, hidden_size=5, output_size=2)

# Sample input and a target output
x = np.array([0.1, 0.2, 0.3])
target = np.array([0.5, 0.5])

# Print the initial output and loss
init_out = nn_model.forward(x)
print("Initial output:", init_out)

# Train the network for many iterations
num_iterations = 1000
for _i in range(num_iterations):
  nn_model.train(x, target, iterations=1)

# After training, check the output
final_out = nn_model.forward(x)
print("Final output:", final_out)
print("Training iterations:", nn_model.training_iterations)
print("Recent loss history:", nn_model.training_loss_history[-5:])
