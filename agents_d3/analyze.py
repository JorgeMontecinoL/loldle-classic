"""Analiza partidas completas y parciales, costes y ablaciones del Entregable 3."""
import argparse
import csv
import gzip
import json
from math import comb
from pathlib import Path
from statistics import mean

from analyze_results import analyze as historical_analysis
from .evaluate import ROOT, atomic_json
from run_benchmark import load_engine
from .state import public_history, observed_state, query_roster


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.name.endswith('.gz') else data)


def metrics(payload, source):
    records = payload['records']
    if not records:
        return None
    label = payload.get('weights', '') + '/' + payload['variant']
    historical = historical_analysis({**payload, 'model_name': label, 'params_b': 3.4,
                                      'mean_latency_s': None, 'wall_seconds': None, 'api_errors': 0})
    events = [e for r in records for e in r.get('agent_trace', [])]
    attempts = [e for r in records for e in r['trace']]
    outputs = [e for e in events if e['kind'] == 'model_output']
    eligible = [e for e in attempts if e.get('eligible') and not e.get('invalid')]
    calls = sum(e['kind'] == 'model_call' for e in events)
    if payload['variant'] in ('direct', 'd2_lora', 'd2_tool'):
        calls = sum(1 + (e.get('retries') or 0) for e in attempts)
    latency = sum(e.get('latency_s') or 0 for e in outputs or attempts)
    stops = [r for r in records if r.get('stop_reason')]
    failures = [{'target': r['target'], 'attempts': r['attempts_used'], 'stop': r.get('stop_reason'),
                 'guesses': [e.get('guess') for e in r['trace']]} for r in records if not r['solved']]
    memory_checked = memory_equivalent = 0
    if events:
        ns = load_engine()
        for record in records:
            states = {e['turn']: e['state'] for e in record.get('agent_trace', [])
                      if e['kind'] == 'handoff' and e.get('source') == 'memory'}
            for turn, state in states.items():
                before = [e for e in record['trace'] if e['turn'] < turn]
                expected = observed_state(public_history(ns, before))
                predicted_pool = query_roster(state, ns['CHAMPIONS'], 173)['candidates']
                expected_pool = query_roster(expected, ns['CHAMPIONS'], 173)['candidates']
                memory_checked += 1
                memory_equivalent += set(predicted_pool) == set(expected_pool)
    return {'label': label, 'source': str(source.relative_to(ROOT)), 'split': payload['split'],
            'complete': payload.get('complete', False), 'games': len(records),
            'solved': sum(r['solved'] for r in records), 'solve_rate': mean(r['solved'] for r in records),
            'attempts': len(attempts), 'mean_attempts_solved': historical['intentos_prom_resueltas'],
            'historical_violation_rate': historical['tasa_violacion'],
            'strict_violation_rate': (sum(e.get('strict_violation', False) for e in eligible) / len(eligible)) if eligible else None,
            'eligible_attempts': len(eligible), 'invalid_rate': historical['tasa_invalidos'],
            'repeat_rate': historical['tasa_repeticiones'], 'cfs_historical': historical['CFS'],
            'stopped_games': len(stops), 'zero_submission_games': sum(not r['trace'] for r in records),
            'calls': calls, 'calls_per_game': calls / len(records),
            'model_seconds': round(latency, 3), 'model_seconds_per_game': latency / len(records),
            'completion_tokens': sum(e.get('usage', {}).get('completion_tokens', 0) or 0 for e in outputs) if outputs else sum(e.get('completion_tokens') or 0 for e in attempts),
            'api_errors': sum(e['kind'] == 'model_error' for e in events) + sum(bool(e.get('api_error')) for e in attempts),
            'protocol_errors': sum(e['kind'] == 'protocol_error' for e in events),
            'memory_turns_checked': memory_checked,
            'memory_pool_equivalence_rate': memory_equivalent / memory_checked if memory_checked else None,
            'revisions': sum(e['kind'] == 'handoff' and e.get('destination') in ('memory', 'selector') and e.get('source') in ('selector', 'verifier') for e in events),
            'tool_calls': sum(e['kind'] == 'decision' and e.get('decision', {}).get('action') in ('validar_estado', 'validar_jugada', 'consultar_roster') for e in events), 'failures': failures}


def paired(left, right):
    a = {r['target']: r for r in left['records']}
    b = {r['target']: r for r in right['records']}
    common = sorted(a.keys() & b.keys())
    wins = sum(b[t]['solved'] and not a[t]['solved'] for t in common)
    losses = sum(a[t]['solved'] and not b[t]['solved'] for t in common)
    n = wins + losses
    p = min(1, 2 * sum(comb(n, i) for i in range(min(wins, losses) + 1)) / 2 ** n) if n else 1
    return {'paired_targets': len(common), 'wins': wins, 'losses': losses, 'mcnemar_exact_p': p}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', default='results/d3/raw')
    parser.add_argument('--out', default='results/d3')
    args = parser.parse_args()
    paths = sorted((ROOT / args.input).glob('*.json.gz'))
    payloads = [(p, read(p)) for p in paths]
    rows = [metrics(p, path) for path, p in payloads if p.get('records')]
    out = ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)
    comparisons = {}
    for path, reference in payloads:
        if reference['variant'] != 'full' or not reference.get('complete'):
            continue
        for other_path, other in payloads:
            if other_path == path or other['split'] != reference['split'] or not other.get('complete'):
                continue
            if other['targets'] != reference['targets']:
                continue
            comparisons[f"{other['weights']}/{other['variant']} → {reference['weights']}/full"] = paired(other, reference)
    atomic_json(out / 'summary.json', {'rows': rows, 'comparisons': comparisons,
                'note': 'Una partida por objetivo, temperatura 0. No son réplicas independientes. Los paros cuentan como no resueltos.'})
    columns = [k for k in (rows[0] if rows else {}) if k != 'failures']
    with (out / 'summary.csv').open('w') as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
    lines = ['# Entregable 3 · resultados observados', '',
             'Cada fila declara su tamaño y si terminó. Los fallos y paros permanecen en los denominadores.', '',
             '| Variante | Partidas | Resueltas | Violación histórica | Violación estricta | Paros | Llamadas/partida | Segundos modelo/partida |',
             '|---|---:|---:|---:|---:|---:|---:|---:|']
    fmt = lambda value: '—' if value is None else f'{100 * value:.1f}%'
    for row in rows:
        lines.append(f"| {row['label']}{'' if row['complete'] else ' (parcial)'} | {row['games']} | {row['solved']} | {fmt(row['historical_violation_rate'])} | {fmt(row['strict_violation_rate'])} | {row['stopped_games']} | {row['calls_per_game']:.1f} | {row['model_seconds_per_game']:.1f} |")
    lines += ['', '## Interpretación y límites', '',
              '- La tasa histórica conserva el checker D1/D2, que ignora amarillos. La estricta agrega amarillos y repetición, sobre intentos válidos posteriores a feedback.',
              '- CFS histórico se exporta para referencia; no ordena variantes: una ejecución sin jugadas puede aparentar cumplimiento alto. Leer siempre resolución, paros y cobertura juntos.',
              '- El control algorítmico reconstruye todo el feedback sin LLM. Permite separar la capacidad del filtro de la coordinación de agentes.',
              '- La equivalencia de Memoria exportada compara el conjunto de candidatos de su última entrega por turno con el derivado del feedback público. No garantiza igualdad de todas las cláusulas ni evalúa estados que nunca llegaron a entregarse.',
              '- Directo y D2 permiten 64 tokens por turno. Cada agente permite hasta 768 por llamada y varias llamadas; los costes no son iguales.',
              '- McNemar mide diferencias pareadas de resolución en estos objetivos. No prueba que un agente razone ni generaliza a otros juegos. Las múltiples comparaciones son exploratorias.',
              '- La mejora de 14 a 25 frente al D2 corresponde a toda la configuración (adaptador, hasta 768 tokens por llamada, 46,5 frente a 7,2 llamadas por partida), no a un agente.',
              '- Sin revisión: 13 de los 16 paros son `revision_disabled` (el Verificador pidió revisar y la ablación detiene la partida) y 3 `call_limit`; la prueba mide a la vez revisar y poder continuar. El motivo de `revisar_selector` sólo se registra y no llega al Selector; sólo `revisar_memoria` lo entrega, y no se usó en prueba.',
              '- Sin ejemplos (p = 0,12) y sin resumen previo de Memoria (29/30, p = 0,22) no son significativos. El adaptador se entrenó con ejemplos en el prompt. Que sin resumen se resuelva más cuestiona la ventaja del resumen incremental, sin probar que reconstruir sea mejor.',
              '- Paginación, prellenado JSON y `ver_atributos` no tienen ablación propia.', '',
              '## Comparaciones pareadas', '',
              'En «X → paginas/full», victorias y derrotas son las del sistema completo respecto de X.', '']
    for label, comparison in comparisons.items():
        lines.append(f"- {label}: {comparison['wins']} victorias, {comparison['losses']} derrotas discordantes; p={comparison['mcnemar_exact_p']:.6g} (n={comparison['paired_targets']}).")
    lines += ['', '## Fallos reales', '',
              'Se listan todos los fallos del sistema completo y los tres primeros de cada otra variante; la lista completa está en `summary.json`.', '']
    for row in rows:
        for failure in row['failures'] if row['label'] == 'paginas/full' else row['failures'][:3]:
            lines.append(f"- **{row['label']} · {failure['target']}**: {failure['attempts']} jugadas; {failure['stop'] or '10 intentos agotados'}; secuencia: {', '.join(str(n) for n in failure['guesses']) or 'ninguna'}. Fuente: `{row['source']}`.")
    (out / 'ANALISIS_D3.md').write_text('\n'.join(lines) + '\n')
    print(out / 'ANALISIS_D3.md')


if __name__ == '__main__':
    main()
