from zorg.buildbot.builders import ClangBuilder
reload(ClangBuilder)
from zorg.buildbot.builders import ClangBuilder

from zorg.buildbot.builders import LLVMBuilder
reload(LLVMBuilder)
from zorg.buildbot.builders import LLVMBuilder

from zorg.buildbot.builders import LNTBuilder
reload(LNTBuilder)
from zorg.buildbot.builders import LNTBuilder

from zorg.buildbot.builders import NightlytestBuilder
reload(NightlytestBuilder)
from zorg.buildbot.builders import NightlytestBuilder

from zorg.buildbot.builders import PollyBuilder
reload(PollyBuilder)
from zorg.buildbot.builders import PollyBuilder

from zorg.buildbot.builders import LLDBBuilder
reload(LLDBBuilder)
from zorg.buildbot.builders import LLDBBuilder
from zorg.buildbot.builders.LLDBBuilder import RemoteConfig

from zorg.buildbot.builders import LLDBuilder
reload(LLDBuilder)
from zorg.buildbot.builders import LLDBuilder

from zorg.buildbot.builders import LLGoBuilder
reload(LLGoBuilder)
from zorg.buildbot.builders import LLGoBuilder

from zorg.buildbot.builders import ClangAndLLDBuilder
reload(ClangAndLLDBuilder)
from zorg.buildbot.builders import ClangAndLLDBuilder

from zorg.buildbot.builders import SanitizerBuilder
reload(SanitizerBuilder)
from zorg.buildbot.builders import SanitizerBuilder

from zorg.buildbot.builders import SanitizerBuilderII
reload(SanitizerBuilderII)
from zorg.buildbot.builders import SanitizerBuilderII

from zorg.buildbot.builders import SanitizerBuilderWindows
reload(SanitizerBuilderWindows)
from zorg.buildbot.builders import SanitizerBuilderWindows

from zorg.buildbot.builders import Libiomp5Builder
reload(Libiomp5Builder)
from zorg.buildbot.builders import Libiomp5Builder

from zorg.buildbot.builders import LibcxxAndAbiBuilder
reload(LibcxxAndAbiBuilder)
from zorg.buildbot.builders import LibcxxAndAbiBuilder
from zorg.buildbot.builders.LibcxxAndAbiBuilder import LitTestConfiguration

from zorg.buildbot.builders import LibcxxABIChecker
reload(LibcxxABIChecker)
from zorg.buildbot.builders import LibcxxABIChecker

from zorg.buildbot.builders import SphinxDocsBuilder
reload(SphinxDocsBuilder)
from zorg.buildbot.builders import SphinxDocsBuilder

from zorg.buildbot.builders import ABITestsuitBuilder
reload(ABITestsuitBuilder)
from zorg.buildbot.builders import ABITestsuitBuilder

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
         'LIBCXX_USE_CCACHE': '1',
         'CC': cc, 'CXX': cxx}
    # Disable CCACHE for coverage builds.
    if generate_coverage:
        del env['LIBCXX_USE_CCACHE']
    return {'name': name,
     'slavenames': ['my_buildslave'],
     'builddir' : name,
     'factory': LibcxxAndAbiBuilder.getLibcxxAndAbiBuilder(
        env=env,
        cmake_extra_opts=cmake_opts,
        lit_invocations=lit_invocations,
        enable_libcxxabi=enable_libcxxabi,
        generate_coverage=generate_coverage),
    'category': 'libcxx',
    'builder_type': 'nightly'}

def get_builders():
    gcc_dialect_args = del dialect_args()[0] # Remove C++03
    return [
        getLibcxxBuilder('libcxx-coverage',
            cmake_opts={
                'LIBCXX_GENERATE_COVERAGE': 'ON',
                'LIBCXX_COVERAGE_LIBRARY': '/usr/local/lib/clang/3.8.0/lib/linux/libclang_rt.profile-x86_64.a'},
            lit_invocations=default_args(),
            generate_coverage='/shared/libcxx-coverage'),
        
        getLibcxxBuilder('gcc-builder',
            cc='/opt/gcc-5.3/bin/gcc', cxx='/opt/gcc-5.3/bin/g++',
            lit_invocations=gcc_dialect_args),
        
        getLibcxxBuilder('static-libcxxabi-builder',
            cmake_opts={'LIBCXX_ENABLE_STATIC_ABI_LIBRARY': 'ON'}),
        
        getLibcxxBuilder('abi-unstable',
            cmake_opts={'LIBCXX_ABI_UNSTABLE': 'ON'},
            lit_invocations=min_dialect_args()),
        
        getLibcxxBuilder('no-threads',
            cmake_opts={'LIBCXX_ENABLE_THREADS': 'OFF',
                        'LIBCXXABI_ENABLE_THREADS': 'OFF'},
            lit_invocations=min_dialect_args())
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
