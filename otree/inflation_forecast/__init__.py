from otree.api import *
import csv
import time
import json
from pathlib import Path

doc = '''
Single-player repeated inflation forecasting experiment.
Students forecast one-period-ahead inflation using lagged macro data.
Includes 5-year history table and chart, plus post-experiment reflection survey.
'''


class C(BaseConstants):
    NAME_IN_URL = 'inflation_forecast'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 20

    PRACTICE_ROUNDS = [1, 2]
    HISTORY_YEARS = 5
    MIN_FORECAST = -5.0
    MAX_FORECAST = 15.0
    TIME_LIMIT_SECONDS = 1200  # 20 minutes — override via session config 'time_limit_seconds'


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # ---------- Forecasting fields ----------
    forecast = models.FloatField(
        min=C.MIN_FORECAST,
        max=C.MAX_FORECAST,
        label="Your forecast for next period's inflation rate (percent):",
        blank=False,
    )

    lag_inflation = models.FloatField()
    lag_unemp = models.FloatField()
    lag_fed_funds = models.FloatField()
    actual_inflation = models.FloatField()

    error = models.FloatField(blank=True)
    squared_error = models.FloatField(blank=True)
    is_timeout = models.BooleanField(initial=False)

    # ---------- Intro fields (round 1 only) ----------
    leaderboard_opt_in = models.BooleanField(
        choices=[[True, 'Yes'], [False, 'No']],
        widget=widgets.RadioSelect,
        label="Do you want to be eligible for the class leaderboard?",
    )
    leaderboard_name = models.StringField(
        blank=True,
        label="Leaderboard name or nickname (optional — leave blank to stay anonymous):",
    )

    # ---------- Post-experiment survey (last round only) ----------
    used_indicators = models.StringField(
        choices=[
            ['lag_inflation_only', 'Lagged inflation only'],
            ['all_three', 'All three indicators (inflation, unemployment, fed funds rate)'],
            ['inflation_and_one', 'Lagged inflation plus one other indicator'],
            ['other', 'Some other approach'],
        ],
        widget=widgets.RadioSelect,
        label="Which information did you primarily use when forming your forecasts?",
    )
    effort_rating = models.IntegerField(
        choices=[
            [1, '1 — I mostly clicked through without thinking'],
            [2, '2 — Some effort, but not much'],
            [3, '3 — Moderate effort'],
            [4, '4 — Fairly serious effort'],
            [5, '5 — I tried hard to forecast as accurately as possible'],
        ],
        widget=widgets.RadioSelect,
        label="How much effort did you put into making accurate forecasts?",
    )
    strategy_description = models.LongStringField(
        blank=True,
        label="Optional: briefly describe the strategy or rule of thumb you used (if any):",
    )


# ---------- Helper functions ----------

def data_file_path():
    return Path(__file__).resolve().parent / 'inflation_data.csv'


def load_data():
    with open(data_file_path(), encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def get_time_limit(player: Player):
    """Read time limit from session config, falling back to C.TIME_LIMIT_SECONDS."""
    return int(player.session.config.get('time_limit_seconds', C.TIME_LIMIT_SECONDS))


def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        rows = load_data()
        if len(rows) < C.NUM_ROUNDS:
            raise ValueError(
                f"inflation_data.csv has {len(rows)} rows but needs at least {C.NUM_ROUNDS}."
            )
        for player in subsession.get_players():
            player.participant.vars['macro_data'] = rows[:C.NUM_ROUNDS]

    for player in subsession.get_players():
        row = player.participant.vars['macro_data'][subsession.round_number - 1]
        player.lag_inflation    = float(row['inflation_lag'])
        player.lag_unemp        = float(row['unemployment_lag'])
        player.lag_fed_funds    = float(row['fed_funds_lag'])
        player.actual_inflation = float(row['inflation'])


def is_practice_round(player: Player):
    return player.round_number in C.PRACTICE_ROUNDS


def init_start_time(player: Player):
    """Set experiment start time once, on the first Forecast page."""
    if 'experiment_start_time' not in player.participant.vars:
        player.participant.vars['experiment_start_time'] = time.time()


def remaining_seconds(player: Player):
    start_time = player.participant.vars.get('experiment_start_time')
    if start_time is None:
        return get_time_limit(player)
    return max(0, int(get_time_limit(player) - (time.time() - start_time)))


def scored_rounds(player: Player):
    return [
        p for p in player.in_all_rounds()
        if p.round_number not in C.PRACTICE_ROUNDS and p.squared_error is not None
    ]


def running_mse(player: Player):
    rounds = scored_rounds(player)
    if not rounds:
        return None
    return sum(p.squared_error for p in rounds) / len(rounds)


def fmt(value, decimals=1):
    return '{:.{}f}'.format(value, decimals)


def history_table(player: Player):
    row = player.participant.vars['macro_data'][player.round_number - 1]
    R = player.round_number

    entries = []
    for k in range(C.HISTORY_YEARS - 1, -1, -1):
        relative_year = (R - 1) - k
        label = f'Year {relative_year}'

        inf_val   = row.get(f'hist_inflation_{k}', '')
        unemp_val = row.get(f'hist_unemp_{k}', '')
        ff_val    = row.get(f'hist_fed_funds_{k}', '')

        entries.append({
            'label':     label,
            'inflation': fmt(float(inf_val))   if inf_val   != '' else '—',
            'unemp':     fmt(float(unemp_val)) if unemp_val != '' else '—',
            'fed_funds': fmt(float(ff_val))    if ff_val    != '' else '—',
            'is_last':   k == 0,
        })
    return entries


def chart_data_json(player: Player, include_current=False):
    """
    JSON for the Chart.js sparkline.
    include_current=True: also include the current round's actual + forecast
                          (used on the Feedback page after submission).
    """
    row = player.participant.vars['macro_data'][player.round_number - 1]
    R = player.round_number

    # Pre-game history points (relative year <= 0)
    hist_labels = []
    hist_actuals = []
    for k in range(C.HISTORY_YEARS - 1, -1, -1):
        relative_year = (R - 1) - k
        if relative_year > 0:
            continue
        val = row.get(f'hist_inflation_{k}', '')
        if val != '':
            label = f'Year {relative_year}' if relative_year != 0 else 'Year 0'
            hist_labels.append(label)
            hist_actuals.append(round(float(val), 2))

    # Completed prior rounds
    prior_labels = []
    prior_actuals = []
    prior_forecasts = []
    for p in player.in_previous_rounds():
        prior_labels.append(f'Year {p.round_number}')
        prior_actuals.append(round(p.actual_inflation, 2))
        prior_forecasts.append(round(p.forecast, 2) if p.forecast is not None else None)

    # Current round (Feedback page only)
    if include_current:
        prior_labels.append(f'Year {R}')
        prior_actuals.append(round(player.actual_inflation, 2))
        prior_forecasts.append(round(player.forecast, 2) if player.forecast is not None else None)

    all_labels    = hist_labels + prior_labels
    all_actuals   = hist_actuals + prior_actuals
    all_forecasts = [None] * len(hist_labels) + prior_forecasts

    return json.dumps({
        'labels':    all_labels,
        'actuals':   all_actuals,
        'forecasts': all_forecasts,
    })


# ---------- Pages ----------

class Intro(Page):
    form_model = 'player'
    form_fields = ['leaderboard_opt_in', 'leaderboard_name']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.participant.vars['leaderboard_opt_in'] = player.leaderboard_opt_in
        name = (player.leaderboard_name or '').strip()
        if player.leaderboard_opt_in and not name:
            name = 'Anonymous'
        player.participant.vars['leaderboard_name'] = name


class Instructions(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        minutes = get_time_limit(player) // 60
        return dict(time_limit_minutes=minutes)


class InstructionsMSE(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Forecast(Page):
    form_model = 'player'
    form_fields = ['forecast']

    @staticmethod
    def get_timeout_seconds(player: Player):
        return remaining_seconds(player)

    @staticmethod
    def vars_for_template(player: Player):
        # Timer starts here — first time a student hits the Forecast page
        init_start_time(player)
        time_limit = get_time_limit(player)
        return dict(
            is_practice=is_practice_round(player),
            remaining_seconds=remaining_seconds(player),
            time_limit=time_limit,
            lag_inflation_display=fmt(player.lag_inflation),
            lag_unemp_display=fmt(player.lag_unemp),
            lag_fed_funds_display=fmt(player.lag_fed_funds),
            history=history_table(player),
            chart_data=chart_data_json(player, include_current=False),
            forecast_year=player.round_number,
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.is_timeout = timeout_happened
        if timeout_happened:
            player.forecast = 0.0
        player.error = player.forecast - player.actual_inflation
        player.squared_error = player.error ** 2


class Feedback(Page):
    @staticmethod
    def get_timeout_seconds(player: Player):
        return remaining_seconds(player)

    @staticmethod
    def vars_for_template(player: Player):
        mse = running_mse(player)
        over_under = 'over-forecasted' if player.error > 0 else 'under-forecasted'
        time_limit = get_time_limit(player)
        return dict(
            is_practice=is_practice_round(player),
            mse=round(mse, 3) if mse is not None else None,
            remaining_seconds=remaining_seconds(player),
            time_limit=time_limit,
            forecast_display=fmt(player.forecast),
            actual_display=fmt(player.actual_inflation),
            error_display=fmt(player.error),
            sq_error_display=fmt(player.squared_error),
            chart_data=chart_data_json(player, include_current=True),
            over_under=over_under,
        )


class Survey(Page):
    form_model = 'player'
    form_fields = ['used_indicators', 'effort_rating', 'strategy_description']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        mse = running_mse(player)
        rounds = scored_rounds(player)
        return dict(
            mse=round(mse, 3) if mse is not None else None,
            completed_scored_rounds=len(rounds),
            leaderboard_opt_in=player.participant.vars.get('leaderboard_opt_in', False),
            leaderboard_name=player.participant.vars.get('leaderboard_name', ''),
        )


page_sequence = [Intro, Instructions, InstructionsMSE, Forecast, Feedback, Survey, Results]


# ---------- Data export ----------

def custom_export(players):
    yield [
        'participant_code',
        'round_number',
        'is_practice',
        'forecast',
        'actual_inflation',
        'error',
        'squared_error',
        'lag_inflation',
        'lag_unemp',
        'lag_fed_funds',
        'is_timeout',
        'leaderboard_opt_in',
        'leaderboard_name',
        'used_indicators',
        'effort_rating',
        'strategy_description',
    ]
    for p in players:
        yield [
            p.participant.code,
            p.round_number,
            is_practice_round(p),
            p.forecast,
            p.actual_inflation,
            p.error,
            p.squared_error,
            p.lag_inflation,
            p.lag_unemp,
            p.lag_fed_funds,
            p.is_timeout,
            p.participant.vars.get('leaderboard_opt_in', ''),
            p.participant.vars.get('leaderboard_name', ''),
            getattr(p, 'used_indicators', '') or '',
            getattr(p, 'effort_rating', '') or '',
            getattr(p, 'strategy_description', '') or '',
        ]
