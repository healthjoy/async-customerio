from datetime import datetime

import pytest

from async_customerio import AsyncCustomerIOError
from async_customerio.utils import datetime_to_timestamp, join_url, sanitize, stringify_list


@pytest.mark.parametrize(
    "dt, exp_result", (
        (datetime(2022, 12, 8, 12, 0, 59), 1670500859),
        (datetime(2022, 12, 31, 23, 59, 59), 1672531199),
        (datetime(2022, 9, 1, 0, 0, 1), 1661990401),
    )
)
def test_datetime_to_timestamp(dt, exp_result):
    result = datetime_to_timestamp(dt)
    assert result == exp_result


@pytest.mark.parametrize(
    "base, parts, params, leading_slash, trailing_slash, exp_result",
    (
        ("http://base.ai", ["a", "b"], None, False, False, "http://base.ai/a/b"),
        ("http://base.ai", ["foo", 42], None, False, False, "http://base.ai/foo/42"),
        (
            "http://base.ai",
            ["foo", "bar"],
            {"q": "test"},
            False,
            False,
            "http://base.ai/foo/bar?q=test",
        ),
        (
            "base_path/path_1",
            ["foo", "bar"],
            None,
            True,
            False,
            "/base_path/path_1/foo/bar",
        ),
        (
            "http://base.ai",
            ["foo", "bar"],
            None,
            False,
            True,
            "http://base.ai/foo/bar/",
        ),
        (
            "base_path/path_1",
            ["foo", 42],
            {"q": "test"},
            True,
            True,
            "/base_path/path_1/foo/42/?q=test",
        ),
        (
            "base_path/path_1",
            [],
            {"q": "test"},
            True,
            False,
            "/base_path/path_1?q=test",
        ),
        (
            "https://customer.io/api",
            ["/v1/", "/send/email"],
            {},
            False,
            False,
            "https://customer.io/api/v1/send/email",
        )
    ),
)
def test_join_url_common_flows(base, parts, params, leading_slash, trailing_slash, exp_result):
    result = join_url(base, *parts, params=params, leading_slash=leading_slash, trailing_slash=trailing_slash)
    assert result == exp_result


@pytest.mark.parametrize(
    "data, exp_result", (
        ({"foo": "bar", "number": 42}, {"foo": "bar", "number": 42}),
        ({"dt_attr": datetime(2022, 12, 31, 23, 59, 59), "qqq": "e-42"}, {"dt_attr": 1672531199, "qqq": "e-42"}),
        ({"float_nan": float("NaN")}, {"float_nan": None}),
        (
            {"attr_list": [True], "attr_dict": {1: 1}, "attr_bool": False},
            {"attr_list": [True], "attr_dict": {1: 1}, "attr_bool": False}
        ),
        ({}, {})
    )
)
def test_sanitize(data, exp_result):
    result = sanitize(data)
    assert result == exp_result


def test_sanitize_does_not_mutate():
    data = {"dt_attr": datetime(2022, 12, 31, 23, 59, 59), "float_nan": float("NaN")}
    original = dict(data)
    _ = sanitize(data)
    # original mapping must remain unchanged
    assert data == original


@pytest.mark.parametrize(
    "customer_ids, exp_result", (
        (["1", "2", "3"], ["1", "2", "3"]),
        ([1, 2, 3], ["1", "2", "3"]),
    )
)
def test_stringify_list(customer_ids, exp_result):
    result = stringify_list(customer_ids)
    assert result == exp_result


@pytest.mark.parametrize(
    "customer_ids", (
        [45j, 1],
        [{}, None],
        [2.2, 4.4],
        [..., []],
        [(), 123],
    )
)
def test_stringify_list_wrong_type(customer_ids):
    with pytest.raises(AsyncCustomerIOError):
        stringify_list(customer_ids)
