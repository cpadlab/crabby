import json
from typing import Iterable, TypeVar

import keyring
from cryptography.fernet import Fernet, InvalidToken
from pydantic import BaseModel

from crabby.schemas.connections import HeaderItem

_SERVICE = "Crabby"
_ACCOUNT = "connection-headers-key-v1"
_PREFIX = "enc:v1:"
HeaderModel = TypeVar("HeaderModel", bound=BaseModel)


def _cipher() -> Fernet:
    backend = keyring.get_keyring()
    backend_name = f"{type(backend).__module__}.{type(backend).__name__}".lower()
    if "fail" in backend_name or "plaintext" in backend_name or "keyrings.alt" in backend_name:
        raise RuntimeError("No secure operating-system credential store is available.")

    key = keyring.get_password(_SERVICE, _ACCOUNT)
    if key is None:
        key = Fernet.generate_key().decode("ascii")
        keyring.set_password(_SERVICE, _ACCOUNT, key)
        # Confirm the operating-system store accepted and retained the key.
        if keyring.get_password(_SERVICE, _ACCOUNT) != key:
            raise RuntimeError("The operating-system credential store did not retain the encryption key.")
    try:
        return Fernet(key.encode("ascii"))
    except (ValueError, UnicodeEncodeError) as exc:
        raise RuntimeError("The saved credential encryption key is invalid.") from exc


def encode_headers(headers: Iterable[BaseModel]) -> str:
    values = [header.model_dump() for header in headers]
    if not values:
        return "[]"
    payload = json.dumps(values, separators=(",", ":"))
    return _PREFIX + _cipher().encrypt(payload.encode("utf-8")).decode("ascii")


def decode_headers(
    value: str,
    header_model: type[HeaderModel] = HeaderItem,
) -> tuple[list[HeaderModel], str | None]:
    """Return decoded headers and an encrypted replacement for legacy plaintext."""
    if value.startswith(_PREFIX):
        try:
            payload = _cipher().decrypt(value[len(_PREFIX):].encode("ascii"))
            raw = json.loads(payload.decode("utf-8"))
        except (InvalidToken, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            raise RuntimeError("Could not decrypt saved connection credentials. The OS credential store may have changed.") from exc
        return [header_model(**item) for item in raw], None

    raw = json.loads(value)
    headers = [header_model(**item) for item in raw]
    if not headers:
        return [], None
    return headers, encode_headers(headers)
