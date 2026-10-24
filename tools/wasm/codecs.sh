#!/bin/bash
set -euo pipefail
cd "$1"
node_dir="${WASM_NODE_DIR:-}"
if command -v cygpath >/dev/null && [ -n "$node_dir" ]; then node_dir="$(cygpath -u "$node_dir")"; fi
export PATH="$PWD/bin:/usr/bin:$node_dir:$PATH"
export CC=emcc CXX=em++ AR=emar RANLIB=emranlib NM=emnm
export STRINGS="$PWD/emsdk/upstream/bin/llvm-strings.exe"
export CFLAGS='-O3' CXXFLAGS='-O3'

export PKG_CONFIG_PATH="$PWD/prefix/lib/pkgconfig"
export EM_PKG_CONFIG_PATH="$PKG_CONFIG_PATH"
prefix="$PWD/prefix"
if command -v cygpath >/dev/null; then prefix="$(cygpath -m "$prefix")"; fi
cd x264
./configure --prefix="$prefix" --host=x86-gnu --cross-prefix= --enable-static --disable-cli --disable-asm --disable-thread --disable-opencl --bit-depth=8 --chroma-format=420
make -j"${BUILD_JOBS:-8}" > ../x264-build.log 2>&1
make install >> ../x264-build.log 2>&1
cd ../lame
if [ ! -f configure ]; then autoreconf -fi; fi
./configure --prefix="$prefix" --host=x86-gnu --disable-shared --enable-static --disable-frontend --disable-gtktest --disable-analyzer-hooks --disable-decoder
make -j"${BUILD_JOBS:-8}" > ../lame-build.log 2>&1
make install >> ../lame-build.log 2>&1