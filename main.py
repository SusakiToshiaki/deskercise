import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# OpenAI APIキー設定
client = OpenAI(api_key=os.environ.get("API_KEY"))

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

# Streamlitアプリ
st.title("Deskercise | デスクサイズ")
st.write("クイックエクササイズのリマインダーを受け取る間隔を設定してください！")

# 通知間隔をユーザーに入力させる
interval = st.number_input("通知間隔を設定（分）:", min_value=1, max_value=120, value=1, step=1)

# 運動提案を取得
exercise = get_exercise_suggestion()

st.subheader("提案された運動:")
st.write(exercise)

# Webブラウザ通知用のJavaScriptコード
notification_script = f"""
<script>
let notificationInterval;

function requestNotificationPermission() {{
    if (Notification.permission !== "granted") {{
        Notification.requestPermission();
    }}
}}

function showNotification() {{
    if (Notification.permission === "granted") {{
        new Notification("運動の時間です！", {{
            body: "提案された運動: {exercise}",
        }});
    }}
}}

function startNotifications(intervalMinutes) {{
    clearInterval(notificationInterval); // 既存の通知をクリア
    notificationInterval = setInterval(showNotification, intervalMinutes * 60 * 1000);
    showNotification(); // 最初の通知を即時表示
}}

function stopNotifications() {{
    clearInterval(notificationInterval);
}}
</script>
"""

st.markdown(notification_script, unsafe_allow_html=True)

# 通知開始ボタン
if st.button("通知を開始"):
    st.markdown(f"""
    <script>
    requestNotificationPermission();
    startNotifications({interval});
    </script>
    """, unsafe_allow_html=True)
    st.success(f"通知を{interval}分ごとに設定しました。")

# 通知停止ボタン
if st.button("通知を停止"):
    st.markdown("""
    <script>
    stopNotifications();
    </script>
    """, unsafe_allow_html=True)
    st.success("通知を停止しました。")
