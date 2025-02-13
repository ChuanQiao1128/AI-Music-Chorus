# model.py
"""
在此定义PyTorch或TensorFlow模型，如一个简单的MLP网络
"""

import torch
import torch.nn as nn

class ChorusMLP(nn.Module):
    def __init__(self, input_dim, hidden_size=32, output_dim=2):
        super(ChorusMLP, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, output_dim)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x