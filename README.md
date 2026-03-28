<p align="center">
  <img src="logo.svg" alt="async-customerio logo" width="480"/>
</p>

<h1 align="center">async-customerio</h1>
<p align="center"><em>A lightweight asynchronous Python client to interact with Customer.io</em></p>

<p align="center">
  <a href="https://pypi.python.org/pypi/async-customerio/"><img src="https://img.shields.io/pypi/dm/async-customerio.svg" alt="PyPI downloads"></a>
  <a href="https://pypi.python.org/pypi/async-customerio/"><img src="https://badge.fury.io/py/async-customerio.svg" alt="PyPI version"></a>
  <a href="https://pypi.python.org/pypi/async-customerio/"><img src="https://img.shields.io/pypi/l/async-customerio.svg" alt="License"></a>
  <a href="https://pypi.python.org/pypi/async-customerio/"><img src="https://img.shields.io/pypi/pyversions/async-customerio.svg" alt="Python versions"></a>
  <a href="https://github.com/healthjoy/async-customerio/actions/workflows/ci.yml"><img src="https://github.com/healthjoy/async-customerio/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://www.codacy.com/gh/healthjoy/async-customerio/dashboard?utm_source=github.com&utm_medium=referral&utm_content=healthjoy/async-customerio&utm_campaign=Badge_Coverage"><img src="https://app.codacy.com/project/badge/Coverage/3629b50827ef4e89ba0eaa5c09584273" alt="Coverage"></a>
</p>

- Free software: MIT license
- Requires: Python 3.10+

## Features

- Fully asynchronous — built on [httpx](https://www.python-httpx.org/) with HTTP/2 support
- Async context manager support for clean resource management
- Compatible interface with the official [customerio](https://github.com/customerio/customerio-python) Python client
- Track API v1 & v2 (persons, objects, relationships, batch operations)
- App API support (customers, segments, send messages)
- Pluggable retry strategy via the `RetryStrategy` protocol
- Webhook signature verification

## Table of Contents

- [Installation](#installation)
- [Getting started](#getting-started)
- [Configuration](#configuration)
- [Track API v1](#track-api-v1)
- [Track API v2](#track-api-v2)
- [App API](#app-api)
- [Custom Retry Strategy](#custom-retry-strategy)
- [Webhook Signature Verification](#webhook-signature-verification)
- [API Coverage](#api-coverage)

## Installation

```shell
pip install async-customerio
```

## Getting started

```python
import asyncio

from async_customerio import AsyncCustomerIO, Regions


async def main():
    async with AsyncCustomerIO(site_id="YOUR_SITE_ID", api_key="YOUR_API_KEY", region=Regions.US) as cio:
        await cio.identify(
            id=5,
            email="customer@example.com",
            first_name="John",
            last_name="Doe",
            subscription_plan="premium",
        )
        await cio.track(
            customer_id=5, name="product.purchased", product_sku="XYZ-12345", price=23.45
        )


if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration

### Region

Create an instance of the client with your [Customer.io credentials](https://fly.customer.io/settings/api_credentials).

```python
from async_customerio import AsyncCustomerIO, Regions


cio = AsyncCustomerIO(site_id, api_key, region=Regions.US)
```

`region` is optional and takes one of two values — `Regions.US` or `Regions.EU`. If you do not specify your region, we assume
that your account is based in the US (`Regions.US`). If your account is based in the EU and you do not provide the correct region
(`Regions.EU`), we'll route requests to our EU data centers accordingly, however, this may cause data to be logged in the US.

### Custom User-Agent

By default every request is sent with the `User-Agent` header set to `async-customerio/<version>`.
You can override it via the `user_agent` parameter:

```python
cio = AsyncCustomerIO(site_id, api_key, user_agent="my-app/1.0")
```

The same parameter is available on `AsyncAPIClient`.

## Track API v1

```python
async with AsyncCustomerIO(site_id="site", api_key="key", region=Regions.US) as cio:
    # Identify a customer
    await cio.identify(id=5, email="customer@example.com", first_name="John")

    # Track an event
    await cio.track(customer_id=5, name="product.purchased", product_sku="XYZ-12345", price=23.45)
```

## Track API v2

The v2 Track API is accessed via the `.v2` property on the `AsyncCustomerIO` instance. It provides
typed convenience methods for all person and object operations, sharing the same connection and
credentials as the v1 client.

### Person operations

```python
async with AsyncCustomerIO(site_id="site", api_key="key", region=Regions.US) as cio:
    # Identify (create or update) a person
    await cio.v2.identify_person(identifiers={"id": 123}, name="Jane", plan="premium")

    # Track an event
    await cio.v2.track_person_event(identifiers={"id": 123}, name="purchase", amount=49.99)

    # Page view / screen view (mobile)
    await cio.v2.person_pageview(identifiers={"id": 123}, name="/pricing")
    await cio.v2.person_screen(identifiers={"id": 123}, name="home_screen")

    # Device management
    await cio.v2.add_person_device(identifiers={"id": 123}, device_id="tok_abc", platform="ios")
    await cio.v2.delete_person_device(identifiers={"id": 123}, device_id="tok_abc")

    # Suppress / unsuppress
    await cio.v2.suppress_person(identifiers={"id": 123})
    await cio.v2.unsuppress_person(identifiers={"id": 123})

    # Merge two person profiles (secondary is deleted)
    await cio.v2.merge_persons(primary={"id": 123}, secondary={"email": "old@example.com"})

    # Delete a person
    await cio.v2.delete_person(identifiers={"id": 123})
```

### Object operations

```python
async with AsyncCustomerIO(site_id="site", api_key="key") as cio:
    # Identify (create or update) an object
    await cio.v2.identify_object(
        identifiers={"object_type_id": "1", "object_id": "acme"},
        name="Acme Corp",
        industry="Software",
    )

    # Track an event on an object
    await cio.v2.track_object_event(
        identifiers={"object_type_id": "1", "object_id": "acme"},
        name="plan_changed",
    )

    # Delete an object
    await cio.v2.delete_object(identifiers={"object_type_id": "1", "object_id": "acme"})
```

### Relationships

```python
async with AsyncCustomerIO(site_id="site", api_key="key") as cio:
    # Relate a person to an object
    await cio.v2.add_person_relationships(
        identifiers={"id": 123},
        relationships=[{"identifiers": {"object_type_id": "1", "object_id": "acme"}}],
    )

    # Relate an object to people
    await cio.v2.add_object_relationships(
        identifiers={"object_type_id": "1", "object_id": "acme"},
        relationships=[{"identifiers": {"id": 123}}, {"identifiers": {"id": 456}}],
    )

    # Remove relationships
    await cio.v2.delete_person_relationships(
        identifiers={"id": 123},
        relationships=[{"identifiers": {"object_type_id": "1", "object_id": "acme"}}],
    )
```

### Batch operations

```python
from async_customerio.track.v2 import Actions

async with AsyncCustomerIO(site_id="site", api_key="key") as cio:
    batch = [
        {
            "type": "person",
            "action": Actions.identify.value,
            "identifiers": {"id": 123},
            "attributes": {"name": "Jane"},
        },
        {
            "type": "object",
            "action": Actions.identify.value,
            "identifiers": {"object_type_id": "1", "object_id": "acme"},
            "attributes": {"name": "Acme Corp"},
        },
    ]
    await cio.v2.send_batch(batch)
```

### Notes

- All v2 methods validate required parameters and raise `AsyncCustomerIOError` for missing identifiers, names, etc.
- The API enforces size limits: each item <= 32 KB, whole batch < 500 KB.
- `send_batch` returns the parsed JSON response body. On **200** the batch fully succeeded; on **207** the response contains per-item `"errors"` for partial failures. HTTP 400+ raises `AsyncCustomerIOError`.
- The legacy `cio.send_entity()` and `cio.send_batch()` methods still work for backwards compatibility but delegate to the `.v2` class internally.

## App API

The `AsyncAPIClient` provides access to the [Customer.io App API](https://docs.customer.io/api/app/).

### Send messages

```python
import asyncio

from async_customerio import AsyncAPIClient, SendInboxMessageRequest, Regions


async def main():
    api = AsyncAPIClient(key="your-app-api-key", region=Regions.US)
    request = SendInboxMessageRequest(
        transactional_message_id="3",
        identifiers={"id": "user_123"},
        message_data={"name": "Jane", "order_id": "1234"},
    )
    response = await api.send_inbox_message(request)
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
```

### Customers

Customer endpoints are accessed via the `.customers` namespace:

```python
async with AsyncAPIClient(key="your-app-api-key", region=Regions.US) as client:
    # Look up customers by email
    result = await client.customers.get_by_email("test@example.com")

    # Search with filters and pagination
    result = await client.customers.search(
        filter={"and": [{"segment": {"id": 1}}]},
        limit=10,
    )

    # Get customers with attributes by IDs
    result = await client.customers.get_by_ids([1, 2, 3])

    # Look up a single customer's attributes, segments, messages, etc.
    attrs = await client.customers.get_attributes(42)
    segments = await client.customers.get_segments(42)
    messages = await client.customers.get_messages(42, start_ts=1700000000, limit=5)
    activities = await client.customers.get_activities(42, type="event")
    relationships = await client.customers.get_relationships(42)
    prefs = await client.customers.get_subscription_preferences(42)

    # Use id_type to reference by email or cio_id instead of id
    attrs = await client.customers.get_attributes("test@example.com", id_type="email")
```

### Segments

```python
async with AsyncAPIClient(key="your-app-api-key") as client:
    # List all segments
    result = await client.segments.list()

    # Create a manual segment
    result = await client.segments.create("VIP Users", description="High-value customers")

    # Get a segment, its customer count, and dependencies
    segment = await client.segments.get(segment_id=1)
    count = await client.segments.get_customer_count(segment_id=1)
    deps = await client.segments.get_used_by(segment_id=1)

    # List customers in a segment with pagination
    members = await client.segments.get_membership(segment_id=1, limit=50)

    # Delete a segment
    await client.segments.delete(segment_id=1)
```

## Custom Retry Strategy

By default the library does **not** retry failed requests — it raises
`AsyncCustomerIORetryableError` for transient failures (transport errors, 429, 502-504)
so you can handle retries however you like.

If you want **automatic retries**, pass a `retry_strategy` that implements the
`RetryStrategy` protocol. Any object with an `async execute(func, *args, **kwargs)` method
will work.

### Using Tenacity

```python
import asyncio

from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from async_customerio import AsyncCustomerIO, AsyncCustomerIORetryableError, Regions


class TenacityRetryStrategy:
    """Retry strategy backed by tenacity."""

    def __init__(self, **kwargs):
        self._kwargs = kwargs

    async def execute(self, func, *args, **kwargs):
        async for attempt in AsyncRetrying(**self._kwargs):
            with attempt:
                return await func(*args, **kwargs)


async def main():
    retry = TenacityRetryStrategy(
        retry=retry_if_exception_type(AsyncCustomerIORetryableError),
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=30),
    )
    async with AsyncCustomerIO(
        site_id="YOUR_SITE_ID",
        api_key="YOUR_API_KEY",
        region=Regions.US,
        retry_strategy=retry,
    ) as cio:
        await cio.identify(id=1, name="Jane")


if __name__ == "__main__":
    asyncio.run(main())
```

The same `retry_strategy` parameter is available on `AsyncAPIClient`.

## Webhook Signature Verification

Securely verify that incoming webhooks originate from Customer.io ([docs](https://customer.io/docs/journeys/webhooks/#securely-verify-requests)).

```python
from async_customerio import validate_signature


webhook_signing_key = "755781b5e03a973f3405a85474d5a032a60fd56fabaad66039b12eadd83955fa"
x_cio_timestamp = 1692633432   # header value
x_cio_signature = "d7c655389bb364d3e8bdbb6ec18a7f1b6cf91f39bba647554ada78aa61de37b9"  # header value
body = b'{"key": "value"}'

if validate_signature(
    signing_key=webhook_signing_key,
    timestamp=x_cio_timestamp,
    request_body=body,
    signature=x_cio_signature,
):
    print("Request is sent from CustomerIO")
else:
    print("Malicious request received")
```

## API Coverage

<details>
<summary><strong>Track API</strong> — 14 of 18 endpoints implemented</summary>

| Category | Endpoints | Status |
|---|---|---|
| Track Customers | 8 | Implemented |
| Track Events | 4 | Implemented |
| Track v2 | 2 | Implemented |
| Track Segments | 2 | Not yet |
| Region | 1 | Not yet |
| Forms | 1 | Not yet |

</details>

<details>
<summary><strong>App API</strong> — 21 of 131 endpoints implemented</summary>

| Category | Endpoints | Status |
|---|---|---|
| Customers | 9 | Implemented |
| Segments | 7 | Implemented |
| Send Messages | 5 | Implemented |
| Transactional | 9 | Not yet |
| Campaigns | 13 | Not yet |
| Broadcasts | 15 | Not yet |
| Newsletters | 16 | Not yet |
| Messages | 3 | Not yet |
| Objects | 4 | Not yet |
| Activities | 1 | Not yet |
| Collections | 7 | Not yet |
| Exports | 5 | Not yet |
| Imports | 2 | Not yet |
| Snippets | 4 | Not yet |
| Design Studio | 20 | Not yet |
| Assets | 10 | Not yet |
| Sender Identities | 3 | Not yet |
| Reporting Webhooks | 5 | Not yet |
| ESP Suppression | 4 | Not yet |
| Subscription Center | 1 | Not yet |
| Data Index | 2 | Not yet |
| Workspaces | 1 | Not yet |
| Info | 1 | Not yet |

</details>

## License

`async-customerio` is offered under the MIT license.
