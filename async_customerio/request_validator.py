import hashlib
import hmac


def validate_signature(signing_key: str, timestamp: int, request_body: bytes, signature: str) -> bool:
    """Validate that request was sent from Customer.io
    Doc: https://customer.io/docs/journeys/webhooks/#securely-verify-requests

    :param signing_key: value for SIGNING KEY from Customer.io
    :param timestamp: unix timestamp, value from header  X-CIO-Timestamp
    :param request_body: body of the request
    :param signature: value from header X-CIO-Signature

    :returns: True if the request passes validation, False if not
    """
    payload = b"v0:" + str(timestamp).encode() + b":" + request_body
    computed_signature = hmac.new(key=signing_key.encode(), msg=payload, digestmod=hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed_signature, signature)
