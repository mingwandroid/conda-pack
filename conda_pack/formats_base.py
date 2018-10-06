import os


tar_mode = {
            # These are tarfile format options:
            'tar.gz': 'w:gz',
            'tgz': 'w:gz',
            'tar.bz2': 'w:bz2',
            'tbz2': 'w:bz2',
            'tar': 'w',
            # This is a libarchive format option:
            'tar.zstd': 'zstd:compression-level=22'}


class ArchiveBase(object):
    def __exit__(self, *args):
        if hasattr(self.archive, "close"):
            self.archive.close()

    def add(self, source, target):
        target = os.path.join(self.arcroot, target)
        self._add(source, target)

    def add_bytes(self, source, sourcebytes, target):
        target = os.path.join(self.arcroot, target)
        self._add_bytes(source, sourcebytes, target)
