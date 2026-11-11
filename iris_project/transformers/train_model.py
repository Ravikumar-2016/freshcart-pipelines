from sklearn.tree import DecisionTreeClassifier

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

# Quality gate: a model below this test accuracy must not be saved.
# (The reference notebook is not available, so this threshold is my own choice.)
MIN_ACCURACY = 0.90


@transformer
def train_model(df, *args, **kwargs):
    """Train a decision tree on the train split; return the test rows with predictions.

    `max_depth` is a runtime variable (mage run ... --runtime-vars '{"max_depth": 3}'),
    default 3.
    """
    max_depth = int(kwargs.get('max_depth', 3))
    features = [c for c in df.columns if c not in ('target', 'split')]
    train = df[df['split'] == 'train']
    test_rows = df[df['split'] == 'test'].copy()

    model = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
    model.fit(train[features], train['target'])

    test_rows['predicted'] = model.predict(test_rows[features])
    test_rows['max_depth'] = max_depth
    accuracy = (test_rows['predicted'] == test_rows['target']).mean()
    print(f'max_depth={max_depth} test_accuracy={accuracy:.4f}')
    return test_rows


@test
def test_accuracy(output, *args) -> None:
    assert output is not None, 'The output is undefined'
    assert len(output) == 30, f'Expected 30 test rows, got {len(output)}'
    accuracy = (output['predicted'] == output['target']).mean()
    assert accuracy >= MIN_ACCURACY, (
        f'test accuracy {accuracy:.4f} is below the {MIN_ACCURACY} gate'
    )
