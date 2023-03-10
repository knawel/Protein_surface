import torch.nn as nn
import torch.nn.functional as F


class AmberNN(nn.Module):
    def __init__(self, input_size, num_classes, hidden_size, p=0.15):
        super(AmberNN, self).__init__()
        # self.layer_norm = nn.LayerNorm(input_size)
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, hidden_size)
        self.fc4 = nn.Linear(hidden_size, 64)
        # self.fc5 = nn.Linear(64, 64)
        # self.fc6 = nn.Linear(64, 16)
        self.fc7 = nn.Linear(64, num_classes)
        self.dropout = nn.Dropout(p)

    def forward(self, x):
        # output = self.layer_norm(x)
        out = F.relu(self.fc1(x))
        # out = self.dropout(out)
        out = F.relu(self.fc2(out))
        out = self.dropout(out)
        out = F.relu(self.fc3(out))
        out = self.dropout(out)
        out = F.relu(self.fc4(out))
        # out = F.relu(self.fc5(out))
        # out = F.relu(self.fc6(out))
        out = F.relu(self.fc7(out))
        return out

