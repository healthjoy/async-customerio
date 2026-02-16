# Changelog

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
- Changed transactional email request default values for optional boolean arguments `disable_css_preproceessing`, `queue_draft`, `disable_message_retention`, `tracked`, `send_to_unsubscribed`

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
