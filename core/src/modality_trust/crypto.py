"""Small bounded JSON signing profile; deliberately not JOSE, COSE or RFC 8785."""

from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass
from typing import Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

MAX_BYTES = 32768
DOMAIN = b"OpenModalityTrust/local-profile/1\x00"


def _check(value, depth=0):
    if depth > 12:
        raise ValueError("JSON nesting limit")
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        if abs(value) > 2**53 - 1:
            raise ValueError("integer out of profile")
    elif type(value) is str:
        if len(value) > 8192 or any(0xD800 <= ord(c) <= 0xDFFF for c in value):
            raise ValueError("string out of profile")
    elif type(value) is list:
        if len(value) > 512:
            raise ValueError("array limit")
        for item in value:
            _check(item, depth + 1)
    elif type(value) is dict:
        if len(value) > 64:
            raise ValueError("object limit")
        for key, item in value.items():
            if type(key) is not str or not 1 <= len(key) <= 128:
                raise ValueError("invalid key")
            _check(key, depth + 1)
            _check(item, depth + 1)
    else:
        raise ValueError("only null, booleans, bounded integers, strings, arrays and objects")


def canonical(value) -> bytes:
    _check(value)
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode("ascii")
    if len(encoded) > MAX_BYTES:
        raise ValueError("message limit")
    return encoded


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def unpack(encoded: bytes | str):
    if type(encoded) not in (str, bytes) or len(encoded) > MAX_BYTES:
        raise ValueError("message limit or type")
    try:
        obj = json.loads(encoded, object_pairs_hook=_pairs)
        canonical(obj)
        return obj
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise ValueError("invalid JSON") from error


def digest(value) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def identifier(value: str) -> str:
    if type(value) is not str or not 1 <= len(value) <= 128 or not value.isascii():
        raise ValueError("invalid identifier")
    if any(ord(c) < 33 or ord(c) > 126 for c in value):
        raise ValueError("invalid identifier")
    return value


def exact(obj, keys):
    if type(obj) is not dict or set(obj) != set(keys):
        raise ValueError("unexpected fields")


def integer(value, low=0, high=2**53 - 1):
    if type(value) is not int or not low <= value <= high:
        raise ValueError("invalid integer")
    return value


@dataclass(frozen=True)
class Signer:
    issuer: str
    key: Ed25519PrivateKey

    @classmethod
    def generate(cls, issuer: str):
        return cls(identifier(issuer), Ed25519PrivateKey.generate())

    @property
    def public_key(self) -> bytes:
        return self.key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)

    def sign(self, kind: str, body: dict) -> bytes:
        protected = {"v": 1, "kind": identifier(kind), "issuer": identifier(self.issuer), "body": body}
        signature = self.key.sign(DOMAIN + canonical(protected))
        return canonical({"protected": protected, "signature": base64.b64encode(signature).decode("ascii")})


def verify(token: bytes | str, keys: Mapping[str, bytes], kind: str) -> dict:
    envelope = unpack(token)
    exact(envelope, ("protected", "signature"))
    protected = envelope["protected"]
    exact(protected, ("v", "kind", "issuer", "body"))
    if type(protected["v"]) is not int or protected["v"] != 1 or protected["kind"] != kind:
        raise ValueError("wrong protocol version or role")
    issuer = identifier(protected["issuer"])
    if issuer not in keys or type(protected["body"]) is not dict:
        raise ValueError("unconfigured issuer")
    try:
        signature = base64.b64decode(envelope["signature"], validate=True)
        if len(signature) != 64:
            raise ValueError("invalid signature length")
        Ed25519PublicKey.from_public_bytes(keys[issuer]).verify(signature, DOMAIN + canonical(protected))
    except (InvalidSignature, TypeError, ValueError) as error:
        raise ValueError("signature rejected") from error
    return protected
