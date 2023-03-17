import sys
import argparse

# Local includes
from src.configs.general_opts import path_opts
from src.pdb.input_output import extract_bfactor

# For trial with predict charges
# TODO add threshold as the constant

# input arguments:
parser = argparse.ArgumentParser(description='Precompute charges on surface and write it')
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
        extract_bfactor(pid, chains, path_opts, mode='logp')

    elif args.pdb_list != '':
        with open(args.pdb_list) as f:
            pdb_list = f.read().splitlines()
        for ent in pdb_list:
            if ent[0] != '#':
                pdb = ent.split('_')
                chains = pdb[1]
                pid = pdb[0]
                pid = pid
                extract_bfactor(pid, chains, path_opts, mode='logp')
            else:
                pass
    else:
        parser.print_help(sys.stderr)
        sys.exit(1)





