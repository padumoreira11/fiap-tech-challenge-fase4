"""Métricas para avaliar transcrições; não avalia diagnóstico ou fala patológica."""
import re
import unicodedata


def normalize(text):
    text = unicodedata.normalize('NFKC', text).casefold()
    return re.findall(r'\w+', text, flags=re.UNICODE)


def word_error_rate(reference, hypothesis):
    expected, actual = normalize(reference), normalize(hypothesis)
    if not expected:
        raise ValueError('A transcrição de referência não pode ser vazia.')
    previous = list(range(len(actual) + 1))
    for i, word in enumerate(expected, 1):
        current = [i]
        for j, output in enumerate(actual, 1):
            current.append(min(current[-1] + 1, previous[j] + 1,
                               previous[j - 1] + (word != output)))
        previous = current
    return {'reference_words': len(expected), 'errors': previous[-1],
            'wer': previous[-1] / len(expected)}
