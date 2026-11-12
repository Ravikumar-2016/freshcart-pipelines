"""Unit test for the pure topic-routing model used by Part D (no broker, no pika)."""
import pytest

from stream.topic import CASES, DRIVERS, recipients, topic_matches


@pytest.mark.parametrize("key, expected", CASES)
def test_six_routing_cases(key, expected):
    assert recipients(key) == expected


def test_star_matches_exactly_one_word():
    assert topic_matches("bangalore.*.ride", "bangalore.whitefield.ride")
    assert not topic_matches("bangalore.*.ride", "bangalore.ride")                 # zero words
    assert not topic_matches("bangalore.*.ride", "bangalore.a.b.ride")             # two words


def test_hash_matches_zero_or_more_words():
    assert topic_matches("bangalore.#", "bangalore")                               # zero words
    assert topic_matches("bangalore.#", "bangalore.koramangala")                   # one word
    assert topic_matches("bangalore.#", "bangalore.koramangala.food")              # two words
    assert not topic_matches("bangalore.#", "chennai.tnagar.food")


def test_two_word_key_only_reaches_the_hash_binding():
    assert [n for n, p in DRIVERS.items() if topic_matches(p, "bangalore.koramangala")] == ["Control"]
