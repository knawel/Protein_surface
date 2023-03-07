import argparse
import sys
from pathlib import Path
import torch
from torch.utils.data import random_split
from torch.utils.data import DataLoader
import torch.nn as nn
# parameters
from src.data import AllVertices
from src.nn_model import AmberNN
from run_opts import config_runtime

# input arguments:
parser = argparse.ArgumentParser(description='Run NN model and save it')
parser.add_argument(
    "pdb_list",
    type=str,
    default='',
    help="A text file that includes a list of PDB codes along with chains, example 1ABC_AB"
    # required=True
)
# arguments
args = parser.parse_args()
# configs
n_cls = 3  # number of classes
conf_dev = config_runtime['device']
train_f = config_runtime['train_frac']
seed = config_runtime['seed']
learning_rate = config_runtime['learning_rate']
batch_size = config_runtime['batch_size']
hid_size = config_runtime['hidden_size']
log_step = config_runtime['log_step']
epochs = config_runtime['num_epochs']
run_name = config_runtime['run_name']


# Read list of the proteins
proteins = []
with open(args.pdb_list, 'r') as iFile:
    for i in iFile:
        if i[0] != '#':
            proteins.append(i.strip())

# print(proteins)
_ = torch.manual_seed(seed)
device = torch.device(conf_dev)

pd = AllVertices(proteins)
n_features = pd[0][0].shape[0]
train_dataset, test_dataset = random_split(pd, [train_f, 1.0 - train_f],
                                           generator=torch.Generator().manual_seed(seed))

# Create data loaders.
train_dataloader = DataLoader(train_dataset, batch_size=batch_size)
test_dataloader = DataLoader(test_dataset, batch_size=batch_size)

model = AmberNN(n_features, n_cls, hid_size).to(device)
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)


def train_loop(dataloader, model, loss_fn, optimizer):
    size = len(dataloader.dataset)
    for batch, (X, y) in enumerate(dataloader):
        # Compute prediction and loss
        X = X.to(device)
        y = y.to(device)
        pred = model(X)
        loss = loss_fn(pred, y)
        # Backpropagation
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if batch % log_step == 0:
            loss, current = loss.item(), (batch + 1) * len(X)
            sys.stdout.write(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]\n")


def test_loop(dataloader, model, loss_fn):
    size = len(dataloader.dataset)
    num_batches = len(dataloader)
    test_loss, correct = 0, 0

    with torch.no_grad():
        for X, y in dataloader:
            X = X.to(device)
            y = y.to(device)
            pred = model(X)
            test_loss += loss_fn(pred, y).item()
            correct += (pred.argmax(1) == y).type(torch.float).sum().item()
        test_loss /= num_batches
    correct /= size
    sys.stdout.write(f"Test Error: \n Accuracy: {(100 * correct):>0.1f}%, Avg loss: {test_loss:>8f} \n")


for t in range(epochs):
    sys.stdout.write(f"Epoch {t + 1}\n-------------------------------\n")
    train_loop(train_dataloader, model, loss_fn, optimizer)
    test_loop(test_dataloader, model, loss_fn)
sys.stdout.write("\nDone!\n")
# sys.stdout.flush()
torch.save(model.state_dict(), f"{run_name}.pt")
