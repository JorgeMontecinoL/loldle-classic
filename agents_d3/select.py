"""Fija los pesos y el protocolo usando exclusivamente 15 objetivos de validación."""
import argparse
import hashlib
from datetime import datetime, timezone
from pathlib import Path

from .analyze import read, metrics
from .evaluate import ROOT, atomic_json


def source_hashes():
    paths = sorted((ROOT / 'agents_d3/prompts').glob('*.txt'))
    paths += [ROOT / 'agents_d3' / name for name in ('runtime.py', 'state.py', 'client.py')]
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', default='results/d3/dev')
    args = parser.parse_args()
    choices = []
    for weights in ('base', 'lora'):
        path = ROOT / args.input / f'valid_{weights}_full.json.gz'
        payload = read(path)
        if not payload['complete'] or payload['split'] != 'valid' or len(payload['targets']) != 15:
            raise ValueError('Se requieren las dos corridas completas de 15 objetivos de validación')
        row = metrics(payload, path)
        choices.append((row, payload))
    choices.sort(key=lambda pair: (-pair[0]['solved'], pair[0]['stopped_games'],
                                  pair[0]['strict_violation_rate'] if pair[0]['strict_violation_rate'] is not None else 1,
                                  pair[0]['calls_per_game']))
    best, payload = choices[0]
    atomic_json(ROOT / 'results/d3/selection.json', {
        'selected_weights': payload['weights'], 'selected_at': datetime.now(timezone.utc).isoformat(),
        'rule': 'Mayor resolución; desempate por menos paros, menor violación estricta, menos llamadas.',
        'validation': [row for row, _ in choices], 'source_hashes': source_hashes(),
        'agent_config': payload['config']['agents'], 'max_tokens': payload['config']['max_tokens_per_call'],
        'adapter_sha256': payload['config']['adapter_sha256'], 'test_targets_used_for_selection': False,
        'note': 'Objetivos test ya usados en D1/D2; no se usan para ajustar el protocolo D3.'})
    print(f"Pesos seleccionados: {payload['weights']} ({best['solved']}/15)")


if __name__ == '__main__':
    main()
