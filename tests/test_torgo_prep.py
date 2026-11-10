import importlib.util
import io
import tarfile
import wave
from pathlib import Path

spec = importlib.util.spec_from_file_location('torgo_prep', Path(__file__).resolve().parents[1] / 'experimentos' / 'preparar_torgo.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_extracts_only_matching_wav_and_never_uses_archive_path(tmp_path):
    buffer=io.BytesIO()
    with wave.open(buffer,'wb') as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(16000); f.writeframes(b'\0\0'*16000)
    payload=buffer.getvalue()
    archive=tmp_path/'test.tar.bz2'
    with tarfile.open(archive,'w:bz2') as tar:
        for name in ['F01/Session1/wav_headMic/0001.wav','../../evil.wav']:
            info=tarfile.TarInfo(name); info.size=len(payload); tar.addfile(info,io.BytesIO(payload))
    output=tmp_path/'out'
    assert module.prepare([archive],output,limit=1)=={'F01':1}
    assert (output/'F01_000.wav').exists()
    assert not (tmp_path/'evil.wav').exists()
