#!/bin/env python3

import itertools
import os
import re
import subprocess
import sys
import tempfile

def make_lib(dll):
    lib_dir, dll_name = os.path.split(dll)
    if lib_dir.endswith('bin'):
        lib_dir = lib_dir[:-3] + 'lib'
    lib_name = re.sub(r'(?:lib)?(.*?)(?:-\d)?\.dll', r'\1.lib', dll_name)
    if lib_name == 'zlib1.lib': lib_name = 'z.lib'
    print(lib_name)
    try:
        os.remove(os.path.join(lib_dir, lib_name))
    except FileNotFoundError:
        pass
    dumpbin = subprocess.run(['dumpbin', '/exports', dll],
            stdout=subprocess.PIPE, check=True)
    lines = dumpbin.stdout.splitlines()
    export_start = [i for i in enumerate(lines)
            if i[1].find(b'ordinal hint') != -1][0][0] + 2
    exports = itertools.takewhile(lambda x: x != b'', lines[export_start:])
    exports = [i.split() for i in exports]
    def_file = tempfile.NamedTemporaryFile(suffix=b'.def', delete=False)
    def_file.write(b'LIBRARY ' + dll_name.encode('utf8') + b'\r\n')
    def_file.write(b'EXPORTS\r\n')
    for ordinal,_,_,name in exports:
        def_file.write(name + b' @' + ordinal + b'\r\n')
    def_file.close()
    subprocess.run(['lib', '/def:' + def_file.name.decode('utf8'),
            '/out:' + os.path.join(lib_dir, lib_name)], check=True,
            stdout=subprocess.DEVNULL)
    os.remove(def_file.name)

def make_libs(args):
    base = r'C:\msys64\mingw64\bin'
    for f in os.listdir(base):
        if f.endswith('.dll'):
            print('generating for %s ...' % f, end='')
            sys.stdout.flush()
            make_lib(os.path.join(base, f))
            print('done')

if __name__ == '__main__':
    sys.exit(make_libs(sys.argv[1:]))
