import os

import buildbot
import buildbot.process.factory
from buildbot.steps.shell import SetProperty
from buildbot.steps.shell import ShellCommand
from buildbot.steps.slave import RemoveDirectory
from buildbot.steps.source import SVN
from buildbot.process.properties import Property
from buildbot.process.properties import WithProperties
from zorg.buildbot.builders.Util import getVisualStudioEnvironment
from zorg.buildbot.builders.Util import extractSlaveEnvironment
from zorg.buildbot.builders.Util import extractClangVersion
from zorg.buildbot.commands.NinjaCommand import NinjaCommand

def getSource(f,llvmTopDir='llvm'):
    f.addStep(SVN(name='svn-llvm',
                  mode='update', baseURL='http://llvm.org/svn/llvm-project/llvm/',
                  defaultBranch='trunk',
                  workdir=llvmTopDir))
    f.addStep(SVN(name='svn-clang',
                  mode='update', baseURL='http://llvm.org/svn/llvm-project/cfe/',
                  defaultBranch='trunk',
                  workdir='%s/tools/clang' % llvmTopDir))
    f.addStep(SVN(name='svn-lld',
                  mode='update', baseURL='http://llvm.org/svn/llvm-project/lld/',
                  defaultBranch='trunk',
                  workdir='%s/tools/lld' % llvmTopDir))
    f.addStep(SVN(name='svn-compiler-rt',
                  mode='update',
                  baseURL='http://llvm.org/svn/llvm-project/compiler-rt/',
                  defaultBranch='trunk',
                  workdir='%s/projects/compiler-rt' % llvmTopDir))
    return f

def getSanitizerWindowsBuildFactory(
            clean=False,
            cmake='cmake',

            # Default values for VS devenv and build configuration
            vs=r"""%VS120COMNTOOLS%""",
            config='Release',
            target_arch='x86',

            extra_cmake_args=[]):

    ############# PREPARING
    f = buildbot.process.factory.BuildFactory()

    # Kill any stale symbolizer processes for the last run. If there are any
    # stale processes, the build will fail during linking. This can happen to
    # any process, but it is most likely to happen to llvm-symbolizer if its
    # pipe isn't closed.
    taskkill_cmd = 'taskkill /f /im llvm-symbolizer.exe || exit /b 0'
    f.addStep(ShellCommand(name='taskkill',
                           description='kill stale processes',
                           command=['cmd', '/c', taskkill_cmd],
                           haltOnFailure=False))

    # Determine Slave Environment and Set MSVC environment.
    f.addStep(SetProperty(
        command=getVisualStudioEnvironment(vs, target_arch),
        extract_fn=extractSlaveEnvironment))

    f = getSource(f,'llvm')

    # Global configurations
    build_dir = 'build'

    ############# CLEANING
    cleanBuildRequested = lambda step: step.build.getProperty("clean") or clean
    f.addStep(RemoveDirectory(name='clean '+build_dir,
                dir=build_dir,
                haltOnFailure=False,
                flunkOnFailure=False,
                doStepIf=cleanBuildRequested
                ))

    f.addStep(ShellCommand(name='cmake',
                           command=[cmake, "-G", "Ninja", "../llvm",
                                    "-DCMAKE_BUILD_TYPE="+config,
                                    "-DLLVM_ENABLE_ASSERTIONS=ON"]
                                   + extra_cmake_args,
                           haltOnFailure=True,
                           workdir=build_dir,
                           env=Property('slave_env')))

    # Build compiler-rt first to speed up detection of Windows-specific
    # compiler-time errors in the sanitizer runtimes.
    f.addStep(NinjaCommand(name='build compiler-rt',
                           targets=['compiler-rt'],
                           haltOnFailure=True,
                           description='ninja compiler-rt',
                           workdir=build_dir,
                           env=Property('slave_env')))

    # Build Clang and LLD next so that most compilation errors occur in a build
    # step.
    f.addStep(NinjaCommand(name='build clang lld',
                           targets=['clang', 'lld'],
                           haltOnFailure=True,
                           description='ninja clang lld',
                           workdir=build_dir,
                           env=Property('slave_env')))

    # Only run sanitizer tests.
    # Don't build targets that are not required in order to speed up the cycle.
    for target in ['check-asan', 'check-asan-dynamic', 'check-sanitizer',
                   'check-cfi']:
      f.addStep(NinjaCommand(name='run %s' % target,
                             targets=[ target ],
                             haltOnFailure=False,
                             description='ninja %s' % target,
                             workdir=build_dir,
                             env=Property('slave_env')))

    return f
