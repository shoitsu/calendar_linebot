import os
import json
import requests
import datetime 
import google.auth 
from googleapiclient.discovery import build 

def lambda_handler(event, context):
    CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
    CALENDAR_ID = os.environ["CALENDAR_ID"] # 環境変数からカレンダーIDを取得

    print(event)
    body = json.loads(event["body"])
    replyToken = body["events"][0]["replyToken"]
    receivedText = body["events"][0]["message"]["text"]
    
    json_text = get_json_from_gemini(receivedText)
    
    # 予定追加処理
    success, message = add_google_calendar_event(json_text, CALENDAR_ID)

    # 返信メッセージを設定
    reply_message = message

    # LINE Messaging APIを使用してユーザーからのメッセージに対してリプライを送信する
    # HTTPリクエストでLINEのエンドポイントにJSONデータを送信
    url = "https://api.line.me/v2/bot/message/reply"
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
    }
    body = json.dumps({
        "replyToken": replyToken,
        "messages": [
            {
                "type": "text",
                "text": reply_message
            }
        ]
    })
    
    res = requests.post(url=url, headers=header, data=body)
    print(res.text)
    
    return "OK"

def get_json_from_gemini(received_message):
    """Gemini APIを使用してJSONを取得する関数"""
    try:
        # 環境変数からAPIキーを取得
        api_key = os.environ["GEMINI_API_KEY"]
        
        # 現在の日時を取得
        JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
        now = datetime.datetime.now(JST)
        today = now.strftime("%Y-%m-%d %H:%M")
        
        # 曜日を日本語で取得
        weekday_ja = ["月", "火", "水", "木", "金", "土", "日"][now.weekday()]
        today_with_weekday = f"{today}（{weekday_ja}曜日）"
        
        # プロンプトテンプレート
        system_prompt = (
            "あなたの役割は、ユーザーが入力した日本語のテキストからイベント情報を抽出し、\n"
            "Googleカレンダーに登録できる形式のJSONを生成することです。\n\n"
        )
        user_prompt = (
            "入力から抽出すべき情報：\n"
            "1. 予定の概要（summary）\n"
            "2. 開始日時（start）\n"
            "3. 終了日時（end）\n"
            "4. タイムゾーン（\"Asia/Tokyo\" で固定）\n\n"
            "- JSONは以下の形式で出力してください。出力は**JSONのみ**とし、それ以外の文字は含めないでください。\n\n"
            "```json"
            "{"
            "    \"summary\": \"予定の概要\","
            "    \"start\": {"
            "    \"dateTime\": \"YYYY-MM-DD HH:MM\","
            "    },"
            "    \"end\": {"
            "    \"dateTime\": \"YYYY-MM-DD HH:MM\","
            "    }"
            "}"
            "```\n\n"
            "- 日付と時間は24時間表記で「YYYY-MM-DD HH:MM」形式にしてください。\n"
            f"- 現在の日付は{today_with_weekday}です。\n"
            "- 時間が明示されていない場合は、開始時間を00:00、終了時間を23:59としてください。\n"
            "- 明らかにカレンダー登録とかけ離れる内容の場合は、\"no event found\" と出力してください。\n\n"
            "### 入力テキスト\n"
            f"{received_message}\n\n"
            "### 出力JSON\n"
        )

        # Gemini APIを直接呼び出す
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        headers = {
            "Content-Type": "application/json"
        }
        
        # リクエストデータ
        data = {
            "system_instruction": {
                "parts": {
                    "text": system_prompt
                }
            },
            "contents": {
                "parts": {
                    "text": user_prompt
                }
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        response_json = response.json()
        
        print("Gemini API response:", response_json)  # デバッグ用ログ
        
        # レスポンスからテキスト部分を抽出
        content = response_json.get("candidates", [{}])[0].get("content", {})
        parts = content.get("parts", [{}])
        result_text = parts[0].get("text", "") if parts else ""

        # マークダウン記法(```json と ```)，改行を削除
        result_text = result_text.replace("```json", "").replace("```", "").replace("\n", "").strip()
        
        print("result_text",result_text)  # デバッグ用ログ

        return result_text
    
    except Exception as e:
        error_message = f"予定の追加に失敗しました。エラー：{e}"
        print(error_message)
        return error_message


def add_google_calendar_event(json_text, calendar_id):
    """Googleカレンダーに予定を追加する関数 (OAuth 2.0 サービスアカウント認証を使用)"""

    try:
        # サービスアカウント認証情報を使用してGoogle Calendar APIクライアントを構築
        credentials, project_id = google.auth.default()  # タプルを分解して取り出す
        service = build('calendar', 'v3', credentials=credentials)  # credentials のみを渡す

        # json_textが"no event found"の場合はエラーを発生させる
        if json_text == '"no event found"' or json_text == 'no event found':
            raise Exception("カレンダーに追加したい予定を送ってね！！")
        
        # json_textが文字列の場合、パース
        if isinstance(json_text, str):
            json_text = json.loads(json_text)
            
        JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
        summary = json_text["summary"]
        start_time = json_text["start"]["dateTime"]
        end_time = json_text["end"]["dateTime"]

        event_details = {
            'summary': summary,
            'start': {
                'dateTime': datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M").replace(tzinfo=JST).isoformat(),
                'timeZone': 'Asia/Tokyo', 
            },
            'end': {
                'dateTime': datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M").replace(tzinfo=JST).isoformat(),
                'timeZone': 'Asia/Tokyo', 
            },
        }

        event = service.events().insert(calendarId=calendar_id, body=event_details).execute() # APIリクエストを実行

        print("Google Calendar event created successfully")
        return True, f"予定を追加しました！！\n 概要：「{summary}」\n時刻：（{start_time}～{end_time}）"

    except Exception as e: # エラー処理を修正
        error_message = f"予定の追加に失敗しました。\nエラー：{e}" # エラーメッセージに例外オブジェクトeを含める
        print(error_message)
        return False, error_message