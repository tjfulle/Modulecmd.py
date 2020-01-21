import json
import base64
from textwrap import wrap
import pymod.config


def serialize(raw):
    return _encode(json.dumps(raw))


def deserialize(serialized):
    return json.loads(_decode(serialized))


def serialize_chunked(raw):
    chunk_size = pymod.config.get("serialize_chunk_size")
    return wrap(serialize(raw), chunk_size)


def deserialize_chunked(serialized_chunks):
    return deserialize("".join(serialized_chunks))


def _encode(item):
    return base64.urlsafe_b64encode(str(item).encode()).decode()


def _decode(item):
    return base64.urlsafe_b64decode(str(item)).decode()
