# -*- coding: utf-8 -*-
"""
Created on Fri Mar 21 23:55:19 2025

@author: DR_lucKY
"""

import matplotlib.pyplot as plt
import numpy as np

# Coordenadas
puntos = np.array([
    [74, 34, 0],
    [244, 200, 55],
    [195, 428, 85],
    [354, 342, 88],
    [392, 356, 94],
    [431, 334, 94],
    [495, 272, 95]
])

# Crear figura 3D
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Graficar puntos
ax.scatter(puntos[:,0], puntos[:,1], puntos[:,2], c='red', s=50)

# Etiquetas y conexiones
for i, (x, y, z) in enumerate(puntos):
    ax.text(x, y, z, f'P{i+1}', fontsize=8)

# Opcional: Conectar puntos en orden (si hay una secuencia)
ax.plot(puntos[:,0], puntos[:,1], puntos[:,2], linestyle='--', alpha=0.5)

# Ajustes visuales
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.title('Coordenadas 3D de la red')
plt.show()