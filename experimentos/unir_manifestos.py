"""Merge prepared TORGO manifests without copying recordings."""
import argparse
import csv
import os
from pathlib import Path


def merge(inputs, output):
    output = Path(output)
    if output.exists(): raise FileExistsError(output)
    rows=[]
    for filename in inputs:
        filename=Path(filename).resolve()
        with filename.open(encoding='utf-8',newline='') as stream:
            for row in csv.DictReader(stream):
                audio=(filename.parent/row['path']).resolve()
                if not audio.is_file(): raise FileNotFoundError(audio)
                rows.append({'path':os.path.relpath(audio,output.parent.resolve()),
                             'participant':row['participant'], 'label':row['label']})
    with output.open('x',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=['path','participant','label'])
        writer.writeheader(); writer.writerows(rows)
    return len(rows)


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('inputs',nargs='+',type=Path)
    args=parser.parse_args()
    print('Gravações:',merge(args.inputs,args.output))
