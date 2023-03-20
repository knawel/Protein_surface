import torch.nn as nn
import torch.nn.functional as F


class AmberNN(nn.Module):
    def __init__(self, input_size, num_classes, hidden_size, p=0.10):
            super().__init__()
            self.linear_relu_stack = nn.Sequential(
                nn.Linear(input_size, hidden_size),
                nn.ReLU(),
                nn.Linear(hidden_size, hidden_size),
                nn.ReLU(),
                nn.Dropout(p=p),
                nn.Linear(hidden_size, 32),
                nn.ReLU(),
                nn.Linear(32, num_classes),
            )
    def forward(self, x):
            logits = self.linear_relu_stack(x)
            return logits

