"""Genera las figuras originales de los capítulos numéricos de MGP."""
from pathlib import Path
import argparse
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "contenidos/libro/numeros/figuras"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "svg.fonttype": "none", "svg.hashsalt": "mgp-numeros"})
BLUE, ORANGE, LIGHT = "#2563a6", "#c05621", "#e7edf3"

def save(fig, name, previews=None):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / (name + ".svg"), bbox_inches="tight", facecolor="white", metadata={"Date": None})
    if previews:
        previews.mkdir(parents=True, exist_ok=True)
        fig.savefig(previews / (name + ".png"), dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)

def render(previews=None):
    fig, ax = plt.subplots(figsize=(8, 2.6))
    for y, denominator, numerator in [(1.2,4,3),(0.2,8,6)]:
        for i in range(denominator):
            ax.add_patch(Rectangle((i/denominator,y),1/denominator,0.55,facecolor=BLUE if i<numerator else LIGHT,edgecolor="white",linewidth=2))
        ax.text(-0.06,y+0.27,f"{numerator}/{denominator}",ha="right",va="center",fontsize=13)
        ax.text(1.04,y+0.27,"misma unidad",va="center")
    ax.set_xlim(-0.18,1.45);ax.set_ylim(0,2);ax.axis("off")
    ax.set_title("Una cantidad, dos particiones",loc="left",pad=12)
    save(fig,"fracciones-equivalentes",previews)
    fig, axes = plt.subplots(1,3,figsize=(10.5,3.4),constrained_layout=True)
    x=np.linspace(0,5,200)
    for ax,title in zip(axes,["Directa: y = 3x","Inversa: y = 12/x","Afín: y = 3x + 2"]):
        ax.set(xlim=(0,5),ylim=(0,18),xlabel="x",ylabel="y",title=title)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:g}".replace(".", ",")))
        ax.set_xticks(range(6));ax.grid(alpha=0.2);ax.spines[["top","right"]].set_visible(False)
    axes[0].plot(x,3*x,color=BLUE,lw=2.5)
    xi=np.linspace(0.7,5,200);axes[1].plot(xi,12/xi,color=BLUE,lw=2.5)
    axes[2].plot(x,3*x+2,color=ORANGE,lw=2.5)
    axes[0].scatter([1,2,4],[3,6,12],color=BLUE,zorder=3)
    axes[1].scatter([1,2,4],[12,6,3],color=BLUE,zorder=3)
    axes[2].scatter([1,2,4],[5,8,14],color=ORANGE,zorder=3)
    save(fig,"modelos-proporcionalidad",previews)
    fig, ax = plt.subplots(figsize=(8,3.2))
    labels=["Referencia inicial","Después de −20 %","Después de −10 %"]
    values=[100,80,72]
    for i,(label,value) in enumerate(zip(labels,values)):
        ax.barh(2-i,value,height=0.5,color=BLUE)
        ax.barh(2-i,100-value,left=value,height=0.5,color=LIGHT)
        ax.text(value+1,2-i,f"{value} de 100",va="center",fontsize=11)
    ax.set_yticks([2,1,0],labels);ax.set_xlim(0,120);ax.set_xticks([0,20,40,60,80,100])
    ax.set_xlabel("Cantidad, expresada respecto del valor inicial 100")
    ax.set_title("Cambios sucesivos: 100 × 0,8 × 0,9 = 72",loc="left",pad=14)
    ax.spines[["top","right","left"]].set_visible(False);ax.tick_params(axis="y",length=0)
    fig.tight_layout()
    save(fig,"porcentajes-sucesivos",previews)

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--previews",type=Path)
    render(parser.parse_args().previews)
