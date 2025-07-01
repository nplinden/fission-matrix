import openmc

model = openmc.examples.pwr_assembly()

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

# p_j = openmc.Tally(name="nufission")
# p_j.derivative = openmc.TallyDerivative(variable='temperature', material=1, nuclide="U235")
# p_j.filters = [openmc.MeshFilter(mesh)]
# p_j.scores = ["nu-fission"]

# f_ij = openmc.Tally(name="f_ij")
# f_ij.filters = [openmc.MeshFilter(mesh), openmc.MeshBornFilter(mesh)]
# f_ij.scores = ["nu-fission"]
# model.tallies.append(p_j)
# model.tallies.append(f_ij)

mesh_filter = openmc.MeshFilter(mesh)
meshborn_filter = openmc.MeshBornFilter(mesh)
tally = openmc.Tally()
tally.filters = [mesh_filter, meshborn_filter]
tally.nuclides = ['U235']
tally.scores = ['nu-fission']
tally.derivative = openmc.TallyDerivative(
    variable='nuclide_density', material=1, nuclide='U235'
)
tally.triggers = [openmc.Trigger('rel_err', 0.025)]
tally.triggers[0].scores = ['total', 'fission']
model.tallies = openmc.Tallies([tally])


model.plots[0].color_by = "material"
model.plots[0].pixels = (1000, 1000)

model.plot_geometry()
model.run()
