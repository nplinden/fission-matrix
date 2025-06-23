# An Exploration of Fission Matrices with OpenMC

The 0.15.0 release of OpenMC saw the addition of the `MeshBornFilter` tally filter, this allows OpenMC users to compute the space-discretized fission matrices in a very straighforward manner.

This article aims to give an overview of the building of a fission matrix, and translate theory into OpenMC instruction.

## Theory of Fission Matrices

## An example with OpenMC

### Mesh Definition

```python
bb = model.geometry.bounding_box
mesh = openmc.RegularMesh()
mesh.dimension = (17, 17)
mesh.lower_left = (bb.lower_left[0], bb.lower_left[1])
mesh.upper_right = (bb.upper_right[0], bb.upper_right[1])
mesh.width = [
    (bb.upper_right[0] - bb.lower_left[0]) / 17,
    (bb.upper_right[1] - bb.lower_left[1]) / 17,
]
```

### Tally Definition

```python
p_j = openmc.Tally(name="nufission")
p_j.filters = [openmc.MeshFilter(mesh)]
p_j.scores = ["nu-fission"]

f_ij = openmc.Tally(name="f_ij")
f_ij.filters = [openmc.MeshFilter(mesh), openmc.MeshBornFilter(mesh)]
f_ij.scores = ["nu-fission"]
model.tallies.append(p_j)
model.tallies.append(f_ij)
```

### Post-Treatment

```python

```

![f_ij matrix](animated.gif)