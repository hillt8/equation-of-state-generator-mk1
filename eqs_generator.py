import os
import numpy as np
import shutil

# === Constants ===
TEMPLATE_DIR = "input"
BASE_POSCAR = os.path.join(TEMPLATE_DIR, "input.txt")
POTCAR_SOURCE_DIR = "/home/e05/e05/c23091473/POTCAR"

# === Generate scaled POSCAR ===
def generate_scaled_poscar(base_poscar_path, output_path, direction, scale):
    with open(base_poscar_path, "r") as f:
        lines = f.readlines()

    direction_index = {"x": 2, "y": 3, "z": 4}[direction]
    vec = [float(x) for x in lines[direction_index].split()]
    scaled_vec = [f"{x * scale:.16f}" for x in vec]
    lines[direction_index] = " ".join(scaled_vec) + "\n"

    with open(os.path.join(output_path, "POSCAR"), "w") as f:
        f.writelines(lines)

VALENCE_ELECTRONS = {
    "H": 1, "He": 2,
    "Li": 1, "Be": 2, "B": 3, "C": 4, "N": 5, "O": 6, "F": 7,
    "Na": 1, "Mg": 2, "Al": 3, "Si": 4, "P": 5, "S": 6, "Cl": 7,
    "K": 1, "Ca": 2,
    "Sc": 3, "Ti": 4, "V": 5, "Cr": 6, "Mn": 7, "Fe": 8, "Co": 9, "Ni": 10, "Cu": 11, "Zn": 12,
    "Ga": 3, "Ge": 4, "As": 5, "Se": 6, "Br": 7,
    "Y": 3, "Zr": 4, "Nb": 5, "Mo": 6, "Tc": 7, "Ru": 8, "Rh": 9, "Pd": 10,
    "Ag": 11, "Cd": 12, "In": 3, "Sn": 4, "Sb": 5, "Te": 6, "I": 7
}

def estimate_nbands(poscar_path, multiplier=1.3):
    with open(poscar_path, "r") as f:
        lines = f.readlines()
    elements = lines[5].split()
    counts = list(map(int, lines[6].split()))

    total_valence = 0
    for element, count in zip(elements, counts):
        valence = VALENCE_ELECTRONS.get(element, 10)
        total_valence += valence * count

    nbands = int(total_valence * multiplier)
    return max(nbands, 1)

def generate_incar(u_value, output_path, base_dir, poscar_path):
    nbands = estimate_nbands(poscar_path)

    incar_lines = [
        "PREC=Accurate",
        "ISTART=0",
        "ICHARG=2",
        "ISPIN=2",
        "NCORE=4",
        "KPAR=1",
        f"NBANDS={nbands}",
        "GGA=PE",
        "IVDW=11" if "d3u" in base_dir else "",
        "LDAU=.TRUE.",
        "LDAUTYPE=2",
        "LDAUL=2 -1",
        f"LDAUU={u_value} 0.0",
        "ENCUT=750",
        "NELM=9999",
        "EDIFF=1E-05",
        "ALGO=normal",
        "EDIFFG=-1E-02",
        "NSW=9999",
        "IBRION=2",
        "ISIF=2",
        "ISYM=0",
        "POTIM=0.1",
        "LWAVE=F",
        "LCHARG=F",
        "ISMEAR=0",
        "SIGMA=0.02",
        "LMONO=T",
        "LDIPOL=T",
        "IDIPOL=4"
    ]

    incar_lines = [line for line in incar_lines if line]

    with open(os.path.join(output_path, "INCAR"), "w") as f:
        f.write("\n".join(incar_lines) + "\n")

# === Generate KPOINTS ===
def generate_kpoints(output_path):
    kpoints_content = """7x7x7
0
Monkhorst-Pack
7 7 7
0 0 0
"""
    with open(os.path.join(output_path, "KPOINTS"), "w") as f:
        f.write(kpoints_content)

# === Generate POTCAR ===
def generate_potcar_from_poscar(poscar_path, output_path, potcar_base_dir):
    with open(poscar_path, "r") as f:
        lines = f.readlines()

    elements_line = lines[5].strip()
    elements = elements_line.split()

    potcar_path = os.path.join(output_path, "POTCAR")
    with open(potcar_path, "wb") as outfile:
        for element in elements:
            potcar_file = os.path.join(potcar_base_dir, f"POTCAR_{element}")
            if not os.path.exists(potcar_file):
                raise FileNotFoundError(f"POTCAR file not found for element: {element}")
            with open(potcar_file, "rb") as infile:
                shutil.copyfileobj(infile, outfile)

# === Main logic ===
def create_vasp_folder_structure(base_dirs=["u", "d3u"], 
                                 u_values=np.arange(0.0, 10.1, 1.0), 
                                 scaling_range=(0.95, 1.10), 
                                 scaling_step=0.01):
    directions = ["x", "y", "z"]
    scaling_factors = np.round(np.arange(scaling_range[0], scaling_range[1] + scaling_step, scaling_step), 2)

    for base in base_dirs:
        for u in u_values:
            u_str = f"{u:.1f}"
            for direction in directions:
                for scale in scaling_factors:
                    scale_str = f"{scale:.2f}"
                    path = os.path.join(base, u_str, direction, scale_str)
                    os.makedirs(path, exist_ok=True)

                    # === Generate files ===
                    generate_scaled_poscar(BASE_POSCAR, path, direction, scale)
                    generate_kpoints(output_path=path)
                    generate_incar(u_value=u, output_path=path, base_dir=path, poscar_path=os.path.join(path, "POSCAR"))
                    generate_potcar_from_poscar(
                        poscar_path=os.path.join(path, "POSCAR"),
                        output_path=path,
                        potcar_base_dir=POTCAR_SOURCE_DIR
                    )

if __name__ == "__main__":
    create_vasp_folder_structure()
