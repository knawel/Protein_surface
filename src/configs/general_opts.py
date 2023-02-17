import tempfile

path_opts = {}
# Default directories
path_opts["pdb_dir"] = "/images/images_calc/Protein_surface/data/data_preparation/00-pdbs/"
path_opts["pdb_chain_dir"] = "/images/images_calc/Protein_surface/data/data_preparation/00a-pdbs_chains/" # don't need it?
path_opts["pdb_charges"] = "/images/images_calc/Protein_surface/data/data_preparation/00b-pdb_charge"
path_opts["precomputed_dir"] = "/images/images_calc/Protein_surface/data/data_preparation/02-precomputed"
path_opts["tmp_dir"] = tempfile.gettempdir()




