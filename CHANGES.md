# Changelog

## 0.5.1

- [FIX] Change parameter name from ``id_`` to ``identifier`` of the method ``identify`` to avoid naming collision.

## 0.5.0

- Add a couple of new attributes to object ``SendEmailRequest``

## 0.4.1

- The ``Content-Type`` we use has been updated so that Customer.io is happy when we try to send emails.

## 0.4.0

- Class ``AsyncCustomerIO`` updated with docstrings.

## 0.3.0

- ``AsyncClientBase`` has been adjusted to handle properly non-successful codes and connection retries.
- Class ``SendEmailRequest`` has been updated with type annotations.

## 0.2.0

- `README.md` has been updated with examples of how to use.

## 0.1.0

- First release on PyPI.
