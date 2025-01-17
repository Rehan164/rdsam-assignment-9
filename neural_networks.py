import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.animation import FuncAnimation
import os
from functools import partial
from matplotlib.patches import Circle

result_dir = "results"
os.makedirs(result_dir, exist_ok=True)

# Activation functions and their derivatives
def tanh(x):
    return np.tanh(x)

def tanh_derivative(x):
    return 1 - np.tanh(x)**2

def relu(x):
    return np.maximum(0, x)

def relu_derivative(x):
    return (x > 0).astype(float)

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def sigmoid_derivative(x):
    s = sigmoid(x)
    return s * (1 - s)

# Define a simple MLP class
class MLP:
    def __init__(self, input_dim, hidden_dim, output_dim, lr, activation='tanh'):
        np.random.seed(0)
        self.lr = lr  # learning rate
        
        # Initialize weights and biases
        self.W1 = np.random.randn(input_dim, hidden_dim) * 0.1
        self.b1 = np.zeros((1, hidden_dim))
        self.W2 = np.random.randn(hidden_dim, output_dim) * 0.1
        self.b2 = np.zeros((1, output_dim))
        
        # Set activation function
        self.activation_fn = {'tanh': tanh, 'relu': relu, 'sigmoid': sigmoid}[activation]
        self.activation_derivative = {'tanh': tanh_derivative, 'relu': relu_derivative, 'sigmoid': sigmoid_derivative}[activation]
        
        # Store activations and gradients for visualization
        self.hidden_features = None
        self.gradients = {}

    def forward(self, X):
        # Forward pass
        self.Z1 = X @ self.W1 + self.b1
        self.A1 = self.activation_fn(self.Z1)  # Hidden layer activations
        self.Z2 = self.A1 @ self.W2 + self.b2
        self.A2 = sigmoid(self.Z2)  # Output layer activations
        self.hidden_features = self.A1
        return self.A2

    def backward(self, X, y):
        # Compute gradients using backpropagation
        m = X.shape[0]
        dZ2 = self.A2 - y
        self.gradients['W2'] = (self.A1.T @ dZ2) / m
        self.gradients['b2'] = np.sum(dZ2, axis=0, keepdims=True) / m
        
        dA1 = dZ2 @ self.W2.T
        dZ1 = dA1 * self.activation_derivative(self.Z1)
        self.gradients['W1'] = (X.T @ dZ1) / m
        self.gradients['b1'] = np.sum(dZ1, axis=0, keepdims=True) / m
        
        # Update weights and biases
        self.W2 -= self.lr * self.gradients['W2']
        self.b2 -= self.lr * self.gradients['b2']
        self.W1 -= self.lr * self.gradients['W1']
        self.b1 -= self.lr * self.gradients['b1']

def generate_data(n_samples=100):
    np.random.seed(0)
    # Generate input
    X = np.random.randn(n_samples, 2)
    y = (X[:, 0] ** 2 + X[:, 1] ** 2 > 1).astype(int).reshape(-1, 1)
    return X, y

# Visualization update function
def update(frame, mlp, ax_input, ax_hidden, ax_gradient, X, y):
    ax_hidden.clear()
    ax_input.clear()
    ax_gradient.clear()

    # Perform multiple training steps
    for _ in range(10):
        mlp.forward(X)
        mlp.backward(X, y)

    # Hidden space visualization
    hidden_features = mlp.hidden_features
    ax_hidden.scatter(hidden_features[:, 0], hidden_features[:, 1], c=y.ravel(), cmap='bwr', alpha=0.7)
    ax_hidden.set_title("Hidden Space")

    # Input space decision boundary
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 100), np.linspace(y_min, y_max, 100))
    grid = np.c_[xx.ravel(), yy.ravel()]
    Z = mlp.forward(grid)
    Z = Z.reshape(xx.shape)
    ax_input.contourf(xx, yy, Z, levels=[0, 0.5, 1], cmap='bwr', alpha=0.3)
    ax_input.scatter(X[:, 0], X[:, 1], c=y.ravel(), cmap='bwr', edgecolors='k')
    ax_input.set_title("Input Space Decision Boundary")

    # Gradient visualization
    grad_magnitudes = np.linalg.norm(mlp.gradients["W1"], axis=0)
    ax_gradient.bar(range(len(grad_magnitudes)), grad_magnitudes)
    ax_gradient.set_title("Gradients")

def visualize(activation, lr, step_num):
    X, y = generate_data()
    mlp = MLP(input_dim=2, hidden_dim=3, output_dim=1, lr=lr, activation=activation)

    # Set up visualization
    matplotlib.use('agg')
    fig = plt.figure(figsize=(21, 7))
    ax_hidden = fig.add_subplot(131, projection='3d')
    ax_input = fig.add_subplot(132)
    ax_gradient = fig.add_subplot(133)

    # Create animation
    ani = FuncAnimation(fig, partial(update, mlp=mlp, ax_input=ax_input, ax_hidden=ax_hidden, ax_gradient=ax_gradient, X=X, y=y), frames=step_num // 10, repeat=False)

    # Save the animation as a GIF
    ani.save(os.path.join(result_dir, "visualize.gif"), writer='pillow', fps=10)
    plt.close()

if __name__ == "__main__":
    activation = "tanh"
    lr = 0.1
    step_num = 1000
    visualize(activation, lr, step_num)
