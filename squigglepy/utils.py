import math
import random
import numpy as np
from scipy import stats


def _process_weights_values(weights, values):
    if isinstance(weights, float):
        weights = [weights]
    elif isinstance(weights, np.ndarray):
        weights = list(weights)
    elif not isinstance(weights, list) and weights is not None:
        raise ValueError('passed weights must be a list')

    if isinstance(values, np.ndarray):
        values = list(values)
    elif not isinstance(values, list):
        raise ValueError('passed values must be a list')

    if weights is None:
        if isinstance(values[0], list) and len(values[0]) == 2:
            weights = [v[0] for v in values]
            values = [v[1] for v in values]
        else:
            len_ = len(values)
            weights = [1 / len_ for _ in range(len_)]

    sum_weights = sum(weights)

    if len(weights) == len(values) - 1 and sum_weights < 1:
        weights.append(1 - sum_weights)
    elif sum_weights <= 0.99 or sum_weights >= 1.01:
        raise ValueError('weights don\'t sum to 1 -' +
                         ' they sum to {}'.format(sum_weights))

    if len(weights) != len(values):
        raise ValueError('weights and distributions not same length')

    return weights, values


def event_occurs(p):
    return random.random() < p


def get_percentiles(data,
                    percentiles=[1, 5, 10, 20, 30, 40, 50,
                                 60, 70, 80, 90, 95, 99],
                    reverse=False,
                    digits=None):
    percentile_labels = list(reversed(percentiles)) if reverse else percentiles
    percentiles = np.percentile(data, percentiles)
    if digits is not None:
        percentiles = np.round(percentiles, digits)
    return dict(list(zip(percentile_labels, percentiles)))


def get_log_percentiles(data, percentiles,
                        reverse=False, display=True, digits=1):
    percentiles = get_percentiles(data,
                                  percentiles=percentiles,
                                  reverse=reverse,
                                  digits=digits)
    if display:
        return dict([(k, '10^{}'.format(np.round(np.log10(v), digits))) for
                     k, v in percentiles.items()])
    else:
        return dict([(k, np.round(np.log10(v), digits)) for
                    k, v in percentiles.items()])


def geomean(a, weights=None):
    if weights is not None:
        weights, a = _process_weights_values(weights, a)
    return stats.mstats.gmean(a, weights=weights)


def p_to_odds(p):
    return p / (1 - p)


def odds_to_p(odds):
    return odds / (1 + odds)


def geomean_odds(a, weights=None):
    a = p_to_odds(np.array(a))
    return odds_to_p(geomean(a, weights=weights))


def laplace(s, n=None, time_passed=None,
            time_remaining=None, time_fixed=False):
    # Returns probability of success on next trial
    if time_passed is None and time_remaining is None and n is not None:
        return (s + 1) / (n + 2)
    elif time_passed is not None and time_remaining is not None and s == 0:
        # https://www.lesswrong.com/posts/wE7SK8w8AixqknArs/a-time-invariant-version-of-laplace-s-rule
        return 1 - ((1 + time_remaining/time_passed) ** -1)
    elif (time_passed is not None and time_remaining is not None
          and s > 0 and not time_fixed):
        return 1 - ((1 + time_remaining/time_passed) ** -s)
    elif (time_passed is not None and time_remaining is not None
          and s > 0 and time_fixed):
        return 1 - ((1 + time_remaining/time_passed) ** -(s + 1))
    else:
        raise ValueError


def roll_die(sides):
    from .sample import sample as samp
    from .distributions import discrete
    return samp(discrete(list(range(1, sides + 1)))) if sides > 0 else None


def flip_coin():
    return 'heads' if roll_die(2) == 2 else 'tails'
