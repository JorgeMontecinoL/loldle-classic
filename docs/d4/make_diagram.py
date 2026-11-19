"""Grafo del D4 con el Selector ajustado marcado (PDF y PNG), sin ejecutar el modelo.

    .venv-ft/bin/python docs/d4/make_diagram.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = Path(__file__).resolve().parent
INK, MUTED, LINE, HOT, TOOL = "#1d2b3a", "#5f6b7a", "#9aa6b5", "#c2410c", "#f4ead2"
fig, ax = plt.subplots(figsize=(7.4, 1.95))
ax.set(xlim=(0, 16), ylim=(0, 4.2))
ax.set_aspect("equal")
ax.axis("off")
W, H, Y = 2.5, 1.2, 2.3
nodes = {
    "game": (1.4, Y, "Juego", "pistas públicas", None),
    "memory": (4.7, Y, "Memoria", "estado", "LoRA D3"),
    "selector": (8.0, Y, "Selector", "veredicto por fila", "LoRA D4 · nuevo"),
    "ctrl": (11.3, Y, "Controlador", "código", None),
    "verifier": (14.6, Y, "Verificador", "aprueba / devuelve", "LoRA D3"),
}
for key, (x, y, title, sub, weights) in nodes.items():
    hot, tool = key == "selector", key == "ctrl"
    ax.add_patch(FancyBboxPatch((x - W / 2, y - H / 2), W, H, boxstyle="round,pad=0.02,rounding_size=.15",
                                facecolor="#fff1e6" if hot else (TOOL if tool else "white"),
                                edgecolor=HOT if hot else LINE, lw=2.2 if hot else 1.0))
    ax.text(x, y + .3, title, ha="center", va="center", fontsize=8.6, weight="bold", color=HOT if hot else INK)
    ax.text(x, y - .02, sub, ha="center", va="center", fontsize=6.0, color=MUTED)
    if weights:
        ax.text(x, y - .33, weights, ha="center", va="center", fontsize=6.0,
                weight="bold" if hot else "normal", color=HOT if hot else MUTED)


def line(points, color=LINE, dashed=False, label="", at=None):
    for i, (a, b) in enumerate(zip(points, points[1:])):
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>" if i == len(points) - 2 else "-", mutation_scale=8,
                                     color=color, lw=0.9, linestyle="--" if dashed else "-", shrinkA=0, shrinkB=0))
    if label:
        ax.text(*at, label, ha="center", va="center", fontsize=5.8, color=color if color != LINE else MUTED,
                backgroundcolor="white")


for a, b in (("game", "memory"), ("memory", "selector"), ("selector", "ctrl"), ("ctrl", "verifier")):
    line([(nodes[a][0] + W / 2, Y), (nodes[b][0] - W / 2, Y)])
ax.text(6.35, Y + .2, "estado", fontsize=5.6, color=MUTED, ha="center")
ax.text(9.65, Y + .2, "lista", fontsize=5.6, color=MUTED, ha="center")
ax.text(12.95, Y + .2, "nombre", fontsize=5.6, color=MUTED, ha="center")
top = Y + H / 2
line([(14.6, top), (14.6, 3.75), (1.4, 3.75), (1.4, top)], color=INK, label="aprueba → se juega; nuevas pistas", at=(8.0, 3.75))
bot = Y - H / 2
line([(14.1, bot), (14.1, .95), (11.3, .95), (11.3, bot)], color=HOT, dashed=True,
     label="rechazo → siguiente", at=(12.7, .95))
line([(8.0, .25), (8.0, bot)], label="roster: 7 páginas de 25", at=(8.0, .25))
line([(7.4, bot), (7.4, .95), (4.7, .95), (4.7, bot)], color=HOT, dashed=True,
     label="sin candidatos", at=(6.0, .95))
fig.savefig(HERE / "grafo_d4.pdf", bbox_inches="tight", pad_inches=0.02)
fig.savefig(HERE / "grafo_d4.png", bbox_inches="tight", dpi=240, pad_inches=0.02)
plt.close(fig)
print(HERE / "grafo_d4.pdf")
