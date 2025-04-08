import os
import shutil
from pathlib import Path

# Define input and output paths
input_poscar = Path("input/input.txt")
final_dir = Path("final")
final_dir.mkdir(parents=True, exist_ok=True)

# Create subdirectories for u and d3u
u_dir = final_dir / "u"
d3u_dir = final_dir / "d3u"
u_dir.mkdir(parents=True, exist_ok=True)
d3u_dir.mkdir(parents=True, exist_ok=True)

# Log file path
log_path = Path("eqs_final.log")
log_path.unlink(missing_ok=True)  # Clear log on each run

# Function to read lattice file and return x values and scales
def read_lattice_file(file_path, log_file, label):
    x_vals, scale_vals = [], []
    errors = 0
    with open(file_path, 'r') as f, open(log_file, 'a') as log:
        log.write(f"Errors in {label}:\n")
        for line in f:
            if line.strip():
                parts = line.split()
                try:
                    x = float(parts[0])
                    scale = float(parts[1])
                    x_vals.append(x)
                    scale_vals.append(scale)
                except (IndexError, ValueError):
                    try:
                        u_str = parts[0]
                    except IndexError:
                        u_str = "Unknown"
                    log.write(f"{u_str} error found in scaling factor! Could not generate files!\n")
                    errors += 1
        if errors == 0:
            log.write("No errors found.\n")
        log.write("\n")
    return x_vals, scale_vals, errors

# Read from u_lattice.txt and d3u_lattice.txt
u_lattice_file = Path("results/analysis/u_lattice.txt")
d3u_lattice_file = Path("results/analysis/d3u_lattice.txt")

u_x_values, u_scales, u_errors = read_lattice_file(u_lattice_file, log_path, "u_lattice.txt")
d3u_x_values, d3u_scales, d3u_errors = read_lattice_file(d3u_lattice_file, log_path, "d3u_lattice.txt")

# INCAR templates
incar_template_u = """PREC=Accurate
ISTART=0
ICHARG=2
ISPIN=2
NCORE=4
KPAR=1
NBANDS=42
GGA=PE
##IVDW=11
LDAU=.FALSE.
LDAUTYPE=2
LDAUL={x_val} -1
LDAUU=2.0 0.0
ENCUT=750
NELM=9999
EDIFF=1E-05
ALGO=normal
EDIFFG=-1E-02
NSW=9999
IBRION=2
ISIF=2
ISYM=0
POTIM=0.1
LWAVE=F
LCHARG=F
ISMEAR=0
SIGMA=0.02
LMONO=T
LDIPOL=T
IDIPOL=4
"""

incar_template_d3u = """PREC=Accurate
ISTART=0
ICHARG=2
ISPIN=2
NCORE=4
KPAR=1
NBANDS=42
GGA=PE
IVDW=11
LDAU=.FALSE.
LDAUTYPE=2
LDAUL={x_val} -1
LDAUU=2.0 0.0
ENCUT=750
NELM=9999
EDIFF=1E-05
ALGO=normal
EDIFFG=-1E-02
NSW=9999
IBRION=2
ISIF=2
ISYM=0
POTIM=0.1
LWAVE=F
LCHARG=F
ISMEAR=0
SIGMA=0.02
LMONO=T
LDIPOL=T
IDIPOL=4
"""

# KPOINTS content
kpoints_content = """7x7x7
0
Monkhorst-Pack
7 7 7
0 0 0
"""

# Read original POSCAR
with open(input_poscar, 'r') as f:
    poscar_lines = f.readlines()

# Extract lattice vectors (assume standard POSCAR format)
a1 = list(map(float, poscar_lines[2].split()))
a2 = list(map(float, poscar_lines[3].split()))
a3 = list(map(float, poscar_lines[4].split()))

# Extract element list from POSCAR line 5
elements = poscar_lines[5].split()

# Define the POTCAR source directory
potcar_dir = Path("/home/e05/e05/c23091473/POTCAR")

# Function to create folders and write VASP input files
def create_vasp_inputs(base_dir, x_vals, scales, incar_template):
    for i, x in enumerate(x_vals):
        scale = scales[i]
        x_folder = base_dir / f"{x:.1f}"
        x_folder.mkdir(parents=True, exist_ok=True)

        # Write INCAR
        incar_path = x_folder / "INCAR"
        with open(incar_path, 'w') as incar_file:
            incar_file.write(incar_template.format(x_val=int(x)))

        # Write KPOINTS
        kpoints_path = x_folder / "KPOINTS"
        with open(kpoints_path, 'w') as kpoints_file:
            kpoints_file.write(kpoints_content)

        # Modify lattice vectors
        new_poscar_lines = poscar_lines.copy()
        new_poscar_lines[2] = f"{a1[0]*scale:.16f} {a1[1]:.16f} {a1[2]:.16f}\n"
        new_poscar_lines[3] = f"{a2[0]:.16f} {a2[1]*scale:.16f} {a2[2]:.16f}\n"
        new_poscar_lines[4] = f"{a3[0]:.16f} {a3[1]:.16f} {a3[2]*scale:.16f}\n"

        # Write POSCAR
        poscar_path = x_folder / "POSCAR"
        with open(poscar_path, 'w') as poscar_file:
            poscar_file.writelines(new_poscar_lines)

        # Create POTCAR by concatenating POTCAR_<element> files
        potcar_path = x_folder / "POTCAR"
        with open(potcar_path, 'wb') as potcar_file:
            for element in elements:
                element_path = potcar_dir / f"POTCAR_{element}"
                if not element_path.exists():
                    raise FileNotFoundError(f"POTCAR for element '{element}' not found at {element_path}")
                with open(element_path, 'rb') as elem_pot:
                    shutil.copyfileobj(elem_pot, potcar_file)

# Create inputs for u and d3u
create_vasp_inputs(u_dir, u_x_values, u_scales, incar_template_u)
create_vasp_inputs(d3u_dir, d3u_x_values, d3u_scales, incar_template_d3u)

# Print final result
total_errors = u_errors + d3u_errors
if total_errors > 0:
    print(f"Script completed with {total_errors} error(s). Check 'eqs_final.log' for details.")
else:
    print("Final VASP submission folders created successfully in final/u and final/d3u. No errors found.")
