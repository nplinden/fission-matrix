# An Exploration of Fission Matrices with OpenMC

The 0.15.0 release of OpenMC saw the addition of the `MeshBornFilter` tally filter, this allows OpenMC users to compute the space-discretized fission matrices in a very straighforward manner.

This article aims to give an overview of the building of a fission matrix, and translate theory into OpenMC instruction.

## Theory of Fission Matrices

# Théorie

Soit une simulation Monte-Carlo simulant $L$ histoires de neutron, on note $l$ le numéro de chaque histoire.
Un histoire individuelle comprend $C_l$ collision, on note $c$ le numéro de collision dans une histoire $l$.

Lors de la collision $c$ d'une histoire $l$, la probabilité que la collision soit un évenement de fission vaut

$$p_\mathrm{f} = \frac{\Sigma_\mathrm{f}}{\Sigma_\mathrm{tot}}$$

Dans le cadre d'une simulation non-analogue, un poid $w_\mathrm{l,c}$ est associé au neutron entrant.
Ce poid entrant doit être multiplié par la probabilité de fission et par la multiplicité des neutrons $\nu$ pour obtenir le poid d'un neutron naissant au site de fission correspondant à l'emplacement de la collision dans l'espace des phases. On note $f_\mathrm{l,c}$ le poid des neutrons nés du site de fission $\left(l,c\right)$

$$f_\mathrm{l,c} = w_\mathrm{l,c} \frac{\nu \Sigma_f}{\Sigma_\mathrm{tot}}$$

Ce poid représente le nombre de neutrons nés à ce site de fission par particule simulé.
La somme sur $l$ et $c$ de ce poid est égal au facteur de multiplication $k_\mathrm{eff}$ par définition:

$$\sum_{l,c} f_{l,c} = k_\mathrm{eff}$$

Imaginons maintenant la partition de l'espace des phases en $M$ mailles $z_m$. 
On peut définir la grandeur $z(l, c)$ qui désigne la maille de laquelle a lieu la collision $c$ de l'histoire $l$.
La maille d'origine d'une histoire est donc naturellement identifiée par $z(l, 0)$.

Pour décrire le nombre de neutrons qui naissent dans une maille $z_i$ et qui sont issus d'un site de fission créé par une histoire débutant dans une maille $j$, on peut écrire

$$F(i,j) = \sum_{\begin{subarray}{c}
        l, c \\
        z(l, c) = i \\
        z(l, 0) = j
        \end{subarray}}{f_{c, l}}$$

On peut également définir l'intensité de la source de fission en une maille $j$ par

$$t(j) = \sum_{\begin{subarray}{c} 
    l \\
    z(l, 0) = j
\end{subarray}}{w_{l, 0}}$$

On définit les coefficient de la matrice de fission comme

$$H(i, j) = \frac{F(i, j)}{t(i, j)}$$

# Avec OpenMC

L'objet de cette partie est de faire le lien entre les grandeurs utilisées pour construire la matrice de fission et les outils disponibles dans le code OpenMC.

Le compte $f_{l,c}$ des neutrons né dans un site de fission généré par une colision $(l,c)$ individuelle n'est pas directement accessible, mais la somme des $f_{l,c}$ peut l'être sur tout ou partie de l'espace des phases au travers du score ``nu-fission``, associé à des filtres géométriques ou énergétiques.

Si aucun filtre n'est appliqué, on obtient la somme 

$$\sum_{l,c} f_{l,c}$$

qui est égale au $k_\mathrm{eff}$ par définition.

Le code associé est:

```python
keff = openmc.Tally(name="keff")
keff.scores = ["nu-fission"]
```

Si un filtre géométrique est appliqué avec un maillage, on obtient 

$$t(j) = \sum_{\begin{subarray}{c} 
    l \\
    z(l, 0) = j
\end{subarray}}{w_{l, 0}}\quad \forall j \in \mathrm{maillage} $$

Si le maillage couvre tout l'espace des phases, on doit pouvoir vérifier que 

$$\sum_{j} t(j) = k_\mathrm{eff}$$

Le code associé est:

```python
mesh = ...
t_j = openmc.Tally(name="t_j")
t_j.scores = ["nu-fission"]
t_j.filters = [openmc.MeshFilter(mesh)]
```

L'obtention des $f_{c,l}$ proprement dit se fait en utilisant le filtre ``MeshBornFilter``

```python
mesh = ...
f_ij = openmc.Tally(name="fij")
f_ij.scores = ["nu-fission"]
f_ij.filters = [
    openmc.MeshFilter(mesh),
    openmc.MeshBornFilter(mesh),
]
```%        

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