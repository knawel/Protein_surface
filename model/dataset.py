import numpy as np
from pathlib import Path
import gzip

from src.configs.general_opts import path_opts


def read_item(pid, cid):
    comp_dir = Path(path_opts["precomputed_dir"])

    with gzip.GzipFile(comp_dir / pid / f"{pid}_{cid}_points.npy.gz", "rb") as npz_f:
        P = np.load(npz_f)
    with gzip.GzipFile(comp_dir / pid / f"{pid}_{cid}_features.npy.gz", "rb") as npz_f:
        feat = np.load(npz_f)
    with gzip.GzipFile(comp_dir / pid / f"{pid}_{cid}_charge.npy.gz", "rb") as npz_f:
        charge = np.load(npz_f)
    return P, feat, charge


def read_list(pid_cids_list):
    P = None
    feat = None
    charge = None
    for i in pid_cids_list:
        pid, chains = i.strip().split('_')
        for cid in chains:
            if P is not None:
                P1, feat1, charge1 = read_item(pid, cid)
                P = np.vstack([P, P1])
                feat = np.vstack([feat, feat1])
                charge = np.hstack([charge, charge1])

            else:
                P, feat, charge = read_item(pid, cid)
    # print(f"Sizes: points {P.shape}; features {feat.shape}; charges {charge.shape}")
    return P, feat, charge
