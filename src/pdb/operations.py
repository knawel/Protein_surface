from pathlib import Path
import subprocess



def protonate(in_pdb_file: str, out_pdb_file: Path):
    """
    Protonate and deprotonate a PDB file.

    Parameters
    ----------
    in_pdb_file : str
        The input PDB file.
    out_pdb_file : str
        The output PDB file with protonated structure.

    Notes
    -----
    This function uses the 'reduce' to protonate and deprotonate a PDB file. It first calls reduce
    with the '-Trim' option to remove protons, then calls it again with the '-HIS' option to add back protons.
    """

    # TODO
    # - change the protonation of the small molecules, acpype instead of reduce.

    # remove Hs
    result = subprocess.run(["reduce", "-Trim", in_pdb_file], capture_output=True)
    stdout = result.stdout
    with open(out_pdb_file, "w") as outfile:
        outfile.write(stdout.decode('utf-8').rstrip())
    # add H
    result_H = subprocess.run(["reduce", "-HIS", out_pdb_file], capture_output=True)
    stdout_H = result_H.stdout
    with open(out_pdb_file, "w") as outfile:
        outfile.write(stdout_H.decode('utf-8'))