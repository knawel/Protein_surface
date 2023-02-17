from Bio.PDB import *
import numpy as np
from pathlib import Path
import gzip
import sys
import torch
from pykeops.torch import LazyTensor

# Local includes
from src.configs.general_opts import path_opts
from src.pdb.input_output import read_bfactor
from src.geometry_processing import get_atom_charge

# For trial with predict charges
# TODO add threshold as the constant

if len(sys.argv) <= 1:
    print(f"Usage: {sys.argv[0]} PDBID_AB or PDBID_ABC ...")
    print("A <- chain name")
    sys.exit(1)
else:
    chains_list = []
    pid, chains = sys.argv[1].strip().split('_')



if __name__ == '__main__':

    chain_dir = Path(path_opts["pdb_charges"])
    comp_dir = Path(path_opts["precomputed_dir"]) / pid

    for cid in chains:
        print(f'structure {pid}, chain {cid}')
        with gzip.GzipFile(comp_dir / f"{pid}_{cid}_points.npy.gz", "rb") as npz_f:
            P = torch.tensor(np.load(npz_f))

        # read new PDB
        atoms, atoms_chr = read_bfactor(pid, cid, chain_dir)
        print(atoms.shape, atoms_chr.shape)
        # calculate charges for points
        levels = get_atom_charge(atoms, P, atoms_chr)

        print('charges are computed')
        print(f'Shapes: charges {levels.shape}; atoms  {atoms.shape}; points {P.shape}')

        with gzip.GzipFile(comp_dir / f"{pid}_{cid}_charge.npy.gz", "wb") as npz_file:
            np.save(npz_file, levels)
