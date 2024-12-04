import streamlit as st
from plyer import notification
from openai import OpenAI
import time
from threading import Thread, Event
import os
from dotenv import load_dotenv
import webbrowser

# 環境変数の読み込み
load_dotenv()

# OpenAI APIキー設定
client = OpenAI(api_key=os.environ.get("API_KEY"))

# スレッド停止用のイベント
stop_event = Event()

# 運動提案を生成する関数
def get_exercise_suggestion():
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a fitness coach. Please respond in Japanese."},
                {"role": "user", "content": "デスクワーカーに適した1分間でできる簡単なストレッチやエクササイズを一つ提案してください。ストレッチやエクササイズの内容だけ簡潔に答えてください。運動の手順がテキストだけで分かるように答えてください。"}
            ],
            max_tokens=200
        )
        suggestion = response.choices[0].message.content.strip()
        return suggestion[:200] + ('...' if len(suggestion) > 200 else '')
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"

# 通知のスケジュール設定
def schedule_notifications(interval):
    while not stop_event.is_set():
        # 通知送信
        notification.notify(
            title="運動の時間です！",
            message="ここをクリックして運動提案を確認してください。",
            app_name="運動リマインダー",
            timeout=10
        )
        # 指定した間隔分だけ停止（秒単位）
        for _ in range(interval * 60):
            if stop_event.is_set():  # 停止イベントがセットされていれば終了
                break
            time.sleep(1)  # 1秒ごとにチェック

def open_streamlit_app():
    webbrowser.open(st.get_option("server.baseUrlPath"))

# Streamlitアプリ
st.title("運動リマインダーアプリ")
st.write("クイックエクササイズのリマインダーを受け取る間隔を設定してください！")

# ユーザー入力
interval = st.number_input("通知間隔を設定（分）:", min_value=1, max_value=120, value=60, step=1)

# セッションステートの初期化
if 'notification_active' not in st.session_state:
    st.session_state.notification_active = False
if 'exercise' not in st.session_state:
    st.session_state.exercise = None
if 'notification_thread' not in st.session_state:
    st.session_state.notification_thread = None

# 通知開始ボタン
if st.button("通知を開始"):
    if not st.session_state.notification_active:
        stop_event.clear()
        st.session_state.notification_active = True
        st.success(f"通知は{interval}分ごとに送信されます。")
        st.session_state.notification_thread = Thread(target=schedule_notifications, args=(interval,))
        st.session_state.notification_thread.start()
    else:
        st.warning("通知はすでに開始されています。")

# 通知停止ボタン
if st.button("通知を停止"):
    if st.session_state.notification_active:
        stop_event.set()
        if st.session_state.notification_thread:
            st.session_state.notification_thread.join()
        st.session_state.notification_active = False
        st.session_state.notification_thread = None
        st.success("通知を停止しました。")
    else:
        st.warning("通知はまだ開始されていません。")

# 運動提案を表示
if st.button("運動提案を表示"):
    st.session_state.exercise = get_exercise_suggestion()

if st.session_state.exercise:
    st.subheader("提案された運動:")
    st.write(st.session_state.exercise)
else:
    st.info("運動提案を表示するには上のボタンをクリックしてください。")
