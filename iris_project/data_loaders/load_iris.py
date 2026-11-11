from sklearn.datasets import load_iris as _load_iris

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_loader
def load_data(*args, **kwargs):
    """Load the 150-row Iris dataset (4 features + `target`) as a DataFrame."""
    return _load_iris(as_frame=True).frame


@test
def test_output(output, *args) -> None:
    assert output is not None, 'The output is undefined'
    assert len(output) == 150, f'Expected 150 rows, got {len(output)}'
    assert 'target' in output.columns, 'Missing target column'
