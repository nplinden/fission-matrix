import openmc
from contextlib import chdir
from pathlib import Path
import numpy as np


def run():
    model = openmc.Model()

    fuel = openmc.Material(name="Fuel")
    fuel.add_element("U", 1., enrichment=8.1)
    fuel.set_density("g/cm3", 20)

    R = 50
    root = openmc.Universe(cells=[openmc.Cell(region=-openmc.Sphere(r=R, boundary_type="vacuum"), fill=fuel)])

    model.materials = [fuel]
    model.geometry = openmc.Geometry(root=root)

    model.settings.batches = 1000
    model.settings.inactive = 100
    model.settings.particles = 100_000

    n_cell = 100
    sphere_volume = 4/3 * np.pi * R**3
    single_cell_volume = sphere_volume / n_cell
    r_grid = [0, pow(3 * single_cell_volume / 4 / np.pi, 1/3)]
    for _ in range(1, n_cell):
        inner_volume = 4/3 * np.pi * (r_grid[-1])**3
        outer_volume = inner_volume + single_cell_volume
        outer_r = pow(3 * outer_volume / 4 / np.pi, 1/3)
        r_grid.append(outer_r)
    print(r_grid)
    r_grid[-1] = R

    r_grid = np.linspace(0, 50, 100)
    mesh = openmc.SphericalMesh(r_grid=r_grid)

    p_j = openmc.Tally(name="nufission")
    p_j.filters = [openmc.MeshFilter(mesh)]
    p_j.scores = ["nu-fission"]

    f_ij = openmc.Tally(name="f_ij")
    f_ij.filters = [openmc.MeshFilter(mesh), openmc.MeshBornFilter(mesh)]
    f_ij.scores = ["nu-fission"]
    model.tallies.append(p_j)
    model.tallies.append(f_ij)

    model.run()


if __name__ == "__main__":
    p = Path("results")
    p.mkdir(exist_ok=True)
    with chdir(p):
        run()
