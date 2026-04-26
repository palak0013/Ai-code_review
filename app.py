import streamlit as st
from reviewer import review_code
from github_utils import *
import re

def section_header(icon, text, size=18):
    return f"""
    <div style="display:flex; align-items:center; gap:8px; margin-top:10px;">
        <span style="font-size:{size}px;">{icon}</span>
        <span style="font-size:22px; font-weight:600;">{text}</span>
    </div>
    """

# ------------------ Helpers ------------------

def detect_language_from_filename(filename):
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    ext_map = {
        "py": "Python",
        "js": "JavaScript",
        "java": "Java",
        "cpp": "C++",
        "c": "C",
        "txt": "Python",
    }
    return ext_map.get(ext, "Python")


def split_output(text):
    try:
        issues = text.split("IMPROVED_CODE:")[0].replace("ISSUES:", "").strip()
        code_part = text.split("IMPROVED_CODE:")[1].split("EXPLANATION:")[0].strip()
        explanation = text.split("EXPLANATION:")[1].strip()
        return issues, code_part, explanation
    except:
        return text, "", ""


# ------------------ App Setup ------------------

st.set_page_config(page_title="AI Code Mentor", layout="wide")
st.title("🧠 AI Code Mentor for Students")

# Session State
if "upload_result" not in st.session_state:
    st.session_state.upload_result = None

if "repo_results" not in st.session_state:
    st.session_state.repo_results = []

if "code" not in st.session_state:
    st.session_state.code = ""


# ------------------ Sidebar ------------------

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

    repo_url = st.text_input("🔗 Enter GitHub Repo URL")
    repo_file_limit = st.slider("📚 Repo files to analyze", 1, 10, 2)

    if st.button("🧪 Analyze Upload + Repo"):

        st.session_state.upload_result = None
        st.session_state.repo_results = []

        # -------- Upload --------
        if st.session_state.code.strip():
            with st.spinner("Analyzing uploaded file..."):
                st.session_state.upload_result = review_code(
                    st.session_state.code, language, mode
                )

        # -------- Repo --------
        if repo_url.strip():

            try:
                # ✅ Reset results
                st.session_state.repo_results = []

                user, repo = parse_github_url(repo_url)

                if not user or not repo:
                    st.error("Invalid GitHub URL")
                    st.stop()

                files = get_repo_files(user, repo)

                if not isinstance(files, list) or len(files) == 0:
                    st.error("Failed to fetch repository files")
                    st.stop()

                code_files = get_code_files(files)

                for file in code_files[:repo_file_limit]:
                    try:
                        download_url = file.get("download_url")

                        if not download_url:
                            continue

                        content = get_file_content(download_url)

                        if not isinstance(content, str) or not content.strip():
                            continue

                        repo_lang = detect_language_from_filename(file.get("name", ""))

                        with st.spinner(f"Analyzing {file.get('name', 'file')}..."):
                            result = review_code(content, repo_lang, mode)

                        st.session_state.repo_results.append({
                            "file_name": file.get("name", "unknown"),
                            "result": result,
                            "language": repo_lang
                        })

                    except Exception as file_error:
                        st.warning(f"Skipped file: {file_error}")
                        continue

                # ✅ THIS was causing your error (must be inside try)
                st.success("Analysis complete!")

            except Exception as e:
                st.error(f"Repo error: {e}")

    if st.button("🔄 Reset App"):
        st.session_state.upload_result = None
        st.session_state.repo_results = []
        st.session_state.code = ""
        st.session_state.reset_trigger = True
        st.rerun()


# ------------------ Code Editor ------------------

st.markdown("## 📝 Code Editor")

if "reset_trigger" in st.session_state and st.session_state.reset_trigger:
    st.session_state.code = ""
    st.session_state.reset_trigger = False
    
code = st.text_area(
    "Paste your code here",
    height=350,
    key="code"
)

if st.button("🚀 Review Code"):
    if code.strip():
        with st.spinner("Analyzing code..."):
            st.session_state.upload_result = review_code(code, language, mode)
            st.session_state.repo_results = []
    else:
        st.warning("Please enter some code")


# ------------------ Results ------------------

if st.session_state.upload_result or st.session_state.repo_results:

    st.markdown("## 📊 Code Insights")

    tab1, tab2, tab3 = st.tabs([
        "📌 Issues",
        "💻 Code (Original)",
        "📖 Explanation (Improved Code)"
    ])

    # ------------------ Issues ------------------
    with tab1:

        # Upload
        if st.session_state.upload_result:
            st.markdown(section_header("📂", "Uploaded File"),unsafe_allow_html=True)
            issues, _, _ = split_output(st.session_state.upload_result)
            st.markdown(issues)
            st.divider()

        # Repo
        for file in st.session_state.repo_results:
            st.markdown(section_header("📁", f"{file['file_name']}"),unsafe_allow_html=True)
            issues, _, _ = split_output(file["result"])
            st.markdown(issues)
            st.divider()

    # ------------------ Original Code ------------------
    with tab2:

        if st.session_state.upload_result:
            st.markdown(section_header("📂", "Uploaded File"),unsafe_allow_html=True)
            st.code(code, language=language.lower(), line_numbers=True)
            st.divider()

        for file in st.session_state.repo_results:
            st.markdown(section_header("📁", f"{file['file_name']}"),unsafe_allow_html=True)
            st.caption("Original code preview not shown")
            st.divider()

    # ------------------ Explanation + Improved ------------------
    with tab3:

        # Upload
        if st.session_state.upload_result:
            st.markdown(section_header("📂", "Uploaded File"),unsafe_allow_html=True)

            _, improved_code, explanation = split_output(
                st.session_state.upload_result
            )

            st.markdown(explanation)

            if improved_code:
                st.markdown(section_header("💻", "Improved Code"),unsafe_allow_html=True)
                st.code(improved_code, language=language.lower(), line_numbers=True)

            st.divider()

        # Repo
        for file in st.session_state.repo_results:
            st.markdown(section_header("📁", f"{file['file_name']}"),unsafe_allow_html=True)

            _, improved_code, explanation = split_output(file["result"])

            st.markdown(explanation)

            if improved_code:
                st.markdown(section_header("💻", "Improved Code"),unsafe_allow_html=True)
                st.code(improved_code, language=file["language"].lower(), line_numbers=True)

            st.divider()

else:
    st.info("👈 Upload code or enter repo to start analysis")
