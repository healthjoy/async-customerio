# Identifier types

from typing import TypedDict, Union


ID: str = "id"
EMAIL: str = "email"
CIOID: str = "cio_id"

# Person identifiers.
IdentifierID = TypedDict("IdentifierID", {"id": Union[str, int]})
IdentifierEMAIL = TypedDict("IdentifierEMAIL", {"email": str})
IdentifierCIOID = TypedDict("IdentifierCIOID", {"cio_id": Union[str, int]})

# Object identifiers (v2 API).
IdentifierObject = TypedDict("IdentifierObject", {"object_type_id": str, "object_id": str})
IdentifierCIOObject = TypedDict("IdentifierCIOObject", {"cio_object_id": str})

# Convenience union aliases.
PersonIdentifiers = Union[IdentifierID, IdentifierEMAIL, IdentifierCIOID]
ObjectIdentifiers = Union[IdentifierObject, IdentifierCIOObject]
