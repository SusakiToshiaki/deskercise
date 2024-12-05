import streamlit as st
import openai
import time

# OpenAI APIキーの設定
openai.api_key = st.secrets["API_KEY"]

# 運動提案を生成する関数
def get_exercise_suggestion():
    try:
        # OpenAI APIで運動提案を生成
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a fitness coach. Please respond in Japanese."},
                {"role": "user", "content": "デスクワーカーに適した1分間でできる簡単なストレッチやエクササイズを一つ提案してください。ストレッチやエクササイズの内容だけ簡潔に答えてください。運動の手順がテキストだけで分かるように答えてください。（170字以内）"}
            ],
            max_tokens=200
        )
        # レスポンスから運動提案を抽出
        suggestion = response.choices[0].message.content.strip()
        return suggestion
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"

# Streamlit UI
st.title("デスクサイズ | Deskercise")
st.write("デスクで１分でできるクイックエクササイズ！次の運動までの間隔を設定してください！")

# Intervalのユーザー設定
interval = st.number_input("通知間隔を設定（分）:", min_value=1, max_value=120, value=60, step=1)

# セッション状態の初期化
if "exercise" not in st.session_state:
    st.session_state["exercise"] = None
if "time_remaining" not in st.session_state:
    st.session_state["time_remaining"] = 0
if "is_started" not in st.session_state:
    st.session_state["is_started"] = False

# 運動提案の表示（スタート後のみ表示）
if st.session_state["exercise"]:
    st.subheader("提案されたデスクサイズ：")
    st.write(st.session_state["exercise"])

    #運動やった！ボタンの追加
    if st.button("このデスクサイズおわった！"):
        st.balloons()
        #Next Deskercise and reset count-down
        st.session_state["exercise"] = get_exercise_suggestion()
        st.session_state["time_remaining"] = interval * 60
        st.rerun()

# スタートボタン
if st.button("スタート"):
    st.session_state["exercise"] = get_exercise_suggestion()
    st.session_state["time_remaining"] = interval * 60
    st.session_state["is_started"] = True
    st.rerun()

# カウントダウンロジック
if st.session_state["is_started"]:
    placeholder = st.empty()
    mins, secs = divmod(st.session_state["time_remaining"], 60)
    timer = f"{mins:02d}:{secs:02d}"
    placeholder.markdown(f"### 次の運動まで: {timer}")

    if st.session_state["time_remaining"] > 0:
        time.sleep(1)
        st.session_state["time_remaining"] -= 1
        st.rerun()
    else:
        # 時間切れで次の運動提案を表示
        st.session_state["exercise"] = get_exercise_suggestion()
        st.session_state["time_remaining"] = interval * 60
        st.rerun()
