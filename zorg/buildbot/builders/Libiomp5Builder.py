import os

import buildbot
import buildbot.process.factory
from buildbot.steps.source import SVN
from buildbot.steps.shell import ShellCommand
from buildbot.steps.shell import WarningCountingShellCommand
from buildbot.process.properties import WithProperties

import zorg.buildbot.commands as commands
import zorg.buildbot.commands.LitTestCommand as lit_test_command


def getLibompCMakeBuildFactory(clean=True, env=None, test=True, c_compiler="gcc", cxx_compiler="g++"):

    # Prepare environmental variables. Set here all env we want everywhere.
    merged_env = {
        'TERM' : 'dumb' # Make sure Clang doesn't use color escape sequences.
                 }
    if env is not None:
        # Overwrite pre-set items with the given ones, so user can set anything.
        merged_env.update(env)

    openmp_srcdir = "openmp.src"
    openmp_builddir = "openmp.build"
    llvm_srcdir = "llvm.src"
    llvm_builddir = "llvm.build"

    f = buildbot.process.factory.BuildFactory()

    # Get libomp
    f.addStep(SVN(name='svn-libomp',
                  mode='update',
                  baseURL='http://llvm.org/svn/llvm-project/openmp/',
                  defaultBranch='trunk',
                  workdir=openmp_srcdir))

    # Get llvm to build llvm-lit
    f.addStep(SVN(name='svn-llvm',
                  mode='update',
                  baseURL='http://llvm.org/svn/llvm-project/llvm/',
                  defaultBranch='trunk',
                  workdir=llvm_srcdir))

    # Clean directory, if requested.
    if clean:
        f.addStep(ShellCommand(name="clean",
                               command=["rm", "-rf",openmp_builddir,llvm_builddir],
                               warnOnFailure=True,
                               description=["clean"],
                               workdir='.',
                               env=merged_env))

    # CMake llvm
    f.addStep(ShellCommand(name='cmake llvm',
                           command=["cmake", "../"+llvm_srcdir,
                                    "-DCMAKE_C_COMPILER="+c_compiler,
                                    "-DCMAKE_CXX_COMPILER="+cxx_compiler],
                           haltOnFailure=True,
                           description='cmake llvm',
                           workdir=llvm_builddir,
                           env=merged_env))

    # Make llvm utils
    f.addStep(WarningCountingShellCommand(name='make llvm utils build',
                                          command=['make', 'LLVMX86Utils', '-j8'],
                                          haltOnFailure=True,
                                          description='make llvm utils build',
                                          workdir=llvm_builddir,
                                          env=merged_env))

    # Add llvm-lit to PATH
    merged_env.update( { 'PATH' : WithProperties("${PATH}:" + "%(workdir)s/" + llvm_builddir + "/bin")} )

    # CMake libomp
    f.addStep(ShellCommand(name='cmake libomp',
                           command=["cmake", "../"+openmp_srcdir,
                                    "-DCMAKE_C_COMPILER="+c_compiler,
                                    "-DCMAKE_CXX_COMPILER="+cxx_compiler],
                           haltOnFailure=True,
                           description='cmake libomp',
                           workdir=openmp_builddir,
                           env=merged_env))

    # Make libomp
    f.addStep(WarningCountingShellCommand(name='make libomp build',
                                          command=['make'],
                                          haltOnFailure=True,
                                          description='make libomp build',
                                          workdir=openmp_builddir,
                                          env=merged_env))

    # Test, if requested
    if test:
        f.addStep(lit_test_command.LitTestCommand(name='make check-libomp',
                                                  command=['make', 'check-libomp'],
                                                  haltOnFailure=True,
                                                  description=["make check-libomp"],
                                                  descriptionDone=["build checked"],
                                                  workdir=openmp_builddir,
                                                  env=merged_env))

    return f
