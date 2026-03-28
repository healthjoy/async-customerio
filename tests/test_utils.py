from datetime import datetime, timedelta, timezone

import pytest

from async_customerio import AsyncCustomerIOError
from async_customerio.utils import datetime_to_timestamp, join_url, sanitize, stringify_list, to_dict


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


def test_datetime_to_timestamp_timezone_aware_utc():
    dt = datetime(2023, 1, 1, tzinfo=timezone.utc)
    assert datetime_to_timestamp(dt) == 1672531200


def test_datetime_to_timestamp_timezone_aware_non_utc():
    est = timezone(timedelta(hours=-5))
    dt = datetime(2023, 1, 1, tzinfo=est)
    assert datetime_to_timestamp(dt) == 1672549200


def test_datetime_to_timestamp_non_datetime_raises():
    with pytest.raises(AsyncCustomerIOError):
        datetime_to_timestamp("2023-01-01")


def test_sanitize_recursive_datetime_in_nested_dict():
    dt = datetime(2023, 1, 1, tzinfo=timezone.utc)
    data = {"outer": {"dt": dt}}
    result = sanitize(data)
    assert result == {"outer": {"dt": 1672531200}}


def test_sanitize_recursive_datetime_in_list():
    dt = datetime(2023, 1, 1, tzinfo=timezone.utc)
    data = {"events": [dt]}
    result = sanitize(data)
    assert result == {"events": [1672531200]}


def test_sanitize_recursive_nan_in_nested_dict():
    data = {"m": {"v": float("nan")}}
    result = sanitize(data)
    assert result == {"m": {"v": None}}


def test_sanitize_recursive_nan_in_list():
    data = {"vals": [1.0, float("nan"), 3.0]}
    result = sanitize(data)
    assert result == {"vals": [1.0, None, 3.0]}


def test_sanitize_deeply_nested():
    dt = datetime(2023, 1, 1, tzinfo=timezone.utc)
    data = {"a": {"b": {"c": [{"d": dt}]}}}
    result = sanitize(data)
    assert result == {"a": {"b": {"c": [{"d": 1672531200}]}}}


def test_to_dict_basic_mapping():
    class Obj:
        name = "Alice"
        age = 30

    field_map = {"name": "user_name", "age": "user_age"}
    result = to_dict(field_map, Obj())
    assert result == {"user_name": "Alice", "user_age": 30}


def test_to_dict_excludes_none_by_default():
    class Obj:
        name = "Alice"
        age = None

    field_map = {"name": "user_name", "age": "user_age"}
    result = to_dict(field_map, Obj())
    assert result == {"user_name": "Alice"}
    assert "user_age" not in result


def test_to_dict_includes_none_when_configured():
    class Obj:
        name = "Alice"
        age = None

    field_map = {"name": "user_name", "age": "user_age"}
    result = to_dict(field_map, Obj(), exclude_none=False)
    assert result == {"user_name": "Alice", "user_age": None}
