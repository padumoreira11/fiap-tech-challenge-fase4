"""Avaliação exploratória por indivíduo de atributos fornecidos pela UCI.

Não aceita áudio nem produz diagnóstico. Recebe o ZIP oficial como argumento.
"""
import argparse
import json
import re
from zipfile import ZipFile

import numpy as np
import pandas as pd
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, balanced_accuracy_score, accuracy_score
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def evaluate(zip_path):
    with ZipFile(zip_path) as archive:
        with archive.open('parkinsons.data') as source:
            df = pd.read_csv(source)
    groups = df['name'].str.replace(r'_\d+$', '', regex=True)
    if not groups.str.fullmatch(r'phon_R\d+_S\d+').all():
        raise ValueError('Identificadores inesperados; não é seguro agrupar.')
    labels = df.groupby(groups)['status'].nunique()
    if (labels != 1).any():
        raise ValueError('Um participante possui rótulos inconsistentes.')
    X = df.drop(columns=['name', 'status'])
    y = df['status'].to_numpy(dtype=int)
    probabilities = np.zeros(len(df))
    for train, test in LeaveOneGroupOut().split(X, y, groups):
        model = make_pipeline(StandardScaler(), LogisticRegression(class_weight='balanced', max_iter=2000, random_state=0))
        model.fit(X.iloc[train], y[train])
        probabilities[test] = model.predict_proba(X.iloc[test])[:, 1]
    subject = pd.DataFrame({'group': groups, 'label': y, 'probability': probabilities}).groupby('group').agg(label=('label', 'first'), probability=('probability', 'mean'))
    truth = subject['label'].to_numpy(dtype=int)
    predicted = (subject['probability'].to_numpy() >= .5).astype(int)
    matrix = confusion_matrix(truth, predicted, labels=[0, 1])
    tn, fp, fn, tp = matrix.ravel()
    return {'dataset': 'UCI Parkinsons 174', 'doi': '10.24432/C59C74',
            'rows': len(df), 'subjects': len(subject), 'class_counts': {'0': int(sum(truth == 0)), '1': int(sum(truth == 1))},
            'method': 'leave-one-subject-out; standard scaling and balanced logistic regression fitted only on training subjects; mean probability per held-out subject; threshold 0.5',
            'confusion_matrix_rows_true_columns_predicted_0_1': matrix.tolist(),
            'accuracy': float(accuracy_score(truth, predicted)),
            'balanced_accuracy': float(balanced_accuracy_score(truth, predicted)),
            'sensitivity': float(tp/(tp+fn)) if tp+fn else None,
            'specificity': float(tn/(tn+fp)) if tn+fp else None,
            'majority_class_accuracy': float(max(sum(truth == 0), sum(truth == 1))/len(truth)),
            'versions': {'sklearn': sklearn.__version__, 'pandas': pd.__version__, 'numpy': np.__version__},
            'limitations': 'Small dataset, repeated recordings, predefined voice features and Parkinson status; no raw audio, external validation, dysarthria/fatigue labels or clinical use.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('zip_path')
    args = parser.parse_args()
    print(json.dumps(evaluate(args.zip_path), indent=2, ensure_ascii=False))
