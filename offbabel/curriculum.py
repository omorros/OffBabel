"""Curriculum content: what OffBabel teaches. Pure data, no logic.

Speak: scenario lessons at CEFR levels. Targets are concept glosses (English); the tutor
teaches and evaluates them IN the target language, so we score meaning, not exact strings
(robust to transcription variation). Sign: a fingerspelling progression, vowels first, then
visually distinct consonants, then words (BSL is two-handed).
"""

# ---- SPEAK: scenario lessons ----
LEVEL_SPEECH = {
    "A1": "Use very short sentences (<=6 words), present tense, speak slowly, repeat key words.",
    "A2": "Use short connected sentences, everyday vocabulary, some past tense.",
    "B1": "Speak at a natural pace, use connectors (because, although) and follow-up questions.",
}

LEVEL_SUPPORT = {
    "A1": "Model the target phrase first and invite the learner to repeat it.",
    "A2": "Give a small hint (the first word) then wait for the learner.",
    "B1": "Only rephrase or help if the learner stalls for a full turn.",
}

SPEAK_SCENARIOS = [
    {
        "id": "greetings",
        "level": "A1",
        "title": "Greetings & introductions",
        "tutor_role": "a friendly local meeting someone new",
        "targets": ["say hello", "ask how someone is", "say your name", "say goodbye"],
    },
    {
        "id": "numbers_prices",
        "level": "A1",
        "title": "Numbers & prices",
        "tutor_role": "a market vendor",
        "targets": ["count to ten", "ask the price", "say a number", "say thank you"],
    },
    {
        "id": "ordering_food",
        "level": "A2",
        "title": "Ordering food",
        "tutor_role": "a friendly cafe waiter",
        "targets": ["ask for the menu", "order a dish", "ask the price", "ask for the bill"],
    },
    {
        "id": "directions",
        "level": "A2",
        "title": "Asking for directions",
        "tutor_role": "a helpful passer-by",
        "targets": ["ask where something is", "understand left/right", "ask how far", "say thanks"],
    },
    {
        "id": "making_plans",
        "level": "B1",
        "title": "Making plans",
        "tutor_role": "a friend organizing a weekend",
        "targets": ["suggest an activity", "agree or disagree", "propose a time", "give a reason"],
    },
]


def scenario(scenario_id):
    for s in SPEAK_SCENARIOS:
        if s["id"] == scenario_id:
            return s
    return None


# ---- SIGN: BSL fingerspelling progression (two-handed) ----
# Vowels first (distinct points on the passive hand), then visually distinct consonants,
# then words. Look-alikes are kept out of the same early batch.
SIGN_LEVELS = [
    {"id": "L1_vowels", "title": "Vowels", "kind": "letters", "items": ["A", "E", "I", "O", "U"]},
    {"id": "L2_distinct", "title": "Distinct letters", "kind": "letters", "items": ["B", "C", "L", "R", "T"]},
    {"id": "L3_words", "title": "Short words", "kind": "words", "items": ["HELLO", "CAT", "DOG"]},
    {"id": "L4_common", "title": "Common words", "kind": "words", "items": ["THANK", "NAME", "GOOD"]},
]


def sign_level(level_id):
    for lv in SIGN_LEVELS:
        if lv["id"] == level_id:
            return lv
    return None
