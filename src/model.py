# src/model.py

import torch
import torch.nn as nn

class ChorusMLP(nn.Module):
    def __init__(self, input_dim=114, hidden_size=64, output_dim=2):
        super(ChorusMLP, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, output_dim)

    def forward(self, x):
        # x shape: (batch_size, 114)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x