# Media engine builds

The shipped engines were built on Windows with Emscripten 3.1.74 (LLVM release
c2655005234810c7c42e02a18e4696554abe0352), CMake/Ninja, and MSYS2 make/pkgconf/binutils.
The SDK is a build dependency only; the application never loads its Node.js runtime.

`build.py` pins the full commits of libheif 1.23.6, libde265 1.1.3, FFmpeg 5.1.10,
x264 and LAME. `ffmpeg-cli.patch` adapts the current upstream FFmpeg CLI to the
ffmpeg.wasm interface: it was derived from ffmpegwasm/ffmpeg.wasm commit
f876f907c7e9b9bf51d4ed0b913a855a63ae63fc against FFmpeg n5.1.4 and applied to n5.1.10.
It does not replace n5.1.10's library sources with the older version.
`ffmpeg-bind.js` is the JS binding from the same ffmpeg.wasm commit (MIT).

## Rebuild on Windows

Use a separate ignored build directory, for example `tmp/security-build`.
Install Emscripten 3.1.74 there with emsdk and activate it without `--permanent`.
Install MSYS2 there, then install make, pkgconf, diffutils, binutils, autoconf,
automake and libtool using its pacman. CMake and Ninja must also be available.
No system-wide environment changes are required.

From the repository root (replace the paths to match your local tools):

```powershell
python tools/wasm/build.py --target all `
  --emsdk C:/path/to/emsdk `
  --bash C:/path/to/msys64/usr/bin/bash.exe `
  --ninja C:/path/to/ninja.exe
python tools/wasm/vendor-manifest.py
powershell -NoProfile -File HEIC2JPG/GenerateLicenses.ps1
node --test tests/security.test.cjs
```

The script retrieves and verifies the pinned source commits, then produces
`libheif.js`, `libheif.wasm`, `ffmpeg-core.js`, and `ffmpeg-core.wasm` directly
under `HEIC2JPG/wwwroot/lib/`. A fresh build directory is required when changing
source pins or compiler versions. `--target heif` / `--target ffmpeg` rebuild one
engine; `--link-only` reuses the FFmpeg archives for linker debugging.
Retain the generated static archives in `prefix/lib/` and `heif-build/libheif/`
if you need to relink the LGPL components with modified source.

The HEIC build contains only libde265 decoding, with plugin loading, extra
codecs and parallel decoding disabled, a 512 MiB WASM memory limit and no
JavaScript dynamic execution. FFmpeg has network support and all protocols
except `file` disabled, uses no pthreads, and includes x264 encoding and LAME
MP3 encoding. Its WASM memory can grow up to 2 GiB; each conversion limits an
individual native allocation to 256 MiB and supplies a 120 second timeout.
The latter is FFmpeg's interrupt timeout, not a hard worker/process kill.

## Browser libraries

The non-native assets came from these exact npm tarballs. No package lifecycle
scripts were run. Compare the SHA-512 before extracting and copying `dist/`:

| Package | Tarball integrity |
| --- | --- |
| @ffmpeg/ffmpeg 0.12.15 | sha512-1C8Obr4GsN3xw+/1Ww6PFM84wSQAGsdoTuTWPOj2OizsRDLT4CXTaVjPhkw6ARyDus1B9X/L2LiXHqYYsGnRFw== |
| bootstrap 5.3.8 | sha512-HP1SZDqaLDPwsNiqRqi5NcP0SSXciX2s9E+RyqJIIqGo+vJeN5AJVM98CXmW/Wux0nQ5L7jeWUdplCEf0Ee+tg== |
| jszip 3.10.2 | sha512-3l+rb15IOWtUhU0H5MFqES/T6Kh7abYwjosBey/vD6hDt8zoEffkSC5Ws5SGtgVw3gBx2NEbhTeSW1+kWkpyTQ== |

The ffmpeg UMD entry is stored as `lib/ffmpeg/ffmpeg.min.js`, alongside its
`814.ffmpeg.js` Worker. The old 0.12.10 core is not used or published.
After updating assets, regenerate `vendor-manifest.json`; it refuses to record
new engine versions unless the expected version strings exist in the WASM.
The manifest records hashes of the runtime entry points; a published build's
Service Worker manifest additionally hashes every published asset.

## Verification

`node --test tests/security.test.cjs` checks artifact digests, engine identity,
real HEIC decoding, corrupt input handling, cache isolation, install failures,
and explicit update acceptance.

`tests/browser-smoke.cjs` requires Playwright and an installed Edge browser.
Set `PLAYWRIGHT_MODULE` to an installed Playwright module's path if it is not
on the normal Node.js module search path, then run:

```powershell
node tests/browser-smoke.cjs output/wwwroot
```

It starts a loopback-only static server using the supplied production headers
and checks the UI, JPEG/MP3/MP4/ZIP output, offline reload, update activation,
and the absence of external requests and uncaught browser errors.

## Upstream security references

- https://github.com/strukturag/libheif/releases/tag/v1.23.6
- https://github.com/strukturag/libde265/releases/tag/v1.1.3
- https://ffmpeg.org/security.html
- https://github.com/dotnet/aspnetcore/security/advisories/GHSA-qjpx-jqm5-h2c4

These changes do not prove absence of all vulnerabilities. Keep the native
engines under review separately from NuGet/npm package audit results.