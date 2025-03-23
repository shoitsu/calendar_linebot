# カレンダー自動とうろくん

## 📝 プロジェクト概要

「カレンダー自動とうろくん」は、LINEで送信された自然言語のメッセージから予定情報を抽出し、Googleカレンダーに自動で登録するLINE Botです。AWS Lambdaを活用したサーバーレスアーキテクチャで構築されており、ユーザーは複雑な操作なしに、日常会話のような文章でカレンダー登録が可能です。

![カレンダー自動とうろくん イメージ図1](images/calendar_zidoutourokun1.png)
![カレンダー自動とうろくん イメージ図1](images/calendar_zidoutourokun2.png)

## 🎯 開発の背景と目的

予定管理をするにあたって、カレンダーアプリを開いて入力する手間がめんどくさいなぁと思ってました。
また、移動中や会話の合間など、すぐにメモしたい瞬間に素早く予定を登録できないことが課題でした。

そこで、日常的に使用するLINEを通じて、自然な会話感覚で予定を登録できるサービスを開発しました。「明日の15時から会議」のような簡潔なメッセージだけで、適切にカレンダーに予定が追加される便利さを実現しています。

## 🛠️ 使用技術

### バックエンド
- **AWS Lambda**: サーバーレスでアプリケーションを実行
- **Python3.9**: バックエンドロジックの実装言語
- **Google Calendar API**: カレンダーへの予定追加
- **LINE Messaging API**: LINEとの連携

### AI/ML
- **Google Gemini AI**: 自然言語処理による予定情報の抽出

### インフラ
- **AWS Lambda**: サーバーレスでアプリケーションを実行（関数URL機能を使用）
- **AWS IAM**: アクセス権限管理
- **Google Cloud Platform**: Googleサービスとの連携

### 開発ツール
- **Git/GitHub**: バージョン管理
- **AWS CloudWatch**: ログ監視とデバッグ

## 🏗️ システムアーキテクチャ

```
[ユーザー] → [LINE] → [AWS Lambda] → [Google Gemini API]
                                               ↓
[ユーザー] ← [LINE] ← [AWS Lambda] ← [Google Calendar API]
```

1. ユーザーがLINEで予定の内容を送信
2. LINE Messaging APIからLambda関数URL経由でLambda関数が起動
3. Lambda関数がGemini APIを使用して自然言語から予定情報を抽出
4. 抽出された情報をGoogle Calendar APIを使ってカレンダーに登録
5. 処理結果をLINE経由でユーザーに返信

## 💡 主要機能

### 1. 自然言語解析
- Gemini AIを活用し、ユーザーの自由な文章から予定名、日時、場所などを正確に抽出

### 2. カレンダー自動登録
- 抽出した情報を適切な形式に変換し、Googleカレンダーに自動登録

### 3. フィードバック機能
- 登録結果をLINEで即時フィードバック
- エラー発生時には原因を分かりやすく通知

## 🔍 工夫した点・課題解決

### 自然言語処理の最適化
- 様々な日本語表現（「明後日」「来週の金曜」など）を正確に日付に変換できるよう、Gemini AIへのプロンプトを工夫
- 日本語特有の曖昧な表現にも対応できるよう調整

### サーバーレスアーキテクチャの採用
- AWS Lambdaを活用することで、サーバー管理の手間を省きながら低コストで運用
- スケーラビリティを確保し、将来的なユーザー増加にも対応可能な設計

### エラーハンドリングの強化
- ユーザー入力の不備や外部APIの障害に対して堅牢なエラー処理を実装
- ユーザーにとって分かりやすいエラーメッセージを返すよう配慮

## 📚 開発を通じて学んだこと

- **サーバーレスアーキテクチャの実践**: AWSのサーバーレスサービスを活用したアプリケーション設計と実装
- **外部API連携**: 複数のAPIを連携させるシステム設計とセキュリティ対策
- **自然言語処理の活用**: 生成AIを活用した実用的なアプリケーション開発
- **ユーザー体験の最適化**: 技術的な複雑さを隠蔽し、シンプルで使いやすいインターフェースの実現

## 🚀 今後の展望

- **機能拡張**: 予定の編集・削除機能、リマインダー設定などの追加
- **多言語対応**: 英語など他言語でも利用可能にすることでグローバル展開
- **他カレンダーサービス対応**: Google以外のカレンダーサービスとの連携
- **UI改善**: リッチメニューの実装などによるユーザビリティの向上

## 📦 デプロイ方法

詳細は、
https://qiita.com/shoitsu/items/afaf26599e3788843cb4

### 前提条件
- AWS アカウント
- LINE Developersアカウント
- Google Cloud Platformアカウント
- Googleカレンダー

### 1. Google Cloud Platform設定
1. Google Cloud Platformでプロジェクトを作成
2. Google Calendar APIを有効化
3. サービスアカウントを作成し、JSONキーをダウンロード
4. 使用したいGoogleカレンダーのIDを取得
### 2. LINE Bot設定
1. LINE Developersコンソールでプロバイダーとチャネルを作成
2. Messaging APIを設定
3. チャネルアクセストークン（長期）を発行
4. Webhook URLを設定（AWS Lambda関数URLを後で設定）

### 3. AWS Lambda設定
1. Lambda関数を作成（Pythonランタイム）
2. 必要なライブラリを含むレイヤーを作成
   ```bash
   pip install -t ./package google-auth google-api-python-client requests
   cd package
   zip -r ../deployment-package.zip .
   cd ..
   zip -g deployment-package.zip lambda_function.py
   ```
3. Lambda関数にレイヤーをアップロード
4. 関数URLを有効化し、認証タイプを「NONE」に設定
5. 環境変数を設定:
   - `CHANNEL_ACCESS_TOKEN`: LINE Bot用チャネルアクセストークン
   - `CALENDAR_ID`: GoogleカレンダーID
   - `GEMINI_API_KEY`: Google Gemini API Key
6. 取得したLambda関数URLをLINE DevelopersコンソールのWebhook URLに設定

### 4. Google認証の設定
1. ダウンロードしたサービスアカウントキー（JSON）をLambdaにアップロード
2. 環境変数`GOOGLE_APPLICATION_CREDENTIALS`にJSONファイルのパスを設定
3. GoogleカレンダーでLambda用サービスアカウントに共有権限を付与

### 5. 動作確認
1. LINE公式アカウントを友だち追加
2. メッセージを送信して予定が正しく登録されるか確認

## 🔒 セキュリティ上の注意点

- API KeyやアクセストークンはAWS Lambda環境変数で安全に管理
- サービスアカウントキーは最小権限の原則に従って設定
- 個人情報の取り扱いには十分注意し、プライバシーポリシーを整備