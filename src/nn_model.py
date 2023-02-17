import torch.nn as nn


class Amber_NN(nn.Module):

    def __init__(self, nfeatures, nclasses):
        super().__init__()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(nfeatures, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, nclasses)
        )

    def forward(self, x):
        # x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits