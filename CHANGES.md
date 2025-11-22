# Changelog

## 2.3.0

- Add support for CustomerIO Track V2 API. Two new methods are introduced ``send_entity`` and ``send_batch``.
  ``send_entity`` - This method lets you create, update, or delete a single person or object—including managing relationships between objects and people.
  ``send_batch`` - This method lets you batch requests for different people and objects in a single request. Each object in your array represents an individual "entity" operation—it represents a change for a person, an object, or a delivery.

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
