import os
import numpy as np
from pathlib import Path

input_files = ["u.txt", "d3u.txt"]
output_dir = Path("results/analysis")
output_dir.mkdir(parents=True, exist_ok=True)

output_eqs_u = output_dir / "u_eqs.txt"
output_eqs_d3u = output_dir / "d3u_eqs.txt"
output_lattice_u = output_dir / "u_lattice.txt"
output_lattice_d3u = output_dir / "d3u_lattice.txt"

def process_file(filename, output_eqs, output_lattice):
    path = Path(filename)
    if not path.exists():
        print(f"File {path} does not exist.")
        return

    with open(path, 'r') as f:
        lines = f.readlines()

    datasets = {}
    for line in lines:
        parts = line.strip().split()
        if len(parts) < 2:
            continue
        x, j = parts[0:2]
        try:
            x = float(x)
            j = float(j)
        except ValueError:
            continue

        y_vals = []
        for val in parts[2:]:
            if val == "error":
                y_vals.append(None)
            else:
                try:
                    y_vals.append(float(val))
                except ValueError:
                    y_vals.append(None)

        if x not in datasets:
            datasets[x] = []
        datasets[x].append((j, *y_vals))

    with open(output_eqs, 'w') as eqs_f, open(output_lattice, 'w') as lat_f:
        for x in sorted(datasets):
            data = np.array(datasets[x], dtype=object)
            j_vals = data[:, 0]
            y_minima = []

            eqs_f.write(f"{x:.1f}\n")
            for col in range(1, 4):
                y_col = []
                j_col = []
                for i in range(len(j_vals)):
                    y_val = data[i, col]
                    if y_val is not None and isinstance(y_val, float) and np.isfinite(y_val):
                        j_col.append(j_vals[i])
                        y_col.append(y_val)

                if len(j_col) < 4:
                    eqs_f.write("Error! insufficient valid data for fit!\n")
                    y_minima.append("Error")
                    continue

                rounded_y = np.round(y_col, 4)
                unique_vals, counts = np.unique(rounded_y, return_counts=True)
                if counts.max() > len(y_col) / 2:
                    eqs_f.write("Error! all y values are the same!\n")
                    y_minima.append("Error")
                    continue

                try:
                    coeffs = np.polyfit(j_col, y_col, 3)
                    p = np.poly1d(coeffs)
                    eqs_f.write(f"y = {coeffs[0]:.8f}*x^3 + {coeffs[1]:.8f}*x^2 + {coeffs[2]:.8f}*x + {coeffs[3]:.8f}\n")
                    dp = p.deriv()
                    critical_points = dp.r
                    real_crit = critical_points[np.isreal(critical_points)].real

                    eqs_f.write(f"# J range: {min(j_col):.8f} to {max(j_col):.8f}\n")
                    eqs_f.write(f"# Critical points: {', '.join([f'{val:.8f}' for val in real_crit])}\n")

                    min_val = None
                    min_j_val = None
                    for val in real_crit:
                        if min(j_col) <= val <= max(j_col):
                            if min_val is None or p(val) < min_val:
                                min_val = p(val)
                                min_j_val = val
                    if min_j_val is not None:
                        eqs_f.write(f"{min_j_val:.8f} {min_val:.8f}\n")
                        y_minima.append(f"{min_j_val:.8f}")
                    else:
                        eqs_f.write("Error! no valid minimum found!\n")
                        y_minima.append("Error")
                except Exception as e:
                    eqs_f.write(f"Fit failed: {str(e)}\n")
                    y_minima.append("Error")

            lat_f.write(f"{x:5.1f}  {y_minima[0]:>14}  {y_minima[1]:>14}  {y_minima[2]:>14}\n")

clean_dir = Path("results/clean")
process_file(clean_dir / "u.txt", output_eqs_u, output_lattice_u)
process_file(clean_dir / "d3u.txt", output_eqs_d3u, output_lattice_d3u)

print("Analysis complete. Output written to:")
print(f"- {output_eqs_u}")
print(f"- {output_eqs_d3u}")
print(f"- {output_lattice_u}")
print(f"- {output_lattice_d3u}")
