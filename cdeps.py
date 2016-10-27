#!/bin/env python
import sys
import re
import os.path
import argparse
import io

class Dep(object):
    def __init__(self, fn, path=None, sysinc=False):
        if path:
            self.path = path
        else:
            self.path = ''
        self.deps = []
        if sysinc:
            self.incre = re.compile(r'#\s*include\s*["<](.*)[">]')
        else:
            self.incre = re.compile(r'#\s*include\s*["](.*)["]')
        self.dep(fn.strip())

    def open(self, fn):
        try:
            org = fn
            f = io.open(fn, encoding='utf-8', errors='replace')
        except:
            for p in self.path.split(os.path.pathsep):
                try:
                    fn = os.path.sep.join([p, org])
                    f = io.open(fn, encoding='utf-8', errors='replace')
                    return f
                except Exception:
                    pass
            raise
        return f

    def dep(self, fn):
        try:
            f = self.open(fn)
        except Exception as e:
            sys.stderr.write('exception: {}\n'.format(e))
            return False
        try:
            for l in f:
                mo = self.incre.search(l)
                if mo:
                    d = mo.group(1).strip()
                    if not (d in self.deps):
                        self.deps.append(d)
                        self.dep(d)
        finally:
            f.close()
        return True


description = 'Outputs header file dependencies suitable for makefile inclusion.'

epilog = '''
By default only includes following the '#include "foo.h"' pattern are output.
Specify --system-includes to also output '#include <bar.h>' includes.

Example:
%(prog)s main.c

Result:
main.o: main.h foo.h bar.h

main.h:

foo.h:

bar.h:
'''

ArgDefaults = argparse.ArgumentDefaultsHelpFormatter
RawDescription = argparse.RawDescriptionHelpFormatter

class MyFormatter(RawDescription, ArgDefaults):
    pass

def parseopt():
    parser = argparse.ArgumentParser(
        formatter_class=MyFormatter,
        description=description,
        epilog=epilog
    )
    parser.add_argument('filename', help='file to scan')
    parser.add_argument('-p', '--path', default='', help='search path')
    parser.add_argument('-s', '--system-includes', action="store_true"
                        , help='include "#include <foo.h>" includes in output :-)')
    parser.add_argument('-o', '--object-file-extension', default='o'
                        , help='file extension for the target, i.e.'
                        'if filename is "foo.c", the target filename will be foo.o')
    return parser
    
def main():
    ap = parseopt()
    args = ap.parse_args()
    d = Dep(args.filename, path=args.path, sysinc=args.system_includes)
    ext = args.object_file_extension
    stem = os.path.splitext(args.filename)[0]
    target = '{}.{}'.format(stem, ext)
    sys.stdout.write('{}: {}\n\n'.format(target, ' '.join(d.deps)))
    for n in d.deps:
        sys.stdout.write('{}:\n\n'.format(n))

if __name__ == '__main__':
    main()
