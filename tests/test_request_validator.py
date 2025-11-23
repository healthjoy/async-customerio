import pytest

from async_customerio import validate_signature


BODY = (
    b'{"data":{"action_id":42,"campaign_id":23,"content":"Welcome to the club, we are with you.",'
    b'"customer_id":"user-123","delivery_id":"RAECAAFwnUSneIa0ZXkmq8EdkAM==","headers":{"Custom-Header":["custom-value"]},'
    b'"identifiers":{"id":"user-123"},"recipient":"test@example.com","subject":"Thanks for signing up"},'
    b'"event_id":"01E2EMRMM6TZ12TF9WGZN0WJQT","metric":"sent","object_type":"email","timestamp":1692633432}'
)
X_CIO_SIGNATURE = "c097b83a7d57a0810625180a61213eab7e0389a54b33dd11c3a6f17790c8427a"
X_CIO_TIMESTAMP = 1692633432


@pytest.mark.parametrize("signature, body, x_cio_timestamp, expected", [
    (X_CIO_SIGNATURE, BODY, X_CIO_TIMESTAMP, True),
    (X_CIO_SIGNATURE, BODY, int(f'{X_CIO_TIMESTAMP + 1}'), False),
    ("WRONG" + X_CIO_SIGNATURE[5:], BODY, X_CIO_TIMESTAMP, False),
    (X_CIO_SIGNATURE, b'{"malicious_key": "malicious_value"}', X_CIO_TIMESTAMP,  False),
])
def test_validate_signature(signature, body, x_cio_timestamp, expected):
    signing_key = '755781b5e03a973f3405a85474d5a032a60fd56fabaad66039b12eadd83955fa'
    assert validate_signature(
        signing_key=signing_key,
        timestamp=x_cio_timestamp,
        request_body=body,
        signature=signature
    ) is expected


def test_validate_signature_with_v0_prefix():
    signing_key = '755781b5e03a973f3405a85474d5a032a60fd56fabaad66039b12eadd83955fa'
    signature = "v0=" + X_CIO_SIGNATURE
    assert validate_signature(signing_key=signing_key, timestamp=X_CIO_TIMESTAMP, request_body=BODY, signature=signature)

