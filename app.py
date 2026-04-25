import streamlit as st
from reviewer import review_code
import re

st.set_page_config(page_title="AI Code Mentor", layout="wide")

st.title("🧠 AI Code Mentor for Students")

# Session state
if "result" not in st.session_state:
    st.session_state.result = ""

if "code" not in st.session_state:
    st.session_state.code = ""

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    language = st.selectbox(
        "💻 Language",
        ["Python", "JavaScript", "Java", "C++", "C"]
    )

    mode = st.selectbox(
        "🎯 Mode",
        ["Beginner", "Production"]
    )

    st.divider()

    uploaded_file = st.file_uploader(
        "📁 Upload file",
        type=["py", "js", "java", "cpp", "c", "txt"]
    )

    if uploaded_file:
        st.session_state.code = uploaded_file.read().decode("utf-8")
        st.success("File loaded!")

    if st.button("📌 Load Example"):
        st.session_state.code = """def divide(a, b):
    return a / b

print(divide(10, 0))"""
        #st.rerun()

    if st.button("🔄 Reset"):
        st.session_state.result = ""
        st.session_state.code = ""
        #st.rerun()

# Code editor
st.markdown("## 📝 Code Editor")

code = st.text_area(
    "Paste your code here",
    height=350,
    key="code"
)


#st.session_state.code = code

review_clicked = st.button("🚀 Review Code")

if review_clicked:
    if code.strip():
        with st.spinner(f"Reviewing {language} code in {mode} mode..."):
            st.session_state.result = review_code(code, language, mode)
    else:
        st.warning("Please enter some code")

# ================= RESULT SECTION =================
if st.session_state.result:

    result = st.session_state.result

    # 🔥 CLEAN UNWANTED HEADINGS
    result = re.sub(r"IMPROVED CODE\s*", "", result, flags=re.IGNORECASE)
    result = re.sub(r"FIXED_CODE\s*", "", result, flags=re.IGNORECASE)
    result = re.sub(r"\*\*", "", result)

    # 🔥 EXTRACT CODE BLOCKS
    code_blocks = re.findall(r"```(?:\w+)?\n(.*?)```", result, re.DOTALL)

    if code_blocks:
        clean_code = "\n\n".join([block.strip() for block in code_blocks])
    else:
        clean_code = ""

    # 🔥 OPTIONAL: REMOVE COMMENTS & DOCSTRINGS
    if mode == "Production" and clean_code:
        clean_code = re.sub(r'""".*?"""', '', clean_code, flags=re.DOTALL)
        clean_code = "\n".join(
            line for line in clean_code.split("\n")
            if not line.strip().startswith("#")
        )

    # 🔥 REMOVE CODE FROM TEXT OUTPUT
    text_output = re.sub(r"```(?:\w+)?\n.*?```", "", result, flags=re.DOTALL)

    # SPLIT issues & explanation
    issues = ""
    explanation = ""

    exp_match = re.search(r"(EXPLANATION|Explanation)\s*:?\s*(.*)", text_output, re.DOTALL)

    if exp_match:
        explanation = exp_match.group(2).strip()
        issues = text_output[:exp_match.start()].strip()
    else:
        issues = text_output.strip()

    # UI
    st.markdown("## 📊 Code Insights")
    st.info("💡 Tip: Select same language to avoid conversion.")

    col1, col2 = st.columns(2)

    with col1:
        st.caption("Lines of Code")
        st.write(len(code.split("\n")))

    with col2:
        st.caption("Mode")
        st.write(mode)

    tab1, tab2, tab3 = st.tabs([
        "📌 Issues",
        "💻 Code (Original)",
        "📖 Explanation (Improved Code)"
    ])

    # 🔹 Issues Tab
    with tab1:
        st.markdown(issues)

    # 🔹 Original Code
    with tab2:
        st.caption("Original Code")
        st.code(code, language=language.lower(), line_numbers=True)

    # 🔹 Explanation + Improved Code
    with tab3:
        st.markdown(explanation)

        if clean_code:
            st.markdown("### 💻 Improved Code")

            st.code(clean_code, language=language.lower(), line_numbers=True)

            # File extension mapping
            ext_map = {
                "Python": "py",
                "JavaScript": "js",
                "Java": "java",
                "C++": "cpp",
                "C": "c"
            }

            file_ext = ext_map.get(language, "txt")

            st.download_button(
                "⬇ Download Improved Code",
                clean_code,
                f"improved_code.{file_ext}",
                mime="text/plain"
            )

else:
    st.info("👈 Paste your code and click 'Review Code'")