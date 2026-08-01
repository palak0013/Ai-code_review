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

st.set_page_config(page_title="AI Code Review Assistant", layout="wide")
st.title("AI Code Review Assistant")
st.caption("Review source code, analyze GitHub repositories, and receive AI-powered suggestions for bugs, performance, security, and best practices.")

# Session State
if "upload_result" not in st.session_state:
    st.session_state.upload_result = None

if "repo_results" not in st.session_state:
    st.session_state.repo_results = []

if "code" not in st.session_state:
    st.session_state.code = ""

if "repo_file_list" not in st.session_state:
    st.session_state.repo_file_list = []

if "previous_input" not in st.session_state:
    st.session_state.previous_input = "Upload File"

if "upload_code" not in st.session_state:
    st.session_state.upload_code = ""

if "editor_code" not in st.session_state:
    st.session_state.editor_code = ""

if "analysis_source" not in st.session_state:
    st.session_state.analysis_source = None

if "clear_uploaded_file" not in st.session_state:
    st.session_state.clear_uploaded_file = False

if "show_editor" not in st.session_state:
    st.session_state.show_editor = False

if "previous_show_editor" not in st.session_state:
    st.session_state.previous_show_editor = False

if "language" not in st.session_state:
    st.session_state.language = "Python"

with st.sidebar:
    st.header("Settings")
    mode = st.selectbox(
        "Mode",
        ["Beginner", "Production"],
        key="mode"
    )

    show_editor = st.checkbox("Use Code Editor", key="show_editor")

    st.divider()

    if st.session_state.get("show_editor"):
        st.info("Editor enabled: Upload and GitHub inputs hidden.")

        # Only clear upload/repo state when editor is newly enabled
        if not st.session_state.get("previous_show_editor", False):
            st.session_state.upload_code = ""
            st.session_state.upload_result = None
            st.session_state.clear_uploaded_file = True
            st.session_state.repo_results = []
            st.session_state.repo_file_list = []

    else:

        input_source = st.radio(
            "Input source",
            ["Upload File", "GitHub Repo"],
            horizontal=True,
            key="input_source",
        )
        if st.session_state.previous_input != input_source:
            if input_source == "GitHub Repo":
                st.session_state.upload_code = ""
                st.session_state.upload_result = None
                st.session_state.analysis_source = None
            else:
                st.session_state.repo_results = []
                # Clear editor when switching to upload source so previous text doesn't persist
                st.session_state.editor_code = ""

            st.session_state.previous_input = input_source

        if input_source == "Upload File":

            # If a previous action requested clearing the file uploader, remove the widget state
            if st.session_state.get("clear_uploaded_file"):
                if "uploaded_file" in st.session_state:
                    st.session_state.pop("uploaded_file", None)
                st.session_state.clear_uploaded_file = False

            uploaded_file = st.file_uploader(
                "Choose file",
                type=["py", "js", "java", "cpp", "c", "txt"],
                key="uploaded_file",
            )

            if uploaded_file:
                st.session_state.upload_code = uploaded_file.read().decode("utf-8")
                # Clear editor input when a file is uploaded to avoid mixed provenance
                st.session_state.editor_code = ""
                # detect language from filename for uploaded files
                st.session_state.language = detect_language_from_filename(uploaded_file.name)
                st.success("File uploaded successfully")

            if st.session_state.upload_code:
                st.caption(f"Selected: {uploaded_file.name if uploaded_file else 'file'}")

                if st.button("Analyze File"):
                    with st.spinner("Analyzing file..."):
                        st.session_state.upload_result = review_code(
                            st.session_state.upload_code, st.session_state.get("language", "Python"), mode
                        )
                        st.session_state.analysis_source = "upload"
                        st.session_state.repo_results = []

        else:

            repo_url = st.text_input("GitHub repo URL", key="repo_url")

            if st.button("Load Repo Files"):

                try:
                    user, repo = parse_github_url(repo_url)

                    if not user or not repo:
                        st.error("Invalid GitHub URL")
                        st.stop()

                    files = get_repo_files(user, repo)

                    code_files = get_code_files(files)

                    # store files in session
                    st.session_state.repo_file_list = code_files

                    st.success("Repo loaded successfully!")

                except Exception as e:
                    st.error(f"Error: {e}")

            selected_files = []

            if "repo_file_list" in st.session_state:

                st.markdown("### Select repo files to analyze")

                for file in st.session_state.repo_file_list:
                    if st.checkbox(file["name"], key=file["name"]):
                        selected_files.append(file)

            if st.button("Analyze Repo"):

                st.session_state.repo_results = []

                for file in selected_files:
                    try:
                        content = get_file_content(file["download_url"])
                        repo_lang = detect_language_from_filename(file["name"])

                        with st.spinner(f"Analyzing {file['name']}..."):
                            result = review_code(content, repo_lang, mode)

                        st.session_state.repo_results.append({
                            "file_name": file["name"],
                            "result": result,
                            "language": repo_lang
                        })

                    except Exception as e:
                        st.warning(f"Skipped {file['name']}")

                st.success("Analysis complete!")

    st.session_state.previous_show_editor = st.session_state.get("show_editor", False)

    st.divider()

    if st.button("Reset App"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# Render editor only when toggle is enabled in the sidebar
if st.session_state.get("show_editor"):

    st.markdown("## Code Editor")

    if "reset_trigger" in st.session_state and st.session_state.reset_trigger:
        st.session_state.editor_code = ""
        st.session_state.reset_trigger = False

    code = st.text_area(
        "Paste your code here",
        height=350,
        key="editor_code"
    )

    if st.button("Review Code", key="review_editor"):
        if st.session_state.editor_code.strip():
            with st.spinner("Analyzing code..."):
                # Editor default language is Python
                st.session_state.language = "Python"
                st.session_state.upload_result = review_code(
                    st.session_state.editor_code, "Python", st.session_state.get("mode", "Beginner")
                )
                st.session_state.analysis_source = "editor"

                st.session_state.upload_code = ""
                st.session_state.clear_uploaded_file = True
                st.session_state.repo_results = []

                st.rerun()
        else:
            st.warning("Please enter some code")

# current language for upload/editor displays
language = st.session_state.get("language", "Python")

if st.session_state.upload_result or st.session_state.repo_results:

    st.markdown("## Code Insights")

    tab1, tab2, tab3 = st.tabs([
        "Issues",
        "Code (Original)",
        "Explanation (Improved Code)"
    ])

    with tab1:

        # Upload
        if st.session_state.upload_result:
            upload_label = (
                "Uploaded File" if st.session_state.analysis_source == "upload" else "Editor Input"
            )
            st.markdown(section_header("📂", upload_label),unsafe_allow_html=True)
            issues, _, _ = split_output(st.session_state.upload_result)
            st.markdown(issues)
            st.divider()

        # Repo
        for file in st.session_state.repo_results:
            st.markdown(section_header("📁", f"{file['file_name']}"),unsafe_allow_html=True)
            issues, _, _ = split_output(file["result"])
            st.markdown(issues)
            st.divider()

    with tab2:

        if st.session_state.upload_result:
            upload_label = (
                "Uploaded File" if st.session_state.analysis_source == "upload" else "Editor Input"
            )
            st.markdown(section_header("📂", upload_label),unsafe_allow_html=True)
            original_code = (
                st.session_state.upload_code
                if st.session_state.analysis_source == "upload"
                else st.session_state.editor_code
            )
            st.code(original_code, language=language.lower(), line_numbers=True)
            st.divider()

        for file in st.session_state.repo_results:
            st.markdown(section_header("📁", f"{file['file_name']}"),unsafe_allow_html=True)
            st.caption("Original code preview not shown")
            st.divider()

    with tab3:

        # Upload
        if st.session_state.upload_result:
            upload_label = (
                "Uploaded File" if st.session_state.analysis_source == "upload" else "Editor Input"
            )
            st.markdown(section_header("📂", upload_label),unsafe_allow_html=True)

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
    st.info("Upload code or enter repo to start analysis")
