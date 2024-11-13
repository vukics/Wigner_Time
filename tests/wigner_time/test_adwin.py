import pytest
import pandas as pd

from wigner_time import adwin as adwin
from wigner_time import connection as con
from wigner_time import device as device
from wigner_time.internal import dataframe as frame


@pytest.fixture
def df_simple():
    return pd.DataFrame(
        [
            [0.0, "AOM_imaging", 0.0, "init"],
            [0.0, "AOM_imaging__V", 2.0, "init"],
            [0.0, "AOM_repump", 1.0, "init"],
            [0.0, "virtual", 1.0, "MOT"],
        ],
        columns=["time", "variable", "value", "context"],
    )


@pytest.fixture
def connections_simple():
    return con.connection(
        ["AOM_imaging", 1, 1],
        ["AOM_imaging__V", 1, 2],
        ["AOM_repump", 2, 3],
    )


def test_remove_unconnected_variables(df_simple, connections_simple):
    return pd.testing.assert_frame_equal(
        adwin.remove_unconnected_variables(df_simple, connections_simple),
        pd.DataFrame(
            {
                "time": [0.0] * 3,
                "variable": ["AOM_imaging", "AOM_imaging__V", "AOM_repump"],
                "value": [0.0, 2.0, 1.0],
                "context": ["init"] * 3,
            }
        ),
    )


def test_add_linear_conversion(df_simple):
    df_devs = device.add_devices(
        df_simple,
        pd.DataFrame(
            columns=["variable", "unit_range", "safety_range"],
            data=[
                ["AOM_imaging__V", (-3, 3), (-3, 3)],
            ],
        ),
    )

    return pd.testing.assert_frame_equal(
        adwin.add_linear_conversion(df_devs, "V"),
        pd.DataFrame(
            {
                "time": [0.0, 0.0, 0.0, 0.0],
                "variable": ["AOM_imaging", "AOM_imaging__V", "AOM_repump", "virtual"],
                "value": [0.0, 2.0, 1.0, 1.0],
                "context": ["init", "init", "init", "MOT"],
                "unit_range": [None, (-3, 3), None, None],
                "safety_range": [None, (-3, 3), None, None],
                "value__digits": [None, 54613.0, None, None],
            }
        ),
    )


def test_add_cycles():
    df = pd.DataFrame({"time": range(10), "other": range(11, 21)})
    df["context"] = (
        ["MOT"] * 4 + ["ADwin_LowInit"] * 3 + ["ADwin_Init"] * 2 + ["ADwin_Finish"]
    )
    tst = adwin.add_cycle(df)

    return pd.testing.assert_frame_equal(
        tst,
        pd.DataFrame(
            {
                "time": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                "other": [11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
                "context": [
                    "MOT",
                    "MOT",
                    "MOT",
                    "MOT",
                    "ADwin_LowInit",
                    "ADwin_LowInit",
                    "ADwin_LowInit",
                    "ADwin_Init",
                    "ADwin_Init",
                    "ADwin_Finish",
                ],
                "cycle": [
                    0,
                    200000,
                    400000,
                    600000,
                    -2,
                    -2,
                    -2,
                    -1,
                    -1,
                    2147483648,
                ],
            }
        ),
    )


###############################################################################
#                        dealing with special contexts                        #
###############################################################################

df_special1 = frame.new(
    [
        [0.0, "AOM_imaging", 0.0, "ADwin_Init"],
        [10.0, "AOM_imaging", 0.0, "ADwin_Init"],
        [0.0, "AOM_imaging__V", 2.0, "ADwin_Init"],
        [0.0, "AOM_repump", 1.0, "init"],
        [0.0, "virtual", 1.0, "MOT"],
    ],
    columns=["time", "variable", "value", "context"],
)


df_special2 = frame.new(
    [
        [0.0, "AOM_imaging", 0, "ADwin_Init"],
        [10.0, "AOM_imaging", 1, "ADwin_Init"],
        [0.0, "AOM_imaging__V", 2.0, "ADwin_Init"],
        [0.0, "AOM_repump", 1.0, "init"],
        [0.0, "virtual", 1.0, "MOT"],
    ],
    columns=["time", "variable", "value", "context"],
)

df_special3 = frame.new(
    [
        [0.0, "AOM_imaging", 0.0, "ADwin_Init", 1, 1, 0, 1],
        [0.0, "AOM_imaging__V", 2.0, "ADwin_Init", 1, 1, 0, 5],
        [0.0, "AOM_repump", 1.0, "init", 1, 1, 0, 5],
    ],
    columns=[
        "time",
        "variable",
        "value",
        "context",
        "module",
        "channel",
        "cycle",
        "value_digits",
    ],
)


@pytest.mark.parametrize("input_value", [df_special1, df_special2])
def test_sanitize_raises(input_value):
    with pytest.raises(ValueError):
        adwin.sanitize_special_contexts(input_value)


def test_sanitize_success():
    return pd.testing.assert_frame_equal(adwin.sanitize(df_special3), df_special3)
