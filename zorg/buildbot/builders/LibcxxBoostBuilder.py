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
                  workdir=boost_path))

    return f


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

    libcxx_compile_args = properties.WithProperties(
        'cxxflags=-std=c++14 -nostdinc++ -cxx-isystem %(builddir)s/llvm/projects/libcxx/include/ -Wno-unused-command-line-argument')
    libcxx_link_args = properties.WithProperties(
        'linkflags=-stdlib=libc++ -L%(builddir)s/build/lib/ -Wl,-rpath,%(builddir)s/build/lib/')

    f.addStep(buildbot.steps.shell.ShellCommand(
        name='boost.bootstrap', command=['./bootstrap.sh', '--with-toolset=clang'],
        haltOnFailure=True, workdir=boost_src_root, env=env))
    f.addStep(buildbot.steps.shell.ShellCommand(
        name='boost.b2.clean', command=['./b2', jobs_flag, 'toolset=clang', libcxx_compile_args, libcxx_link_args, 'clean'],
        haltOnFailure=True, workdir=boost_src_root, env=env))
    f.addStep(buildbot.steps.shell.ShellCommand(
        name='boost.b2.headers', command=['./b2', jobs_flag, 'toolset=clang', libcxx_compile_args, libcxx_link_args, 'headers'],
        haltOnFailure=True, workdir=boost_src_root, env=env))

    f.addStep(buildbot.steps.shell.ShellCommand(
        name='boost.b2.build', command=['./b2', jobs_flag, 'toolset=clang', libcxx_compile_args, libcxx_link_args],
        haltOnFailure=False, workdir=boost_src_root, env=env))

    f.addStep(buildbot.steps.shell.ShellCommand(
        name='boost.b2.test', command=['./../b2', jobs_flag, 'toolset=clang', libcxx_compile_args, libcxx_link_args],
        haltOnFailure=True, workdir=boost_test_root, env=env))

    return f
"""
    libcxx_compile_args = properties.WithProperties(
        '-DCMAKE_CXX_FLAGS=-nostdinc++ -cxx-isystem %(builddir)s/llvm/projects/libcxx/include/ -Wno-unused-command-line-argument')
    libcxx_link_args = properties.WithProperties(
        '-stdlib=libc++ -L%(builddir)s/build/lib/ -Wl,-rpath,%(builddir)s/build/lib/')
    cmake_flags = [libcxx_compile_args]
    env_cp = dict(env)
    env_cp.update({'LDFLAGS': libcxx_link_args})
    f.addStep(buildbot.steps.shell.ShellCommand(
        name='cmake.boost', command=['cmake', libcxx_compile_args, boost_src_root],
        haltOnFailure=True, workdir=boost_build_path, env=env_cp))

    f.addStep(buildbot.steps.shell.ShellCommand(
              name='build.boost', command=['make', jobs_flag],
              haltOnFailure=True, workdir=boost_build_path))
    f.addStep(buildbot.steps.shell.ShellCommand(
              name='test.boost', command=['make', jobs_flag, 'test'],
              haltOnFailure=True, workdir=boost_build_path))
"""

