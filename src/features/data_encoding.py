import numpy as np
from Bio.PDB import *
import numpy as np
from src.configs.chemistry import std_elements, std_names, std_resnames



def onehot(x, v):
    m = (x.reshape(-1, 1) == np.array(v).reshape(1,-1))
    return np.concatenate([m, ~np.any(m, axis=1).reshape(-1,1)], axis=1)


def encode_features(structure):
    # charge features
    qe = onehot(structure['element'], std_elements).astype(np.float32)
    qr = onehot(structure['resname'], std_resnames).astype(np.float32)
    qn = onehot(structure['name'], std_names).astype(np.float32)

    return [qe, qr, qn]


def numpy_structure(protein_filename):
    parser = PDBParser()
    structure = parser.get_structure('structure', protein_filename)
    atoms = structure.get_atoms()
    strucure_dict = dict()
    strucure_dict['element'] = []
    strucure_dict['resname'] = []
    strucure_dict['name'] = []
    strucure_dict['coordinates'] = []

    for atom in atoms:
        strucure_dict['resname'].append(atom.get_parent().get_resname())
        strucure_dict['name'].append(atom.get_name())
        strucure_dict['element'].append(atom.element)
        strucure_dict['coordinates'].append(atom.get_coord())
    strucure_dict['resname'] = np.array(strucure_dict['resname'])
    strucure_dict['name'] = np.array(strucure_dict['name'])
    strucure_dict['element'] = np.array(strucure_dict['element'])
    strucure_dict['coordinates'] = np.array(strucure_dict['coordinates'])
    a = encode_features(strucure_dict)
    a.append(strucure_dict['coordinates'])

    return a  # np.hstack(a)

