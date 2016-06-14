import os

import buildbot
import buildbot.process.factory
import buildbot.steps.shell
import buildbot.process.properties as properties

from buildbot.steps.source.svn import SVN
from buildbot.steps.source.git import Git


import zorg.buildbot.commands.LitTestCommand as lit_test_command
import zorg.buildbot.util.artifacts as artifacts
import zorg.buildbot.util.phasedbuilderutils as phased_builder_utils

from zorg.buildbot.commands.LitTestCommand import LitTestCommand

reload(lit_test_command)
reload(artifacts)
reload(phased_builder_utils)

def getLibcxxWholeTree(f, src_root):
    llvm_path = src_root
    libcxx_path = properties.WithProperties(
        '%(builddir)s/llvm/projects/libcxx')
    libcxxabi_path = properties.WithProperties(
        '%(builddir)s/llvm/projects/libcxxabi')
    boost_path = properties.WithProperties(
        '%(builddir)s/boost')

    mode = 'full'
    method = 'clean'
    f = phased_builder_utils.SVNCleanupStep(f, llvm_path)
    f.addStep(SVN(name='svn-llvm',
                  mode=mode,
                  method=method,
                  repourl='http://llvm.org/svn/llvm-project/llvm/trunk',
                  workdir=llvm_path))
    f.addStep(SVN(name='svn-libcxx',
                  mode=mode,
                  method=method,
                  repourl='http://llvm.org/svn/llvm-project/libcxx/trunk',
                  workdir=libcxx_path))
    f.addStep(SVN(name='svn-libcxxabi',
                  mode=mode,
                  method=method,
                  repourl='http://llvm.org/svn/llvm-project/libcxxabi/trunk',
                  workdir=libcxxabi_path))
    f.addStep(Git(name='git-boost',
                  mode='full',
                  method='fresh',
                  submodules=True,
                  repourl='git@github.com:boostorg/boost.git',
                  branch='master',
                  workdir=boost_path))

    return f

def get_libs_with_tests():
    return [
            "smart_ptr",
            "flyweight",
            "conversion",
            "bimap",
            "container",
            "dll",
            "wave",
            "pool",
            "type_traits",
            "foreach",
            "proto",
            "chrono",
            "multiprecision",
            "msm",
            "test",
            "multi_index",
            "assign",
            "coroutine",
            "graph_parallel",
            "timer",
            "predef",
            "tuple",
            "functional",
            "intrusive",
            "iterator",
            "integer",
            "coroutine2",
            "endian",
            "phoenix",
            "convert",
            "algorithm",
            "throw_exception",
            "bind",
            "tr1",
            "xpressive",
            "ratio",
            "regex",
            "property_tree",
            "program_options",
            "graph",
            "statechart",
            "asio",
            "qvm",
            "circular_buffer",
            "any",
            "locale",
            "system",
            "random",
            "assert",
            "format",
            "iostreams",
            "mpi",
            "signals",
            "uuid",
            "exception",
            "gil",
            "utility",
            "accumulators",
            "context",
            "polygon",
            "core",
            "sort",
            "io",
            "parameter",
            "filesystem",
            "ptr_container",
            "geometry",
            "preprocessor",
            "function",
            "vmd",
            "range",
            "units",
            "scope_exit",
            "typeof",
            "heap",
            "detail",
            "metaparse",
            "function_types",
            "type_erasure",
            "tti",
            "lambda",
            "crc",
            "date_time",
            "variant",
            "interprocess",
            "tokenizer",
            "fusion",
            "unordered",
            "move",
            "winapi",
            "thread",
            "hana",
            "optional",
            "config",
            "log",
            "multi_array",
            "icl",
            "math",
            "align",
            "property_map",
            "spirit",
            "atomic",
            "type_index",
            "serialization",
            "logic",
            "signals2",
            "lexical_cast",
            "array",
            "lockfree",
            "python",
            "local_function",
            "compute",
            "mpl",
            "rational"]

def getLibcxxBoostBuilder(f=None, env={}):
    if f is None:
        f = buildbot.process.factory.BuildFactory()

    # Determine the build directory.
    f.addStep(buildbot.steps.shell.SetProperty(
        name="get_builddir",
        command=["pwd"],
        property="builddir",
        description="set build dir",
        workdir="."))

    src_root = properties.WithProperties('%(builddir)s/llvm')
    build_path = properties.WithProperties('%(builddir)s/build')
    boost_src_root = properties.WithProperties('%(builddir)s/boost')
    boost_test_root = properties.WithProperties('%(builddir)s/boost/status')
    boost_build_path = properties.WithProperties('%(builddir)s/boost-build')
    f = getLibcxxWholeTree(f, src_root)

    # Nuke/remake build directory and run CMake
    f.addStep(buildbot.steps.shell.ShellCommand(
        name='rm.builddir', command=['rm', '-rf', build_path],
        haltOnFailure=False, workdir=src_root))
    f.addStep(buildbot.steps.shell.ShellCommand(
        name='make.builddir', command=['mkdir', build_path],
        haltOnFailure=True, workdir=src_root))
    f.addStep(buildbot.steps.shell.ShellCommand(
        name='rm.boost.builddir', command=['rm', '-rf', boost_build_path],
        haltOnFailure=False, workdir=src_root))
    f.addStep(buildbot.steps.shell.ShellCommand(
        name='make.boost.builddir', command=['mkdir', boost_build_path],
        haltOnFailure=True, workdir=src_root))
    f.addStep(buildbot.steps.shell.ShellCommand(
        name='cmake', command=['cmake', src_root],
        haltOnFailure=True, workdir=build_path, env=env))

    # Build libcxxabi
    jobs_flag = properties.WithProperties('-j%(jobs)s')
    f.addStep(buildbot.steps.shell.ShellCommand(
              name='build.libcxxabi', command=['make', jobs_flag, 'cxxabi'],
              haltOnFailure=True, workdir=build_path))

    # Build libcxx
    f.addStep(buildbot.steps.shell.ShellCommand(
              name='build.libcxx', command=['make', jobs_flag, 'cxx'],
              haltOnFailure=True, workdir=build_path))

    f.addStep(buildbot.steps.shell.ShellCommand(
        name='build.libcxxexperimental',
        command=['make', jobs_flag, 'cxx_experimental'],
        haltOnFailure=True, workdir=build_path))

    # Configure Boost
    b2_path = boost_path = properties.WithProperties(
        '%(builddir)s/boost/b2')
    compile_args_str = 'cxxflags=-std=c++11 -nostdinc++ -cxx-isystem %(builddir)s/llvm/projects/libcxx/include/ -Wno-unused-command-line-argument '
    build_args = ['-ftemplate-backtrace-limit=0']
    test_args = ['-Wno-unused-local-typedef',
                 '-Wno-unused-const-variable',
                 '-Wno-#pragma-messages',
                 '-Wno-unused-private-field',
                 '-Wno-missing-braces',
                 '-Wno-unused-variable',
                 '-Wno-c99-extensions',
                 '-Wno-variadic-macros',
                 '-w']

    build_compile_args = properties.WithProperties(
        str(compile_args_str) + ' '.join(build_args))
    test_compile_args = properties.WithProperties(
        str(compile_args_str) + ' '.join(test_args))
    libcxx_link_args = properties.WithProperties(
        'linkflags=-stdlib=libc++ -L%(builddir)s/build/lib/ -Wl,-rpath,%(builddir)s/build/lib/')
    b2_cmd = [b2_path, jobs_flag, 'toolset=clang', build_compile_args, libcxx_link_args]
    b2_test_cmd = [b2_path, jobs_flag, 'toolset=clang', test_compile_args, libcxx_link_args]

    # Bootstrap
    f.addStep(buildbot.steps.shell.ShellCommand(
        name='boost.bootstrap', command=['./bootstrap.sh', '--with-toolset=clang'],
        haltOnFailure=True, workdir=boost_src_root, env=env))

    # Clean
    f.addStep(buildbot.steps.shell.ShellCommand(
        name='boost.b2.clean', command=list(b2_cmd) + ['clean'],
        haltOnFailure=True, workdir=boost_src_root, env=env))

    # Generate headers
    f.addStep(buildbot.steps.shell.ShellCommand(
        name='boost.b2.headers', command=list(b2_cmd) + ['headers'],
        haltOnFailure=True, workdir=boost_src_root, env=env))

    # Build the libraries
    f.addStep(buildbot.steps.shell.ShellCommand(
        name='boost.b2.build', command=b2_cmd,
        haltOnFailure=False, workdir=boost_src_root, env=env))

    # Run the test suite
    for lib in get_libs_with_tests():
        lib_regex = '%(builddir)s/boost/libs/' + lib + '/test'
        f.addStep(buildbot.steps.shell.ShellCommand(
            name='boost.b2.test.%s' % lib, command=b2_test_cmd,
            haltOnFailure=True, workdir=properties.WithProperties(lib_regex), env=env))

    return f
