from typing import List

import rocksdb

# see: https://python-rocksdb.readthedocs.io/en/latest/tutorial/


def _open_rocksdb(data_path: str, create_if_missing: bool = True, read_only: bool = True):
    opts = rocksdb.Options()
    opts.create_if_missing = create_if_missing
    opts.max_open_files = 300000
    opts.write_buffer_size = 67108864
    opts.max_write_buffer_number = 3
    opts.target_file_size_base = 67108864

    opts.table_factory = rocksdb.BlockBasedTableFactory(
        # use a bloom filter for faster lookups
        filter_policy=rocksdb.BloomFilterPolicy(10),
        block_cache=rocksdb.LRUCache(2 * (1024 ** 3)),
        block_cache_compressed=rocksdb.LRUCache(500 * (1024 ** 2)))

    return rocksdb.DB(data_path, opts, read_only=read_only)


class RocksDB(object):
    def __init__(self, data_path: str, create_if_missing: bool = True, read_only: bool = True):
        self._rocksdb = _open_rocksdb(
            data_path, create_if_missing=create_if_missing, read_only=read_only)

    def scan_db(self, reversed_scan: bool = False, fetch: bool = True):
        iterator = self._rocksdb.iterkeys()

        if reversed_scan:
            iterator.seek_to_last()
        else:
            iterator.seek_to_first()

        if reversed_scan:
            iterator = reversed(iterator)

        for key in iterator:
            yield (key, self._rocksdb.get(key) if fetch else None)

    def exists(self, key_bytes: bytes):
        # potentially lighter-weight than invoking get().
        return self._rocksdb.key_may_exist(key_bytes)

    def get(self, key_bytes: bytes):
        value_bytes = self._rocksdb.get(key_bytes)
        return value_bytes

    def multi_get(self, keys: List[bytes]):
        return self._rocksdb.multi_get(keys)

    def put(self, key_bytes: bytes, data_bytes: bytes):
        self._rocksdb.put(key_bytes, data_bytes, sync=True)

    def multi_put(self, doc_keys: List[bytes], data_bytes: List[bytes]):
        write_batch = rocksdb.WriteBatch()
        for key_bytes, value_bytes in zip(doc_keys, data_bytes):
            write_batch.put(key_bytes, value_bytes)
        self._rocksdb.write(write_batch, sync=True)

    def delete(self, key_bytes: bytes):
        self._rocksdb.delete(key_bytes, sync=True)

    def close(self):
        self._rocksdb.close()

    def backup(self, backup_path: str):
        backup = rocksdb.BackupEngine(backup_path)
        backup.create_backup(self._rocksdb, flush_before_backup=True)
