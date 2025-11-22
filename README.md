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

This client now includes convenience helpers for the Customer.io Track V2 API. V2 uses two endpoints:

- `/api/v2/entity` — single-entity operations (identify, delete, event, relationships, devices, etc.)
- `/api/v2/batch` — submit multiple entity operations in one request (useful for bulk uploads).

Basic usage:

```python
import asyncio

from async_customerio import AsyncCustomerIO, Regions
from async_customerio.track import Actions


async def v2_examples():
    cio = AsyncCustomerIO(site_id="site", api_key="key", region=Regions.US)

    # Single entity operation (identify a person)
    await cio.send_entity(
        identifiers={"id": 123},
        type="person",
        action=Actions.identify,
        name="Jane",
        plan="premium",
    )

    # Batch of entity operations
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
            "identifiers": {"id": "account_1"},
            "attributes": {"name": "Account A"},
        },
    ]

    await cio.send_batch(batch)


if __name__ == "__main__":
    asyncio.run(v2_examples())
```

Notes:

- `send_entity` validates that `identifiers` is present and constructs a payload of the shape ``{type, action, identifiers, attributes}``.
- `send_batch` accepts a list of entity payloads. The API enforces size limits (each item <= 32kb, whole batch < 500kb); obey those limits in production.
- Response handling: the client treats HTTP 200 and 207 as success (methods return `None`, matching other Track methods). HTTP 400 (malformed request) will raise `AsyncCustomerIOError`.

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
