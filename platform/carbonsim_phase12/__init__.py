from datetime import datetime, timezone

from otree.api import *

from . import engine


doc = """
Phase 1 through 3 CarbonSim prototype built on oTree with a deterministic year engine,
facilitator-controlled session start, and live dashboard decisions for abatement and offsets.
"""


class C(BaseConstants):
    NAME_IN_URL = "carbonsim_phase12"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    display_name = models.StringField(label="Name for the workshop dashboard")
    company_id = models.StringField(blank=True)
    company_name = models.StringField(blank=True)
    sector = models.StringField(blank=True)
    is_facilitator = models.BooleanField(initial=False)


def creating_session(subsession: Subsession):
    if subsession.round_number != 1:
        return

    session = subsession.session
    players = subsession.get_players()
    state = engine.create_initial_state(
        participant_count=len(players),
        phase_durations=session.config.get("phase_durations"),
    )

    for index, player in enumerate(players):
        assignment = state["companies"][index]
        player.company_id = assignment["company_id"]
        player.company_name = assignment["company_name"]
        player.sector = assignment["sector"]
        player.is_facilitator = index == 0

    session.carbonsim_state = state


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _get_state(player: Player):
    state = player.session.carbonsim_state
    state = engine.advance_state(state, _now())
    player.session.carbonsim_state = state
    return state


def _snapshot_for(player: Player, state=None):
    state = _get_state(player) if state is None else state
    participant_label = player.display_name or f"Participant {player.id_in_group}"
    return engine.build_player_snapshot(
        state,
        company_id=player.company_id,
        is_facilitator=player.is_facilitator,
        participant_label=participant_label,
        now=_now(),
    )


def _broadcast_state(player: Player, state):
    return {
        other_player.id_in_group: {
            "type": "state",
            "payload": _snapshot_for(other_player, state),
        }
        for other_player in player.subsession.get_players()
    }


class Welcome(Page):
    form_model = "player"
    form_fields = ["display_name"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            assigned_company=player.company_name,
            sector_label=player.sector.replace("_", " ").title(),
            is_facilitator=player.is_facilitator,
        )


class WorkshopHub(Page):
    live_method = "live_workshop_hub"

    @staticmethod
    def vars_for_template(player: Player):
        snapshot = _snapshot_for(player)
        return dict(
            initial_snapshot=snapshot,
            company_name=player.company_name,
            sector_label=player.sector.replace("_", " ").title(),
            is_facilitator=player.is_facilitator,
        )

    @staticmethod
    def js_vars(player: Player):
        return dict(initial_snapshot=_snapshot_for(player))


def live_workshop_hub(player: Player, data):
    state = _get_state(player)
    action = data.get("action") if isinstance(data, dict) else None

    if (
        action == "start_session"
        and player.is_facilitator
        and state["phase"] == engine.PHASE_LOBBY
    ):
        state = engine.start_simulation(state, _now())
        player.session.carbonsim_state = state

    if action == "activate_abatement":
        state = engine.apply_company_decision(
            state,
            company_id=player.company_id,
            action="activate_abatement",
            payload={"measure_id": data.get("measure_id")},
            now=_now(),
        )
        player.session.carbonsim_state = state

    if action == "buy_offsets":
        state = engine.apply_company_decision(
            state,
            company_id=player.company_id,
            action="buy_offsets",
            payload={"quantity": data.get("quantity", 0)},
            now=_now(),
        )
        player.session.carbonsim_state = state

    if action == "open_auction" and player.is_facilitator:
        state = engine.open_auction(
            state,
            auction_id=data.get("auction_id"),
            now=_now(),
        )
        player.session.carbonsim_state = state

    if action == "close_auction" and player.is_facilitator:
        state = engine.close_auction(
            state,
            auction_id=data.get("auction_id"),
            now=_now(),
        )
        player.session.carbonsim_state = state

    if action == "submit_auction_bid":
        state = engine.apply_company_decision(
            state,
            company_id=player.company_id,
            action="submit_auction_bid",
            payload={
                "auction_id": data.get("auction_id"),
                "quantity": data.get("quantity", 0),
                "price": data.get("price", 0),
            },
            now=_now(),
        )
        player.session.carbonsim_state = state

    return _broadcast_state(player, state)


page_sequence = [Welcome, WorkshopHub]
