from datetime import timedelta

# XP
XP_BASE = 100
XP_GROWTH = 1.15
XP_BUILDINGS_STAGE_GROWTH = 0.35

# BOOST
BOOST_XP_MULTIPLIERS = {
    "boost_low": {"multiplier": 1.3, "duration_seconds": 120},
    "boost_high": {"multiplier": 1.6, "duration_seconds": 210},
    "boost_jackpot": {"multiplier": 2.2, "duration_seconds": 420},
}

BOOST_MAX_ACTIVE_MULTIPLIER = 2.5
BOOST_MAX_DURATION = timedelta(minutes=12)

# CARDS
CARDS_ALLOWED_REWARD_FOCUS = {
    "event_item",
    "coins_jackpot",
}

CARDS_BASE_PROBABILITIES = {
    "coins_jackpot": 0.01,  # 1.0%
}

CARDS_MIN_PROBABILITIES = {
    "event_item": 0.015,  # 1.5%
    "coins_jackpot": 0.005,  # 0.5%
}

CARDS_ALTERNATIVE_REWARDS_PROBABILITIES_JACKPOT = {
    "value_sum": 1.0,
    "rewards": {
        "coins_low": 0.37,
        "coins_high": 0.24,
        "boost_low": 0.12,
        "boost_high": 0.09,
        "boost_jackpot": 0.04,
        "energy_low": 0.10,
        "energy_high": 0.04,
    },
}

# WALLET
WALLET_MAX_ENERGY_COUNT = 10
WALLET_MAX_ENERGY_SECONDS = 300

# VILLAGE
BUILDING_MAX_STAGE = 4

# TICKETS
TICKETS_BUILDING_REWARD_STAGE = [
    {"index": 0, "tickets": 2},
    {"index": 1, "tickets": 4},
    {"index": 2, "tickets": 10},
    {"index": 3, "tickets": 15},
]

# DAILY REWARD
DAILY_REWARD = [
    {"day": 1, "tickets": 1, "gems": 0},
    {"day": 2, "tickets": 1, "gems": 0},
    {"day": 3, "tickets": 2, "gems": 1},
    {"day": 4, "tickets": 2, "gems": 0},
    {"day": 5, "tickets": 2, "gems": 0},
    {"day": 6, "tickets": 3, "gems": 1},
    {"day": 7, "tickets": 4, "gems": 2},
    {"day": 8, "tickets": 3, "gems": 1},
    {"day": 9, "tickets": 4, "gems": 2},
    {"day": 10, "tickets": 6, "gems": 5},
]
