from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[2]/'HEIC2JPG/wwwroot'
specs=[
 ('libheif','1.23.6','LGPL-3.0-or-later','https://github.com/strukturag/libheif/blob/v1.23.6/COPYING','https://github.com/strukturag/libheif/tree/f81f28ac014b1c28dee483ac45b72c6b05bc421a',['lib/libheif/libheif.js','lib/libheif/libheif.wasm']),
 ('libde265','1.1.3','LGPL-3.0-or-later','https://github.com/strukturag/libde265/blob/v1.1.3/COPYING','https://github.com/strukturag/libde265/tree/ba62bf4cfb3242f3bf0a45617ff09e35236e4d82',[]),
 ('FFmpeg','5.1.10','GPL-2.0-or-later','https://github.com/FFmpeg/FFmpeg/blob/n5.1.10/COPYING.GPLv2','https://github.com/FFmpeg/FFmpeg/tree/19feb712f5c1821d8a3fa1ad63c5bd2e3b9672eb',['lib/ffmpeg/ffmpeg-core.js','lib/ffmpeg/ffmpeg-core.wasm']),
 ('x264','0.164 (0480cb0)','GPL-2.0-or-later','https://code.videolan.org/videolan/x264/-/blob/0480cb05fa188d37ae87e8f4fd8f1aea3711f7ee/COPYING','https://code.videolan.org/videolan/x264/-/tree/0480cb05fa188d37ae87e8f4fd8f1aea3711f7ee',[]),
 ('LAME','3.100','LGPL-2.0-or-later','https://github.com/ffmpegwasm/lame/blob/2badea1974ae36cb8312afe99cff1e6b3b5decee/COPYING','https://github.com/ffmpegwasm/lame/tree/2badea1974ae36cb8312afe99cff1e6b3b5decee',[]),
 ('@ffmpeg/ffmpeg','0.12.15','MIT','https://github.com/ffmpegwasm/ffmpeg.wasm/blob/main/LICENSE','https://registry.npmjs.org/@ffmpeg/ffmpeg/0.12.15',['lib/ffmpeg/ffmpeg.min.js','lib/ffmpeg/814.ffmpeg.js']),
 ('Bootstrap','5.3.8','MIT','https://github.com/twbs/bootstrap/blob/v5.3.8/LICENSE','https://registry.npmjs.org/bootstrap/5.3.8',['lib/bootstrap/dist/js/bootstrap.bundle.min.js','lib/bootstrap/dist/css/bootstrap.min.css']),
 ('JSZip','3.10.2','MIT OR GPL-3.0-or-later','https://github.com/Stuk/jszip/blob/v3.10.2/LICENSE.markdown','https://registry.npmjs.org/jszip/3.10.2',['lib/jszip/jszip.min.js']),
 ('HeroIcons','2.0.18','MIT','https://github.com/tailwindlabs/heroicons/blob/v2.0.18/LICENSE','https://github.com/tailwindlabs/heroicons/tree/v2.0.18',[])]
if b'5.1.10' not in (root/'lib/ffmpeg/ffmpeg-core.wasm').read_bytes():
 raise SystemExit('FFmpeg WASM must be rebuilt before recording its version')
if b'1.23.6' not in (root/'lib/libheif/libheif.wasm').read_bytes():
 raise SystemExit('libheif WASM must be rebuilt before recording its version')
packages=[]
for name,version,license,url,source,files in specs:
 packages.append(dict(name=name,version=version,license=license,licenseUrl=url,source=source,files={f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in files}))
(root/'vendor-manifest.json').write_text(json.dumps(dict(checkedOn='2026-10-23',packages=packages),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')