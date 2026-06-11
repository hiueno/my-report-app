import streamlit as st
from google import genai
import os

# 1. セキュリティ認証（パスワード設定）
# ※ "あなたのパスワード" を、ご自身が決めたパスワードに書き換えてください
PASSWORD = "rivup1120"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 セキュリティ認証")
    user_input = st.text_input("パスワードを入力してください", type="password")
    if st.button("認証"):
        if user_input == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("パスワードが違います")
    st.stop()

# 2. メインアプリ画面
st.title("🎙️ AI音声分析・報告アプリ")
st.write("その場で録音して、AI（Gemini）がすぐに内容を分析・要約します。")

# 隠し金庫（Secrets）からAPIキーを読み込む
# ※万が一金庫が空の時のために、前回の仮の文字列を指定しておきます
api_key = st.secrets.get("GOOGLE_API_KEY", "SECRET_KEY")
client = genai.Client(api_key=api_key)

# 3. 音声の録音・アップロード機能
st.subheader("1. 音声を準備する")
audio_file = st.audio_input("ここを押して録音してください")

if audio_file is not None:
    st.audio(audio_file)
    
    st.subheader("2. AIによる分析を実行する")
    # 分析ボタン
    if st.button("✨ 分析・要約をスタート"):
        with st.spinner("AIが音声を分析しています。しばらくお待ちください..."):
            try:
                # 録音データをGeminiに渡せる形式に変換
                audio_bytes = audio_file.read()
                
                # Geminiへの指示（プロンプト）
                prompt = (
                    "添付された音声を聞き取り、重要ポイントを整理して、"
                    "分かりやすい報告書風に要約してください。"
                )
                
                # Geminiに音声データを送って分析
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[
                        genai.types.Part.from_bytes(
                            data=audio_bytes,
                            mime_type="audio/wav",
                        ),
                        prompt
                    ]
                )
                
                # 結果の表示
                st.success("🎉 分析が完了しました！")
                st.subheader("📋 分析・要約結果")
                st.write(response.text)
                
            except Exception as e:
                st.error("分析中にエラーが発生しました。")
                st.caption(f"エラー詳細: {e}")