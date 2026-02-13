# async-customerio is a lightweight asynchronous client to interact with CustomerIO

[![PyPI download month](https://img.shields.io/pypi/dm/async-customerio.svg)](https://pypi.python.org/pypi/async-customerio/)
[![PyPI version fury.io](https://badge.fury.io/py/async-customerio.svg)](https://pypi.python.org/pypi/async-customerio/)
[![PyPI license](https://img.shields.io/pypi/l/async-customerio.svg)](https://pypi.python.org/pypi/async-customerio/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/async-customerio.svg)](https://pypi.python.org/pypi/async-customerio/)
[![CI](https://github.com/healthjoy/async-customerio/actions/workflows/ci.yml/badge.svg)](https://github.com/healthjoy/async-customerio/actions/workflows/ci.yml)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/3629b50827ef4e89ba0eaa5c09584273)](https://www.codacy.com/gh/healthjoy/async-customerio/dashboard?utm_source=github.com&utm_medium=referral&utm_content=healthjoy/async-customerio&utm_campaign=Badge_Coverage)

- Free software: MIT license
- Requires: Python 3.9+

## Features

- Fully async
- Interface preserved as Official Python Client `customerio` has
- Send push notification
- Send messages

## Installation

```shell script
pip install async-customerio
```

## Getting started

```python
import asyncio

from async_customerio import AsyncCustomerIO, Regions


async def main():
    site_id = "Some-id-gotten-from-CustomerIO"
    api_key = "Some-key-gotten-from-CustomerIO"
    cio = AsyncCustomerIO(site_id, api_key, region=Regions.US)
    await cio.identify(
        id=5,
        email="customer@example.com",
        first_name="John",
        last_name="Doh",
        subscription_plan="premium",
    )
    await cio.track(
        customer_id=5, name="product.purchased", product_sku="XYZ-12345", price=23.45
    )


if __name__ == "__main__":
    asyncio.run(main())
```

### Instantiating `AsyncCustomerIO` object

Create an instance of the client with your [Customer.io credentials](https://fly.customer.io/settings/api_credentials).

```python
from async_customerio import AsyncCustomerIO, Regions


cio = AsyncCustomerIO(site_id, api_key, region=Regions.US)
```

`region` is optional and takes one of two values — `Regions.US` or `Regions.EU`. If you do not specify your region, we assume
that your account is based in the US (`Regions.US`). If your account is based in the EU and you do not provide the correct region
(`Regions.EU`), we'll route requests to our EU data centers accordingly, however, this may cause data to be logged in the US.

## Track API v2

The v2 Track API is accessed via the `.v2` property on the `AsyncCustomerIO` instance. It provides
typed convenience methods for all person and object operations, sharing the same connection and
credentials as the v1 client.

### Person operations

```python
import asyncio

from async_customerio import AsyncCustomerIO, Regions


async def main():
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


if __name__ == "__main__":
    asyncio.run(main())
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
from async_customerio.track_v2 import Actions

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
- HTTP 200 and 207 are treated as success (methods return `None`). HTTP 400+ raises `AsyncCustomerIOError`.
- The legacy `cio.send_entity()` and `cio.send_batch()` methods still work for backwards compatibility but delegate to the `.v2` class internally.

## Securely verify requests [doc](https://customer.io/docs/journeys/webhooks/#securely-verify-requests)

```python
from async_customerio import validate_signature


def main():
    webhook_signing_key = (
        "755781b5e03a973f3405a85474d5a032a60fd56fabaad66039b12eadd83955fa"
    )
    x_cio_timestamp = 1692633432  # header  value
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


if __name__ == "__main__":
    main()
```

## License

`async-customerio` is offered under the MIT license.

## Source code

The latest developer version is available in a GitHub repository:
[https://github.com/healthjoy/async-customerio](https://github.com/healthjoy/async-customerio)
