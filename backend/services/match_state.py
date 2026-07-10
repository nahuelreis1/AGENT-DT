"""In-memory holder of the live `MatchState` and the `Prediction` log.

`MatchStateManager` is the seam between the data-source layer
(`create_data_source()`) and the downstream consumers: the polling
loop calls `update_fixture` / `update_details` to push new snapshots,
and the milestone detector calls `get_context_text()` to build the
n8n prompt payload.

Key behaviors:
- Score is recomputed from Goal events on every `update_details`
  call (the API's `goals` field is incremental; events are
  cumulative). This is Option A in the design — the events list is
  the single source of truth for the score.
- `get_context_text()` emits exactly 7 sections in a fixed order,
  separated by `\\n\\n`, with one trailing `\\n` — pinned by the
  `context-text-format` spec and a snapshot test.
- `save_prediction` appends a `Prediction` to the in-memory log;
  the Pydantic `momento` validator (1..=6) is the gate.

Mode-agnostic: the class never knows whether the `MatchState` came
from the mock JSONs or from a live API-Football HTTP response.

Spec: openspec/changes/backend-services/specs/match-state-manager/spec.md
Spec: openspec/changes/backend-services/specs/context-text-format/spec.md
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

from backend.models import (
    MatchEvent,
    MatchState,
    PlayerStats,
    Prediction,
    TeamStats,
)


# Map API-Football status.short to the Spanish display label used in
# the context text. Exact strings per `context-text-format` spec.
# The live API-Football v3 endpoint emits 18 distinct statuses; any
# unknown status falls back to the raw `short` value (existing
# behavior — see `PERIOD_NAMES.get(short, short)` in `_header_section`).
PERIOD_NAMES: dict[str, str] = {
    "TBD": "Horario a confirmar",
    "NS": "No iniciado",
    "1H": "1er Tiempo",
    "HT": "Entretiempo",
    "2H": "2do Tiempo",
    "ET": "Tiempo extra",
    "BT": "Descanso tiempo extra",
    "P": "Penales en curso",
    "SUSP": "Suspendido",
    "INT": "Interrumpido",
    "FT": "Final",
    "AET": "Final (tiempo extra)",
    "PEN": "Final (penales)",
    "PST": "Postergado",
    "CANC": "Cancelado",
    "ABD": "Abandonado",
    "AWD": "Perdida por regla",
    "WO": "Ganado por ausencia",
    "LIVE": "En curso",
}


# Spanish words for "goal" depending on count. Centralized so the
# highlight composer stays declarative.
_GOL_SINGULAR = "gol"
_GOL_PLURAL = "goles"
_ASIST_SINGULAR = "asistencia"
_ASIST_PLURAL = "asistencias"
_PASE_SINGULAR = "pase"
_PASE_PLURAL = "pases"


class MatchStateManager:
    """In-memory holder of the live `MatchState` and `Prediction` log.

    Plain class — no singleton. One instance per process, created
    by the FastAPI lifespan in change 3. Tests construct one
    directly.
    """

    def __init__(self) -> None:
        self._state: MatchState | None = None
        self._predictions: list[Prediction] = []

    # ------------------------------------------------------------------ #
    # Fixture + details ingestion
    # ------------------------------------------------------------------ #

    def update_fixture(self, state: MatchState) -> None:
        """Store a fresh `MatchState` (snapshot, overwrites prior).

        Per spec: this replaces the entire state, including events,
        stats, and players. Score reconciliation happens later in
        `update_details`, NOT here.
        """
        self._state = state

    def update_details(
        self,
        events: list[MatchEvent],
        home_stats: TeamStats | None,
        away_stats: TeamStats | None,
        home_players: list[PlayerStats],
        away_players: list[PlayerStats],
    ) -> None:
        """Replace events/stats/players and recompute the score.

        Score is recomputed from the `events` list — Goal events per
        team name. This OVERRIDES the score set by `update_fixture`
        because the API's `goals` field is incremental while events
        are cumulative; the events list is the source of truth.
        """
        if self._state is None:
            raise RuntimeError("MatchState not initialized — call update_fixture first")

        self._state.events = list(events)
        self._state.home_stats = home_stats
        self._state.away_stats = away_stats
        self._state.home_players = list(home_players)
        self._state.away_players = list(away_players)

        # Score reconciliation (Option A): count Goal events per team.
        # Uses the shared `_goals_for_team` helper so score recon and
        # the goals-section text cannot drift on Missed Penalty / Own
        # Goal handling. A "Missed Penalty" Goal event is excluded
        # entirely; an "Own Goal" by `team_name` is flipped to the
        # opponent's column.
        home_name = self._state.home.name
        away_name = self._state.away.name
        self._state.home.goals = len(
            _goals_for_team(events, home_name, away_name)
        )
        self._state.away.goals = len(
            _goals_for_team(events, away_name, home_name)
        )

        # Stamp the snapshot time so downstream consumers can tell
        # when the state was last touched.
        self._state.last_updated = datetime.now(tz=timezone.utc)

    # ------------------------------------------------------------------ #
    # State accessors
    # ------------------------------------------------------------------ #

    def get_state(self) -> MatchState:
        """Return the stored `MatchState` or raise if uninitialized."""
        if self._state is None:
            raise RuntimeError("MatchState not initialized — call update_fixture first")
        return self._state

    def get_context_text(self) -> str:
        """Build the 7-section context text per `context-text-format`.

        Sections (in fixed order): Header, Goals, Stats, Standout
        players, Weak players, Substitutions, Cards. Separated by
        `\\n\\n`; one trailing `\\n`. Empty sections use their
        documented fallback (e.g. `GOLES: Sin goles aún`).
        """
        state = self.get_state()
        sections = [
            self._header_section(state),
            self._goals_section(state),
            self._stats_section(state),
            self._standout_players_section(state),
            self._weak_players_section(state),
            self._substitutions_section(state),
            self._cards_section(state),
        ]
        return "\n\n".join(s for s in sections if s) + "\n"

    # ------------------------------------------------------------------ #
    # Prediction log
    # ------------------------------------------------------------------ #

    def save_prediction(self, momento: int, content: str) -> None:
        """Append a `Prediction(momento, now(), content)` to the log.

        The Pydantic model enforces momento in 1..=6. A bad value
        raises `ValidationError` (a `ValueError` subclass) here.
        """
        self._predictions.append(
            Prediction(
                momento=momento,
                timestamp=datetime.now(tz=timezone.utc),
                content=content,
            )
        )

    def get_predictions(self) -> list[Prediction]:
        """Return a copy of the prediction list (in append order)."""
        return list(self._predictions)

    # ================================================================== #
    # Context text section builders (private)
    # ================================================================== #

    @staticmethod
    def _header_section(state: MatchState) -> str:
        """`⚽ {home} {hg} - {ag} {away} | Minuto {elapsed} | {period}`."""
        period = PERIOD_NAMES.get(state.status.short, state.status.short)
        return (
            f"⚽ {state.home.name} {state.home.goals} - {state.away.goals} "
            f"{state.away.name} | Minuto {state.status.elapsed} | {period}"
        )

    @staticmethod
    def _goals_section(state: MatchState) -> str:
        """`GOLES: {home_goals_str} - {away_goals_str}` (or `Sin goles aún`).

        Uses `_goals_for_team` (shared with score reconciliation) so
        Missed Penalties and Own Goals are handled consistently:
          - "Missed Penalty" Goal events are excluded entirely
          - Own Goals are flipped to the BENEFITED team, formatted as
            `{player} (og {minute}')` (NOT `(pen X')` — an own goal
            is not a penalty)
          - Scored penalties are formatted as `{player} (pen {minute}')`
        """
        home_goals = _goals_for_team(state.events, state.home.name, state.away.name)
        away_goals = _goals_for_team(state.events, state.away.name, state.home.name)

        if not home_goals and not away_goals:
            return "GOLES: Sin goles aún"

        def _fmt(event: MatchEvent) -> str:
            # Own Goals are formatted with "(og ...)" — NOT "(pen ...)"
            # since an own goal is not a penalty.
            if "Own Goal" in event.detail:
                return f"{event.player} (og {event.minute}')"
            if "Penalty" in event.detail:
                return f"{event.player} (pen {event.minute}')"
            return f"{event.player} ({event.minute}')"

        home_str = ", ".join(_fmt(e) for e in home_goals)
        away_str = ", ".join(_fmt(e) for e in away_goals)
        return f"GOLES: {home_str} - {away_str}"

    @staticmethod
    def _stats_section(state: MatchState) -> str:
        """Three lines POSESIÓN/TIROS AL ARCO/xG, or fallback if no stats."""
        if state.home_stats is None or state.away_stats is None:
            return "ESTADÍSTICAS: No disponibles aún"

        home_abbr = _team_abbr(state.home.name)
        away_abbr = _team_abbr(state.away.name)
        hs = state.home_stats
        aws = state.away_stats
        return (
            f"POSESIÓN: {home_abbr} {hs.possession} - {away_abbr} {aws.possession}\n"
            f"TIROS AL ARCO: {home_abbr} {hs.shots_on_goal} - {away_abbr} {aws.shots_on_goal}\n"
            f"xG: {home_abbr} {hs.expected_goals} - {away_abbr} {aws.expected_goals}"
        )

    @staticmethod
    def _standout_players_section(state: MatchState) -> str:
        """Up to 3 home/away players with rating >= 7.0, sorted desc."""
        return _format_player_section(
            list(state.home_players) + list(state.away_players),
            predicate=lambda r: r >= 7.0,
            sort_reverse=True,
            limit=3,
            header="JUGADORES DESTACADOS (por rating):",
            fallback="JUGADORES DESTACADOS: Sin datos suficientes",
        )

    @staticmethod
    def _weak_players_section(state: MatchState) -> str:
        """Up to 2 players with 0 < rating < 6.5, sorted asc (worst first)."""
        return _format_player_section(
            list(state.home_players) + list(state.away_players),
            predicate=lambda r: 0 < r < 6.5,
            sort_reverse=False,
            limit=2,
            header="JUGADORES FLOJOS:",
            fallback="JUGADORES FLOJOS: Sin datos suficientes",
        )

    @staticmethod
    def _substitutions_section(state: MatchState) -> str:
        """`CAMBIOS REALIZADOS: {out} → {in} ({m}'), …` or `Ninguno`."""
        subs = [e for e in state.events if e.type == "subst"]
        if not subs:
            return "CAMBIOS REALIZADOS: Ninguno"

        def _fmt(e: MatchEvent) -> str:
            in_player = e.assist or "?"
            return f"{e.player} → {in_player} ({e.minute}')"

        items = ", ".join(_fmt(e) for e in subs)
        return f"CAMBIOS REALIZADOS: {items}"

    @staticmethod
    def _cards_section(state: MatchState) -> str:
        """`TARJETAS: {player} 🟨/🟥 ({m}'), …` or `Ninguna`."""
        cards = [e for e in state.events if e.type == "Card"]
        if not cards:
            return "TARJETAS: Ninguna"

        def _fmt(e: MatchEvent) -> str:
            if "Yellow" in e.detail:
                emoji = "🟨"
            elif "Red" in e.detail:
                emoji = "🟥"
            else:
                emoji = "?"
            return f"{e.player} {emoji} ({e.minute}')"

        items = ", ".join(_fmt(e) for e in cards)
        return f"TARJETAS: {items}"


# ====================================================================== #
# Module-level helpers (testable independently)
# ====================================================================== #


def _is_actual_goal(event: MatchEvent) -> bool:
    """Return True if `event` counts as a goal for score purposes.

    A "Missed Penalty" Goal event is NOT a goal — it is the API
    reporting a missed penalty shot. We exclude it from the score
    and from the goals section.
    """
    return event.type == "Goal" and "Missed" not in event.detail


def _goals_for_team(
    events: list[MatchEvent],
    team_name: str,
    opponent_name: str,
) -> list[MatchEvent]:
    """Filter Goal events for `team_name`, flipping Own Goals to the
    opponent and excluding Missed Penalties.

    Single source of truth for "which events count as goals for
    team X?" — used by `update_details` (score recon) and
    `_goals_section` (context text). Keeping the logic in one place
    means the two cannot drift on edge cases.
    """
    goals: list[MatchEvent] = []
    for e in events:
        if not _is_actual_goal(e):
            continue
        if "Own Goal" in e.detail:
            # An Own Goal by the OPPONENT benefits us. The event's
            # `team` field is the player who scored the own goal,
            # which is the opponent.
            if e.team == opponent_name:
                goals.append(e)
        else:
            if e.team == team_name:
                goals.append(e)
    return goals


def _team_abbr(name: str) -> str:
    """First 3 chars of team name uppercased, or full name if shorter.

    `Argentina` → `ARG`, `FC` → `FC`, `Barça` → `BAR`. Spec:
    `Abbr = first 3 letters of team name uppercased (Argentina→ARG)`.
    """
    if len(name) >= 3:
        return name[:3].upper()
    return name.upper()


def _parse_rating(rating: str | None) -> float:
    """Coerce a rating string to float, defaulting to 0.0 on empty/None.

    The Pydantic model keeps `rating` as `str` (to mirror the API),
    so we parse defensively. Empty string and `None` both mean
    "unrated" — the player MUST NOT appear in standouts OR weak.
    """
    if not rating:
        return 0.0
    return float(rating)


def _player_highlights(p: PlayerStats) -> str:
    """Format goals, assists, key passes, and dribbles for one player.

    Goals/assists/key_passes are shown only when non-zero (the spec
    says "only show non-zero stats except dribbles, which are always
    shown"). Dribbles are always shown as `success/attempts regates`.
    Pluralization is `gol/goles`, `asistencia/asistencias`,
    `pase/pases` based on the count.
    """
    parts: list[str] = []

    if p.goals:
        parts.append(f"{p.goals} {_pluralize(p.goals, _GOL_SINGULAR, _GOL_PLURAL)}")
    if p.assists:
        parts.append(
            f"{p.assists} {_pluralize(p.assists, _ASIST_SINGULAR, _ASIST_PLURAL)}"
        )
    if p.key_passes:
        parts.append(
            f"{p.key_passes} {_pluralize(p.key_passes, _PASE_SINGULAR, _PASE_PLURAL)} clave"
        )
    # Dribbles are ALWAYS shown, even if 0/0.
    parts.append(f"{p.dribbles_success}/{p.dribbles_attempts} regates")

    return ", ".join(parts)


def _pluralize(count: int, singular: str, plural: str) -> str:
    """Return the singular form for count==1, plural otherwise."""
    return singular if count == 1 else plural


def _format_player_section(
    players: list[PlayerStats],
    *,
    predicate: "Callable[[float], bool]",
    sort_reverse: bool,
    limit: int,
    header: str,
    fallback: str,
) -> str:
    """Filter, sort, slice, and render a list of players as a section.

    Used by both `_standout_players_section` and `_weak_players_section`.
    The pattern is identical:
    1. Filter players whose parsed rating satisfies `predicate`.
    2. If none match, return the `fallback` string.
    3. Sort by parsed rating (ascending if `sort_reverse=False`,
       descending if `sort_reverse=True`).
    4. Take the first `limit` entries.
    5. Render the header line + one bullet per player, where each
       bullet is `- {name} ({rating}) - {highlights}`.

    Keeping the rendering in one place means the spec's two
    variants (3 standouts desc, 2 weak asc) can never drift.
    """
    matched = [p for p in players if predicate(_parse_rating(p.rating))]
    if not matched:
        return fallback
    matched.sort(key=lambda p: _parse_rating(p.rating), reverse=sort_reverse)
    matched = matched[:limit]
    lines = [header]
    for p in matched:
        lines.append(f"- {p.name} ({p.rating}) - {_player_highlights(p)}")
    return "\n".join(lines)
