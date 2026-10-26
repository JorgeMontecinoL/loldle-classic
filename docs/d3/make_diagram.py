"""Exporta el grafo D3 como figura vectorial y PNG, sin ejecutar el modelo."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

HERE = Path(__file__).resolve().parent
INK, MUTED, LINE, GOLD, BG = '#17342d', '#6e7b73', '#99aa9e', '#b89b51', '#fffef9'
fig, ax = plt.subplots(figsize=(11, 7.5))
fig.patch.set_facecolor(BG)
ax.set(xlim=(-.2, 12.2), ylim=(-.5, 8.2))
ax.axis('off')
boxes = {'game': (1.3, 6.7, 'Juego / historial', 'feedback público'),
         'memory': (5.2, 6.7, '01 · Memoria', 'reconstruye restricciones'),
         'selector': (10.1, 6.7, '02 · Selector', 'busca de a 25 filas'),
         'state': (5.2, 4.6, 'validar_estado', 'consistencia interna'),
         'roster': (10.1, 4.6, 'roster paginado', '7 páginas · sin filtrar'),
         'verifier': (5.2, 2.8, '03 · Verificador', 'aprueba o devuelve'),
         'check': (5.2, .8, 'ver_atributos', 'fila del roster, sin comparar')}
W, H = 2.75, 1.05
for key, (x, y, title, sub) in boxes.items():
    tool = key in ('state', 'roster', 'check')
    ax.add_patch(FancyBboxPatch((x-W/2, y-H/2), W, H, boxstyle='round,pad=0.04,rounding_size=.15',
                 facecolor='#f7f0db' if tool else BG, edgecolor=GOLD if tool else LINE, lw=1.3))
    ax.text(x, y+.14, title, ha='center', va='center', fontsize=11, weight='bold', color=INK)
    ax.text(x, y-.21, sub, ha='center', va='center', fontsize=9, color=MUTED)

def arrow(points, label='', at=None, revision=False):
    color = GOLD if revision else LINE
    for i, (a, b) in enumerate(zip(points, points[1:])):
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle='-|>' if i == len(points)-2 else '-',
                     mutation_scale=13, color=color, lw=1.4, linestyle='--' if revision else '-'))
    if label and at:
        ax.text(*at, label, ha='center', fontsize=8.5, color=MUTED, backgroundcolor=BG)

arrow([(2.72,6.7),(3.78,6.7)],'historial',(3.2,6.94))
arrow([(6.62,6.7),(8.68,6.7)],'estado',(7.7,6.94))
arrow([(4.98,6.13),(4.98,5.18)])
arrow([(5.42,5.18),(5.42,6.13)],'formato',(6.05,5.65))
arrow([(10.32,5.18),(10.32,6.13)],'una página por llamada',(9.2,5.65))
arrow([(8.68,6.45),(8.0,6.45),(8.0,2.8),(6.62,2.8)],'primer candidato de su lista',(9.25,3.55))
arrow([(9.0,7.27),(9.0,7.75),(5.6,7.75),(5.6,7.27)],'lista vacía en 4 pasadas → revisar estado',(7.3,7.82),revision=True)
arrow([(4.98,2.23),(4.98,1.38)])
arrow([(5.42,1.38),(5.42,2.23)],'atributos',(6.1,1.75))
arrow([(3.78,2.8),(1.8,2.8),(1.8,6.13)],'aprobar → jugar',(2.8,3.04))
arrow([(.6,6.13),(.6,3.8),(3.2,3.8),(3.2,2.98),(3.78,2.98)],'evidencia original',(1.9,4.02))
arrow([(3.78,2.58),(3.18,2.58),(3.18,6.3),(3.78,6.3)],revision=True)
ax.text(2.97,4.25,'revisar memoria + motivo',rotation=90,fontsize=8.5,color=MUTED,ha='center')
arrow([(6.62,2.6),(11.76,2.6),(11.76,6.7),(11.52,6.7)],'rechazo + motivo → siguiente de la lista',(9,2.2),revision=True)
ax.text(.0,.05,'Fin: resuelto · 10 jugadas · stop · tras 3 rechazos sólo aprueba o para · 60 llamadas/turno · 160/partida',fontsize=9,color=MUTED)
fig.savefig(HERE/'pipeline.pdf',bbox_inches='tight',facecolor=BG)
fig.savefig(HERE/'pipeline.png',bbox_inches='tight',dpi=180,facecolor=BG)
plt.close(fig)
