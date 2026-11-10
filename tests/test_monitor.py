import csv
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from monitor import poll


def test_poll_is_idempotent_and_detects_new_row(tmp_path):
    source, output = tmp_path / 'sinais.csv', tmp_path / 'alertas.jsonl'
    fields = ['timestamp', 'heart_rate', 'spo2', 'systolic']
    with source.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerow(dict(timestamp='t1', heart_rate=125, spo2=98, systolic=120))
    assert len(poll(source, output)) == 1
    assert poll(source, output) == []
    with source.open('a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writerow(dict(timestamp='t2', heart_rate=78, spo2=88, systolic=120))
    assert len(poll(source, output)) == 1
    assert len(output.read_text().splitlines()) == 2


def test_poll_rejects_invalid_headers_without_writing(tmp_path):
    source, output = tmp_path / 'sinais.csv', tmp_path / 'alertas.jsonl'
    source.write_text('timestamp,heart_rate\nt1,125\n')
    with pytest.raises(ValueError, match='CSV precisa conter'):
        poll(source, output)
    assert not output.exists()
