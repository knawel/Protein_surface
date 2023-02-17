import torch
from pathlib import Path
from torch.utils.data import Dataset
import glob
import gzip
# from torch_geometric.data import InMemoryDataset, Data, DataLoader
# from torch_geometric.transforms import Compose
import numpy as np
# from scipy.spatial.transform import Rotation
from src.configs.general_opts import path_opts

class ProteinRecord(Dataset):
    # Dataset for specific protein chain.
    # Read the protein chain, so input should be like 6BOY_C
    def __init__(self, pid_cid, normal=False):
        super(ProteinRecord).__init__()
        # Read file with descriptors
        comp_dir = Path(path_opts["precomputed_dir"])
        pid, cid = pid_cid.strip().split('_')

        # print(f'structure {pid}, chain {cid1}')
        with gzip.GzipFile(comp_dir / pid / f"{pid}_{cid}_points.npy.gz", "rb") as npz_f:
            P = torch.tensor(np.load(npz_f))
        with gzip.GzipFile(comp_dir / pid / f"{pid}_{cid}_features.npy.gz", "rb") as npz_f:
            feat = torch.tensor(np.load(npz_f))
        with gzip.GzipFile(comp_dir / pid / f"{pid}_{cid}_charge.npy.gz", "rb") as npz_f:
            charge = torch.tensor(np.load(npz_f))


        # all ifaces for B
        ifaces_files = glob.glob(f"{str(comp_dir)}/{pid}/{pid}_{cid}?_iface*")
        ifaces = []
        for i in ifaces_files:
            with gzip.GzipFile(i, "rb") as npz_f:
                ifaces.append(np.load(npz_f))
        if len(ifaces_files) > 1:
            ifaces_np = np.any(np.array(ifaces), axis=0)
        elif len(ifaces_files) == 1:
            ifaces_np = np.array(ifaces[0])
        else:
            ifaces_np = None

        self.p = P
        self.f = feat
        self.y = ifaces_np
        self.y_aux = charge
        self.pid = pid
        self.cid = cid
        if normal:
            pass
            # self.scaler = Normalizer()
            # self.X_mat = self.scaler.fit_transform(self.X_mat)

    def __len__(self):
        return len(self.p)

    def __getitem__(self, index):
        xyz = self.p[index, :]
        features = self.f[index, :]
        iface = self.y[index]
        y_aux = self.y_aux[index]
        # return xyz, features, iface
        return xyz, features, y_aux  # for testing charges


class ProteinsDataset(Dataset):
    # dataset, whcih contains several proteins, each protein can have several chains
    def __init__(self, pid_cids_list):
        super(ProteinsDataset).__init__()
        self.data = []
        for i in pid_cids_list:
            pid, chains = i.strip().split('_')
            for cid in chains:
                prot_rec = ProteinRecord(f'{pid}_{cid}')
                self.data.append(prot_rec)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        prot_rec = self.data[index]
        return prot_rec


class AllVertices(Dataset):
    # all combined proteins as flat vertices
    def __init__(self, pid_cids_list):
        super(AllVertices).__init__()
        self.p = []
        self.f = []
        self.y_aux = []
        self.id_list = dict()

        for i in pid_cids_list:
            pid, chains = i.strip().split('_')
            for cid in chains:
                prot_rec = ProteinRecord(f'{pid}_{cid}')
                self.p.append(prot_rec.p)
                self.f.append(prot_rec.f)
                self.y_aux.append(prot_rec.y_aux)
                self.id_list[f'{pid} {cid}'] = len(prot_rec.y_aux)
        self.p = torch.cat(self.p, dim=0)
        self.f = torch.cat(self.f, dim=0)
        self.y_aux = torch.cat(self.y_aux, dim=0)

    def __len__(self):
        return len(self.y_aux)

    def __getitem__(self, index):
        xyz = self.p[index, :]
        features = self.f[index, :]
        y_aux = self.y_aux[index]
        return features, y_aux

    def info(self):
        return self.id_list

