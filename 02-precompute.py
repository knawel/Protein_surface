import numpy as np
import sys
from pathlib import Path
# import torch
import itertools
import gzip
# Local includes
from src.configs.general_opts import path_opts
from src.geometry_processing import get_interface_for_pair, get_atom_features, atoms_to_points_normals
from src.features.data_encoding import numpy_structure


# TODO
# - think if I should not consider protein dimers
# - add filter for the too small PPI (from dMasif iface_valid_filter)


if len(sys.argv) <= 1:
    print(f"Usage: {sys.argv[0]} PDBID_AB or PDBID_ABC ...")
    print("A <- chain name")
    sys.exit(1)
else:
    chains_list = []
    pid, chains = sys.argv[1].strip().split('_')

if __name__ == '__main__':

    chain_dir = Path(path_opts["pdb_chain_dir"])
    # TODO add check for existing folder. If it exists, skip the computing.
    comp_dir = Path(path_opts["precomputed_dir"]) / pid
    comp_dir.mkdir(parents=True, exist_ok=True)

    P = dict()

    for cid in chains:
        print(f'structure {pid}, chain {cid}')
        p_filename = chain_dir / f"{pid}_{cid}.pdb"
        protein_encoded = numpy_structure(str(p_filename))
        xyz = protein_encoded[-1]  # coordinates

        # TODO re-write it for tensorflow
        xyz_pt = torch.Tensor(xyz)
        b = torch.zeros((xyz_pt.size()[0],), dtype=torch.int8)  # batch numbers, here is only one batch.
        P[cid], n, bm = atoms_to_points_normals(xyz_pt, b)

        all_features = np.hstack(protein_encoded[:-1])  # all features except coordinates
        features = get_atom_features(P[cid], xyz_pt,
                                     torch.Tensor(all_features), 16)

        with gzip.GzipFile(comp_dir / f"{pid}_{cid}_features.npy.gz", "wb") as npz_file:
            np.save(npz_file, features)
        with gzip.GzipFile(comp_dir / f"{pid}_{cid}_points.npy.gz", "wb") as npz_file:
            np.save(npz_file, P[cid])
        with gzip.GzipFile(comp_dir / f"{pid}_{cid}_normals.npy.gz", "wb") as npz_file:
            np.save(npz_file, n)

        print('features are computed')
        print(f'Shapes: features {all_features.shape}; atoms  {xyz.shape}; points {P[cid].shape}')

    if len(chains) > 1:
        chains_iter = itertools.combinations(chains, r=2)  # to get all uniq pairs
        for cid_pair in chains_iter:
            cid1, cid2 = cid_pair
            iface1, iface2 = get_interface_for_pair(P[cid1], P[cid2])

            if iface1.sum() > 30 and iface2.sum() > 30:  # here should be better iface check
                with gzip.GzipFile(comp_dir / f"{pid}_{cid1}{cid2}_iface.npy.gz", "wb") as npz_file:
                    np.save(npz_file, iface1)
                with gzip.GzipFile(comp_dir / f"{pid}_{cid2}{cid1}_iface.npy.gz", "wb") as npz_file:
                    np.save(npz_file, iface2)

    else:
        print(f'structure {pid} contains a single chain {chains}, iface computation skipped')
