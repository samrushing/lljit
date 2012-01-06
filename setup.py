
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

# we need compiler flags from llvm-config

import subprocess
cxxflags = subprocess.check_output (['llvm-config', '--cxxflags']).strip().split()
ldflags  = subprocess.check_output (['llvm-config', '--ldflags']).strip().split()
linkargs = subprocess.check_output (['llvm-config', '--libs', 'core', 'bitreader', 'jit', 'native', 'asmparser']).strip().split()

ext = Extension (
    'lljit.lljit',
    ['lljit/lljit.pyx', 'lljit/llvm.pxd'],
    language='c++',
    extra_compile_args = cxxflags,
    extra_link_args = ldflags + linkargs,
    )

setup (
    name             = 'lljit',
    version          = '0.1',
    description      = 'cython interface to LLVM Jit',
    author           = "Sam Rushing",
    packages         = ['lljit'],
    ext_modules      = [ext],
    install_requires = ['cython>=0.15'],
    url              = 'http://github.com/samrushing/lljit/',
    download_url     = "http://github.com/samrushing/lljit/tarball/master#egg=lljit-0.1",
    license          = 'Simplified BSD',
    cmdclass = {'build_ext': build_ext},
    )
