#!/usr/bin/env bash

set -x
set -e
set -u

echo @@@BUILD_STEP tsan analyze@@@
BIN=$(mktemp -t tsan_exe.XXXXXXXX)
echo "int main() {return 0;}" | clang -x c++ - -fsanitize=thread -O2 -o ${BIN}
./check_analyze.sh ${BIN} || echo @@@STEP_FAILURE@@@

echo @@@BUILD_STEP tsan racecheck_unittest@@@
SUPPRESS_WARNINGS="-Wno-format-security -Wno-null-dereference -Wno-unused-private-field"
EXTRA_COMPILER_FLAGS="-fsanitize=thread -DTHREAD_SANITIZER -fPIC -g -O2 $SUPPRESS_WARNINGS"
(cd $RACECHECK_UNITTEST_PATH && \
make clean && \
OMIT_DYNAMIC_ANNOTATIONS_IMPL=1 make l64 -j16 CC=clang CXX=clang++ LD=clang++ LDOPT="-fsanitize=thread" OMIT_CPP0X=1 EXTRA_CFLAGS="$EXTRA_COMPILER_FLAGS" EXTRA_CXXFLAGS="$EXTRA_COMPILER_FLAGS" && \
bin/racecheck_unittest-linux-amd64-O0 --gtest_filter=-*Ignore*:*Suppress*:*EnableRaceDetectionTest*:*Rep*Test*:*NotPhb*:*Barrier*:*Death*:*PositiveTests_RaceInSignal*:StressTests.FlushStateTest:*Mmap84GTest:*.LibcStringFunctions:LockTests.UnlockingALockHeldByAnotherThread:LockTests.UnlockTwice:PrintfTests.RaceOnPutsArgument)

#Ignore: ignores do not work yet
#Suppress: suppressions do not work yet
#EnableRaceDetectionTest: the annotation is not supported
#Rep*Test: uses inline assembly
#NotPhb: not-phb is not supported
#Barrier: pthread_barrier_t is not fully supported yet
#Death: there is some flakyness
#PositiveTests_RaceInSignal: signal() is not intercepted yet
#StressTests.FlushStateTest: uses suppressions
#Mmap84GTest: too slow, causes paging
#LockTests.UnlockingALockHeldByAnotherThread: causes tsan report and non-zero exit code
#LockTests.UnlockTwice: causes tsan report and non-zero exit code
#PrintfTests.RaceOnPutsArgument: seems to be an issue with tsan shadow eviction, lit tests contain a similar test and it passes

