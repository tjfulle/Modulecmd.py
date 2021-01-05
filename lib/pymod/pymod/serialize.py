import json
import zlib
import base64
from textwrap import wrap
import pymod.config


def serialize(string):
    return _encode(json.dumps(string))


def deserialize(serialized):
    string = _decode(serialized)
    return json.loads(string)


def serialize_chunked(raw):
    serialized = serialize(raw)
    chunk_size = pymod.config.get("serialize_chunk_size")
    if chunk_size < 0:
        return [serialized]
    return wrap(serialized, chunk_size)


def deserialize_chunked(serialized_chunks):
    return deserialize("".join(serialized_chunks))


def _encode(item):
    encoded = str(item).encode("utf-8")
    compress = pymod.config.get("compress_serialized_variables")
    if compress:
        encoded = zlib.compress(encoded)
    return base64.urlsafe_b64encode(encoded).decode()


def _decode(item):
    encoded = base64.urlsafe_b64decode(str(item))
    compress = pymod.config.get("compress_serialized_variables")
    if compress:
        encoded = zlib.decompress(encoded)
    return encoded.decode()
