from datetime import datetime, timezone

from otree.api import *

from . import engine


doc = """
Phase 1 through 7 CarbonSim prototype built on oTree with a deterministic year engine,
facilitator-controlled session pause/resume/advance, participant status tracking,
exportable session data, scenario packs, bot participants, shock events,
and live dashboard decisions for abatement, offsets, auctions, and bilateral trading.
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
    config = session.config or {}
    scenario = config.get("scenario", "vietnam_pilot")
    bot_count = config.get("bot_count", 0)
    bot_strategy = config.get("bot_strategy", engine.BOT_STRATEGY_MODERATE)

    state = engine.create_initial_state(
        participant_count=len(players),
        phase_durations=config.get("phase_durations"),
        scenario=scenario,
        bot_count=bot_count,
        bot_strategy=bot_strategy,
    )

    for index, player in enumerate(players):
        if index >= len(state["companies"]):
            break
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


class FacilitatorPanel(Page):
    live_method = "live_facilitator_panel"

    @staticmethod
    def is_displayed(player: Player):
        return player.is_facilitator

    @staticmethod
    def vars_for_template(player: Player):
        state = _get_state(player)
        facilitator_snapshot = engine.build_facilitator_snapshot(state, now=_now())
        return dict(
            initial_facilitator_snapshot=facilitator_snapshot,
        )

    @staticmethod
    def js_vars(player: Player):
        state = _get_state(player)
        facilitator_snapshot = engine.build_facilitator_snapshot(state, now=_now())
        return dict(initial_facilitator_snapshot=facilitator_snapshot)


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

    if action == "pause_session" and player.is_facilitator:
        state = engine.pause_session(state, _now())
        player.session.carbonsim_state = state

    if action == "resume_session" and player.is_facilitator:
        state = engine.resume_session(state, _now())
        player.session.carbonsim_state = state

    if action == "force_advance_phase" and player.is_facilitator:
        state = engine.force_advance_phase(state, _now())
        player.session.carbonsim_state = state

    if action == "activate_abatement":
        state = engine.apply_company_decision(
            state,
            company_id=player.company_id,
            action="activate_abatement",
            payload={"measure_id": data.get("measure_id")},
            now=_now(),
        )
        engine.update_participant_status(
            state, company_id=player.company_id, action="activate_abatement", now=_now()
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
        engine.update_participant_status(
            state, company_id=player.company_id, action="buy_offsets", now=_now()
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
        engine.update_participant_status(
            state, company_id=player.company_id, action="submit_auction_bid", now=_now()
        )
        player.session.carbonsim_state = state

    if action == "propose_trade":
        state = engine.apply_company_decision(
            state,
            company_id=player.company_id,
            action="propose_trade",
            payload={
                "buyer_company_id": data.get("buyer_company_id"),
                "quantity": data.get("quantity", 0),
                "price_per_allowance": data.get("price_per_allowance", 0),
            },
            now=_now(),
        )
        engine.update_participant_status(
            state, company_id=player.company_id, action="propose_trade", now=_now()
        )
        player.session.carbonsim_state = state

    if action == "respond_trade":
        state = engine.respond_to_trade(
            state,
            trade_id=data.get("trade_id"),
            responder_company_id=player.company_id,
            response=data.get("response"),
            now=_now(),
        )
        engine.update_participant_status(
            state, company_id=player.company_id, action="respond_trade", now=_now()
        )
        player.session.carbonsim_state = state

    if action == "export_session" and player.is_facilitator:
        export = engine.export_session_data(state)
        player.session.carbonsim_state = state
        return {
            **_broadcast_state(player, state),
            player.id_in_group: {
                "type": "export",
                "payload": export,
            },
        }

    return _broadcast_state(player, state)


def live_facilitator_panel(player: Player, data):
    state = _get_state(player)
    action = data.get("action") if isinstance(data, dict) else None

    if action == "pause_session" and player.is_facilitator:
        state = engine.pause_session(state, _now())
        player.session.carbonsim_state = state

    if action == "resume_session" and player.is_facilitator:
        state = engine.resume_session(state, _now())
        player.session.carbonsim_state = state

    if action == "force_advance_phase" and player.is_facilitator:
        state = engine.force_advance_phase(state, _now())
        state = engine.run_bot_turns(state, now=_now())
        player.session.carbonsim_state = state

    if action == "apply_shock" and player.is_facilitator:
        state = engine.apply_shock(
            state,
            shock_type=data.get("shock_type", "emissions_spike"),
            magnitude=float(data.get("magnitude", 0.1)),
            now=_now(),
        )
        player.session.carbonsim_state = state

    if action == "run_bots" and player.is_facilitator:
        state = engine.run_bot_turns(state, now=_now())
        player.session.carbonsim_state = state

    if action == "export_session" and player.is_facilitator:
        export = engine.export_session_data(state)
        summary = engine.build_session_summary(state)
        player.session.carbonsim_state = state
        return {
            player.id_in_group: {
                "type": "export",
                "payload": export,
                "summary": summary,
            },
        }

    facilitator_snapshot = engine.build_facilitator_snapshot(state, now=_now())
    return {
        player.id_in_group: {
            "type": "facilitator_state",
            "payload": facilitator_snapshot,
        },
    }


page_sequence = [Welcome, WorkshopHub, FacilitatorPanel]
