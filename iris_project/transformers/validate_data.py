if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def validate_data(df, *args, **kwargs):
    """Pass the data through unchanged and report basic quality facts.

    The @test below is the gate: it stops the pipeline if the data is unusable.
    """
    print(f'validate_data: {len(df)} rows, {int(df.isna().sum().sum())} missing values, '
          f'{df["target"].nunique()} classes')
    return df


@test
def test_no_missing_values(output, *args) -> None:
    assert output is not None, 'The output is undefined'
    missing = int(output.isna().sum().sum())
    assert missing == 0, f'Found {missing} missing values'


@test
def test_three_classes(output, *args) -> None:
    classes = sorted(output['target'].unique())
    assert len(classes) == 3, f'Expected exactly 3 classes, got {classes}'
