const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../HEIC2JPG/wwwroot');

function worker({ fail = false, windows = 1 } = {}) {
    const handlers = {};
    const stores = new Map([['heic2jpg-v3', new Map()], ['another-app', new Map()]]);
    const requests = [];
    let skipped = false;
    const cacheAPI = {
        has: async name => stores.has(name),
        open: async name => {
            if (!stores.has(name)) stores.set(name, new Map());
            const store = stores.get(name);
            return {
                addAll: async list => { requests.push(...list); if (fail) throw Error('integrity failure'); for (const r of list) store.set(r.url, new Response(r.url)); },
                match: async req => store.get(typeof req === 'string' ? req : req.url)
            };
        },
        keys: async () => [...stores.keys()],
        delete: async name => stores.delete(name)
    };
    const self = {
        location: { origin: 'https://app.test' },
        registration: { scope: 'https://app.test/' },
        assetsManifest: { version: 'new', assets: [{url:'index.html',hash:'sha256-YQ=='}, {url:'lib/engine.wasm',hash:'sha256-Yg=='}] },
        addEventListener: (name, fn) => handlers[name] = fn,
        skipWaiting: async () => { skipped = true; },
        clients: { matchAll: async () => Array.from({length:windows}, () => ({url:'https://app.test/'})) }
    };
    vm.runInNewContext(fs.readFileSync(path.join(root,'sw.published.js'),'utf8'), {self,caches:cacheAPI,importScripts:()=>{},URL,Request,fetch:async()=>new Response('network')});
    const fire = async (name, extra = {}) => { let pending; handlers[name]({waitUntil:p=>pending=p,respondWith:p=>pending=p,...extra}); return await pending; };
    return { fire, stores, requests, skipped:()=>skipped };
}

test('vendor bytes match the recorded SHA-256 digests and engine versions', () => {
    const manifest = JSON.parse(fs.readFileSync(path.join(root,'vendor-manifest.json')));
    for (const pkg of manifest.packages) for (const [file,hash] of Object.entries(pkg.files)) {
        assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(root,file))).digest('hex'),hash,file);
    }
    assert.ok(fs.readFileSync(path.join(root,'lib/libheif/libheif.wasm')).includes(Buffer.from('1.23.6')));
    assert.ok(fs.readFileSync(path.join(root,'lib/ffmpeg/ffmpeg-core.wasm')).includes(Buffer.from('5.1.10')));
    assert.equal(fs.existsSync(path.join(root,'lib/ffmpeg/ffmpeg-core-0.12.10.wasm')),false);
});

test('updated SW verifies integrity, selects its own cache, and preserves unrelated caches', async () => {
    const w=worker(); await w.fire('install');
    assert.equal(w.skipped(),false);
    assert.ok(w.requests.every(r=>r.integrity.startsWith('sha256-') && r.cache==='no-cache'));
    await w.fire('activate');
    assert.equal(w.stores.has('heic2jpg-v3'),false);
    assert.equal(w.stores.has('another-app'),true);
    const response=await w.fire('fetch',{request:{method:'GET',url:'https://app.test/licenses',mode:'navigate'}});
    assert.equal(await response.text(),'https://app.test/index.html');
    const asset=await w.fire('fetch',{request:{method:'GET',url:'https://app.test/lib/engine.wasm',mode:'navigate'}});
    assert.equal(await asset.text(),'https://app.test/lib/engine.wasm');
    assert.equal(await w.fire('fetch',{request:{method:'GET',url:'https://cdn.test/code.js'}}),undefined);
    assert.equal(await w.fire('fetch',{request:{method:'POST',url:'https://app.test/api'}}),undefined);
});

test('failed/incomplete installation never activates a new cache', async () => {
    const w=worker({fail:true}); await assert.rejects(w.fire('install'),/integrity failure/);
    assert.equal(w.stores.has('heic2jpg-new'),false);
    assert.equal(w.stores.has('heic2jpg-v3'),true);
    assert.equal(w.skipped(),false);
});

test('SW applies updates only with one remaining tab and explicit acceptance', async () => {
    const w=worker({windows:2}); let message;
    await w.fire('message',{data:{type:'APPLY_UPDATE'},source:{postMessage:m=>message=m}});
    assert.equal(message.type,'CLOSE_OTHER_TABS'); assert.equal(w.skipped(),false);
    const single=worker(); await single.fire('message',{data:{type:'APPLY_UPDATE'}}); assert.equal(single.skipped(),true);
});

test('HEIC decoding uses the patched engine on a real fixture and rejects corrupt input', async () => {
    const factory=require(path.join(root,'lib/libheif/libheif.js'));
    const lib=await factory(); assert.equal(lib.heif_get_version(),'1.23.6');
    for (const corrupt of [false,true]) {
        const decoder=new lib.HeifDecoder(); let images=[];
        try {
            images=decoder.decode(corrupt ? new Uint8Array([1,2,3,4]) : fs.readFileSync(path.join(__dirname,'fixtures/rainbow.heic'))) || [];
            if (corrupt) assert.equal(images.length,0);
            else {
                assert.equal(images.length,1); assert.equal(images[0].get_width(),451); assert.equal(images[0].get_height(),461);
                await new Promise((resolve,reject)=>images[0].display({width:451,height:461,data:new Uint8ClampedArray(451*461*4)},r=>r?resolve():reject(Error('decode failed'))));
            }
        } finally { for(const image of images)image.free();lib.heif_context_free(decoder.decoder); }
    }
});
