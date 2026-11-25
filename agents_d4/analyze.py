"""Resultados del Entregable 4: partidas completas, Selector aislado y curvas de pérdida.

    .venv-ft/bin/python -m agents_d4.analyze --run-id test_v1

Las filas «histórico» vienen de results/d3/summary.json (trazas del D3, commit 10da2ec).
Las filas «reproducido» son corridas nuevas guardadas en results/d4/runs/<run-id>/.
"""
import argparse
import json
import re
from pathlib import Path

from agents_d3.analyze import metrics, paired, read
from agents_d3.evaluate import ROOT

LABELS = {"base/direct": "D1 · prompting directo", "lora/d2_lora": "D2 · LoRA sin agentes",
          "paginas/full": "D3 · tres agentes (LoRA común)", "d3/full": "D3 · tres agentes (LoRA común)",
          "d4/full": "D4 · Selector con adaptador propio", "d4_selector_base/full": "D3 con Selector base (sin LoRA)",
          "none/algorithmic": "Control · filtro por reglas"}
ORDER = ["base/direct", "lora/d2_lora", "paginas/full", "d3/full", "d4/full", "d4_selector_base/full", "none/algorithmic"]


def loss_curves(log):
    train, valid = [], []
    for line in Path(log).read_text(errors="ignore").replace("\r", "\n").splitlines():
        m = re.match(r"Iter (\d+): Train loss ([\d.]+), Learning Rate ([\d.e+-]+), It/sec ([\d.]+), Tokens/sec ([\d.]+), Trained Tokens (\d+), Peak mem ([\d.]+) GB", line)
        if m:
            train.append({"iter": int(m[1]), "loss": float(m[2]), "lr": float(m[3]), "it_s": float(m[4]),
                          "tokens": int(m[6]), "peak_gb": float(m[7])})
        m = re.match(r"Iter (\d+): Val loss ([\d.]+), Val took ([\d.]+)s", line)
        if m and not any(v["iter"] == int(m[1]) for v in valid):
            valid.append({"iter": int(m[1]), "loss": float(m[2])})
    return train, valid


def plot_losses(train, valid, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(4.2, 2.4), dpi=200)
    ax.plot([t["iter_global"] for t in train], [t["loss"] for t in train], color="#2b6cb0", lw=1, label="entrenamiento")
    ax.plot([v["iter_global"] for v in valid], [v["loss"] for v in valid], "o-", color="#c05621", lw=1.2, ms=3, label="validación (95 ej.)")
    starts = sorted({t["iter_global"] - t["iter"] for t in train})
    for s in starts[1:]:
        ax.axvline(s, color="#888", lw=.8, ls="--")
        ax.text(s + 15, ax.get_ylim()[1] * .92, "ronda 2", fontsize=6, color="#555")
    ax.set_xlabel("iteración acumulada (1 ejemplo por iteración)")
    ax.set_ylabel("pérdida")
    ax.grid(alpha=.3, lw=.5)
    ax.legend(frameon=False, fontsize=7)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(out)
    fig.savefig(Path(out).with_suffix(".pdf"))


def selector_rows():
    rows = []
    for path in sorted((ROOT / "results/d4/selector_eval").glob("*.summary.json")):
        rows.append(json.loads(path.read_text())["summary"])
    return rows


def pct(x):
    return "—" if x is None else f"{100 * x:.1f}%"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run-id", required=True)
    p.add_argument("--logs", nargs="+", default=["finetune/logs/d4_selector_r1.log:1000", "finetune/logs/d4_selector_r2.log"],
                   help="logs de cada ronda; ':N' corta la ronda en la iteración N (de donde parte la siguiente)")
    args = p.parse_args()
    out = ROOT / "results/d4"
    historical = json.loads((ROOT / "results/d3/summary.json").read_text())["rows"]
    historical = {r["label"]: r for r in historical if r["label"] in LABELS}
    run_dir = ROOT / "results/d4/runs" / args.run_id
    payloads = {}
    for path in sorted(run_dir.rglob("*.json.gz")):
        payload = read(path)
        if payload.get("records"):
            label = payload.get("weights", "") + "/" + payload["variant"]
            payloads[label] = (path, payload)
    reproduced = {label: metrics(payload, path) for label, (path, payload) in payloads.items()}
    comparisons = {}
    if "d3/full" in payloads and "d4/full" in payloads:
        comparisons["D3 → D4 (reproducidos)"] = paired(payloads["d3/full"][1], payloads["d4/full"][1])
    if "d4_selector_base/full" in payloads and "d4/full" in payloads:
        comparisons["Selector base → D4"] = paired(payloads["d4_selector_base/full"][1], payloads["d4/full"][1])
    train, valid, offset, rounds = [], [], 0, []
    for item in args.logs:
        path, _, cut = item.partition(":")
        t, v = loss_curves(ROOT / path)
        if cut:
            t, v = [x for x in t if x["iter"] <= int(cut)], [x for x in v if x["iter"] <= int(cut)]
        for x in t + v:
            x["round"], x["iter_global"] = len(rounds) + 1, x["iter"] + offset
        train += t
        valid += v
        rounds.append({"log": path, "start": offset, "iters": t[-1]["iter"] if t else 0})
        offset += int(cut) if cut else (t[-1]["iter"] if t else 0)
    if train:
        plot_losses(train, valid, out / "loss_d4_selector.png")
    sel = selector_rows()
    summary = {"run_id": args.run_id, "historical": historical, "reproduced": reproduced, "comparisons": comparisons,
               "selector": sel, "loss": {"train": train, "valid": valid}}
    (out / f"summary_{args.run_id}.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1))
    lines = [f"# Entregable 4 · resultados ({args.run_id})", "",
             "Partidas resueltas en hasta 10 jugadas; los paros cuentan como no resueltas. «Histórico» = trazas del D3 "
             "(results/d3/raw, commit 10da2ec); «reproducido» = corrida nueva en este repositorio.", "",
             "| Sistema | Origen | Resueltas | Intentos incompatibles (estricta) | Paros | Llamadas/partida | s modelo/partida |",
             "|---|---|---:|---:|---:|---:|---:|"]
    for label in ORDER:
        for origin, row in (("histórico", historical.get(label)), ("reproducido", reproduced.get(label))):
            if not row:
                continue
            strict = row["strict_violation_rate"]
            n_strict = f" ({round(strict * row['eligible_attempts'])}/{row['eligible_attempts']})" if strict is not None else ""
            lines.append(f"| {LABELS[label]} | {origin}{'' if row['complete'] else ' (parcial)'} | {row['solved']}/{row['games']} | "
                         f"{pct(strict)}{n_strict} | {row['stopped_games']} | {row['calls_per_game']:.1f} | {row['model_seconds_per_game']:.1f} |")
    lines += ["", "## Comparaciones pareadas (McNemar exacto, exploratorio)", ""]
    for name, c in comparisons.items():
        lines.append(f"- {name}: {c['wins']} victorias y {c['losses']} derrotas discordantes del segundo; p={c['mcnemar_exact_p']:.4g} (n={c['paired_targets']}).")
    lines += ["", "## Selector aislado (mismas entradas, temperatura 0)", "",
              "| Conjunto | Pesos · prompt | Páginas | Conserva compatibles | Precisión | Páginas exactas | Descarta al secreto | Amarillo de un valor: conserva | Fuera de protocolo |",
              "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for s in sel:
        target = f"{s['target_dropped']}/{s['target_pages']}" if s["target_pages"] else "—"
        ys = f"{pct(s['yellow_single_recall'])} ({round((s['yellow_single_recall'] or 0) * s['yellow_single_fits'])}/{s['yellow_single_fits']})" if s["yellow_single_fits"] else "—"
        lines.append(f"| {s['set']} | {s['label']} | {s['pages']} | {pct(s['recall'])} ({s['true_pos']}/{s['fits']}) | "
                     f"{pct(s['precision'])} ({s['true_pos']}/{s['listed']}) | {s['exact_pages']}/{s['pages']} | {target} | {ys} | {s['protocol_errors']} |")
    if train:
        lines += ["", "## Entrenamiento", "",
                  f"- Rondas: " + "; ".join(f"{r['log']} desde la iteración {r['start']}" for r in rounds) + ".",
                  f"- Pérdida de entrenamiento final {train[-1]['loss']:.3f}; validación (iteración acumulada→pérdida): "
                  + ", ".join(f"{v['iter_global']}→{v['loss']:.3f}" for v in valid) + ".",
                  f"- Pico de memoria {max(t['peak_gb'] for t in train):.1f} GB; tokens entrenados {train[-1]['tokens']}.",
                  "- Curva: `results/d4/loss_d4_selector.png`."]
    for label, row in reproduced.items():
        if row["failures"]:
            lines += ["", f"## Fallos · {LABELS.get(label, label)} (reproducido)", ""]
            for f in row["failures"]:
                lines.append(f"- {f['target']}: {f['attempts']} jugadas; {f['stop'] or '10 intentos agotados'}; {', '.join(str(g) for g in f['guesses'])}.")
    (out / f"RESULTADOS_{args.run_id}.md").write_text("\n".join(lines) + "\n")
    print(out / f"RESULTADOS_{args.run_id}.md")


if __name__ == "__main__":
    main()
