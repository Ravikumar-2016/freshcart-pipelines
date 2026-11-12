"""Pure-Python model of RabbitMQ topic routing (no broker, no pika needed).

Used in two ways: (1) as an independent reference implementation that the live-broker verification is compared
against, and (2) by a CI unit test. Also holds the driver table of Part D.

Rules (RabbitMQ topic exchange): a routing key is words separated by dots.
  *  matches exactly one word
  #  matches zero or more words
  any other word must match literally
"""

# Part D, D1: driver name -> binding pattern (order matters for readable output)
DRIVERS = {
    "Ravi": "bangalore.koramangala.*",
    "Priya": "bangalore.indiranagar.*",
    "Arjun": "bangalore.*.ride",
    "Meena": "bangalore.*.food",
    "Karthik": "chennai.tnagar.food",
    "Control": "bangalore.#",
}

# Part D, D1: the six routing cases and the recipients predicted on paper (an empty list means "dropped")
CASES = [
    ("bangalore.koramangala.food", ["Ravi", "Meena", "Control"]),
    ("bangalore.indiranagar.ride", ["Priya", "Arjun", "Control"]),
    ("bangalore.whitefield.ride", ["Arjun", "Control"]),
    ("chennai.tnagar.food", ["Karthik"]),
    ("chennai.whitefield.ride", []),
    ("bangalore.koramangala", ["Control"]),
]


def topic_matches(pattern, key):
    """True if the binding `pattern` matches the routing `key` under RabbitMQ topic rules."""
    pat, words = pattern.split("."), key.split(".")

    def match(i, j):
        if i == len(pat):
            return j == len(words)
        if pat[i] == "#":                                   # zero or more words
            return any(match(i + 1, k) for k in range(j, len(words) + 1))
        if j == len(words):                                 # '*' or a literal needs a word
            return False
        if pat[i] == "*" or pat[i] == words[j]:             # exactly one word
            return match(i + 1, j + 1)
        return False

    return match(0, 0)


def recipients(key, drivers=None):
    """Names of the drivers whose pattern matches `key`, in table order."""
    drivers = DRIVERS if drivers is None else drivers
    return [name for name, pattern in drivers.items() if topic_matches(pattern, key)]
