"""Empaqueta el adaptador del Selector para Hugging Face y verifica la descarga.

    .venv-ft/bin/python -m agents_d4.hf_package build             # arma hf_release/d4_selector/
    .venv-ft/bin/hf upload <usuario>/loldle-d4-selector-lora hf_release/d4_selector . --repo-type model
    .venv-ft/bin/python -m agents_d4.hf_package verify --repo <usuario>/loldle-d4-selector-lora

`verify` descarga el repositorio público en una carpeta nueva, compara el SHA-256 de
`adapters.safetensors` con el del adaptador local que produjo los resultados y deja la
ruta lista para `agents_d4.eval_selector --adapter` y `agents_d4.evaluate --adapter`.
"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ADAPTER = ROOT / "finetune/adapters/d4_selector"
OUT = ROOT / "hf_release/d4_selector"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build(args):
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    shutil.copy(ADAPTER / "adapters.safetensors", OUT / "adapters.safetensors")
    config = json.loads((ADAPTER / "adapter_config.json").read_text())
    (OUT / "adapter_config.json").write_text(json.dumps(config, indent=4))
    for r in ("r1", "r2"):
        shutil.copy(ROOT / f"finetune/lora_config_d4_selector_{r}.yaml", OUT / f"lora_config_d4_selector_{r}.yaml")
    (OUT / "data/ronda1").mkdir(parents=True)
    (OUT / "data/ronda2").mkdir(parents=True)
    for name in ("train.jsonl", "valid.jsonl", "report.json"):
        shutil.copy(ROOT / "finetune/data/d4_selector" / name, OUT / "data/ronda1" / name)
        shutil.copy(ROOT / "finetune/data/d4_selector_r2" / name, OUT / "data/ronda2" / name)
    shutil.copy(ROOT / "results/d4/checkpoint_selection.json", OUT / "checkpoint_selection.json")
    for name in ("selector.txt", "memoria.txt", "verificador.txt"):
        shutil.copy(ROOT / "agents_d4/prompts" / name, OUT / f"prompt_{name}")
    card = (ROOT / "agents_d4/MODEL_CARD.md").read_text().replace("{SHA256}", sha(OUT / "adapters.safetensors"))
    (OUT / "README.md").write_text(card)
    files = {p.relative_to(OUT).as_posix(): sha(p) for p in sorted(OUT.rglob("*")) if p.is_file()}
    (ROOT / "results/d4/hf_manifest.json").write_text(json.dumps(files, indent=1))
    print(json.dumps(files, indent=1))


def verify(args):
    from huggingface_hub import snapshot_download
    target = ROOT / "hf_release/descarga"
    if target.exists():
        shutil.rmtree(target)
    path = Path(snapshot_download(args.repo, local_dir=target, revision=args.revision))
    remote, local = sha(path / "adapters.safetensors"), sha(ADAPTER / "adapters.safetensors")
    result = {"repo": args.repo, "revision": args.revision, "downloaded_to": str(path.relative_to(ROOT)),
              "sha256_remote": remote, "sha256_local": local, "identical": remote == local}
    (ROOT / "results/d4/hf_verify.json").write_text(json.dumps(result, indent=1))
    print(json.dumps(result, indent=1))
    if remote != local:
        raise SystemExit("El adaptador publicado no es el que produjo los resultados")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build")
    v = sub.add_parser("verify")
    v.add_argument("--repo", required=True)
    v.add_argument("--revision", default="main")
    args = p.parse_args()
    {"build": build, "verify": verify}[args.cmd](args)


if __name__ == "__main__":
    main()
