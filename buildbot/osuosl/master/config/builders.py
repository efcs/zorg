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

from zorg.buildbot.builders import LLDBuilder
reload(LLDBuilder)
from zorg.buildbot.builders import LLDBuilder

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

from zorg.buildbot.builders import LibcxxABIChecker
reload(LibcxxABIChecker)
from zorg.buildbot.builders import LibcxxABIChecker

from zorg.buildbot.builders import SphinxDocsBuilder
reload(SphinxDocsBuilder)
from zorg.buildbot.builders import SphinxDocsBuilder

from zorg.buildbot.builders import ABITestsuitBuilder
reload(ABITestsuitBuilder)
from zorg.buildbot.builders import ABITestsuitBuilder

def get_builders():
    return [
        {'name': 'abi-checker-release',
         'slavenames': ['my_buildslave'],
         'builddir' : 'abi-checker-release',
         'factory': LibcxxABIChecker.getLibcxxABIChecker(
            env={'PATH': '/usr/local/bin:/usr/bin:/bin',
                 'CC': 'clang', 'CXX': 'clang++'},
            cmake_extra_opts={'CMAKE_BUILD_TYPE': 'RELWITHDEBINFO'}),
        'category': 'libcxx'},

        {'name': 'abi-checker-debug',
         'slavenames': ['my_buildslave'],
         'builddir' : 'abi-checker-debug',
         'factory': LibcxxABIChecker.getLibcxxABIChecker(
            env={'PATH': '/usr/local/bin:/usr/bin:/bin',
                 'CC': 'clang', 'CXX': 'clang++'},
            cmake_extra_opts={'CMAKE_BUILD_TYPE': 'DEBUG'}),
        'category': 'libcxx'}
    ]
