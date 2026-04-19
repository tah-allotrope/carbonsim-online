from os import environ

SESSION_CONFIGS = [
    dict(
        name="carbonsim_workshop_phase12",
        display_name="CarbonSim Workshop (Vietnam Pilot)",
        app_sequence=["carbonsim_phase12"],
        num_demo_participants=6,
        phase_durations=dict(year_start=5, decision_window=20, compliance=5),
        scenario="vietnam_pilot",
        bot_count=0,
        bot_strategy="moderate",
        doc="Phase 1-7 prototype with scenario packs, bots, shocks, facilitator tools, and full trading.",
    ),
    dict(
        name="carbonsim_high_pressure",
        display_name="CarbonSim Workshop (High Pressure)",
        app_sequence=["carbonsim_phase12"],
        num_demo_participants=6,
        phase_durations=dict(year_start=5, decision_window=20, compliance=5),
        scenario="high_pressure",
        bot_count=0,
        bot_strategy="moderate",
        doc="High pressure scenario with sharper cap decline and higher penalties.",
    ),
    dict(
        name="carbonsim_generous",
        display_name="CarbonSim Workshop (Generous Allocation)",
        app_sequence=["carbonsim_phase12"],
        num_demo_participants=6,
        phase_durations=dict(year_start=5, decision_window=25, compliance=5),
        scenario="generous",
        bot_count=0,
        bot_strategy="moderate",
        doc="Introductory scenario with gentler cap decline and lower penalties.",
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = ["carbonsim_state"]

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = "en"

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = "USD"
USE_POINTS = True

ADMIN_USERNAME = "admin"
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get("OTREE_ADMIN_PASSWORD")

DEMO_PAGE_INTRO_HTML = """ """

ROOMS = [
    dict(
        name="workshop_room",
        display_name="CarbonSim Workshop Room",
    )
]

SECRET_KEY = "1314886002300"
