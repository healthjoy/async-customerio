## Quick orientation

This repository implements a small, fully-async Python client for Customer.io (async-customerio).
Key modules:
- `async_customerio/track.py` — public Track API client (v1 + v2 stub). Main entrypoint for typical usage: `AsyncCustomerIO`.
- `async_customerio/api.py` — App API client used for transactional messages (email/push/sms) with `SendEmailRequest`/`SendPushRequest` helpers.
- `async_customerio/client_base.py` — base HTTP client: manages a single `httpx.AsyncClient` instance, headers, retries and error mapping.
- `async_customerio/utils.py` — helpers used across the library (`sanitize`, `to_dict`, `join_url`, `datetime_to_timestamp`).
- `async_customerio/request_validator.py` — webhook signature check (`validate_signature`).

Design notes an agent should preserve:
- Everything is async (use `await`). Public client methods (e.g. `AsyncCustomerIO.track`, `AsyncAPIClient.send_email`) are `async` and return `None` or `dict` results.
- HTTP plumbing is centralized in `AsyncClientBase.send_request` which:
  - Reuses a single `httpx.AsyncClient` via the `_client` property and `AsyncHTTPTransport` limits.
  - Prepares headers (`X-Request-Id`, `X-Timestamp`, `User-Agent`) — do not duplicate this logic; extend headers via the `headers` arg.
  - Raises `AsyncCustomerIORetryableError` for retryable network/status errors and `AsyncCustomerIOError` for others.
- Data payload helpers follow two common patterns:
  - `to_dict(field_map, instance)` builds JSON payloads from request-like objects (see `api.py:SendEmailRequest.to_dict`).
  - `sanitize()` converts datetimes and NaNs (call before sending JSON).

Auth and integration points
- Track API (site_id, api_key): `async_customerio.track.AsyncCustomerIO` methods call `send_request` with `auth=(site_id, api_key)` (see `track.py`).
- App API (app key): `async_customerio.api.AsyncAPIClient` uses `Authorization: Bearer <key>` in headers for transactional endpoints.
- Region selection is modeled with `async_customerio/regions.py` (`Regions.US` and `Regions.EU`) — agents should keep region-aware host selection when editing URL construction.

Developer workflows (commands discovered from repository files)
- Dependency & environment (this repo uses Poetry as the build tool):
  - Install: `poetry install`
  - Run tests: `poetry run pytest` (or `pytest` after installing dev dependencies)
  - Typecheck: `poetry run mypy`
  - Formatting: `poetry run black .` and `poetry run isort .`
- Tests use `pytest`, `pytest-asyncio`, and `pytest-httpx`. See `pyproject.toml` for pinned dev dependencies.

Project-specific patterns and conventions
- Keep things small and explicit: request objects (see `api.py`) expose a `to_dict()` implementation instead of implicit marshaling.
- Avoid mutating global state — clients are lightweight objects that hold credentials and an HTTP transport.
- Use `sanitize()` for any payload-building to normalize datetimes/NaNs.
- When creating new endpoints, prefer calling `join_url(base, *parts)` from `utils.py` to build URLs consistently.
- Return values: Track client methods generally return `None` (they just `await send_request`), while `AsyncAPIClient.send_*` returns the parsed JSON response.

Testing guidance for an agent
- Add tests under `tests/` using `pytest` + `pytest-asyncio` for async functions.
- Use `pytest-httpx` to mock `httpx` requests; look at existing tests to follow patterns.

Small examples for quick copy
- Track an event (example from README usage):
  ```py
  from async_customerio import AsyncCustomerIO, Regions
  cio = AsyncCustomerIO(site_id, api_key, region=Regions.US)
  await cio.track(customer_id=5, name="product.purchased", product_sku="XYZ")
  ```
- Send transactional email using `SendEmailRequest` (pattern to respect `to_dict` mapping):
  ```py
  from async_customerio.api import AsyncAPIClient, SendEmailRequest
  client = AsyncAPIClient(key=app_key, region=Regions.US)
  req = SendEmailRequest(to="a@b.com", subject="Hi", body="...", message_data={"k": "v"})
  res = await client.send_email(req)
  ```

When editing the repo
- Keep edits minimal and focused. Follow existing typing hints and raise `AsyncCustomerIOError` for synchronous validation failures.
- Reuse `to_dict` and `sanitize` rather than duplicating serialization logic.
- When adding network calls, use the `send_request` interface so headers, timeouts and retry semantics remain consistent.

Where to look for examples
- `async_customerio/track.py` — full set of track-related methods and validation checks.
- `async_customerio/api.py` — demonstrates request-object -> payload pattern and bearer token usage.
- `async_customerio/client_base.py` — centralized HTTP behavior, exceptions and header construction.
- `tests/` — provide reference tests for mocking `httpx` and exercising async methods.

If anything is unclear or you want additional examples (more tests, CI notes, or contributing guidelines), tell me which section to expand and I will iterate.
