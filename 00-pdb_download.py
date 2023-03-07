import pathlib
import os
import sys
from pathlib import Path
import argparse
from src.pdb.input_output import get_single

# Local includes
from src.configs.general_opts import path_opts

# input arguments:
parser = argparse.ArgumentParser(description='Download and prepare PDB file')
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

pdb_dir = Path(path_opts['pdb_dir'])
chain_dir = Path(path_opts['pdb_chain_dir'])
tmp_dir = Path(path_opts["tmp_dir"])
pdb_dir.mkdir(parents=True, exist_ok=True)
chain_dir.mkdir(parents=True, exist_ok=True)


if __name__ == '__main__':
    args = parser.parse_args()
    if args.pdb != '':
        pdb = args.pdb.split('_')
        chains = pdb[1]
        pid = pdb[0]
        get_single(pid, chains, pdb_dir, chain_dir, tmp_dir)

    elif args.pdb_list != '':
        with open(args.pdb_list) as f:
            pdb_list = f.read().splitlines()
        for ent in pdb_list:
            if ent[0] != '#':
                pdb = ent.split('_')
                chains = pdb[1]
                pid = pdb[0]
                pid = pid
                get_single(pid, chains, pdb_dir, chain_dir, tmp_dir)
            else:
                pass
    else:
        parser.print_help(sys.stderr)
        sys.exit(1)
        # raise ValueError('Must specify PDB or PDB list')

    # remove "obsolete" folder, it's created by biopyton
    obs_path = Path('obsolete')
    try:
        os.rmdir(obs_path)
    except FileNotFoundError:
        print(f"{obs_path} directory not found.")
