"""Experimento offline de áudio rotulado. Não é ferramenta clínica.

Manifesto CSV: path,participant,label. Label 1 = disartria, 0 = controle.
Cada participante deve ter rótulo único. Não inclui dados nem baixa modelos.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine import audio_features


def features(path):
    measured = audio_features(str(path))
    duration = measured['duration_seconds']
    return [measured['pause_count_300ms'] / duration,
            sum(measured['pause_durations_seconds']) / duration,
            np.mean(measured['rms_per_second']),
            np.std(measured['rms_per_second']),
            measured['clipped_fraction']]


def evaluate(manifest):
    manifest = Path(manifest)
    df = pd.read_csv(manifest, dtype={'participant': str})
    if not {'path', 'participant', 'label'}.issubset(df.columns) or df.empty:
        raise ValueError('Manifesto deve conter path, participant e label.')
    if df[['path','participant','label']].isna().any().any() or not set(df.label.unique()) == {0,1}:
        raise ValueError('São necessários identificadores e rótulos 0 e 1 válidos.')
    if (df.groupby('participant').label.nunique() != 1).any():
        raise ValueError('Cada participante deve ter um único rótulo.')
    group_labels = df.groupby('participant').label.first()
    if (group_labels.value_counts() < 2).any():
        raise ValueError('São necessários ao menos dois participantes por classe.')
    resolved = [(manifest.parent / Path(p)).resolve() for p in df.path]
    if len(set(resolved)) != len(resolved):
        raise ValueError('O mesmo caminho aparece mais de uma vez no manifesto.')
    X = np.asarray([features(p) for p in resolved], dtype=float)
    y, groups = df.label.to_numpy(dtype=int), df.participant.to_numpy()
    probabilities = np.zeros(len(df))
    for train, test in LeaveOneGroupOut().split(X, y, groups):
        model = make_pipeline(StandardScaler(), LogisticRegression(class_weight='balanced', max_iter=2000, random_state=0))
        model.fit(X[train], y[train])
        probabilities[test] = model.predict_proba(X[test])[:, 1]
    subject = pd.DataFrame({'participant':groups, 'label':y, 'probability':probabilities}).groupby('participant').agg(label=('label','first'), probability=('probability','mean'))
    truth = subject.label.to_numpy(dtype=int)
    predicted = (subject.probability.to_numpy() >= .5).astype(int)
    matrix = confusion_matrix(truth,predicted,labels=[0,1])
    tn, fp, fn, tp = matrix.ravel()
    return {'recordings':len(df), 'participants':len(subject), 'classes':{'0':int(sum(truth==0)), '1':int(sum(truth==1))},
            'confusion_matrix_rows_true_columns_predicted':matrix.tolist(), 'accuracy':float(accuracy_score(truth,predicted)),
            'balanced_accuracy':float(balanced_accuracy_score(truth,predicted)), 'sensitivity':float(tp/(tp+fn)),
            'specificity':float(tn/(tn+fp)), 'majority_class_accuracy':float(max(sum(truth==0),sum(truth==1))/len(truth)),
            'method':'leave one participant out; train-only scaling; average held-out recording probabilities per participant',
            'limitations':'Experimental, not diagnosis; recording conditions, prompts, language and small sample can confound results.'}


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('manifest')
    args=parser.parse_args()
    print(json.dumps(evaluate(args.manifest),ensure_ascii=False,indent=2))
