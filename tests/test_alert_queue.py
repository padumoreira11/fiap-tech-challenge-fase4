from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from alert_queue import enqueue, list_alerts, acknowledge


def test_queue_delivers_deduplicates_and_acknowledges(tmp_path):
    path=tmp_path/'queue.sqlite3'
    alert={'source':'sinais vitais','time':'amostra 3','message':'SpO2 baixa no exemplo'}
    assert enqueue(path,'run-1',[alert]) == 1
    assert enqueue(path,'run-1',[alert]) == 0
    assert enqueue(path,'run-2',[alert]) == 1
    item=list_alerts(path,'run-1')[0]
    assert item['acknowledged_utc'] is None
    assert not acknowledge(path,'run-2',item['id'])
    assert acknowledge(path,'run-1',item['id'])
    assert not acknowledge(path,'run-1',item['id'])
    assert list_alerts(path,'run-1')[0]['acknowledged_utc']
