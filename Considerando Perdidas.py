# -*- coding: utf-8 -*-
"""
Created on Fri Mar 21 23:54:44 2025

@author: DR_lucKY
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Mar 21 22:54:53 2025

@author: DR_lucKY
"""

# Librerias Utilizadas
import pulp
import math
# DATOS DE ENTRADA
P = 7 # number of consumption points
Coord = [[74,34,0],[244,200,55],[195,428,85],[354,342,88],[392,356,94],[431,334,94],[495,272,95]] # point coordinates
L = [[0.0 for p in range(P)] for d in range(P)] # [m] distance between points
for p in range(P):
  for d in range(P):
    L[p][d] = math.sqrt((Coord[p][0]-Coord[d][0])**2+(Coord[p][1]-Coord[d][1])**2+(Coord[p][2]-Coord[d][2])**2)
ED = [300,1000,300,300,1000,300,200] # [Wh/day] energy demand para cada punto de consumo
PD = [200,500,200,200,500,200,150] # [W] power demand
AD = 3 # [days] required autonomy

# PANELES SOLARES
S = 3 # types of panels
ES = [217,326,434] # [Wh/day] energy of panels
PS = [50,75,100] # [W] power of panels
CS = [451,636,821] # [$] cost of panels
Z = 3 # types of panel controllers
PZ = [50,75,100] # [W] power of panel controllers
CZ = [67,81,95] # [$] cost of panel controllers

# TURBINAS EOLICOS
A = 2 # Types of wind
EA = [[95,445],[357,1460],[581,2135],[498,1889],[504,1913],[488,1856],[512,1926]]# energy of turbines en cada punto de consumo
PA = [300,1200] # [W] power of turbines
CA = [974,2737] # [$] cost of turbines
R = 2 # types of turbine controllers
PR = [420,1440] # [W] power of turbine controllers
CR = [165,285] # [$] cost of turbine controllers

# BATERIAS
B = 2 # types of batteries
EB = [1500,3000] # [Wh/day] capacity of batteries
CB = [225,325] # [$] cost of batteries

# INVERSORES
I = 2 # types of inverters
PI = [300,1000] # [W] power of inverters
CI = [377,1000] # [$] cost of inverters

# RED
CC = 3 # [$/m] cost of wires
CM = 50 # [] cost of meters
# PORECENTAJE DE PERDIDAS EN LA RED
loss = 0.03 # [pu]

# NO SE
M = 10000000 # very high value
xs = pulp.LpVariable.dicts("Panels",(range(P),range(S)),0,None,pulp.LpInteger)
xz = pulp.LpVariable.dicts("Panel controllers",(range(P),range(Z)),0,None,pulp.LpInteger)
xa = pulp.LpVariable.dicts("Turbines",(range(P),range(A)),0,None,pulp.LpInteger)
xr = pulp.LpVariable.dicts("Turbine controllers",(range(P),range(R)),0,None,pulp.LpInteger)
xb = pulp.LpVariable.dicts("Batteries",(range(P),range(B)),0,None,pulp.LpInteger)
xi = pulp.LpVariable.dicts("Inverters",(range(P),range(I)),0,None,pulp.LpInteger)
fe = pulp.LpVariable.dicts("Eflow",(range(P),range(P)),0,None,pulp.LpContinuous)
fp = pulp.LpVariable.dicts("Pflow",(range(P),range(P)),0,None,pulp.LpContinuous)
xg = pulp.LpVariable.dicts("Generators",range(P),0,1,pulp.LpInteger)
xc = pulp.LpVariable.dicts("Lines",(range(P),range(P)),0,1,pulp.LpInteger)
xm = pulp.LpVariable.dicts("Meters",range(P),0,1,pulp.LpInteger)

# OBJECTIVE FUNCTION
model = pulp.LpProblem("System",pulp.LpMinimize)
model += pulp.lpSum(CA[a]*xa[p][a] for p in range(P) for a in range(A)) \
    + pulp.lpSum(CR[r]*xr[p][r] for p in range(P) for r in range(R)) \
    + pulp.lpSum(CS[s]*xs[p][s] for p in range(P) for s in range(S)) \
    + pulp.lpSum(CZ[z]*xz[p][z] for p in range(P) for z in range(Z)) \
    + pulp.lpSum(CB[b]*xb[p][b] for p in range(P) for b in range(B)) \
    + pulp.lpSum(CI[i]*xi[p][i] for p in range(P) for i in range(I)) \
    + pulp.lpSum(CM*xm[p] for p in range(P)) \
    + pulp.lpSum(L[p][d]*CC*xc[p][d] for p in range(P) for d in range(P) if p!=d)

# CONSTRAINTS
# El numero de paneles xs esta limitado a un numero grande
for p in range(P):
  model += pulp.lpSum(xs[p][s] for s in range(S)) <= M*xg[p]
# Entre el generado solar y eolica esta limitado a la existencia o no de generacion en cada nodo
for p in range(P):
  model += pulp.lpSum(xa[p][a] for a in range(A)) + pulp.lpSum(xs[p][s] for s in range(S)) >= xg[p]
# ---- Balance nodal de energia desde el generador
for p in range(P):
  model += pulp.lpSum(fe[q][p] for q in range(P) if q!=p) + pulp.lpSum(ES[s]*xs[p][s] for s in range(S)) + pulp.lpSum(EA[p][a]*xa[p][a] for a in range(A)) >= ED[p]*(1+loss) + pulp.lpSum(fe[p][d] for d in range(P) if d!=p)
# ---- Balance noda de potencia desdel el inversor
for p in range(P):
  model += pulp.lpSum(fp[q][p] for q in range(P) if q!=p) + pulp.lpSum(PI[i]*xi[p][i] for i in range(I)) >= PD[p]*(1+loss) + pulp.lpSum(fp[p][d] for d in range(P) if d!=p)
# ---- Balance de energia nodal en todos dias de autonomia.
for p in range(P):
  model += pulp.lpSum(EB[b]*xb[p][b] for b in range(B)) + M*(1-xg[p]) >= AD*(ED[p]*(1+loss) + pulp.lpSum(fe[p][d] for d in range(P) if d!=p))
# Limita la existencia del inversor
for p in range(P):
  for i in range(I):
    xi[p][i] <= M*xg[p]
# Limita la existencia del flujo de energia
for p in range(P):
  for d in range(P):
    if p!=d:
      model += fe[p][d] <= M*xc[p][d]
# Limita la existencia del flujo de potencia
for p in range(P):
  for d in range(P):
    if p!=d:
      model += fp[p][d] <= M*xc[p][d]
# Asegura que exista cable o generador
for p in range(P):
  model += pulp.lpSum(xc[q][p] for q in range(P) if q!=p) + xg[p] <= 1
# Limitacion del numero de eolicos
for p in range(P):
  model += pulp.lpSum(xa[p][a] for a in range(A)) <= M*xg[p]
# ---- El controlador debe ser mayor a la potencia de los generadores eolicos
for p in range(P):
  model += pulp.lpSum(PR[r]*xr[p][r] for r in range(R)) >= pulp.lpSum(PA[a]*xa[p][a] for a in range(A))
# ---- El controlador debe ser mayor a la potencia de los generadores solares
for p in range(P):
  model += pulp.lpSum(PZ[z]*xz[p][z] for z in range(Z)) >= pulp.lpSum(PS[s]*xs[p][s] for s in range(S))
# Limita el numero de cables salida
for p in range(P):
  model += pulp.lpSum(xc[p][d] for d in range(P) if d!=p) <= M*xm[p]
# ---- Limita el numero de cables entrada
for p in range(P):
  model += pulp.lpSum(xc[q][p] for q in range(P) if q!=p) <= xm[p]


solver = pulp.PULP_CBC_CMD(msg=True, warmStart=True)
model.solve(solver)

# PRINT RESULTS
print('Costo Total Minimizado:')
print(model.objective.value())


# Panels
print("\n".join([f"Paneles en punto {p}, tipo {s}: {xs[p][s].varValue}"
                 for p in range(P) for s in range(S) if xs[p][s].varValue]))

# Panel controllers
print("\n".join([f"Controlador de panel en punto {p}, tipo {z}: {xz[p][z].varValue}"
                 for p in range(P) for z in range(Z) if xz[p][z].varValue]))

# Turbines
print("\n".join([f"Turbina en punto {p}, tipo {a}: {xa[p][a].varValue}"
                 for p in range(P) for a in range(A) if xa[p][a].varValue]))

# Turbine controllers
print("\n".join([f"Controlador de turbina en punto {p}, tipo {r}: {xr[p][r].varValue}"
                 for p in range(P) for r in range(R) if xr[p][r].varValue]))

# Batteries
print("\n".join([f"Batería en punto {p}, tipo {b}: {xb[p][b].varValue}"
                 for p in range(P) for b in range(B) if xb[p][b].varValue]))

# Inverters
print("\n".join([f"Inversor en punto {p}, tipo {i}: {xi[p][i].varValue}"
                 for p in range(P) for i in range(I) if xi[p][i].varValue]))

# Eflow
print("\n".join([f"Flujo de energía de {q} a {p}: {fe[q][p].varValue}"
                 for p in range(P) for q in range(P) if fe[q][p].varValue]))

# Pflow
print("\n".join([f"Flujo de potencia de {q} a {p}: {fp[q][p].varValue}"
                 for p in range(P) for q in range(P) if fp[q][p].varValue]))

# Generators (Binario)
print("\n".join([f"Puntos de Generación {p}: {xg[p].varValue}"
                 for p in range(P) if xg[p].varValue]))

# Lines (Binario)
print("\n".join([f"Línea de transmisión entre {p} y {d}: {xc[p][d].varValue}"
                 for p in range(P) for d in range(P) if xc[p][d].varValue]))

# Distancia de Lines (m)
print("\n".join([f"Distancia de Línea de transmisión entre {p} y {d}: {L[p][d]}"
                 for p in range(P) for d in range(P) if xc[p][d]]))

# Meters (Binario)
print("\n".join([f"Existencia de cable {p}: {xm[p].varValue}"
                 for p in range(P) if xm[p].varValue]))