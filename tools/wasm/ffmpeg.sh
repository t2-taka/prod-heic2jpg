#!/bin/bash
set -euo pipefail
cd "$1"
node_dir="${WASM_NODE_DIR:-}"
if command -v cygpath >/dev/null && [ -n "$node_dir" ]; then node_dir="$(cygpath -u "$node_dir")"; fi
export PATH="$PWD/bin:/usr/bin:$node_dir:$PATH"

export PKG_CONFIG_PATH="$PWD/prefix/lib/pkgconfig"
export EM_PKG_CONFIG_PATH="$PKG_CONFIG_PATH"
prefix="$PWD/prefix"
if command -v cygpath >/dev/null; then prefix="$(cygpath -m "$prefix")"; fi
cd ffmpeg
./configure --target-os=none --arch=x86_32 --enable-cross-compile --disable-asm --disable-stripping --disable-programs --disable-doc --disable-debug --disable-runtime-cpudetect --disable-autodetect --disable-network --disable-protocols --enable-protocol=file --disable-devices --disable-pthreads --disable-w32threads --disable-os2threads --nm=emnm --ar=emar --ranlib=emranlib --cc=emcc --cxx=em++ --objcc=emcc --dep-cc=emcc --extra-cflags="-I$prefix/include -O3" --extra-ldflags="-L$prefix/lib" --enable-gpl --enable-libx264 --enable-libmp3lame
make -j"${BUILD_JOBS:-8}" > ../ffmpeg-build.log 2>&1