"""
For manipulating column 'origins', particularly 'time' and 'value'.

This is important for inferring what the user means when they want to add rows to their dataframe and is especially important when it comes to chaining `ramp`s together.

"""

# TODO:
# - "variable" flag (i.e. find the previous occurence of this particular variable)
# - "context" (Should we support this?)

from wigner_time import util
from wigner_time.internal import dataframe as frame

_OPTIONS = ["anchor", "last"]
"These origin labels are reserved for interpretation by the package."


def previous(
    timeline: frame.CLASS,
    variable=None,
    column="variable",
    sort_by=None,
    index=-1,
):
    """
    Returns a row from the previous timeline. By default, this is done by finding the highest value for time and returning that row. If `sort_by` is specified (e.g. 'time'), then the dataframe is sorted and then the row indexed by `index` is returned.

    Raises ValueError if the specified variable, or timeline, doesn't exist.
    """
    if variable is not None:
        tl__filtered = timeline[timeline[column] == variable]
        if tl__filtered.empty:
            raise ValueError("Previous {} not found".format(variable))
    else:
        tl__filtered = timeline

    if sort_by is None:
        return frame.row_from_max_column(tl__filtered)
    else:
        if not timeline[sort_by].is_monotonic_increasing:
            tl__filtered.sort_values(sort_by, inplace=True)
            return tl__filtered.iloc[index]
        else:
            return timeline.iloc[index]


def find(
    timeline: frame.CLASS,
    variable: str | None = None,
    origin=None,
    label__anchor="ANCHOR",
):
    """
    Returns a time-value pair, according to the choice of origin.

    Often, `None` will be returned for a value as it would be presumptuous to assume the same value origin for all devices.

    Example origins:
    - [0.0,0.0]
    - 0.0
    - "anchor"
    - ["anchor", 0.0]
    - "variable"
    - "last" (The row highest in time)
    - "...AOM_shutter..." (A variable name that is present in the dataframe)
    """
    _is_available__anchor = (timeline["variable"] == label__anchor).any()

    def _is_available__variable(var):
        return (timeline["variable"] == var).any() if (var is not None) else None

    """
    Falls back to last time entry if anchor is not available.
    TODO:
    - Is this a good idea?
    - More meaningful error if anchor is not available
    """
    if origin is None:
        if _is_available__anchor:
            origin = "anchor"
        else:
            origin = "last"

    o = util.ensure_iterable_with_None(origin)

    error__unsupported_option = ValueError(
        "Unsupported option for 'origin' in `wigner_time.internal.origin.find`. Check the formatting and whether this makes sense for your current timeline. If you feel like this option should be supported then don't hesitate to get in touch with the maintainers."
    )

    if len(o) != 2:
        raise error__unsupported_option

    match o:
        case [float(), float()] | [float(), None] | [None, float()] as lst:
            tv = lst

        case [a, None | float() as b]:
            match a:
                case str(text) if ("anchor" == text) and _is_available__anchor:
                    tv = [
                        previous(timeline, variable=label__anchor).at[0, "time"],
                        b,
                    ]

                case str(text) if "last" == text:
                    tv = [previous(timeline).at[0, "time"], b]

                case str(text) if _is_available__variable(text):
                    tv = [previous(timeline, variable=text).at[0, "time"], b]
                case _:
                    raise error__unsupported_option

        case [str(t1), str(t2)] if (t1 == t2) and _is_available__variable(t1):
            tv = previous(timeline, variable=t1)[["time", "value"]].values[0]

        case [str(t1), str(t2)] if (
            _is_available__variable(t1) and _is_available__variable(t1)
        ):
            tv = [
                previous(timeline, variable=t1).at[0, "time"],
                previous(timeline, variable=t2).at[0, "value"],
            ]

        case _:
            raise error__unsupported_option
    return tv