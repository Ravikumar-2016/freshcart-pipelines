import pandas as pd
from sklearn.datasets import load_iris
from sklearn.metrics import classification_report, confusion_matrix

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def evaluate_model(df, *args, **kwargs):
    """Print the confusion matrix and return a per-class metrics table."""
    names = list(load_iris().target_names)
    labels = [0, 1, 2]

    matrix = confusion_matrix(df['target'], df['predicted'], labels=labels)
    matrix_df = pd.DataFrame(
        matrix,
        index=[f'actual_{n}' for n in names],
        columns=[f'pred_{n}' for n in names],
    )
    print('Confusion matrix:')
    print(matrix_df.to_string())

    report = classification_report(
        df['target'], df['predicted'], labels=labels, target_names=names,
        output_dict=True, zero_division=0,
    )
    metrics = pd.DataFrame(report).T.reset_index().rename(columns={'index': 'class'})
    print('\nMetrics table:')
    print(metrics.round(4).to_string(index=False))
    return metrics


@test
def test_metrics(output, *args) -> None:
    assert output is not None, 'The output is undefined'
    per_class = output[output['class'].isin(['setosa', 'versicolor', 'virginica'])]
    assert len(per_class) == 3, 'Expected one metrics row per class'
    assert per_class['support'].sum() == 30, 'Class supports must sum to 30 test rows'
    assert {'precision', 'recall', 'f1-score'} <= set(output.columns)
