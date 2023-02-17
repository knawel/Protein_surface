import numpy as np
from src.data import ProteinsDataset
from src.geometry_processing import get_atom_features, knn_atoms
import torch
import gzip
from pathlib import Path
from torch.utils.data import random_split
from torch.utils.data import DataLoader
import torch.nn as nn
from src.nn_model import Amber_NN

_ = torch.manual_seed(142)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

protein = ['6BOY_BC', '7WUG_541']
pd = ProteinsDataset(protein)
d1 = pd[2]

N = 2555
train_dataset, test_dataset = random_split(d1, [len(d1) - N, N])

batch_size = 64
# Create data loaders.
train_dataloader = DataLoader(train_dataset, batch_size=batch_size)
test_dataloader = DataLoader(test_dataset, batch_size=batch_size)

model = Amber_NN().to(device)
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=1e-3)

