import httpx
import pytest
from pytest_httpx import HTTPXMock

from async_customerio import AsyncCustomerIO, AsyncCustomerIOError, AsyncCustomerIORetryableError
from async_customerio.track_v2 import Actions


pytestmark = pytest.mark.asyncio


@pytest.fixture()
def cio(faker_):
    return AsyncCustomerIO(
        site_id=faker_.pystr(),
        api_key=faker_.pystr(),
        host="fake-track.customerio.io",
        retries=1,
    )


# ======================================================================
# Person — identify
# ======================================================================


async def test_identify_person(cio, faker_, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await cio.v2.identify_person(
        identifiers={"id": faker_.pystr()},
        first_name="John",
        last_name="Smith",
    )
    assert response is None


async def test_identify_person_by_email(cio, faker_, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await cio.v2.identify_person(
        identifiers={"email": faker_.email()},
        plan="premium",
    )
    assert response is None


async def test_identify_person_empty_identifiers(cio):
    with pytest.raises(AsyncCustomerIOError, match="identifiers cannot be blank in identify_person"):
        await cio.v2.identify_person(identifiers={})


# ======================================================================
# Person — delete
# ======================================================================


async def test_delete_person(cio, faker_, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await cio.v2.delete_person(identifiers={"email": faker_.email()})
    assert response is None


async def test_delete_person_empty_identifiers(cio):
    with pytest.raises(AsyncCustomerIOError, match="identifiers cannot be blank in delete_person"):
        await cio.v2.delete_person(identifiers={})


# ======================================================================
# Person — track event
# ======================================================================


async def test_track_person_event(cio, faker_, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await cio.v2.track_person_event(
        identifiers={"id": faker_.pystr()},
        name="purchase",
        product="widget",
        amount=49.99,
    )
    assert response is None


async def test_track_person_event_empty_identifiers(cio):
    with pytest.raises(AsyncCustomerIOError, match="identifiers cannot be blank in track_person_event"):
        await cio.v2.track_person_event(identifiers={}, name="purchase")


async def test_track_person_event_empty_name(cio, faker_):
    with pytest.raises(AsyncCustomerIOError, match="name cannot be blank in track_person_event"):
        await cio.v2.track_person_event(identifiers={"id": faker_.pystr()}, name="")


# ======================================================================
# Person — pageview
# ======================================================================


async def test_person_pageview(cio, faker_, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await cio.v2.person_pageview(
        identifiers={"id": faker_.pystr()},
        name="/pricing",
        referrer="https://google.com",
    )
    assert response is None


async def test_person_pageview_empty_identifiers(cio):
    with pytest.raises(AsyncCustomerIOError, match="identifiers cannot be blank in person_pageview"):
        await cio.v2.person_pageview(identifiers={}, name="/pricing")


async def test_person_pageview_empty_name(cio, faker_):
    with pytest.raises(AsyncCustomerIOError, match="name cannot be blank in person_pageview"):
        await cio.v2.person_pageview(identifiers={"id": faker_.pystr()}, name="")


# ======================================================================
# Person — screen
# ======================================================================


async def test_person_screen(cio, faker_, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await cio.v2.person_screen(
        identifiers={"id": faker_.pystr()},
        name="home_screen",
    )
    assert response is None


async def test_person_screen_empty_identifiers(cio):
    with pytest.raises(AsyncCustomerIOError, match="identifiers cannot be blank in person_screen"):
        await cio.v2.person_screen(identifiers={}, name="home_screen")


async def test_person_screen_empty_name(cio, faker_):
    with pytest.raises(AsyncCustomerIOError, match="name cannot be blank in person_screen"):
        await cio.v2.person_screen(identifiers={"id": faker_.pystr()}, name="")


# ======================================================================
# Person — add device
# ======================================================================


async def test_add_person_device(cio, faker_, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await cio.v2.add_person_device(
        identifiers={"id": faker_.pystr()},
        device_id="device-token-abc",
        platform="ios",
    )
    assert response is None


async def test_add_person_device_with_attrs(cio, faker_, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await cio.v2.add_person_device(
        identifiers={"id": faker_.pystr()},
        device_id="device-token-abc",
        platform="android",
        last_used=1234567890,
    )
    assert response is None


async def test_add_person_device_empty_identifiers(cio):
    with pytest.raises(AsyncCustomerIOError, match="identifiers cannot be blank in add_person_device"):
        await cio.v2.add_person_device(identifiers={}, device_id="tok", platform="ios")


async def test_add_person_device_empty_device_id(cio, faker_):
    with pytest.raises(AsyncCustomerIOError, match="device_id cannot be blank in add_person_device"):
        await cio.v2.add_person_device(identifiers={"id": faker_.pystr()}, device_id="", platform="ios")


async def test_add_person_device_empty_platform(cio, faker_):
    with pytest.raises(AsyncCustomerIOError, match="platform cannot be blank in add_person_device"):
        await cio.v2.add_person_device(identifiers={"id": faker_.pystr()}, device_id="tok", platform="")


# ======================================================================
# Person — delete device
# ======================================================================


async def test_delete_person_device(cio, faker_, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await cio.v2.delete_person_device(
        identifiers={"id": faker_.pystr()},
        device_id="device-token-abc",
    )
    assert response is None


async def test_delete_person_device_empty_identifiers(cio):
    with pytest.raises(AsyncCustomerIOError, match="identifiers cannot be blank in delete_person_device"):
        await cio.v2.delete_person_device(identifiers={}, device_id="tok")


async def test_delete_person_device_empty_device_id(cio, faker_):
    with pytest.raises(AsyncCustomerIOError, match="device_id cannot be blank in delete_person_device"):
        await cio.v2.delete_person_device(identifiers={"id": faker_.pystr()}, device_id="")


# ======================================================================
# Person — suppress / unsuppress
# ======================================================================


async def test_suppress_person(cio, faker_, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await cio.v2.suppress_person(identifiers={"id": faker_.pystr()})
    assert response is None


async def test_suppress_person_empty_identifiers(cio):
    with pytest.raises(AsyncCustomerIOError, match="identifiers cannot be blank in suppress_person"):
        await cio.v2.suppress_person(identifiers={})


async def test_unsuppress_person(cio, faker_, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await cio.v2.unsuppress_person(identifiers={"id": faker_.pystr()})
    assert response is None


async def test_unsuppress_person_empty_identifiers(cio):
    with pytest.raises(AsyncCustomerIOError, match="identifiers cannot be blank in unsuppress_person"):
        await cio.v2.unsuppress_person(identifiers={})


# ======================================================================
# Person — merge
# ======================================================================


async def test_merge_persons(cio, faker_, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await cio.v2.merge_persons(
        primary={"id": faker_.pystr()},
        secondary={"email": faker_.email()},
    )
    assert response is None


async def test_merge_persons_empty_primary(cio, faker_):
    with pytest.raises(AsyncCustomerIOError, match="primary identifiers cannot be blank in merge_persons"):
        await cio.v2.merge_persons(primary={}, secondary={"id": faker_.pystr()})


async def test_merge_persons_empty_secondary(cio, faker_):
    with pytest.raises(AsyncCustomerIOError, match="secondary identifiers cannot be blank in merge_persons"):
        await cio.v2.merge_persons(primary={"id": faker_.pystr()}, secondary={})


# ======================================================================
# Person — relationships
# ======================================================================


async def test_add_person_relationships(cio, faker_, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await cio.v2.add_person_relationships(
        identifiers={"id": faker_.pystr()},
        relationships=[{"identifiers": {"object_type_id": "1", "object_id": "acme"}}],
    )
    assert response is None


async def test_add_person_relationships_empty_identifiers(cio):
    with pytest.raises(AsyncCustomerIOError, match="identifiers cannot be blank in add_person_relationships"):
        await cio.v2.add_person_relationships(
            identifiers={},
            relationships=[{"identifiers": {"object_type_id": "1", "object_id": "acme"}}],
        )


async def test_add_person_relationships_empty_relationships(cio, faker_):
    with pytest.raises(AsyncCustomerIOError, match="relationships cannot be blank in add_person_relationships"):
        await cio.v2.add_person_relationships(identifiers={"id": faker_.pystr()}, relationships=[])


async def test_delete_person_relationships(cio, faker_, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await cio.v2.delete_person_relationships(
        identifiers={"id": faker_.pystr()},
        relationships=[{"identifiers": {"object_type_id": "1", "object_id": "acme"}}],
    )
    assert response is None


async def test_delete_person_relationships_empty_identifiers(cio):
    with pytest.raises(AsyncCustomerIOError, match="identifiers cannot be blank in delete_person_relationships"):
        await cio.v2.delete_person_relationships(
            identifiers={},
            relationships=[{"identifiers": {"object_type_id": "1", "object_id": "acme"}}],
        )


async def test_delete_person_relationships_empty_relationships(cio, faker_):
    with pytest.raises(AsyncCustomerIOError, match="relationships cannot be blank in delete_person_relationships"):
        await cio.v2.delete_person_relationships(identifiers={"id": faker_.pystr()}, relationships=[])


# ======================================================================
# Object — identify
# ======================================================================


async def test_identify_object(cio, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await cio.v2.identify_object(
        identifiers={"object_type_id": "1", "object_id": "acme"},
        name="Acme Corp",
        industry="Software",
    )
    assert response is None


async def test_identify_object_by_cio_object_id(cio, faker_, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await cio.v2.identify_object(
        identifiers={"cio_object_id": faker_.pystr()},
        name="Updated Corp",
    )
    assert response is None


async def test_identify_object_empty_identifiers(cio):
    with pytest.raises(AsyncCustomerIOError, match="identifiers cannot be blank in identify_object"):
        await cio.v2.identify_object(identifiers={})


# ======================================================================
# Object — delete
# ======================================================================


async def test_delete_object(cio, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await cio.v2.delete_object(
        identifiers={"object_type_id": "1", "object_id": "acme"},
    )
    assert response is None


async def test_delete_object_empty_identifiers(cio):
    with pytest.raises(AsyncCustomerIOError, match="identifiers cannot be blank in delete_object"):
        await cio.v2.delete_object(identifiers={})


# ======================================================================
# Object — track event
# ======================================================================


async def test_track_object_event(cio, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await cio.v2.track_object_event(
        identifiers={"object_type_id": "1", "object_id": "acme"},
        name="account_upgraded",
        plan="enterprise",
    )
    assert response is None


async def test_track_object_event_empty_identifiers(cio):
    with pytest.raises(AsyncCustomerIOError, match="identifiers cannot be blank in track_object_event"):
        await cio.v2.track_object_event(identifiers={}, name="account_upgraded")


async def test_track_object_event_empty_name(cio):
    with pytest.raises(AsyncCustomerIOError, match="name cannot be blank in track_object_event"):
        await cio.v2.track_object_event(
            identifiers={"object_type_id": "1", "object_id": "acme"},
            name="",
        )


# ======================================================================
# Object — relationships
# ======================================================================


async def test_add_object_relationships(cio, faker_, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await cio.v2.add_object_relationships(
        identifiers={"object_type_id": "1", "object_id": "acme"},
        relationships=[{"identifiers": {"id": faker_.pystr()}}],
    )
    assert response is None


async def test_add_object_relationships_empty_identifiers(cio, faker_):
    with pytest.raises(AsyncCustomerIOError, match="identifiers cannot be blank in add_object_relationships"):
        await cio.v2.add_object_relationships(
            identifiers={},
            relationships=[{"identifiers": {"id": faker_.pystr()}}],
        )


async def test_add_object_relationships_empty_relationships(cio):
    with pytest.raises(AsyncCustomerIOError, match="relationships cannot be blank in add_object_relationships"):
        await cio.v2.add_object_relationships(
            identifiers={"object_type_id": "1", "object_id": "acme"},
            relationships=[],
        )


async def test_delete_object_relationships(cio, faker_, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await cio.v2.delete_object_relationships(
        identifiers={"object_type_id": "1", "object_id": "acme"},
        relationships=[{"identifiers": {"id": faker_.pystr()}}],
    )
    assert response is None


async def test_delete_object_relationships_empty_identifiers(cio, faker_):
    with pytest.raises(AsyncCustomerIOError, match="identifiers cannot be blank in delete_object_relationships"):
        await cio.v2.delete_object_relationships(
            identifiers={},
            relationships=[{"identifiers": {"id": faker_.pystr()}}],
        )


async def test_delete_object_relationships_empty_relationships(cio):
    with pytest.raises(AsyncCustomerIOError, match="relationships cannot be blank in delete_object_relationships"):
        await cio.v2.delete_object_relationships(
            identifiers={"object_type_id": "1", "object_id": "acme"},
            relationships=[],
        )


# ======================================================================
# Batch
# ======================================================================


async def test_send_batch_success_200(cio, faker_, httpx_mock: HTTPXMock):
    """200 — entire batch accepted."""
    httpx_mock.add_response(status_code=200, json={"success": True})

    payload = [
        {
            "type": "person",
            "action": Actions.identify.value,
            "identifiers": {"id": faker_.pyint(min_value=1)},
            "attributes": {"name": "John"},
        }
    ]

    response = await cio.v2.send_batch(payload)
    assert response is None


async def test_send_batch_partial_207(cio, faker_, httpx_mock: HTTPXMock):
    """207 — partial success; still treated as successful by client."""
    httpx_mock.add_response(
        status_code=207,
        json={
            "errors": [
                {
                    "batch_index": 1,
                    "reason": "Invalid identifier: id cannot be null",
                    "field": "identifiers.id",
                    "message": "Invalid identifier: id cannot be null",
                }
            ]
        },
    )

    payload = [
        {
            "type": "person",
            "action": Actions.identify.value,
            "identifiers": {"id": faker_.pyint(min_value=1)},
            "attributes": {"name": "John"},
        },
        {
            "type": "person",
            "action": Actions.identify.value,
            "identifiers": {"id": None},
            "attributes": {"name": "Sarah"},
        },
    ]

    response = await cio.v2.send_batch(payload)
    assert response is None


async def test_send_batch_malformed_400_raises(cio, faker_, httpx_mock: HTTPXMock):
    """400 — entire request malformed; should raise."""
    httpx_mock.add_response(
        status_code=400,
        json={
            "errors": [
                {
                    "reason": "Invalid identifier: id cannot be null",
                    "field": "identifiers.id",
                    "message": "Invalid identifier: id cannot be null",
                }
            ]
        },
    )

    payload = [
        {
            "type": "person",
            "action": Actions.identify.value,
            "identifiers": {"id": None},
            "attributes": {"name": "John"},
        }
    ]

    with pytest.raises(AsyncCustomerIOError):
        await cio.v2.send_batch(payload)


async def test_send_batch_mixed_types(cio, faker_, httpx_mock: HTTPXMock):
    """Batch can mix person and object operations."""
    httpx_mock.add_response(status_code=200, json={"success": True})

    payload = [
        {
            "type": "person",
            "action": Actions.identify.value,
            "identifiers": {"id": faker_.pyint(min_value=1)},
            "attributes": {"name": "John"},
        },
        {
            "type": "object",
            "action": Actions.identify.value,
            "identifiers": {"object_type_id": "1", "object_id": "acme"},
            "attributes": {"name": "Acme Corp"},
        },
    ]

    response = await cio.v2.send_batch(payload)
    assert response is None


# ======================================================================
# Error handling — unauthorized (parametrized across v2 methods)
# ======================================================================


@pytest.mark.parametrize(
    "method, kwargs",
    (
        ("identify_person", {"identifiers": {"id": 1}, "name": "Jack"}),
        ("delete_person", {"identifiers": {"id": 1}}),
        ("track_person_event", {"identifiers": {"id": 1}, "name": "purchase"}),
        ("person_pageview", {"identifiers": {"id": 1}, "name": "/home"}),
        ("person_screen", {"identifiers": {"id": 1}, "name": "home_screen"}),
        ("add_person_device", {"identifiers": {"id": 1}, "device_id": "tok", "platform": "ios"}),
        ("delete_person_device", {"identifiers": {"id": 1}, "device_id": "tok"}),
        ("suppress_person", {"identifiers": {"id": 1}}),
        ("unsuppress_person", {"identifiers": {"id": 1}}),
        ("merge_persons", {"primary": {"id": 1}, "secondary": {"id": 2}}),
        (
            "add_person_relationships",
            {"identifiers": {"id": 1}, "relationships": [{"identifiers": {"object_type_id": "1", "object_id": "a"}}]},
        ),
        (
            "delete_person_relationships",
            {"identifiers": {"id": 1}, "relationships": [{"identifiers": {"object_type_id": "1", "object_id": "a"}}]},
        ),
        ("identify_object", {"identifiers": {"object_type_id": "1", "object_id": "a"}, "name": "Acme"}),
        ("delete_object", {"identifiers": {"object_type_id": "1", "object_id": "a"}}),
        ("track_object_event", {"identifiers": {"object_type_id": "1", "object_id": "a"}, "name": "ev"}),
        (
            "add_object_relationships",
            {"identifiers": {"object_type_id": "1", "object_id": "a"}, "relationships": [{"identifiers": {"id": 1}}]},
        ),
        (
            "delete_object_relationships",
            {"identifiers": {"object_type_id": "1", "object_id": "a"}, "relationships": [{"identifiers": {"id": 1}}]},
        ),
    ),
)
async def test_unauthorized_request(method, kwargs, cio, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=401)
    with pytest.raises(AsyncCustomerIOError):
        await getattr(cio.v2, method)(**kwargs)


# ======================================================================
# Error handling — connection errors
# ======================================================================


@pytest.mark.parametrize("connection_error", (httpx.ConnectError, httpx.ConnectTimeout))
async def test_connection_error_handling(connection_error, cio, faker_, httpx_mock: HTTPXMock):
    httpx_mock.add_exception(connection_error("something went wrong"))
    with pytest.raises(AsyncCustomerIORetryableError):
        await cio.v2.identify_person(identifiers={"id": faker_.pystr()}, name="John")


# ======================================================================
# Backwards compatibility — send_entity / send_batch on AsyncCustomerIO
# ======================================================================


async def test_legacy_send_entity(cio, faker_, httpx_mock: HTTPXMock):
    """cio.send_entity() still works via delegation to v2."""
    httpx_mock.add_response(status_code=200, json={"success": True})

    response = await cio.send_entity(
        identifiers={"id": faker_.pystr()},
        type="person",
        action=Actions.identify,
        name="John",
        activated=True,
    )
    assert response is None


async def test_legacy_send_entity_empty_identifier_raises(cio):
    with pytest.raises(AsyncCustomerIOError, match="identifiers cannot be blank in send_entity"):
        await cio.send_entity(
            identifiers=None,
            type="person",
            action=Actions.identify,
            name="John",
        )


async def test_legacy_send_batch(cio, faker_, httpx_mock: HTTPXMock):
    """cio.send_batch() still works via delegation to v2."""
    httpx_mock.add_response(status_code=200, json={"success": True})

    payload = [
        {
            "type": "person",
            "action": Actions.identify.value,
            "identifiers": {"id": faker_.pyint(min_value=1)},
            "attributes": {"name": "John"},
        }
    ]

    response = await cio.send_batch(payload)
    assert response is None


# ======================================================================
# v2 property — shared instance
# ======================================================================


def test_v2_property_returns_same_instance(cio):
    """The .v2 property should return the same TrackAPIV2 instance."""
    v2_a = cio.v2
    v2_b = cio.v2
    assert v2_a is v2_b
