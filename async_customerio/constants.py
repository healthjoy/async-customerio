# Identifier types

from typing import TypedDict, Union


ID: str = "id"
EMAIL: str = "email"
CIOID: str = "cio_id"

# Identifiers.
IdentifierID = TypedDict("IdentifierID", {"id": Union[str, int]})
IdentifierEMAIL = TypedDict("IdentifierEMAIL", {"email": str})
IdentifierCIOID = TypedDict("IdentifierCIOID", {"cio_id": Union[str, int]})
