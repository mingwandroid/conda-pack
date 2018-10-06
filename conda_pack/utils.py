from contextlib import contextmanager
import os
import sys


@contextmanager
def tmp_chdir(dest):
    curdir = os.getcwd()
    try:
        os.chdir(dest)
        yield
    finally:
        os.chdir(curdir)

'''
# Keeping this around for now in-case I need to inspect libarchive functions some more.
def _get_exports(filename, arch='native'):
    if not os.path.exists(filename):
        return []
    if filename.endswith('.a') or filename.endswith('.lib'):
        # Crappy, sorry.
        import subprocess
        # syms = os.system('nm -g {}'.filename)
        # on macOS at least:
        # -PgUj is:
        # P: posix format
        # g: global (exported) only
        # U: not undefined
        # j is name only
        if sys.platform == 'darwin':
            flags = '-PgUj'
        else:
            flags = '-P'
        out, _ = subprocess.Popen(['nm', flags, filename], shell=False,
                         stdout=subprocess.PIPE).communicate()
        results = out.decode('utf-8').splitlines()
        exports = [r.split(' ')[0] for r in results if (' T ') in r]
        return exports


def get_libarchive_filters():
    # This is horrible!
    exports = _get_exports(os.path.join(sys.prefix, 'lib', 'libarchive.a'))
    filters = {export.replace('_archive_write_add_filter_', '')
               for export in exports if '_archive_write_add_filter_' in export}
    for unwanted in ('by_name', 'program', 'none'):
        if unwanted in filters:
            filters.remove(unwanted)
    return filters


def get_libarchive_formats():
    # This is too!
    exports = _get_exports(os.path.join(sys.prefix, 'lib', 'libarchive.a'))
    formats = {export.replace('_archive_write_set_format_', '')
               for export in exports if '_archive_write_set_format_' in export}
    for unwanted in ('by_name', 'filter_by_ext', 'filter_by_ext_def', 'option'):
        if unwanted in formats:
            formats.remove(unwanted)
    return formats
'''


def get_libarchive_filters():
    from libarchive.ffi import WRITE_FILTERS
    return WRITE_FILTERS


def get_libarchive_formats():
    from libarchive.ffi import WRITE_FORMATS
    return WRITE_FORMATS
