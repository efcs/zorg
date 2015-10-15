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

from zorg.buildbot.builders import LibcxxCoverageBuilder
reload(LibcxxCoverageBuilder)
from zorg.buildbot.builders import LibcxxCoverageBuilder

from zorg.buildbot.builders import SphinxDocsBuilder
reload(SphinxDocsBuilder)
from zorg.buildbot.builders import SphinxDocsBuilder

from zorg.buildbot.builders import ABITestsuitBuilder
reload(ABITestsuitBuilder)
from zorg.buildbot.builders import ABITestsuitBuilder

default_invocations = [LitTestConfiguration(name = 'libcxx')]

dialect_args = [
    LitTestConfiguration(name='libcxx-cxx03', opts={'std': 'c++03'}),
    LitTestConfiguration(name='libcxx-cxx11', opts={'std': 'c++11'}),
    LitTestConfiguration(name='libcxx-cxx14', opts={'std': 'c++14'}),
    LitTestConfiguration(name='libcxx-cxx1z', opts={'std': 'c++1z'})
]

min_dialect_args = [
    LitTestConfiguration(name='libcxx-cxx03', opts={'std': 'c++03'}),
    LitTestConfiguration(name='libcxx-default')
]

tsan_args = []

def getLibcxxBuilder(name, cc='clang', cxx='clang++', cmake_opts={},
                     lit_invocations=default_invocations,
                     enable_libcxxabi=False):
    return {'name': name,
     'slavenames': ['my_buildslave'],
     'builddir' : name,
     'factory': LibcxxAndAbiBuilder.getLibcxxAndAbiBuilder(
        env={'PATH': '/usr/local/bin:/usr/bin:/bin',
             'LIBCXX_USE_CCACHE': '1',
             'CC': cc, 'CXX': cxx},
        cmake_extra_opts=cmake_opts,
        lit_invocations=lit_invocations),
    'category': 'libcxx',
    'builder_type': 'nightly'}

def get_builders():
    return [
        {'name': 'libcxx-coverage',
         'slavenames': ['my_buildslave'],
         'builddir' : 'libcxx-coverage',
         'factory': LibcxxCoverageBuilder.getLibcxxCoverageBuilder(
             '/shared/libcxx-coverage/',
            '/usr/local/lib/clang/3.7.0/lib/linux/libclang_rt.profile-x86_64.a',
            env={'PATH': '/usr/local/bin:/usr/bin:/bin',
                 'CC': 'clang', 'CXX': 'clang++'},
            lit_extra_opts={'std': 'c++1z', 'use_ccache': 'True'}),
        'category': 'libcxx',
        'builder_type': 'nightly'},
        getLibcxxBuilder('gcc-builder',
            cc='gcc', cxx='g++', lit_invocations=dialect_args),
        getLibcxxBuilder('static-libcxxabi-builder',
            cmake_opts={'LIBCXX_ENABLE_STATIC_ABI_LIBRARY=ON'}
            lit_invocations=default_invocations)
        getLibcxxBuilder('abi-unstable',
            cmake_opts={'LIBCXX_ABI_UNSTABLE': 'ON'},
            lit_invocations=min_dialect_args),
        getLibcxxBuilder('no-threads',
            cmake_opts={'LIBCXX_ENABLE_THREADS': 'OFF',
                        'LIBCXXABI_ENABLE_THREADS': 'OFF'},
            lit_invocations=min_dialect_args)
        
            
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
