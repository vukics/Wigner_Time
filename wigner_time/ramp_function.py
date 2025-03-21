# Copyright Thomas W. Clark & András Vukics 2024. Distributed under the Boost Software License, Version 1.0. (See accompanying file LICENSE.txt)

import numpy as np
from wigner_time import util as wt_util

TIME_RESOLUTION = 1e-6
# default meaningful gap between specified times


def linear(origin, terminus, time_resolution=TIME_RESOLUTION):
    """
    A series of [time, value] pairs according to the line defined by two points and the time resolution.
    """
    t1, v1 = origin
    t2, v2 = terminus
    m = (v2 - v1) / (t2 - t1)
    times = np.arange(t1, t2, time_resolution)

    return np.array([times, m * (times - t1) + v1]).transpose()


def tanh(origin, terminus, time_resolution=TIME_RESOLUTION, ti=3):
    """
    Hyperbolic tan, with a call signature adapted for practical timeline population.

    origin/terminus are time-value pairs
    """

    def nonlinear(i, f, factor):
        """
        factor should be in [-0.5,+0.5].
        """
        # TODO: Better name

        return factor * (f - i) + (f + i) / 2.0

    def tanhFactor(cc: np.ndarray, ti=3):
        """ """
        # TODO: ti should be described
        return np.tanh(ti * (2.0 * (cc - cc[0]) / (cc[-1] - cc[0]) - 1.0)) / (
            2.0 * np.tanh(ti)
        )

    t1, v1 = origin
    t2, v2 = terminus
    cc = wt_util.range__inclusive(t1, t2, time_resolution)

    return np.array([cc, nonlinear(v1, v2, tanhFactor(cc, ti))]).transpose()
