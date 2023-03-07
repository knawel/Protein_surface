from Bio.PDB import PDBParser, StructureBuilder, Selection, PDBIO, PDBList
from Bio.PDB.PDBIO import Select
from pathlib import Path
import gzip
import itertools

from src.pdb.operations import protonate
from src.features.data_encoding import numpy_structure
from src.geometry_processing import get_interface_for_pair, get_atom_features, atoms_to_points_normals
from src.geometry_processing import get_atom_charge

import torch
import numpy as np


# Exclude disordered atoms.
class NotDisordered(Select):
    """
    A Select class that filters out disordered atoms and those with alternate location indicators other than "A" or "1"
    """

    def accept_atom(self, atom):
        """
        check if an atom is accepted or not
        """
        return not atom.is_disordered() or atom.get_altloc() == "A" or atom.get_altloc() == "1"


def extractPDB(in_pdb_file, out_pdb_file, chain_ids=None):
    """
    Extract the specified chains from a PDB file and save them to a new PDB file.

    Parameters
    ----------
    in_pdb_file : str
        The path of the PDB file to read.
    out_pdb_file : str
        The path of the PDB file to write.
    chain_ids : Optional[List[str]], optional
        The list of chains to extract, by default None

    Returns
    -------
    None

    TODO
    - Check the necessity of the modified amino acid part
    - Add Heteroatoms (now it is skipped due to `if het[0] == " ":`
    - save as compressed file
    """

    parser = PDBParser(QUIET=True)
    struct = parser.get_structure(in_pdb_file, in_pdb_file)
    model = Selection.unfold_entities(struct, "M")[0]
    # chains = Selection.unfold_entities(struct, "C")

    # Select residues to extract and build new structure
    structBuild = StructureBuilder.StructureBuilder()
    structBuild.init_structure("output")
    structBuild.init_seg(" ")
    structBuild.init_model(0)
    outputStruct = structBuild.get_structure()

    # Load a list of non-standard amino acid names -- these are
    # typically listed under HETATM, so they would be typically
    # ignored by the original algorithm
    # modified_amino_acids = find_modified_amino_acids(in_pdb_file)

    for chain in model:
        if (
                chain_ids is None
                or chain.get_id() in chain_ids
        ):
            structBuild.init_chain(chain.get_id())
            for residue in chain:
                het = residue.get_id()
                if het[0] == " ":
                    outputStruct[0][chain.get_id()].add(residue)
                # elif het[0][-3:] in modified_amino_acids:
                #     outputStruct[0][chain.get_id()].add(residue)

    # Output the selected residues
    pdbio = PDBIO()
    pdbio.set_structure(outputStruct)
    pdbio.save(out_pdb_file, select=NotDisordered())


def get_single(pdb_id: str, chains: str, pdb_dir: Path, chain_dir: Path, tmp_dir: Path):

    protonated_file = pdb_dir / f"{pdb_id}.pdb"
    if not protonated_file.exists():
        # Download pdb
        pdbl = PDBList()
        pdb_filename = pdbl.retrieve_pdb_file(pdb_id, pdir=str(tmp_dir), file_format='pdb')
        # Protonate with reduce, if hydrogens included.
        # - Always protonate as this is useful for charges. If necessary ignore hydrogens later.
        protonate(pdb_filename, protonated_file)

    pdb_filename = protonated_file
    # Extract chains of interest.
    for chain in chains:
        out_filename = chain_dir / f"{pdb_id}_{chain}.pdb"  # change to *tmp* when don't need anymore
        extractPDB(str(pdb_filename), str(out_filename), chain)
        # protein = load_structure_np(out_filename, center=False)
        # with gzip.GzipFile(geom_dir / f"{pdb_id}_{chain}_atomxyz.npy.gz", "wb") as npz_file:
        #     np.save(npz_file, protein["xyz"])
        # with gzip.GzipFile(geom_dir / f"{pdb_id}_{chain}_atomtypes.npy.gz", "wb") as npz_file:
        #     np.save(npz_file, protein["types"])


def read_bfactor(pid_i, cid_i, path_to_chains):
    parser = PDBParser()
    structure = parser.get_structure("structure", path_to_chains / f"{pid_i}_{cid_i}.pdb")
    xyz = []
    b_factors = []
    atoms = structure.get_atoms()
    for atom in atoms:
        xyz.append(atom.get_coord())
        b_factors.append(atom.get_bfactor())
    xyz = np.array(xyz)
    b_factors = np.array(b_factors)
    return xyz, b_factors

def write_precomputed(pid, chains, paths):

    chain_dir = Path(paths["pdb_chain_dir"])
    # TODO add check for existing folder. If it exists, skip the computing.
    comp_dir = Path(paths["precomputed_dir"]) / pid
    comp_dir.mkdir(parents=True, exist_ok=True)

    protein = dict()
    for cid in chains:
        print(f'structure {pid}, chain {cid}')
        p_filename = chain_dir / f"{pid}_{cid}.pdb"
        protein_encoded = numpy_structure(str(p_filename))
        xyz = protein_encoded[-1]  # coordinates

        # TODO re-write it for tensorflow
        xyz_pt = torch.Tensor(xyz)
        b = torch.zeros((xyz_pt.size()[0],), dtype=torch.int8)  # batch numbers, here is only one batch.
        protein[cid], n, bm = atoms_to_points_normals(xyz_pt, b)

        all_features = np.hstack(protein_encoded[:-1])  # all features except coordinates
        features = get_atom_features(protein[cid], xyz_pt,
                                     torch.Tensor(all_features), 16)

        with gzip.GzipFile(comp_dir / f"{pid}_{cid}_features.npy.gz", "wb") as npz_file:
            np.save(npz_file, features)
        with gzip.GzipFile(comp_dir / f"{pid}_{cid}_points.npy.gz", "wb") as npz_file:
            np.save(npz_file, protein[cid])
        with gzip.GzipFile(comp_dir / f"{pid}_{cid}_normals.npy.gz", "wb") as npz_file:
            np.save(npz_file, n)

        print('features are computed')
        print(f'Shapes: features {all_features.shape}; atoms  {xyz.shape}; points {protein[cid].shape}')

    if len(chains) > 1:
        chains_iter = itertools.combinations(chains, r=2)  # to get all uniq pairs
        for cid_pair in chains_iter:
            cid1, cid2 = cid_pair
            iface1, iface2 = get_interface_for_pair(protein[cid1], protein[cid2])

            if iface1.sum() > 30 and iface2.sum() > 30:  # here should be better iface check
                with gzip.GzipFile(comp_dir / f"{pid}_{cid1}{cid2}_iface.npy.gz", "wb") as npz_file:
                    np.save(npz_file, iface1)
                with gzip.GzipFile(comp_dir / f"{pid}_{cid2}{cid1}_iface.npy.gz", "wb") as npz_file:
                    np.save(npz_file, iface2)

    else:
        print(f'structure {pid} contains a single chain {chains}, iface computation skipped')


def write_charges(pid, chains, paths):
    chain_dir = Path(paths["pdb_charges"])
    comp_dir = Path(paths["precomputed_dir"]) / pid

    for cid in chains:
        print(f'structure {pid}, chain {cid}')
        with gzip.GzipFile(comp_dir / f"{pid}_{cid}_points.npy.gz", "rb") as npz_f:
            p = torch.tensor(np.load(npz_f))

        # read new PDB
        atoms, atoms_chr = read_bfactor(pid, cid, chain_dir)
        print(atoms.shape, atoms_chr.shape)
        # calculate charges for points
        levels = get_atom_charge(atoms, p, atoms_chr)

        print('charges are computed')
        print(f'Shapes: charges {levels.shape}; atoms  {atoms.shape}; points {p.shape}')

        with gzip.GzipFile(comp_dir / f"{pid}_{cid}_charge.npy.gz", "wb") as npz_file:
            np.save(npz_file, levels)

