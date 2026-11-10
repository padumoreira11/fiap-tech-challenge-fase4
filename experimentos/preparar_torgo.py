"""Extract a bounded subset of head-mic WAVs from official TORGO tarballs.

Only regular WAV members are copied; paths from archives are never used as paths.
Files shorter than one second are skipped. Output must be a new directory.
"""
import argparse
import csv
import io
import re
import tarfile
import wave
from pathlib import Path


def prepare(archives, output, limit=50):
    if limit <= 0: raise ValueError('O limite precisa ser positivo.')
    output.mkdir(parents=True, exist_ok=False)
    counts, rows = {}, []
    for archive in archives:
        with tarfile.open(archive, mode='r|bz2') as tar:
            for member in tar:
                match = re.fullmatch(r'(F\d{2}|FC\d{2})/Session\d+/wav_headMic/[^/]+\.wav', member.name)
                if not member.isfile() or not match or member.size > 10_000_000: continue
                participant = match.group(1)
                if counts.get(participant, 0) >= limit: continue
                data = tar.extractfile(member).read()
                try:
                    with wave.open(io.BytesIO(data), 'rb') as audio:
                        if audio.getnchannels() != 1 or audio.getsampwidth() != 2 or audio.getnframes() < audio.getframerate(): continue
                except (wave.Error, EOFError):
                    continue
                index = counts.get(participant, 0)
                name = f'{participant}_{index:03d}.wav'
                (output/name).write_bytes(data)
                counts[participant] = index + 1
                rows.append({'path':name, 'participant':participant,
                             'label':0 if participant.startswith('FC') else 1,
                             'original_member':member.name})
    with (output/'manifest.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f,fieldnames=['path','participant','label','original_member'])
        writer.writeheader(); writer.writerows(rows)
    return counts


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--limit',type=int,default=50)
    parser.add_argument('archives',nargs='+',type=Path)
    args=parser.parse_args()
    print(prepare(args.archives,args.output,args.limit))
