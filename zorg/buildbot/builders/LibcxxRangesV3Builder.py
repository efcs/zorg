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
    ranges_path = properties.WithProperties(
        '%(builddir)s/ranges')

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
    f.addStep(Git(name='git-rangesv3',
                  mode='full',
                  method='fresh',
                  repourl='https://github.com/ericniebler/range-v3.git',
                  workdir=ranges_path))

    return f


def getLibcxxRangesV3Builder(f=None, env={}):
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
    ranges_src_root = properties.WithProperties('%(builddir)s/ranges')
    ranges_build_path = properties.WithProperties('%(builddir)s/ranges-build')
    f = getLibcxxWholeTree(f, src_root)

    # Nuke/remake build directory and run CMake
    f.addStep(buildbot.steps.shell.ShellCommand(
        name='rm.builddir', command=['rm', '-rf', build_path],
        haltOnFailure=False, workdir=src_root))
    f.addStep(buildbot.steps.shell.ShellCommand(
        name='make.builddir', command=['mkdir', build_path],
        haltOnFailure=True, workdir=src_root))
    f.addStep(buildbot.steps.shell.ShellCommand(
        name='rm.ranges.builddir', command=['rm', '-rf', ranges_build_path],
        haltOnFailure=False, workdir=src_root))
    f.addStep(buildbot.steps.shell.ShellCommand(
        name='make.ranges.builddir', command=['mkdir', ranges_build_path],
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

    # Configure Ranges
    libcxx_compile_args = properties.WithProperties(
        '-DCMAKE_CXX_FLAGS=-nostdinc++ -cxx-isystem %(builddir)s/llvm/projects/libcxx/include/ -Wno-unused-command-line-argument')
    libcxx_link_args = properties.WithProperties(
        '-stdlib=libc++ -L%(builddir)s/build/lib/ -Wl,-rpath,%(builddir)s/build/lib/')
    cmake_flags = [libcxx_compile_args]
    env_cp = dict(env)
    env_cp.update({'LDFLAGS': libcxx_link_args})
    f.addStep(buildbot.steps.shell.ShellCommand(
        name='cmake.ranges', command=['cmake', libcxx_compile_args, ranges_src_root],
        haltOnFailure=True, workdir=ranges_build_path, env=env_cp))

    f.addStep(buildbot.steps.shell.ShellCommand(
              name='build.ranges', command=['make', jobs_flag],
              haltOnFailure=True, workdir=ranges_build_path))
    f.addStep(buildbot.steps.shell.ShellCommand(
              name='test.ranges', command=['make', jobs_flag, 'test'],
              haltOnFailure=True, workdir=ranges_build_path))
    return f