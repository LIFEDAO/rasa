import numpy as np
import pytest

import scipy.sparse

from rasa.nlu.tokenizers.whitespace_tokenizer import WhitespaceTokenizer
from rasa.nlu.featurizers.sparse_featurizer.text_featurizer import TextFeaturizer
from rasa.nlu.training_data import TrainingData
from rasa.nlu.constants import TEXT_ATTRIBUTE, SPARSE_FEATURE_NAMES
from rasa.nlu.training_data import Message


@pytest.mark.parametrize(
    "sentence, expected, expected_cls",
    [
        (
            "hello goodbye hello",
            [[0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 1.0, 0.0]],
            [[2.0, 3.0, 1.0, 2.0, 2.0, 1.0, 2.0, 1.0, 1.0]],
        ),
        (
            "a 1 2",
            [[0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0]],
            [[2.0, 1.0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.0, 1.0]],
        ),
    ],
)
def test_text_featurizer(sentence, expected, expected_cls):
    featurizer = TextFeaturizer(
        {"features": [["upper"], ["prefix2", "suffix2", "digit"], ["low"]]}
    )

    train_message = Message(sentence)
    test_message = Message(sentence)

    WhitespaceTokenizer().process(train_message)
    WhitespaceTokenizer().process(test_message)

    featurizer.train(TrainingData([train_message]))

    featurizer.process(test_message)

    assert isinstance(
        test_message.get(SPARSE_FEATURE_NAMES[TEXT_ATTRIBUTE]), scipy.sparse.coo_matrix
    )

    actual = test_message.get(SPARSE_FEATURE_NAMES[TEXT_ATTRIBUTE]).toarray()

    assert np.all(actual[0] == expected)
    assert np.all(actual[-1] == expected_cls)


@pytest.mark.parametrize(
    "sentence, expected, expected_cls",
    [
        (
            "hello 123 hello 123 hello",
            [[0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0]],
            [[2.0, 2.0, 3.0, 2.0, 3.0, 2.0, 2.0, 2.0, 1.0]],
        )
    ],
)
def test_text_featurizer_window_size(sentence, expected, expected_cls):
    featurizer = TextFeaturizer(
        {"features": [["upper"], ["digit"], ["low"], ["digit"]]}
    )

    train_message = Message(sentence)
    test_message = Message(sentence)

    WhitespaceTokenizer().process(train_message)
    WhitespaceTokenizer().process(test_message)

    featurizer.train(TrainingData([train_message]))

    featurizer.process(test_message)

    assert isinstance(
        test_message.get(SPARSE_FEATURE_NAMES[TEXT_ATTRIBUTE]), scipy.sparse.coo_matrix
    )

    actual = test_message.get(SPARSE_FEATURE_NAMES[TEXT_ATTRIBUTE]).toarray()

    assert np.all(actual[0] == expected)
    assert np.all(actual[-1] == expected_cls)
