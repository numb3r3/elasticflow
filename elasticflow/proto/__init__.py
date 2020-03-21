import numpy as np

from . import flow_pb2


def blob2array(blob: 'gnes_doc_pb2.NdArray') -> np.ndarray:
    """
    Convert a blob proto to an array.
    """
    x = np.frombuffer(blob.data, dtype=blob.dtype).copy()
    return x.reshape(blob.shape)


def array2blob(x: np.ndarray) -> 'gnes_doc_pb2.NdArray':
    """Converts a N-dimensional array to blob proto.
    """
    blob = flow_pb2.NdArray()
    blob.data = x.tobytes()
    blob.shape.extend(list(x.shape))
    blob.dtype = x.dtype.name
    return blob
