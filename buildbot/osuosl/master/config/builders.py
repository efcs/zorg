

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


def default_args(paths=[], opts=None):
    p = list(paths)
    if opts is not None:
        opts = dict(opts)
    else:
        opts = {}
    return [LitTestConfiguration(name = 'libcxx', paths=p, opts=opts)]


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
    return [
        getLibcxxBuilder('libcxx-coverage',
            cmake_opts={
                'CMAKE_BUILD_TYPE': 'DEBUG',
                'LIBCXX_GENERATE_COVERAGE': 'ON',
                'LIBCXX_COVERAGE_LIBRARY': '/usr/local/lib/clang/6.0.0/lib/linux/libclang_rt.profile-x86_64.a'},
            lit_invocations=default_args(),
            generate_coverage='/opt/libcxx-coverage/'),
        getLibcxxBuilder('libcxx-modules',
                         lit_invocations=default_args(opts={
                            'enable_modules': True
                         })),
        getLibcxxRangesBuilder('ranges-v3'),
        getLibcxxBoostBuilder('boost')
    ]

