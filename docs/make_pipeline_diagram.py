"""Diagrama del pipeline para el documento técnico del Entregable 2.

Genera docs/pipeline_diagram.pdf (vectorial, para \\includegraphics en LaTeX)
y docs/pipeline_diagram.png (vista previa); con --variant tool, la versión en
que una herramienta ejecuta la línea «Sé:» del modelo contra el roster
(docs/pipeline_diagram_tool.*). Pensado para el ancho de texto de una página
vertical:

    \\begin{figure}[t]
      \\centering
      \\includegraphics[width=\\linewidth]{pipeline_diagram.pdf}
    \\end{figure}

Uso (desde la raíz del repo):
    .venv-ft/bin/python docs/make_pipeline_diagram.py
    .venv-ft/bin/python docs/make_pipeline_diagram.py --variant tool
"""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

OUT = Path(__file__).resolve().parent

INK = "#10181D"
INK2 = "#3D4A53"
INK3 = "#66757F"
NEUTRAL = ("#F2F4F6", "#5B6B77")
GAME = ("#E6F2EA", "#16803C")
INTERVENTION = ("#F6EDD9", "#8A6516")
TOOL = ("#E4ECF7", "#3A63A8")
RULE = "#B9C2C9"

# Cifras del entrenamiento publicado (finetune/logs/train.log).
TRAIN_TEXT = "mlx-lm · 12 de 26 bloques · r16\n2 rondas, 1.500 pasos\nM5 Pro, ~5 h, 22 GB de pico"

W, H = 7.2, 2.95   # pulgadas: ancho de texto de una página A4 con márgenes de ~1,7 cm

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 6.6,
    "pdf.fonttype": 42,   # fuentes TrueType incrustadas: texto seleccionable en el PDF
})


def box(ax, x, y, w, h, title, body, style=NEUTRAL, dashed=False, title_color=INK):
    fill, edge = style
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0,rounding_size=0.06",
        linewidth=0.9, edgecolor=edge, facecolor="none" if dashed else fill,
        linestyle=(0, (3, 2)) if dashed else "solid",
    ))
    ax.text(x + 0.09, y + h - 0.1, title, ha="left", va="top",
            fontsize=7.1, fontweight="bold", color=title_color)
    ax.text(x + 0.09, y + h - 0.29, body, ha="left", va="top",
            fontsize=6.0, color=INK2, linespacing=1.3)
    return {"l": x, "r": x + w, "b": y, "t": y + h, "cx": x + w / 2, "cy": y + h / 2}


def arrow(ax, a, b, color=INK2, rad=0.0, style="-|>", lw=0.9, dashed=False):
    ax.add_patch(FancyArrowPatch(
        a, b, arrowstyle=style, mutation_scale=7, linewidth=lw, color=color,
        connectionstyle=f"arc3,rad={rad}", shrinkA=1.5, shrinkB=1.5,
        linestyle=(0, (3, 2)) if dashed else "solid",
    ))


def lane(ax, y, text):
    ax.text(0.04, y, text, ha="left", va="center", fontsize=5.8, color=INK3,
            fontfamily="DejaVu Sans Mono", fontweight="bold")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=("fine-tuning", "tool"), default="fine-tuning")
    variant = parser.parse_args().variant

    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")

    # ---------------- carril superior: entrenamiento ----------------
    lane(ax, 2.84, "ENTRENAMIENTO · una sola vez, fuera de línea")
    top_y, top_h = 1.98, 0.74
    t1 = box(ax, 0.04, top_y, 1.30, top_h, "Motor del juego",
             "el mismo del notebook\ndel Entregable 1:\nroster, feedback, reglas")
    t2 = box(ax, 1.62, top_y, 1.98, top_h, "Datos sintéticos",
             "2.048 turnos simulados, con respuesta\nobjetivo «Sé» · lista · jugada del\nchecker · 30 objetivos reservados",
             style=INTERVENTION)
    t3 = box(ax, 3.88, top_y, 1.52, top_h, "Fine-tuning LoRA",
             TRAIN_TEXT,
             style=INTERVENTION)
    t4 = box(ax, 5.68, top_y, 1.48, top_h, "Adaptador",
             "11,4 M parámetros\n(0,33 % del modelo)\nmismos pesos base",
             style=INTERVENTION)
    for a, b in ((t1, t2), (t2, t3), (t3, t4)):
        arrow(ax, (a["r"], a["cy"]), (b["l"], b["cy"]))

    # ---------------- carril inferior: la partida ----------------
    lane(ax, 1.66, "PARTIDA · cada turno, hasta acertar o 10 intentos")
    bot_y, bot_h = 0.78, 0.76
    b1 = box(ax, 0.04, bot_y, 1.12, bot_h, "Historial",
             "propuestas y\nfeedback de los\nturnos anteriores")
    b2 = box(ax, 1.44, bot_y, 1.36, bot_h, "Prompt",
             "instrucciones\n+ roster de 173\n+ historial (~5,5k tok)")
    b3 = box(ax, 3.08, bot_y, 1.50, bot_h, "Ministral 3 · 3B",
             "4-bit + adaptador LoRA\nescribe: Sé · lista · jugada\n(baseline: sin adaptador)",
             style=INTERVENTION)
    if variant == "tool":
        b4 = box(ax, 4.86, bot_y, 1.00, bot_h, "Herramienta",
                 "ejecuta «Sé» del\nmodelo contra el\nroster; no ve el\nfeedback real", style=TOOL,
                 title_color=TOOL[1])
    else:
        b4 = box(ax, 4.86, bot_y, 1.00, bot_h, "Parser",
                 "toma la última\nlínea: nombre\nexacto del roster")
    b5 = box(ax, 6.14, bot_y, 1.02, bot_h, "Motor",
             "feedback de\n7 atributos:\n✓ ≈ × ↑ ↓", style=GAME, title_color=GAME[1])
    for a, b in ((b1, b2), (b2, b3), (b3, b4), (b4, b5)):
        arrow(ax, (a["r"], a["cy"]), (b["l"], b["cy"]))

    # bucle de feedback: U por debajo de las cajas
    loop_y = 0.30
    green = GAME[1]
    ax.plot([b5["cx"], b5["cx"], b1["cx"]], [b5["b"], loop_y, loop_y],
            color=green, linewidth=1.0, solid_capstyle="round", solid_joinstyle="round")
    arrow(ax, (b1["cx"], loop_y), (b1["cx"], b1["b"]), color=green, lw=1.0)
    ax.text((b1["cx"] + b5["cx"]) / 2, loop_y - 0.13,
            "el feedback vuelve al historial del turno siguiente",
            ha="center", va="center", fontsize=5.9, color=green, style="italic")

    # verificador: mide, no decide (entre las cajas y el bucle)
    ax.text(b2["l"] + 0.05, 0.56,
            "Verificador de restricciones: sólo mide violaciones, repeticiones y aciertos; "
            "no filtra ni corrige la salida del modelo.",
            ha="left", va="center", fontsize=5.5, color=INK3)

    # el adaptador baja al modelo
    arrow(ax, (t4["l"] + 0.20, t4["b"]), (b3["r"] - 0.30, b3["t"]),
          color=INTERVENTION[1], lw=1.0)
    ax.text(5.32, 1.70, "se carga al servir", ha="left", va="center",
            fontsize=5.7, color=INTERVENTION[1], style="italic")

    stem = "pipeline_diagram" if variant == "fine-tuning" else "pipeline_diagram_tool"
    fig.savefig(OUT / f"{stem}.pdf")
    fig.savefig(OUT / f"{stem}.png", dpi=300)
    print(f"docs/{stem}.pdf  docs/{stem}.png")


if __name__ == "__main__":
    main()
