"""Mage transformer block: add an 80/20 train/test `split` column to the Iris data.

The decorators are imported only when Mage has not already injected them, and
fall back to no-ops when mage_ai is not installed (e.g. in CI), so this file
can be imported and tested outside Mage.
"""
from sklearn.model_selection import train_test_split

if 'transformer' not in globals():
    try:
        from mage_ai.data_preparation.decorators import transformer
    except ImportError:
        def transformer(func):
            return func
if 'test' not in globals():
    try:
        from mage_ai.data_preparation.decorators import test
    except ImportError:
        def test(func):
            return func


@transformer
def transform(df, *args, **kwargs):
    """Return a copy of df with a `split` column: 'train' (80%) or 'test' (20%)."""
    train_idx, test_idx = train_test_split(df.index, test_size=0.2, random_state=42)
    out = df.copy()
    out['split'] = 'train'
    out.loc[test_idx, 'split'] = 'test'
    return out


@test
def test_output(output, *args) -> None:
    assert output is not None, 'The output is undefined'
    assert 'split' in output.columns, 'Missing split column'
    assert set(output['split']) == {'train', 'test'}, 'split must be train/test'
