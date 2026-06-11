import streamlit as st
from google import genai
import tempfile
import os

# 1. Geminiの初期設定
# ※ご自身の「AQ.Ab8...」から始まるAPIキーを貼り付けてください。
GOOGLE_API_KEY =
client = genai.Client(api_key=GOOGLE_API_KEY)

# 2. パスワード保護機能（簡易認証）
# ※「お好きなパスワード」をご自身の決めた英数字に書き換えてください。
PASSWORD = "rivup1120"

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        return True

    st.title("🔒 セキュリティ認証")
    user_password = st.text_input("パスワードを入力してください", type="password")
    if st.button("ログイン"):
        if user_password == PASSWORD:
            st.session_state.password_correct = True
            st.rerun()
        else:
            st.error("パスワードが違います")
    return False

# パスワードが合っている場合のみアプリを起動
if check_password():
    st.title("🎙️ 面談感情分析アプリ (スマホ直接起動版)")
    st.write("その場で録音するか、音声ファイルをアップロードして分析できます。")

    tab1, tab2 = st.tabs(["🔴 その場でマイク録音", "📂 音声ファイルアップロード"])

    recorded_audio = None
    uploaded_file = None

    with tab1:
        st.write("下のマイクアイコンを押して、録音してください。")
        recorded_audio = st.audio_input("マイクに向かって話してください")

    with tab2:
        uploaded_file = st.file_uploader("音声ファイルを選択してください (mp3, wav, m4aなど)", type=["mp3", "wav", "m4a"])

    if st.button("🚀 AI感情分析を実行"):
        target_audio = None
        suffix = ".wav"
        
        if recorded_audio is not None:
            target_audio = recorded_audio.getvalue()
            suffix = ".wav"
        elif uploaded_file is not None:
            target_audio = uploaded_file.getvalue()
            suffix = f".{uploaded_file.name.split('.')[-1]}"
            
        if target_audio is not None:
            with st.spinner("Geminiが分析しています...（1〜2分かかる場合があります）"):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                        tmp_file.write(target_audio)
                        tmp_file_path = tmp_file.name

                    audio_file = client.files.upload(file=tmp_file_path)

                    prompt = """
                    添付された音声ファイルを多角的に解析し、以下のフォーマットで出力してください。
                    
                    # 解析の条件
                    1. 音声のニュアンス（声のトーン、話すテンポ、間、笑い声、ため息など）も考慮して分析してください。
                    2. 主に「ゲスト（対談相手）」に焦点を当てて分析してください。
                    
                    # 出力フォーマット
                    ## 1. 文字起こし（タイムスタンプ付き）
                    ## 2. 对談内容の要約
                    ## 3. 声のトーンと言い回しから見る「感情分析」
                    - **全体の感情の推移：**
                    - **本音と建前の分析：**
                    - **感情ステータス：** [喜び・納得・緊張・警戒・退屈] の度合い（％）
                    - **感情ステータス（詳細）：** - 喜び: 〇% / 納得: 〇% / 緊張: 〇% / 警戒: 〇%
                    ## 4. 言動から導く「性格・パーソナリティ分析」
                    - **コミュニケーションの傾向：**
                    - **人物像のプロファイリング：**
                    """

                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[audio_file, prompt]
                    )

                    os.unlink(tmp_file_path)

                    st.success("分析が完了しました！結果を表示します。")
                    st.markdown(response.text)
                    
                    # 分析結果を画面上でコピーしやすいようにテキストエリアにも表示
                    st.subheader("📋 コピー用テキスト")
                    st.text_area("以下の内容をコピーしてメモ帳やメールに貼り付けられます", value=response.text, height=300)

                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
        else:
            st.warning("音声データが見つかりません。")