import openmc
from contextlib import chdir
from pathlib import Path


def run():
    model = openmc.examples.pwr_pin_cell()

    model.settings.batches = 1000
    model.settings.inactive = 100
    model.settings.particles = 100_000

    nx = 17 * 4
    ny = 17 * 4
    bb = model.geometry.bounding_box
    mesh = openmc.RegularMesh()
    mesh.dimension = (nx, ny)
    mesh.lower_left = (bb.lower_left[0], bb.lower_left[1])
    mesh.upper_right = (bb.upper_right[0], bb.upper_right[1])
    mesh.width = [
        (bb.upper_right[0] - bb.lower_left[0]) / nx,
        (bb.upper_right[1] - bb.lower_left[1]) / ny,
    ]

    p_j = openmc.Tally(name="nufission")
    p_j.filters = [openmc.MeshFilter(mesh)]
    p_j.scores = ["nu-fission"]

    f_ij = openmc.Tally(name="f_ij")
    f_ij.filters = [openmc.MeshFilter(mesh), openmc.MeshBornFilter(mesh)]
    f_ij.scores = ["nu-fission"]
    model.tallies.append(p_j)
    model.tallies.append(f_ij)

    model.plots[0].color_by = "material"
    model.plots[0].pixels = (1000, 1000)

    model.plot_geometry()
    model.run()


if __name__ == "__main__":
    p = Path("pincell")
    p.mkdir(exist_ok=True)
    with chdir(p):
        run()
        # process()
