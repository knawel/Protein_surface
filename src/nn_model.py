import torch.nn as nn
import torch.nn.functional as F


class AmberNN(nn.Module):
    def __init__(self, input_size, num_classes, hidden_size, p=0.1):
        super(AmberNN, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, hidden_size)
        self.fc4 = nn.Linear(hidden_size, num_classes)
        self.dropout = nn.Dropout(p)

    def forward(self, x):
        out = F.relu(self.fc1(x))
        out = F.relu(self.fc2(out))
        out = self.dropout(out)
        out = F.relu(self.fc3(out))
        out = self.dropout(out)
        out = F.relu(self.fc4(out))
        return out

