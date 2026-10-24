# NoTransfer Media Converter

## 概要

データ転送なしのメディア変換アプリ（Blazor WebAssembly）

- **HEIC → JPG** 画像変換
- **動画変換** MP4, MOV, AVI, MKV, WMV, FLV, WebM → MP4
- **動画 → MP3** 音声抽出
- **音声変換** MP3, WAV, FLAC, AAC, OGG, M4A, WMA → MP3
- **完全オフライン動作**（データはブラウザ外へ送信されません）
- **バッチ処理対応**（最大100件、2GB/ファイル）
- **レスポンシブデザイン**（PC・タブレット・スマートフォン完全対応）
- **テーマ切り替え**（ライト/ダーク/自動モード）
- **多言語対応**（日本語・英語・中国語簡体字）
- **プライバシー保護**（ネットワーク監視・検証可能）

## 📁 対応フォーマット

### 画像変換
| 入力フォーマット | 出力フォーマット | 特徴                           |
| :--------------- | :--------------- | :----------------------------- |
| `.heic`          | `.jpg`           | 品質調整可能 |

### 動画変換
| 入力フォーマット                                  | 出力フォーマット | 特徴                                   |
| :------------------------------------------------ | :--------------- | :------------------------------------- |
| `.mov` `.mp4` `.avi` `.mkv` `.wmv` `.flv` `.webm` | `.mp4`           | 高速リマックスまたは高品質再エンコード |
| `.mov` `.mp4` `.avi` `.mkv` `.wmv` `.flv` `.webm` | `.mp3`           | 動画から音声のみを抽出                 |

### 音声変換
| 入力フォーマット                                  | 出力フォーマット | 特徴                     |
| :------------------------------------------------ | :--------------- | :----------------------- |
| `.mp3` `.wav` `.flac` `.aac` `.ogg` `.m4a` `.wma` | `.mp3`           | 音声フォーマット間の変換 |

### ファイル制限
- **最大ファイルサイズ**: 2GB/ファイル
- **最大ファイル数**: 100件/バッチ

## 🎯 主な機能

### ✅ 実装完了
- ドラッグ&ドロップファイル受付
- **モダンUI/UX**（ヒーローセクション・使い方ガイド）
- **レスポンシブデザイン**（モバイルファースト設計）
- **テーマ切り替え機能**（ライト/ダーク/自動 + システム設定連動）
- 進捗表示・キャンセル機能
- 設定パネル（品質調整、EXIF保持設定等）
- バッチダウンロード（Zip対応）
- エラーハンドリング・ユーザーフィードバック
- COOP/COEP設定（SharedArrayBuffer対応）
- **多言語UI**（日本語・英語・中国語簡体字）
- **PWA対応**（オフラインインストール・スタンドアロン実行）
- **プライバシー保護UI**（Network Shield バッジ・Trust Center）
- **アクセシビリティ対応**（キーボード操作・WCAG AA準拠）
- **OSSライセンス表示**（使用ライブラリのライセンス情報を自動生成・表示）

### 🔧 技術要件
- **フロントエンド**: Blazor WebAssembly (.NET 10)
- **変換エンジン**:
  - HEIC: libheif 1.23.6 + libde265 1.1.3（公式ソースからWASMビルド） (✅ 導入済み)
  - 動画: @ffmpeg/ffmpeg v0.12.15 (✅ 導入済み)
- **セキュリティ**: COOP/COEP設定済み
- **圧縮**: JSZip v3.10.2 (✅ 導入済み)
- **PWA**: Service Worker + Web App Manifest (✅ 導入済み)
- **多言語**: .NET リソース（.resx）ベース
- **プライバシー**: CSP/COOP/COEP + ネットワーク監視
- **ライセンス管理**: 自動生成されたOSSライセンス表示ページ (✅ 導入済み)

## 📂 プロジェクト構造

```
HEIC2JPG/
├── Models/
│   ├── ConvertModels.cs          # データモデル定義
│   └── LicenseItem.cs            # ライセンス情報モデル
├── Services/
│   ├── IConvertService.cs        # 変換サービスIF
│   ├── ConvertService.cs         # 変換サービス実装
│   ├── ILocalizationService.cs   # 多言語サービスIF
│   ├── LocalizationService.cs    # 多言語サービス実装
│   └── NetworkMonitorService.cs  # ネットワーク監視サービス
├── Resources/
│   ├── Strings.resx              # デフォルト（日本語）リソース
│   ├── Strings.en.resx           # 英語リソース
│   └── Strings.zh-Hans.resx      # 中国語簡体字リソース
├── Components/
│   ├── NetworkShield.razor       # Network Shield バッジ
│   ├── TrustCenter.razor         # Trust Center ダイアログ
│   ├── HeroSection.razor         # ヒーローセクション
│   ├── HeroIcon.razor            # SVGアイコンコンポーネント
│   ├── UsageGuide.razor          # 使い方ガイド
│   ├── ThemeToggle.razor         # テーマ切り替え
│   └── LanguageSelector.razor    # 言語切替メニュー
├── Pages/
│   ├── Home.razor                # メインUI
│   └── Licenses.razor            # OSSライセンス表示ページ
├── Layout/
│   └── MainLayout.razor          # レイアウト
└── wwwroot/
    ├── js/
    │   ├── heicConverter.js      # HEIC変換（libheif統合）
    │   ├── ffmpegConverter.js    # MOV変換（FFmpeg統合）
    │   ├── zipHelper.js          # Zip生成
    │   ├── blobHelper.js         # Blob操作
    │   ├── fileDownload.js       # ダウンロード機能
    │   ├── fileHelper.js         # ファイル操作ヘルパー
    │   ├── networkMonitor.js     # ネットワーク監視
    │   ├── themeManager.js       # テーマ管理
    │   ├── localization.js       # ローカライゼーション
    │   └── commonUtils.js        # 共通ユーティリティ
    ├── css/
    │   ├── variables.css         # CSS変数（テーマ対応）
    │   └── converter.css         # 専用スタイル
    ├── lib/
    │   ├── libheif/              # libheif WASMファイル
    │   ├── ffmpeg/               # FFmpeg WASMファイル
    │   ├── jszip/                # JSZip ライブラリ
    │   └── bootstrap/            # Bootstrap フレームワーク
    ├── manifest.json             # PWA マニフェスト
    ├── sw.js                     # Service Worker
    └── icon-*.png                # PWA アイコン
```

## 🚀 セットアップ・実行

### 必要環境
- .NET SDK 10.0.402以降（global.jsonで、この最低バージョン以上のインストール済み最新正式版を選択。プレビュー版は除外）
- Visual Studioを使う場合: Visual Studio 2026（.NET 10対応）
- 対応ブラウザ: Chrome/Edge/Brave（最新版推奨、PWA対応）

SDKはVisual Studio Installerなどで更新してください。global.jsonは使用するSDKを選択する設定で、自動インストールは行いません。新しいメジャーバージョンのSDKを使う場合は、そのSDKに対応するVisual Studioも必要です。

build.shでは、対象フレームワークの.NET 10に合わせて最新の.NET 10正式版SDKを取得します。

### 実行手順
```bash
cd HEIC2JPG
dotnet run
```

### PWAインストール
1. Chrome/Edge でアプリにアクセス
2. アドレスバーの「インストール」アイコンをクリック
3. スタンドアロンアプリとして使用可能

### 導入済みライブラリ

**HEIC変換**: ✅ 完了
```bash
# libheif 1.23.6 + libde265 1.1.3（公式ソースからWASMビルド）
wwwroot/lib/libheif/libheif.js
```

**MOV変換**: ✅ 完了
```bash
# @ffmpeg/ffmpeg v0.12.15
wwwroot/lib/ffmpeg/ffmpeg.min.js
wwwroot/lib/ffmpeg/ffmpeg-core.js
wwwroot/lib/ffmpeg/ffmpeg-core.wasm (修正版5.1.10のWASM)
```

**Zip機能**: ✅ 完了
```bash
# JSZip v3.10.2
wwwroot/lib/jszip/jszip.min.js
```

**PWA機能**: ✅ 完了
```bash
# Service Worker + Web App Manifest
wwwroot/sw.js
wwwroot/manifest.json
```

## 🔧 設定項目

### 変換設定
- **JPG品質**: 0.6〜1.0（デフォルト: 0.9）
- **EXIF情報**: 保持/削除（デフォルト: 保持）
- **変換方式**: 自動/高速/高品質
- **音声のみ抽出**: 動画からMP3音声を抽出

## 📋 操作方法

1. **言語選択**: 右上の「🌐 Language」メニューから選択（自動検出またはlocalStorage保存）
2. **テーマ切り替え**: 右上のテーマアイコン（🌙/☀️/🔄）で切り替え（ライト/ダーク/自動）
3. **ファイル追加**: ドラッグ&ドロップまたはファイル選択
4. **設定調整**: 右側パネルで品質・変換方式を設定
   - 🎵 **音声のみ抽出（MP3）**: 動画から音声を抽出する場合にチェック
5. **変換実行**: 「▶️ 開始」ボタンをクリック
6. **ダウンロード**: 個別DLまたは「📦 一括DL」
7. **PWAインストール**: ブラウザのインストールプロンプトから追加
8. **プライバシー確認**: 右上の「Network Shield」バッジでネットワーク通信を監視

## 🛡️ セキュリティ・プライバシー

### ローカル完結の保証
- **100%クライアントサイド処理**: ファイルデータはブラウザメモリ内でのみ処理
- **ネットワーク監視**: 外部通信カウンタをUIに常時表示（Network Shield バッジ）
- **検証可能**: Trust Centerで検証手順を公開
- **COOP/COEP**: SharedArrayBuffer利用のため設定済み
- **CSP準拠**: 自己ホストリソースのみ許可

### プライバシー保護UI
- **Network Shield バッジ**: 右上ヘッダーに「LOCAL ONLY | 0」と表示（外部リクエスト数を監視）
- **Trust Center**: クリックで技術的裏付け・検証方法を表示
- **No Upload ラベル**: ファイル入力UIに常時表示
- **オフライン準備トースト**: PWA準備完了時に通知

## 📊 パフォーマンス目安

- **HEIC→JPG（12MP）**: 平均3秒未満（ハイエンド端末）
- **MOV→MP4（1080p/1分）**: リマックス10秒、再エンコード端末依存

## 🐛 トラブルシューティング

### よくある問題
1. **変換が開始されない** → ブラウザがCOOP/COEPに対応しているか確認
2. **大容量ファイルでエラー** → ファイルサイズ上限（2GB）を確認
3. **変換が遅い** → 並列数を調整または端末の性能を確認

### ブラウザ対応
- ✅ Chrome/Edge/Brave（推奨、PWA完全対応）
- ⚠️ Safari（WASM/COEP制約により限定対応、PWA部分対応）
- ❌ Internet Explorer（非対応）

## ♿ アクセシビリティ

- **レスポンシブ対応**:
  - モバイルファースト設計
  - タッチ操作最適化
  - ビューポートに応じた最適レイアウト
- **テーマ対応**:
  - システムのダークモード設定に自動追従
  - 手動切り替え対応（ライト/ダーク/自動）
- **キーボード操作**: すべてのUIコンポーネントは `Tab`/`Arrow`/`Enter` で操作可能
- **コントラスト比**: WCAG AA基準準拠（バッジ・ラベル・ボタン）
- **スクリーンリーダー対応**: ARIA属性・ラベル適切配置
- **フォーカス管理**: フォーカスリングの明示的表示
- **多言語フォント**: 各言語に適切なフォントファミリを指定

## 🌐 多言語対応

### サポート言語
- **日本語** (`ja-JP`): デフォルト
- **英語** (`en-US`): English
- **中国語簡体字** (`zh-CN`): 简体中文

### 言語切替
- **自動検出**: 初回起動時に `navigator.languages` から自動判定
- **手動切替**: 右上「🌐 Language」メニューから選択
- **永続化**: 選択言語を `localStorage("heic2jpg.lang")` に保存
- **反映**: 言語変更時にUIを即座に再描画（ページリロード不要）

### 対象範囲
- ヘッダー（アプリ名・メニュー・言語切替）
- ファイル入出力（ドラッグ&ドロップ・注意書き）
- 操作系（削除・並べ替え・回転・抽出・Undo/Redo）
- 設定パネル（品質・EXIF・変換方式）
- Network Shield / Trust Center
- ダイアログ・トースト（確認・成功・エラー）

## 📄 ライセンス

- **アプリケーション**: オープンソース（リポジトリ: [github.com/t2system-co-jp/Bz002-heic2jpg](https://github.com/t2system-co-jp/Bz002-heic2jpg)）
- **使用OSS**: アプリ内の `/licenses` ページで一覧表示（FFmpeg, libheif など、各ライセンスに準拠）

---

## 🎯 変換機能の動作

- **HEIC変換**: libheif-jsでJPEGへ変換
- **動画・音声変換**: @ffmpeg/ffmpegでMP4またはMP3へ変換
- **一括ダウンロード**: JSZipでZIPファイルを生成
- **エラー処理**: WASMライブラリの初期化・変換に失敗した場合は、ダミーファイルを生成せずエラーとして表示
- **推奨環境**: WASMライブラリが正常に動作するChrome / Edge


## セキュリティ更新（2026-10-23）

- .NET / Blazor 10.0.13へ更新。SDKは.NET 10以降のインストール済み最新正式版を使用。開発サーバーは外部公開しないでください。
- HEIC: libheif 1.23.6 / libde265 1.1.3。不要なコーデック、プラグイン読み込み、並列デコードを無効化。
- HEIC画像は4,000万画素、各辺16,384ピクセルまで。ブラウザ用のRGBAバッファを確保する前に確認します。
- FFmpeg: 5.1.10を再ビルド。ネットワーク機能を無効化し、入力プロトコルはfileのみ許可。H.264出力はx264、MP3出力はLAME。
- FFmpeg本体・Workerを含め全リソースを同一オリジンから配信し、外部CDNへの依存を廃止。
- 公開時に全アセットのハッシュ付きService Workerマニフェストを生成。更新版は整合性検証後に有効化し、利用者の操作なしで変換中のページを再読み込みしません。
- 実体のバージョン・ソース参照・SHA-256は `wwwroot/vendor-manifest.json`。ライセンス画面はこれとcsprojから生成します。

### 配信設定

静的サイトとして `dotnet publish -c Release -o output` の `output/wwwroot` を配信します。
Cloudflare Pages / Netlify等の `_headers` 対応ホストでは、同梱の `wwwroot/_headers` をそのまま配信設定に使います。
IIS、nginx、その他のホストでは、そのファイルに記載したCSP・COOP・COEP・nosniff等をHTTPレスポンスヘッダーとして設定してください。
COOP/COEPはHTMLのmetaタグでは設定できません。HTMLのCSPはヘッダー非対応ホスト向けの補助です。
新しいファイル一式を一度に配信し、CDNに古いHTML・`sw.js`・`service-worker-assets.js`が残らないようにしてください。
更新後は既存のPWAで更新通知から再読み込みします（先に変換結果を保存し、他のタブを閉じる）。

### 再ビルドと検証

通常の.NETビルドでは同梱済みWASMを使用します。エンジンを再ビルドする手順は `tools/wasm/README.md` を参照してください。

```powershell
dotnet publish HEIC2JPG/HEIC2JPG.csproj -c Release -o output
dotnet list HEIC2JPG/HEIC2JPG.csproj package --vulnerable --include-transitive
node --test tests/security.test.cjs
```

Node.jsは検証用ツールであり、公開アプリの実行には不要です。
依存パッケージの自動監査だけでWASM内のC/C++エンジンの安全性は判定できません。エンジンの公式セキュリティ情報も確認してください。
