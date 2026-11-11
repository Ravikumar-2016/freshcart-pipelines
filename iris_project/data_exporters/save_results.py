import os

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

OUTPUT_PATH = 'iris_predictions.csv'


@data_exporter
def export_data(df, *args, **kwargs) -> None:
    """Write the test-set predictions to iris_predictions.csv (relative to the working dir)."""
    df.to_csv(OUTPUT_PATH, index=False)
    print(f'Saved {len(df)} rows to {os.path.abspath(OUTPUT_PATH)}')


@test
def test_output(*args) -> None:
    assert os.path.exists(OUTPUT_PATH), f'{OUTPUT_PATH} was not created'
    with open(OUTPUT_PATH) as f:
        n_lines = sum(1 for _ in f)
    assert n_lines == 31, f'Expected header + 30 rows, got {n_lines} lines'
