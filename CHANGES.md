# Changelog

## 2.13.1

- **Security**: Bump ``cryptography`` from 46.0.6 to 46.0.7 to address upstream security fixes. (#50)

## 2.13.0

### Bug Fixes

- **Fix**: Track v1 ``add_device()`` sent requests to a malformed URL (literal ``%7Bid%7D``
  instead of the customer identifier) due to URL encoding applied before placeholder substitution.

- **Fix**: Track v2 ``add_person_device()`` and ``delete_person_device()`` sent the device
  token under the key ``"id"`` instead of ``"token"`` as required by the v2 API specification.

- **Fix**: Track v2 ``merge_persons()`` sent an incorrect payload structure using
  ``"identifiers"`` / ``"cio_relationships"`` instead of the ``"primary"`` / ``"secondary"``
  top-level keys expected by the API.

- **Fix**: ``SendEmailRequest`` field ``disable_css_preprocessing`` was misspelled as
  ``disable_css_preproceessing`` in both the attribute name and the serialized JSON key,
  causing the API to silently ignore it.

- **Fix**: ``SendEmailRequest.fake_bcc`` was typed as ``Optional[str]`` but the API expects
  a boolean. Changed to ``Optional[bool]``.

- **Fix**: ``datetime_to_timestamp()`` now correctly converts timezone-aware datetimes to UTC
  instead of silently discarding the timezone offset.

- **Fix**: ``sanitize()`` now recursively processes nested dicts and lists. Previously only
  top-level values were sanitized, causing ``TypeError`` when nested datetimes were serialized
  to JSON.

### Improvements

- **Fix**: Resolve race condition in lazy HTTP client initialization. Concurrent coroutines
  could previously create multiple ``httpx.AsyncClient`` instances, orphaning connections.
  Client creation is now protected by an ``asyncio.Lock``.

- **Fix**: After ``close()`` and subsequent reuse, a fresh ``httpx.AsyncHTTPTransport`` is now
  created instead of reusing the previously closed transport.

- **Fix**: ``send_request`` return type annotation corrected from ``Union[dict]`` to
  ``Union[dict, str]`` to reflect the non-JSON text fallback path.

- Both ``AsyncCustomerIO`` and ``AsyncAPIClient`` now accept and forward the
  ``request_limits`` parameter to the base client, allowing users to customize
  connection pool settings.

- ``RequestTimeout`` and ``RequestLimits`` are now exported from the top-level
  ``async_customerio`` package.

- The ``retries`` constructor parameter is deprecated (it was never used for actual retry
  logic). Use ``retry_strategy`` instead.

- Fixed broken ``identify()`` examples in README (missing required positional ``identifier``
  argument) and added context manager usage to the App API example.

### Tests

- Added 80 new tests (219 → 299) bringing coverage from 96% to 98%.
- Track v1 and v2 tests now verify HTTP request URLs, methods, and payload structures.
- Added regression tests for all bug fixes listed above.
- Added tests for recursive sanitization, timezone-aware datetime conversion, concurrent
  client initialization, retryable vs non-retryable HTTP status codes, ``to_dict()`` field
  mapping, ``SendEmailRequest.attach()``, and transport recreation after close.

## 2.12.1

- **Security**: Bump ``cryptography`` from 46.0.5 to 46.0.6 to address upstream security fixes. (#48)

## 2.12.0

- **Fix**: ``send_batch`` now returns the parsed JSON response body instead of ``None``.
  On **200** the API returns an empty dict; on **207 Multi-Status** it returns per-item
  ``"errors"`` (with ``batch_index``, ``reason``, ``field``, ``message``), allowing callers
  to detect partial failures. Previously the 207 response was silently discarded. (#46)

- Align ``send_batch`` test fixtures with the official Customer.io Batch API specification.

## 2.11.0

- Add pluggable retry strategy via the new ``retry_strategy`` parameter on ``AsyncCustomerIO``,
  ``AsyncAPIClient``, and the base client. Any object implementing the ``RetryStrategy`` protocol
  (a single ``async execute(func, *args, **kwargs)`` method) can be passed in to add automatic
  retries with custom backoff logic (e.g. *tenacity*). When no strategy is provided, behaviour
  is unchanged — transient failures raise ``AsyncCustomerIORetryableError`` for the caller to handle.

## 2.10.0

- New ``client.segments`` namespace on ``AsyncAPIClient`` with 7 methods:

  - ``list`` — list all segments.
  - ``get`` — get a single segment by ID.
  - ``create`` — create a manual segment.
  - ``delete`` — delete a segment.
  - ``get_customer_count`` — get the number of customers in a segment.
  - ``get_membership`` — list customers in a segment with pagination.
  - ``get_used_by`` — get a segment's dependencies.

## 2.9.0

- Reorganize project structure into subpackages:

  - **Track API** moved to ``async_customerio.track`` package (``track.v1`` and ``track.v2`` modules).
  - **App API** moved to ``async_customerio.api`` package (``api._client`` and ``api.send`` modules).
  - Top-level imports (``from async_customerio import ...``) remain unchanged.

- Begin implementing the Customer.io App API. New ``client.customers`` namespace on ``AsyncAPIClient``
  with 9 methods:

  - ``get_by_email`` — look up customers by email address.
  - ``search`` — search for customers using audience filters with pagination.
  - ``get_by_ids`` — list customers with attributes and devices by IDs (up to 100).
  - ``get_attributes`` — look up a customer's attributes.
  - ``get_segments`` — look up a customer's segments.
  - ``get_messages`` — look up messages sent to a customer.
  - ``get_activities`` — look up a customer's activities.
  - ``get_relationships`` — look up a customer's relationships to objects.
  - ``get_subscription_preferences`` — look up a customer's subscription topic preferences.

## 2.8.0

- Add support for sending transactional inbox messages via ``SendInboxMessageRequest`` and ``AsyncAPIClient.send_inbox_message()``.

## 2.7.0

- Add optional ``user_agent`` parameter to ``AsyncCustomerIO``, ``AsyncAPIClient``, and the base client.
  Allows overriding the default ``async-customerio/<version>`` User-Agent header.

## 2.6.0

- [BREAKING] Drop support of Python 3.9
- Support of Python 3.14 added

## 2.5.0

- Introduce dedicated ``TrackAPIV2`` class for the Customer.io Track API v2, accessible via the ``cio.v2`` property.

  - **Person operations** (12 methods): ``identify_person``, ``delete_person``, ``track_person_event``,
    ``person_pageview``, ``person_screen``, ``add_person_device``, ``delete_person_device``,
    ``suppress_person``, ``unsuppress_person``, ``merge_persons``, ``add_person_relationships``,
    ``delete_person_relationships``.

  - **Object operations** (5 methods): ``identify_object``, ``delete_object``, ``track_object_event``,
    ``add_object_relationships``, ``delete_object_relationships``.

  - **Batch**: ``send_batch`` for submitting multiple entity operations in one request.

- Add object identifier types: ``IdentifierObject``, ``IdentifierCIOObject``, ``ObjectIdentifiers``,
  ``PersonIdentifiers``.

- Expand ``EntityPayload`` TypedDict with optional ``name``, ``device`` and ``cio_relationships`` fields.

- ``send_entity`` and ``send_batch`` on ``AsyncCustomerIO`` are now thin delegates to ``cio.v2``
  and remain available for backwards compatibility.

## 2.4.1

- Fixed a bug in URL encoding that caused a malformed request.

## 2.4.0

- ``client_base.py``

  - Cache package version and build User-Agent.
  - Use timezone-aware X-Timestamp.
  - Avoid mutating caller payloads (sanitization done locally).
  - Add ``async close()`` and ``__aenter__/__aexit__`` for cleanup.

- ``utils.py``

  - ``sanitize()`` made non-mutating (returns shallow copy, converts datetimes/NaN).
  - ``datetime_to_timestamp()`` validates input.
  - ``join_url()`` rewritten for safer quoting/params.

- ``api.py``

Fixed ``SendEmailRequest.attach()`` behavior and error on duplicate attachments.
Adjusted ``to_dict()`` mappings for request objects (fixed field mapping issues).
Duck-typing check for request objects before sending; Authorization header use.

- ``request_validator.py``. Accept optional ``v0=`` prefix in webhook signatures (HMAC compare logic).

- ``regions.py``. Simplified Region/Regions representation and usage.

- ``track.py``. Minor fixes: use ``sanitize()`` and ``datetime_to_timestamp()`` where appropriate; ``setup_base_url()`` improvements.

## 2.3.0

- Add support for CustomerIO Track V2 API. Two new methods are introduced ``send_entity`` and ``send_batch``.

  - ``send_entity`` - This method lets you create, update, or delete a single person or object—including managing relationships between objects and people.
  - ``send_batch`` - This method lets you batch requests for different people and objects in a single request. Each object in your array represents an individual "entity" operation—it represents a change for a person, an object, or a delivery.

## 2.2.0

- Remove redundant code that transforms the request object to a dictionary before sending it.

## 2.1.0

- Add support for sending transactional SMS messages.

## 2.0.0

- [BREAKING] Drop support of Python 3.7 and Python 3.8

## 1.6.0

- Support of Python 3.13 added

## 1.5.0

- Enhanced error handling in `send_request` method to properly categorize retryable vs non-retryable HTTP errors
- Added support for retryable status codes (500, 502, 503, 504, 429) that throw `AsyncCustomerIORetryableError`
- Improved CI/CD pipeline compatibility with Python 3.7-3.12
- Added conditional import for `importlib.metadata` to support Python 3.7

## 1.4.1

- [FIX] Authentication data is not sent with request.

## 1.4.0

- Refactored  ``async_customerio.client_base.AsyncClientBase`` to take advantage of connection pool. So the HTTP client will be created once during class ``async_customerio.track.AsyncCustomerIO`` and ``async_customerio.api.AsyncAPIClient`` instantiation.

## 1.3.0

- Support of Python 3.12 added.
- [FIX] Add missing dependency `type_extensions` to be able using type annotations on Python 3.7

## 1.2.0

- Added support of sending transactional push notifications. More details of how to send Push Notifications via CustomerIO <https://customer.io/docs/journeys/transactional-api/#transactional-push-notifications>

## 1.1.0

- Added helper function for validation of request origin using X-CIO-Signature and X-CIO-Timestamps

## 1.0.0

- [BREAKING] For consistency across APIs following actions have been taken:
- Renamed transactional email request optional arguments `amp_body` to `body_amp` and `plaintext_body` to `body_plain`
- Changed transactional email request default values for optional boolean arguments `disable_css_preprocessing`, `queue_draft`, `disable_message_retention`, `tracked`, `send_to_unsubscribed`

## 0.5.1

- [FIX] Change parameter name from `id_` to `identifier` of the method `identify` to avoid naming collision.

## 0.5.0

- Add a couple of new attributes to object `SendEmailRequest`

## 0.4.1

- The `Content-Type` we use has been updated so that Customer.io is happy when we try to send emails.

## 0.4.0

- Class `AsyncCustomerIO` updated with docstrings.

## 0.3.0

- `AsyncClientBase` has been adjusted to handle properly non-successful codes and connection retries.
- Class `SendEmailRequest` has been updated with type annotations.

## 0.2.0

- `README.md` has been updated with examples of how to use.

## 0.1.0

- First release on PyPI.
