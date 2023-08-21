from async_customerio import validate_signature


def test_validate_signature():
    signing_key = '755781b5e03a973f3405a85474d5a032a60fd56fabaad66039b12eadd83955fa'
    sig = 'c097b83a7d57a0810625180a61213eab7e0389a54b33dd11c3a6f17790c8427a'
    ts = 1692633432
    body = b'{"data":{"action_id":42,"campaign_id":23,"content":"Welcome to the club, we are with you.","customer_id":"user-123","delivery_id":"RAECAAFwnUSneIa0ZXkmq8EdkAM==","headers":{"Custom-Header":["custom-value"]},"identifiers":{"id":"user-123"},"recipient":"test@example.com","subject":"Thanks for signing up"},"event_id":"01E2EMRMM6TZ12TF9WGZN0WJQT","metric":"sent","object_type":"email","timestamp":1692633432}'

    assert validate_signature(
        signing_key=signing_key,
        timestamp=ts,
        request_body=body,
        signature=sig
    ) is True
