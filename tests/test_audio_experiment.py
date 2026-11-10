import importlib.util
import wave
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

spec = importlib.util.spec_from_file_location('audio_experiment', Path(__file__).resolve().parents[1] / 'experimentos' / 'avaliar_audio_rotulado.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_grouped_experiment_and_duplicate_paths(tmp_path):
    records=[]
    for i in range(4):
        filename=f'{i}.wav'
        with wave.open(str(tmp_path / filename),'wb') as f:
            f.setnchannels(1); f.setsampwidth(2); f.setframerate(16000)
            f.writeframes(np.full(24000,1000+i*1000,dtype='<i2').tobytes())
        records.append({'path':filename,'participant':str(i),'label':i//2})
    manifest=tmp_path/'manifest.csv'
    pd.DataFrame(records).to_csv(manifest,index=False)
    result=module.evaluate(manifest)
    assert result['participants']==4
    assert sum(map(sum,result['confusion_matrix_rows_true_columns_predicted'])) == 4
    records[1]['path']=records[0]['path']
    pd.DataFrame(records).to_csv(manifest,index=False)
    with pytest.raises(ValueError,match='mesmo caminho'):
        module.evaluate(manifest)
