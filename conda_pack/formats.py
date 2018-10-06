import os
import stat
import sys
import tarfile
import time
import zipfile
from io import BytesIO
from .formats_base import ArchiveBase, tar_mode


def archive(fileobj, filename, arcroot, format,
            libarchive_format=None, libarchive_filter=None, libarchive_options=None,
            compress_level=4, zip_symlinks=False, zip_64=True):
    if format == 'zip':
        return ZipArchive(fileobj, filename, arcroot, zip_symlinks=zip_symlinks,
                          zip_64=zip_64)
    elif format == 'tar.bz2':
        return TarArchive(fileobj, filename, arcroot, tar_mode[format],
                          compress_level=compress_level)
    else:
        if not libarchive_options and format in tar_mode:
            libarchive_options = tar_mode[format]
        from .formats_libarchive import TarZstArchive
        return TarZstArchive(fileobj, filename, arcroot,
                             mode=libarchive_options,
                             compress_level=compress_level,
                             format_name=libarchive_format,
                             filter_name=libarchive_filter)


class TarArchive(ArchiveBase):
    def __init__(self, fileobj, filename, arcroot, mode, compress_level):
        self.fileobj = fileobj
        self.filename = filename
        self.arcroot = arcroot
        self.mode = mode
        self.compress_level = compress_level

    def __enter__(self):
        if self.mode != 'w':
            kwargs = {'compresslevel': self.compress_level}
        else:
            kwargs = {}

        self.archive = tarfile.open(fileobj=self.fileobj, mode=self.mode,
                                    dereference=False, **kwargs)
        return self

    def _add(self, source, target):
        self.archive.add(source, target, recursive=False)

    def _add_bytes(self, source, sourcebytes, target):
        info = self.archive.gettarinfo(source, target)
        info.size = len(sourcebytes)
        self.archive.addfile(info, BytesIO(sourcebytes))


class ZipArchive(ArchiveBase):
    def __init__(self, fileobj, filename, arcroot, zip_symlinks=False, zip_64=True):
        self.fileobj = fileobj
        self.filename = filename
        self.arcroot = arcroot
        self.zip_symlinks = zip_symlinks
        self.zip_64 = zip_64

    def __enter__(self):
        self.archive = zipfile.ZipFile(self.fileobj, "w",
                                       allowZip64=self.zip_64,
                                       compression=zipfile.ZIP_DEFLATED)
        return self

    def _add(self, source, target):
        try:
            st = os.lstat(source)
            is_link = stat.S_ISLNK(st.st_mode)
        except (OSError, AttributeError):
            is_link = False

        if is_link:
            if self.zip_symlinks:
                info = zipfile.ZipInfo(target)
                info.create_system = 3
                info.external_attr = (st.st_mode & 0xFFFF) << 16
                if os.path.isdir(source):
                    info.external_attr |= 0x10  # MS-DOS directory flag
                self.archive.writestr(info, os.readlink(source))
            else:
                if os.path.isdir(source):
                    for root, dirs, files in os.walk(source, followlinks=True):
                        root2 = os.path.join(target, os.path.relpath(root, source))
                        for fil in files:
                            self.archive.write(os.path.join(root, fil),
                                               os.path.join(root2, fil))
                        if not dirs and not files:
                            # root is an empty directory, write it now
                            self.archive.write(root, root2)
                else:
                    self.archive.write(source, target)
        else:
            self.archive.write(source, target)

    def _add_bytes(self, source, sourcebytes, target):
        info = zipinfo_from_file(source, target)
        self.archive.writestr(info, sourcebytes)


if sys.version_info >= (3, 6):
    zipinfo_from_file = zipfile.ZipInfo.from_file
else:  # pragma: no cover
    # Backported from python 3.6
    def zipinfo_from_file(filename, arcname=None):
        st = os.stat(filename)
        isdir = stat.S_ISDIR(st.st_mode)
        mtime = time.localtime(st.st_mtime)
        date_time = mtime[0:6]
        # Create ZipInfo instance to store file information
        if arcname is None:
            arcname = filename
        arcname = os.path.normpath(os.path.splitdrive(arcname)[1])
        while arcname[0] in (os.sep, os.altsep):
            arcname = arcname[1:]
        if isdir:
            arcname += '/'
        zinfo = zipfile.ZipInfo(arcname, date_time)
        zinfo.external_attr = (st.st_mode & 0xFFFF) << 16  # Unix attributes
        if isdir:
            zinfo.file_size = 0
            zinfo.external_attr |= 0x10  # MS-DOS directory flag
        else:
            zinfo.file_size = st.st_size

        return zinfo
