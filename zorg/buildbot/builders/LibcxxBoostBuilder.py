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
from buildbot.status.builder import SUCCESS, WARNINGS, FAILURE

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
    method = 'fresh'
    f.addStep(Git(name='git-llvm',
                  mode=mode,
                  method=method,
                  progress=True,
                  repourl='http://llvm.org/git/llvm.git',
                  workdir=llvm_path))
    f.addStep(Git(name='git-libcxx',
                  mode=mode,
                  method=method,
                  progress=True,
                  repourl='http://llvm.org/git/libcxx.git',
                  workdir=libcxx_path))
    f.addStep(Git(name='git-libcxxabi',
                  mode=mode,
                  method=method,
                  progress=True,
                  repourl='http://llvm.org/git/libcxxabi.git',
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
            ("smart_ptr", False),
            ("flyweight", False),
            ("conversion", False),
            ("bimap", False),
            ("container", False),
            ("dll", True),
            ("wave", True),
            ("pool", False),
            ("type_traits", False),
            ("foreach", False),
            ("proto", True),
            ("chrono", False),
            ("multiprecision", False),
            ("msm", False),
            ("test", False),
            ("multi_index", False),
            ("assign", True),
            ("coroutine", False),
            ("graph_parallel", False),
            ("timer", False),
            ("predef", False),
            ("tuple", False),
            ("functional", False),
            ("intrusive", False),
            ("iterator", True),
            ("integer", False),
            ("coroutine2", False),
            ("endian", False),
            ("phoenix", False),
            ("convert", False),
            ("algorithm", False),
            ("throw_exception", False),
            ("bind", False),
            ("tr1", True),
            ("xpressive", False),
            ("ratio", False),
            ("regex", False),
            ("property_tree", False),
            ("program_options", False),
            ("graph", False),
            ("statechart", True),
            ("asio", False),
            ("qvm", False),
            ("circular_buffer", False),
            ("any", False),
            ("locale", False),
            ("system", False),
            ("random", True),
            ("assert", False),
            ("format", False),
            ("iostreams", True),
            ("mpi", False),
            ("signals", False),
            ("uuid", True),
            ("exception", False),
            ("gil", True),
            ("utility", True),
            ("accumulators", True),
            ("context", False),
            ("polygon", False),
            ("core", False),
            ("sort", False),
            ("io", True),
            ("parameter", False),
            ("filesystem", False),
            ("ptr_container", True),
            ("geometry", False),
            ("preprocessor", False),
            ("function", False),
            ("vmd", True),
            ("range", False),
            ("units", False),
            ("scope_exit", False),
            ("typeof", False),
            ("heap", False),
            ("detail", False),
            ("metaparse", False),
            ("function_types", True),
            ("type_erasure", False),
            ("tti", False),
            ("lambda", False),
            ("crc", False),
            ("variant", False),
            ("interprocess", False),
            ("tokenizer", False),
            ("fusion", False),
            ("unordered", False),
            ("move", False),
            ("winapi", False),
            ("thread", False),
            ("hana", False),
            ("optional", False),
            ("config", False),
            ("log", False),
            ("multi_array", False),
            ("icl", False),
            ("math", False),
            ("align", False),
            ("property_map", False),
            ("spirit", True),
            ("atomic", False),
            ("type_index", True),
            ("serialization", False),
            ("logic", False),
            ("signals2", False),
            ("lexical_cast", True),
            ("array", False),
            ("lockfree", False),
            ("python", False),
            ("local_function", True),
            ("compute", True),
            ("mpl", False),
            ("rational", False)]

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
    boost_include_path = properties.WithProperties(
        '%(builddir)s/boost/boost'
    )
    boost_lib_path = properties.WithProperties(
        '%(builddir)s/boost/boost/stage/lib'
    )
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
        name='cmake', command=['cmake', '-DCMAKE_BUILD_TYPE=RELWITHDEBINFO', src_root],
        haltOnFailure=True, workdir=build_path, env=env))

    # Build libcxxabi
    jobs_flag = '-j12' #properties.WithProperties('-j%(jobs)s')
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
    env = dict(env)
    env['LD_LIBRARY_PATH'] = boost_lib_path
    env['LIBRARY_PATH'] = boost_lib_path
    b2_path = boost_path = properties.WithProperties(
        '%(builddir)s/boost/b2')
    compile_args_str = 'cxxflags=-std=c++14 -nostdinc++ -cxx-isystem %(builddir)s/llvm/projects/libcxx/include/ -Wno-unused-command-line-argument '
    build_args = ['-ftemplate-backtrace-limit=0']
    test_args = ['-I%(builddir)s/boost/']
    test_args += ['-Wno-unused-local-typedef',
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
    for lib, expect_fail in get_libs_with_tests():
        decode_rc = {0:SUCCESS}
        if expect_fail:
            decode_rc = {0:FAILURE, 1:WARNINGS}
        expect_pass = not expect_fail
        lib_regex = '%(builddir)s/boost/libs/' + lib + '/test'
        f.addStep(buildbot.steps.shell.ShellCommand(
            name='boost.b2.test.%s' % lib, command=b2_test_cmd,
            haltOnFailure=False, warnOnFailure=expect_fail,
            flunkOnFailure=expect_pass, decodeRC=decode_rc,
            workdir=properties.WithProperties(lib_regex), env=env))

    return f
