import numpy as np
import sys
from pathlib import Path
import torch
import itertools
import gzip
import argparse
# Local includes
from src.configs.general_opts import path_opts
from src.pdb.input_output import write_precomputed
from src.geometry_processing import get_interface_for_pair, get_atom_features, atoms_to_points_normals
from src.features.data_encoding import numpy_structure


# TODO
# - think if I should not consider protein dimers
# - add filter for the too small PPI (from dMasif iface_valid_filter)


# input arguments:
parser = argparse.ArgumentParser(description='Precompute parameters')
parser.add_argument(
    "--pdb",
    type=str,
    default='',
    help="PDB code along with chains to extract, example 1ABC_AB",
    required=False
)
parser.add_argument(
    "--pdb_list",
    type=str,
    default='',
    help="A text file that includes a list of PDB codes along with chains, example 1ABC_AB",
    required=False
)

if __name__ == '__main__':

    args = parser.parse_args()
    if args.pdb != '':
        pass
        pdb = args.pdb.split('_')
        chains = pdb[1]
        pid = pdb[0]
        write_precomputed(pid, chains, path_opts)

    elif args.pdb_list != '':
        with open(args.pdb_list) as f:
            pdb_list = f.read().splitlines()
        for ent in pdb_list:
            if ent[0] != '#':
                pdb = ent.split('_')
                chains = pdb[1]
                pid = pdb[0]
                pid = pid
                write_precomputed(pid, chains, path_opts)
            else:
                pass
    else:
        parser.print_help(sys.stderr)
        sys.exit(1)
