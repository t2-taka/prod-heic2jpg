"""Rebuild the vendored media engines from pinned upstream sources.
Requires an activated Emscripten 3.1.74 SDK, CMake, Ninja and a POSIX shell
with make, pkgconf and binutils (MSYS2 on Windows). No npm install scripts.
"""
import argparse
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess

REPO = Path(__file__).resolve().parents[2]
SOURCES = {
    'libheif': ('https://github.com/strukturag/libheif.git', 'f81f28ac014b1c28dee483ac45b72c6b05bc421a'),
    'libde265': ('https://github.com/strukturag/libde265.git', 'ba62bf4cfb3242f3bf0a45617ff09e35236e4d82'),
    'ffmpeg': ('https://github.com/FFmpeg/FFmpeg.git', '19feb712f5c1821d8a3fa1ad63c5bd2e3b9672eb'),
    'x264': ('https://code.videolan.org/videolan/x264.git', '0480cb05fa188d37ae87e8f4fd8f1aea3711f7ee'),
    'lame': ('https://github.com/ffmpegwasm/lame.git', '2badea1974ae36cb8312afe99cff1e6b3b5decee'),
}
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--build-dir', type=Path, default=REPO/'tmp/security-build')
p.add_argument('--emsdk', type=Path)
p.add_argument('--bash', default='bash')
p.add_argument('--ninja', default=shutil.which('ninja'))
p.add_argument('--jobs', type=int, default=8)
p.add_argument('--link-only', action='store_true', help='Reuse already-built FFmpeg archives')
p.add_argument('--target', choices=['heif', 'ffmpeg', 'all'], default='all')
a = p.parse_args()
b = a.build_dir.resolve()
sdk = (a.emsdk or b/'emsdk').resolve()
python = sdk/'python/3.13.3_64bit/python.exe' if os.name == 'nt' else Path(shutil.which('python3'))
em = sdk/'upstream/emscripten'
output = REPO/'HEIC2JPG/wwwroot/lib'
env = dict(os.environ, EM_CONFIG=str(sdk/'.emscripten'), BUILD_JOBS=str(a.jobs), WASM_NODE_DIR=Path(shutil.which('node')).parent.as_posix())
b.mkdir(parents=True, exist_ok=True)

def run(args, cwd=REPO, **kwargs):
    print('>', shlex.join(map(str,args)), flush=True)
    return subprocess.run([x.as_posix() if isinstance(x,Path) else str(x) for x in args], cwd=cwd, env=env, check=True, **kwargs)

def source(name):
    url, commit = SOURCES[name]
    dest = b/name
    if not (dest/'.git').is_dir():
        run(['git','init',dest])
        run(['git','-C',dest,'remote','add','origin',url])
        run(['git','-C',dest,'fetch','--depth','1','origin',commit])
        run(['git','-C',dest,'checkout','--detach','FETCH_HEAD'])
    actual = subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'], text=True).strip()
    if actual != commit:
        raise RuntimeError(f'{name}: expected {commit}, found {actual}')
    return dest

def cmake(name, src, flags):
    dest = b/(name+'-build')
    args = ['cmake','-S',src,'-B',dest,'-G','Ninja',f'-DCMAKE_TOOLCHAIN_FILE={em.as_posix()}/cmake/Modules/Platform/Emscripten.cmake','-DCMAKE_BUILD_TYPE=Release']
    if a.ninja: args += [f'-DCMAKE_MAKE_PROGRAM={a.ninja}']
    run(args+flags)
    run(['cmake','--build',dest,'--parallel',a.jobs])
    return dest

def link(args):
    run([python,em/'emcc.py']+args)
    js = Path(args[-1])
    js.write_text(js.read_text(encoding='utf-8'),encoding='utf-8',newline='\n')

if a.target in ('heif','all'):
    de265 = source('libde265')
    heif = source('libheif')
    de = cmake('de265', de265, ['-DBUILD_SHARED_LIBS=OFF','-DENABLE_SIMD=OFF','-DENABLE_DECODER=OFF','-DENABLE_ENCODER=OFF','-DENABLE_SDL=OFF',f'-DCMAKE_INSTALL_PREFIX={(b/"prefix").as_posix()}'])
    run(['cmake','--install',de])
    disabled = ['X265','X264','AOM_DECODER','AOM_ENCODER','OpenH264_DECODER','FFMPEG_DECODER','UNCOMPRESSED_CODEC','JPEG_DECODER','JPEG_ENCODER','OpenJPEG_DECODER','OpenJPEG_ENCODER','LIBSHARPYUV','EXAMPLES','GDK_PIXBUF']
    hb = cmake('heif', heif, ['-DBUILD_SHARED_LIBS=OFF','-DENABLE_MULTITHREADING_SUPPORT=OFF','-DENABLE_PARALLEL_TILE_DECODING=OFF','-DENABLE_PLUGIN_LOADING=OFF','-DBUILD_TESTING=OFF','-DBUILD_DOCUMENTATION=OFF']+[f'-DWITH_{x}=OFF' for x in disabled]+[f'-DLIBDE265_INCLUDE_DIR={(b/"prefix/include").as_posix()}',f'-DLIBDE265_LIBRARY={(b/"prefix/lib/libde265.a").as_posix()}'])
    nm = sdk/('upstream/bin/llvm-nm.exe' if os.name=='nt' else 'upstream/bin/llvm-nm')
    symbols = subprocess.check_output([str(nm),str(hb/'libheif/libheif.a'),'--format=just-symbols'],text=True)
    exports = sorted(set('_'+s for s in symbols.splitlines() if s.startswith(('heif_','de265_')) and not s.endswith(':')))+['_free','_malloc','_memcpy']
    (b/'heif-exports.json').write_text(json.dumps(exports))
    link(['-Wl,--whole-archive',str(hb/'libheif/libheif.a'),'-Wl,--no-whole-archive',str(b/'prefix/lib/libde265.a'),'-lembind',f'-sEXPORTED_FUNCTIONS=@{b/"heif-exports.json"}','-sMODULARIZE','-sEXPORT_NAME=libheif','-sWASM_ASYNC_COMPILATION=1','-sALLOW_MEMORY_GROWTH','-sMAXIMUM_MEMORY=536870912','-sDYNAMIC_EXECUTION=0','-sENVIRONMENT=web,worker,node','--post-js',str(heif/'post.js'),'-O3','-o',str(output/'libheif/libheif.js')])

if a.target in ('ffmpeg','all'):
    for name in ['x264','lame','ffmpeg']: source(name)
    patch = Path(__file__).with_name('ffmpeg-cli.patch')
    applied = subprocess.run(['git','-C',str(b/'ffmpeg'),'apply','--reverse','--check',str(patch)],capture_output=True).returncode == 0
    if not applied: run(['git','-C',b/'ffmpeg','apply',patch])
    # Windows Python cannot execute extensionless POSIX launcher scripts.
    wrappers = b/'bin'
    wrappers.mkdir(exist_ok=True)
    for tool in ['emcc','em++','emar','emranlib']:
        f = wrappers/tool
        f.write_text('#!/bin/sh\nexec '+shlex.quote(str(python).replace('\\','/'))+' '+shlex.quote(str(em/(tool+'.py')).replace('\\','/'))+' "$@"\n',newline='\n')
        f.chmod(0o755)
    nm = sdk/('upstream/bin/llvm-nm.exe' if os.name=='nt' else 'upstream/bin/llvm-nm')
    (wrappers/'emnm').write_text('#!/bin/sh\nexec '+shlex.quote(nm.as_posix())+' "$@"\n',newline='\n')
    (wrappers/'emnm').chmod(0o755)
    for script in ([] if a.link_only else ['codecs.sh','ffmpeg.sh']):
        # Scripts receive their absolute working directory as an argument.
        run([a.bash,Path(__file__).with_name(script),b],cwd=b)
    cli = b/'ffmpeg/fftools'
    libs = ['avdevice','avfilter','avformat','avcodec','swresample','swscale','avutil','postproc']
    args = ['-I'+str(b/'ffmpeg'),'-I'+str(cli),'-I'+str(b/'prefix/include'),'-L'+str(b/'prefix/lib')]
    args += ['-L'+str(b/'ffmpeg'/('lib'+lib)) for lib in libs]
    args += [str(cli/(name+'.c')) for name in ['cmdutils','ffmpeg','ffmpeg_filter','ffmpeg_hw','ffmpeg_mux','ffmpeg_opt','opt_common','ffprobe']]
    args += ['-l'+lib for lib in libs]+['-lx264','-lmp3lame','-O3','-Wno-deprecated-declarations','-Wno-parentheses','-Wno-pointer-sign','-Wno-switch','-Wno-implicit-const-int-float-conversion','-sENVIRONMENT=web,worker,node','-sWASM_BIGINT','-sSTACK_SIZE=5242880','-sMODULARIZE','-sEXPORT_NAME=createFFmpegCore','-sINITIAL_MEMORY=33554432','-sALLOW_MEMORY_GROWTH','-sMAXIMUM_MEMORY=2147483648','-sDYNAMIC_EXECUTION=0','-sEXPORTED_FUNCTIONS=_ffmpeg,_abort,_malloc,_free,_ffprobe','-sEXPORTED_RUNTIME_METHODS=FS,setValue,getValue,UTF8ToString,lengthBytesUTF8,stringToUTF8','-lworkerfs.js','--pre-js',str(Path(__file__).with_name('ffmpeg-bind.js')),'-o',str(output/'ffmpeg/ffmpeg-core.js')]
    link(args)