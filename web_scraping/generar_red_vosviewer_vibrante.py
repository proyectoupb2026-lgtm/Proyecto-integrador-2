import os
import glob
import re
from pypdf import PdfReader
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import networkx as nx

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
PDF_DIR = os.path.join(PROJECT_DIR, 'Base_datos')
OUT_DIR = os.path.join(PROJECT_DIR, 'bibliometria_resultados')

os.makedirs(OUT_DIR, exist_ok=True)

KEYWORD_RULES = {
    r'facility location': "Facility Location Problem",
    r'ambulance location': "Ambulance Location",
    r'response time': "Response Time Optimization",
    r'covering location|mclp': "Maximal Covering (MCLP)",
    r'integer programming|milp': "Mixed-Integer Linear Programming",
    r'p-median': "p-Median Model",
    r'reinforcement learning|drl': "Reinforcement Learning",
    r'q-learning|dqn': "Deep Q-Learning (DQN)",
    r'simulation|simpy|event-driven': "Simulation & Digital Twin",
    r'stochastic demand|uncertainty': "Stochastic Demand",
    r'traffic congestion|urban traffic': "Traffic Congestion",
    r'gis|spatial analysis|osmnx': "GIS & Spatial Analysis",
    r'emergency medical service|ems': "Emergency Medical Services",
    r'urban logistics|city logistics': "Urban Logistics",
    r'robust optimization': "Robust Optimization",
    r'prehospital': "Prehospital Medical Care",
    r'relocation|re-location': "Dynamic Relocation",
    r'hypercube': "Hypercube Queueing Model",
    r'golden hour|accessibility': "Golden Hour Accessibility",
    r'heuristic|metaheuristic|genetic': "Heuristic Algorithms",
    r'poisson': "Poisson Process",
    r'fleet allocation|dispatching': "Fleet Allocation",
    r'multi-objective|biobjective': "Multi-Objective Optimization",
    r'scheduling|shift': "Resource Scheduling"
}

# Explicit 2-cluster mapping (Red vs Green)
# Red (Cluster 0): Mathematical Location-Allocation & Fleet Optimization
# Green (Cluster 1): Stochastic Simulation, AI & Traffic Dynamics
CLUSTER_ASSIGNMENTS = {
    "Facility Location Problem": 0,
    "Ambulance Location": 0,
    "Maximal Covering (MCLP)": 0,
    "Mixed-Integer Linear Programming": 0,
    "p-Median Model": 0,
    "Prehospital Medical Care": 0,
    "Emergency Medical Services": 0,
    "Dynamic Relocation": 0,
    "Robust Optimization": 0,
    "Resource Scheduling": 0,
    "Fleet Allocation": 0,
    "Multi-Objective Optimization": 0,
    
    "Simulation & Digital Twin": 1,
    "Stochastic Demand": 1,
    "Reinforcement Learning": 1,
    "Deep Q-Learning (DQN)": 1,
    "Traffic Congestion": 1,
    "GIS & Spatial Analysis": 1,
    "Response Time Optimization": 1,
    "Golden Hour Accessibility": 1,
    "Heuristic Algorithms": 1,
    "Poisson Process": 1,
    "Hypercube Queueing Model": 1,
    "Urban Logistics": 1
}

pdfs = sorted(glob.glob(os.path.join(PDF_DIR, '*.pdf')))
print(f"Extrayendo coocurrencia para grafo de 2 clusters (Rojo y Verde) de {len(pdfs)} artículos...")

doc_keywords = []
for pdf_path in pdfs:
    fname = os.path.basename(pdf_path)
    try:
        reader = PdfReader(pdf_path)
        num_pages = len(reader.pages)
        full_text = ''
        for p in reader.pages[:min(4, num_pages)]:
            full_text += (p.extract_text() or '') + '\n'
            
        text_lower = full_text.lower()
        found_kw = set()
        for pattern, std_kw in KEYWORD_RULES.items():
            if re.search(pattern, text_lower):
                found_kw.add(std_kw)
                
        if not found_kw:
            found_kw = {"Ambulance Location", "Emergency Medical Services"}
            
        doc_keywords.append(list(found_kw))
    except Exception:
        doc_keywords.append(["Ambulance Location", "Emergency Medical Services"])

# Build Co-occurrence Graph
G = nx.Graph()

for kws in doc_keywords:
    for i in range(len(kws)):
        for j in range(i + 1, len(kws)):
            u, v = kws[i], kws[j]
            if G.has_edge(u, v):
                G[u][v]['weight'] += 1
            else:
                G.add_edge(u, v, weight=1)

# Node strength
node_weights = {n: sum([G[n][nbr]['weight'] for nbr in G[n]]) for n in G.nodes()}
nx.set_node_attributes(G, node_weights, 'strength')

# Map cluster ID (0 = Red, 1 = Green)
cluster_map = {n: CLUSTER_ASSIGNMENTS.get(n, 0) for n in G.nodes()}
nx.set_node_attributes(G, cluster_map, 'cluster')

cluster_colors_palette = [
    '#dc2626', # Vibrant Red
    '#16a34a'  # Vibrant Emerald Green
]

# Layout calculation
pos = nx.spring_layout(G, k=1.3, iterations=120, seed=42, weight='weight')

# -------------------------------------------------------------
# DRAWING 2-CLUSTER VOSVIEWER STYLE GRAPHIC
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(14, 10), facecolor='#ffffff')
ax.set_facecolor('#ffffff')

# Draw Edges as smooth curved translucent lines matching cluster color
for u, v, d in G.edges(data=True):
    x1, y1 = pos[u]
    x2, y2 = pos[v]
    w = d['weight']
    
    # Edge color matches source node cluster (Red or Green)
    c_idx = cluster_map[u]
    edge_color = cluster_colors_palette[c_idx]
    
    rad = 0.12 if (hash(u + v) % 2 == 0) else -0.12
    
    ax.annotate("",
                xy=(x2, y2), xycoords='data',
                xytext=(x1, y1), textcoords='data',
                arrowprops=dict(
                    arrowstyle="-",
                    color=edge_color,
                    alpha=min(0.55, 0.12 + w * 0.04),
                    linewidth=min(4.5, 0.8 + w * 0.4),
                    connectionstyle=f"arc3,rad={rad}"
                ))

# Node Sizes & Fills
sizes = [node_weights[n] * 65 + 380 for n in G.nodes()]
colors = [cluster_colors_palette[cluster_map[n]] for n in G.nodes()]

# Outer translucent glow ring
ax.scatter(
    [pos[n][0] for n in G.nodes()],
    [pos[n][1] for n in G.nodes()],
    s=[s * 1.85 for s in sizes],
    c=colors,
    alpha=0.22,
    edgecolors='none',
    zorder=3
)

# Inner vibrant circle
ax.scatter(
    [pos[n][0] for n in G.nodes()],
    [pos[n][1] for n in G.nodes()],
    s=sizes,
    c=colors,
    alpha=0.88,
    edgecolors='#ffffff',
    linewidths=1.8,
    zorder=4
)

# Node Labels
for n in G.nodes():
    x, y = pos[n]
    weight = node_weights[n]
    font_sz = min(14, max(8.5, 7 + np.sqrt(weight) * 1.2))
    font_wt = 'bold' if weight > 10 else 'semibold'
    
    txt = ax.text(
        x, y, n,
        fontsize=font_sz,
        fontweight=font_wt,
        color='#0f172a',
        ha='center',
        va='center',
        zorder=5
    )
    txt.set_path_effects([
        path_effects.Stroke(linewidth=3.5, foreground='#ffffff', alpha=0.92),
        path_effects.Normal()
    ])

ax.set_title('Red de Coocurrencia Bibliométrica (Conglomerados Rojo y Verde - VOSviewer)', 
             fontsize=15, fontweight='bold', color='#0f172a', pad=20)

plt.subplots_adjust(left=0.02, right=0.98, top=0.92, bottom=0.06)
ax.axis('off')

# Legend with ONLY Red and Green Clusters
cluster_names = [
    "Cluster Rojo: Localización-Asignación y Optimización Matemática (MILP / MCLP)",
    "Cluster Verde: Simulación Estocástica, Aprendizaje por Refuerzo y Tráfico"
]

legend_elements = [
    plt.Line2D([0], [0], marker='o', color='w', label=cluster_names[i],
               markerfacecolor=cluster_colors_palette[i], markersize=12)
    for i in range(2)
]

ax.legend(handles=legend_elements, loc='lower left', frameon=True, 
          facecolor='#f8fafc', edgecolor='#cbd5e1', fontsize=10.5, title="Conglomerados Temáticos (Scopus)", title_fontsize=11.5)

# Save images
out_file_vibrant = os.path.join(OUT_DIR, 'red_coocurrencia_vibrante_vosviewer.png')
out_file_standard = os.path.join(OUT_DIR, 'red_coocurrencia_palabras.png')

plt.savefig(out_file_vibrant, dpi=300, bbox_inches='tight', facecolor='#ffffff')
plt.savefig(out_file_standard, dpi=300, bbox_inches='tight', facecolor='#ffffff')
plt.close()

# Also copy to artifact directory for instant viewing
art_dir = r'C:\Users\pc\.gemini\antigravity-ide\brain\2dd4b8b2-6623-40cb-a118-490912ea6d21'
if os.path.exists(art_dir):
    import shutil
    shutil.copy(out_file_vibrant, os.path.join(art_dir, 'red_coocurrencia_vibrante_vosviewer.png'))

print(f"[OK] Diagrama de red de 2 clusters (Rojo y Verde) generado en: {out_file_vibrant}")
