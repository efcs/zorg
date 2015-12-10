import os

import buildbot
import buildbot.process.factory
import buildbot.steps.shell
import buildbot.process.properties as properties

from buildbot.steps.source.svn import SVN

import zorg.buildbot.commands.LitTestCommand as lit_test_command
import zorg.buildbot.util.artifacts as artifacts
import zorg.buildbot.util.phasedbuilderutils as phased_builder_utils

from zorg.buildbot.commands.LitTestCommand import LitTestCommand

reload(lit_test_command)
reload(artifacts)
reload(phased_builder_utils)

class LitTestConfiguration:
    def __init__(self, name, opts={}, paths=[]):
        self.name = name
        assert type(opts) is dict
        assert type(paths) is list
        self.opts = dict(opts)
        self.paths = list(paths)

def getLibcxxWholeTree(f, src_root):
    llvm_path = src_root
    libcxx_path = properties.WithProperties(
        '%(builddir)s/llvm/projects/libcxx')
    libcxxabi_path = properties.WithProperties(
        '%(builddir)s/llvm/projects/libcxxabi')

    mode = 'full'
    method = 'clean'
    f = phased_builder_utils.SVNCleanupStep(f, llvm_path)
    f.addStep(SVN(name='svn-llvm',
                  mode=mode,
                  method=method,
                  baseURL='http://llvm.org/svn/llvm-project/llvm/',
                  defaultBranch='trunk',
                  workdir=llvm_path))
    f.addStep(SVN(name='svn-libcxx',
                  mode=mode,
                  method=method,
                  baseURL='http://llvm.org/svn/llvm-project/libcxx/',
                  defaultBranch='trunk',
                  workdir=libcxx_path))
    f.addStep(SVN(name='svn-libcxxabi',
                  mode=mode,
                  method=method,
                  baseURL='http://llvm.org/svn/llvm-project/libcxxabi/',
                  defaultBranch='trunk',
                  workdir=libcxxabi_path))

    return f

def addTestSuite(litDesc, env={}):
    libcxxTestRoot = properties.WithProperties('%(builddir)s/llvm/projects/libcxx/test')
    litExecutable = properties.WithProperties('%(builddir)s/llvm/utils/lit/lit.py')

    # Specify the max number of threads using properties so LIT doesn't use
    # all the threads on the system.
    litCmd = ['%(builddir)s/llvm/utils/lit/lit.py',
              '-sv', '--show-unsupported', '--show-xfail', '--threads=%(jobs)s',
              '--param=libcxx_site_config=%(builddir)s/build/projects/libcxx/test/lit.site.cfg']

    for key in litDesc.opts:
        litCmd += [('--param=' + key + '=' + litDesc.opts[key]).strip()]
    litCmd += litDesc.paths
    if len(litDesc.paths) == 0:
        litCmd += ['.']
    litCmd = [properties.WithProperties(arg) for arg in litCmd]
    return LitTestCommand(
        name            = 'test.%s' % litDesc.name,
        command         = litCmd,
        description     = ['testing', litDesc.name],
        descriptionDone = ['test', litDesc.name],
        env             = env,
        workdir         = libcxxTestRoot)
    
    

def getLibcxxAndAbiBuilder(f=None, env={}, cmake_extra_opts={}, lit_invocations=[],
    enable_libcxxabi = True, generate_coverage=None):
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

    f = getLibcxxWholeTree(f, src_root)

    cmake_opts = []
    for key in cmake_extra_opts:
        cmake_opts.append('-D' + key + '=' + cmake_extra_opts[key])

    # Nuke/remake build directory and run CMake
    f.addStep(buildbot.steps.shell.ShellCommand(
        name='rm.builddir', command=['rm', '-rf', build_path],
        haltOnFailure=False, workdir=src_root))
    f.addStep(buildbot.steps.shell.ShellCommand(
        name='make.builddir', command=['mkdir', build_path],
        haltOnFailure=True, workdir=src_root))

    f.addStep(buildbot.steps.shell.ShellCommand(
        name='cmake', command=['cmake', src_root] + cmake_opts,
        haltOnFailure=True, workdir=build_path, env=env))

    # Build libcxxabi
    jobs_flag = properties.WithProperties('-j%(jobs)s')
    if enable_libcxxabi:
        f.addStep(buildbot.steps.shell.ShellCommand(
              name='build.libcxxabi', command=['make', jobs_flag, 'cxxabi'],
              haltOnFailure=True, workdir=build_path))

    # Build libcxx
    f.addStep(buildbot.steps.shell.ShellCommand(
              name='build.libcxx', command=['make', jobs_flag, 'cxx'],
              haltOnFailure=True, workdir=build_path))

    # Test libc++abi
    if enable_libcxxabi and not generate_coverage:
        f.addStep(LitTestCommand(
            name            = 'test.libcxxabi',
            command         = ['make', 'check-libcxxabi'],
            description     = ['testing', 'libcxxabi'],
            descriptionDone = ['test', 'libcxxabi'],
            workdir         = build_path))

    # Test libc++
    for inv in lit_invocations:
        f.addStep(addTestSuite(inv, env=env))
        
    if generate_coverage:
        coverage_path = properties.WithProperties(
            '%(builddir)s/build/projects/libcxx/test/coverage/test_coverage/')
        f.addStep(buildbot.steps.shell.ShellCommand(
            name            = 'generate.coverage',
            command         = ['make', jobs_flag, 'generate-libcxx-coverage'],
            env             = env,
            workdir         = build_path,
            haltOnFailure   = True))

        f.addStep(buildbot.steps.shell.ShellCommand(
            name            = 'copy.coverage',
            command         = ['cp', '-R', coverage_path, generate_coverage],
            workdir         = build_path,
            haltOnFailure   = True))
        
        f.addStep(buildbot.steps.shell.ShellCommand(
            name            = 'mark.coverage.new',
            command         = ['touch', '%s/new.lock' % generate_coverage],
            workdir         = build_path,
            haltOnFailure   = True))

    return f
