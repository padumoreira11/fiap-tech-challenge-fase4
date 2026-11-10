"""Monitor local de CSV incremental; não conectar a pacientes reais."""
import argparse
import csv
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from engine import vital_alerts


def event_id(row, alert):
    payload = json.dumps({'row': row, 'alert': alert}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def poll(source, output):
    """Read complete CSV snapshot and append unseen alerts. One writer only."""
    seen = set()
    if output.exists():
        with output.open(encoding='utf-8') as stream:
            for line in stream:
                event = json.loads(line)
                seen.add(event['id'])
    with source.open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    pending = []
    for row in rows:
        for alert in vital_alerts([row]):
            identifier = event_id(row, alert)
            if identifier not in seen:
                seen.add(identifier)
                pending.append({'id': identifier, 'created_utc': datetime.now(timezone.utc).isoformat(),
                                'status': 'pendente de revisão', **alert})
    if pending:
        with output.open('a', encoding='utf-8') as stream:
            for event in pending:
                stream.write(json.dumps(event, ensure_ascii=False) + '\n')
    return pending


def main():
    parser = argparse.ArgumentParser(description='Monitor educacional por arquivo CSV')
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--interval', type=float, default=3)
    args = parser.parse_args()
    if args.interval <= 0: parser.error('O intervalo deve ser positivo.')
    if args.source.resolve() == args.output.resolve(): parser.error('Entrada e saída precisam ser arquivos diferentes.')
    print('Monitor iniciado. Pressione Ctrl+C para parar.', flush=True)
    try:
        while True:
            try:
                for event in poll(args.source, args.output):
                    print(json.dumps(event, ensure_ascii=False), flush=True)
            except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
                print(f'Entrada inválida ou indisponível: {exc}', flush=True)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print('\nMonitor encerrado.')


if __name__ == '__main__': main()
