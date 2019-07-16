import ast
import base64
from textwrap import wrap
import pymod.config


def serialize(item):
    type_name = type(item).__name__
    serialized = _encode('{0}:{1}'.format(type_name, str(item)))
    return serialized


def deserialize(serialized):
    deserialized = _decode(serialized)
    i = deserialized.find(':')
    type_name = deserialized[:i]
    obj = deserialized[i+1:]
    if not obj or not obj.strip():
        return eval('{0}()'.format(type_name))
    else:
        return ast.literal_eval(obj)


def serialize_chunked(item):
    chunk_size = pymod.config.get('serialize_chunk_size')
    return wrap(serialize(item), chunk_size)


def deserialize_chunked(serialized_chunks):
    return deserialize(''.join(serialized_chunks))


def _encode(item):
    return base64.urlsafe_b64encode(str(item).encode()).decode()


def _decode(item):
    return base64.urlsafe_b64decode(str(item)).decode()
