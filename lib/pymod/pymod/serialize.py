import ast
import base64
from textwrap import wrap


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


def serialize_chunked(item, chunk_size=200):
    return wrap(serialize(item), chunk_size)


def deserialize_chunked(serialized_chunks):
    return deserialize(''.join(serialized_chunks))


def serialize_to_dict(item, root_key, chunk_size=200):
    serialized = {}
    for (i, chunk) in enumerate(serialize_chunked(item, chunk_size)):
        key = '{0}_{1}'.format(root_key, i)
        serialized[key] = chunk
    return serialized


def deserialize_from_dict(dict, root_key):
    i = 0
    chunks = []
    while True:
        key = '{0}_{1}'.format(root_key, i)
        chunk = dict.get(key)
        if chunk is None:
            break
        chunks.append(chunk)
        i += 1
    return deserialize_chunked(chunks)


def _encode(item):
    return base64.urlsafe_b64encode(str(item).encode()).decode()


def _decode(item):
    return base64.urlsafe_b64decode(str(item)).decode()
