from typing import List

from .rocksdb import RocksDB


class RocksDatabase(object):
    def __init__(self, data_path: str,
                 create_if_missing: bool = True,
                 read_only: bool = True,
                 **kwargs):
        self._rocksdb = RocksDB(
            data_path, create_if_missing=create_if_missing, read_only=read_only)

    def put(self, doc: 'flow_pb2.Document'):
        key = doc.key
        doc_tytes = doc.SerializeToString()
        self._rocksdb.multi_put([key], [doc_tytes])

    def multi_put(self, docs: List['flow_pb2.Document']):
        doc_keys = []
        doc_bytes = []
        for d in docs:
            doc_keys.append(d.key)
            doc_bytes.append(d.SerializeToString())

        self._rocksdb.multi_put(doc_bytes, doc_bytes)

    def get(self, doc_key: bytes):
        return self._rocksdb.get(doc_key)

    def multi_get(self, doc_keys: List[bytes]):
        return self._rocksdb.multi_get(doc_keys)

    def delete(self, doc_key: bytes):
        self._rocksdb.delete(doc_key)

    def close(self):
        self._rocksdb.close()
