

from zorg.buildbot.builders import LibcxxAndAbiBuilder
reload(LibcxxAndAbiBuilder)
from zorg.buildbot.builders import LibcxxAndAbiBuilder
from zorg.buildbot.builders.LibcxxAndAbiBuilder import LitTestConfiguration

from zorg.buildbot.builders import LibcxxRangesV3Builder
reload(LibcxxRangesV3Builder)
from zorg.buildbot.builders import LibcxxRangesV3Builder

from zorg.buildbot.builders import LibcxxBoostBuilder
reload(LibcxxBoostBuilder)
from zorg.buildbot.builders import LibcxxBoostBuilder

from zorg.buildbot.builders import LibcxxABIChecker
reload(LibcxxABIChecker)
from zorg.buildbot.builders import LibcxxABIChecker


def default_args(paths=[]):
    return [LitTestConfiguration(name = 'libcxx', paths=paths)]

def dialect_args(paths=[]):
    return [
        LitTestConfiguration(name='libcxx-cxx03', opts={'std': 'c++03'}, paths=paths),
        LitTestConfiguration(name='libcxx-cxx11', opts={'std': 'c++11'}, paths=paths),
        LitTestConfiguration(name='libcxx-cxx14', opts={'std': 'c++14'}, paths=paths),
        LitTestConfiguration(name='libcxx-cxx1z', opts={'std': 'c++1z'}, paths=paths)
    ]

def min_dialect_args(paths=[]):
    return [
        LitTestConfiguration(name='libcxx-cxx03', opts={'std': 'c++03'}, paths=paths),
        LitTestConfiguration(name='libcxx-default', paths=paths)
    ]

tsan_args = []

def getLibcxxBuilder(name, cc='clang', cxx='clang++', cmake_opts={},
                     lit_invocations=default_args(),
                     enable_libcxxabi=True, generate_coverage=None):
    env={'PATH': '/usr/local/bin:/usr/bin:/bin',
         'CC': cc, 'CXX': cxx}
    return {'name': name,
     'slavenames': ['my_buildslave'],
     'builddir' : name,
     'factory': LibcxxAndAbiBuilder.getLibcxxAndAbiBuilder(
        env=env,
        cmake_extra_opts=cmake_opts,
        lit_invocations=lit_invocations,
        enable_libcxxabi=enable_libcxxabi,
        generate_coverage=generate_coverage),
    'category': 'libcxx-nightly'}


def getLibcxxRangesBuilder(name, cc='clang', cxx='clang++'):
    env={'PATH': '/usr/local/bin:/usr/bin:/bin',
         'CC': cc, 'CXX': cxx}
    return {'name': name,
     'slavenames': ['my_buildslave'],
     'builddir' : name,
     'factory': LibcxxRangesV3Builder.getLibcxxRangesV3Builder(
        env=env),
    'category': 'libcxx-nightly'}


def getLibcxxBoostBuilder(name, cc='clang', cxx='clang++'):
    env={'PATH': '/usr/local/bin:/usr/bin:/bin',
         'CC': cc, 'CXX': cxx}
    return {'name': name,
     'slavenames': ['my_buildslave'],
     'builddir' : name,
     'factory': LibcxxBoostBuilder.getLibcxxBoostBuilder(
        env=env),
    'category': 'libcxx-nightly'}

def get_builders():
    gcc_dialect_args = list(dialect_args())
    del gcc_dialect_args[0] # Remove C++03
    return [
        getLibcxxBuilder('libcxx-coverage',
            cmake_opts={
                'CMAKE_BUILD_TYPE': 'DEBUG',
                'LIBCXX_GENERATE_COVERAGE': 'ON',
                'LIBCXX_COVERAGE_LIBRARY': '/usr/local/lib/clang/4.0.0/lib/linux/libclang_rt.profile-x86_64.a'},
            lit_invocations=default_args(),
            generate_coverage='/shared/libcxx-coverage'),
        
        getLibcxxBuilder('gcc-builder',
            cc='/opt/gcc-tot/bin/gcc', cxx='/opt/gcc-tot/bin/g++',
            lit_invocations=gcc_dialect_args),

        getLibcxxBuilder('static-libcxxabi-builder',
            cmake_opts={'LIBCXX_ENABLE_STATIC_ABI_LIBRARY': 'ON', 'LIBCXXABI_ENABLE_SHARED': 'OFF'}),

        getLibcxxBuilder('abi-unstable',
            cmake_opts={'LIBCXX_ABI_UNSTABLE': 'ON'},
            lit_invocations=min_dialect_args()),

        getLibcxxRangesBuilder('ranges-v3'),
        getLibcxxBoostBuilder('boost')
    ]

""" Old builders
{'name': 'abi-checker-release',
 'slavenames': ['my_buildslave'],
 'builddir' : 'abi-checker-release',
 'factory': LibcxxABIChecker.getLibcxxABIChecker(
    env={'PATH': '/usr/local/bin:/usr/bin:/bin',
         'CC': 'clang', 'CXX': 'clang++'},
    cmake_extra_opts={'CMAKE_BUILD_TYPE': 'RELWITHDEBINFO'}),
'category': 'libcxx',
'builder_type': 'commit'},

{'name': 'abi-checker-debug',
 'slavenames': ['my_buildslave'],
 'builddir' : 'abi-checker-debug',
 'factory': LibcxxABIChecker.getLibcxxABIChecker(
    env={'PATH': '/usr/local/bin:/usr/bin:/bin',
         'CC': 'clang', 'CXX': 'clang++'},
    cmake_extra_opts={'CMAKE_BUILD_TYPE': 'DEBUG'}),
'category': 'libcxx',
'builder_type': 'commit'},
"""
