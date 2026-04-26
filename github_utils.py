import requests

def parse_github_url(url):
    try:
        url = url.strip().replace("https://github.com/", "")
        url = url.replace(".git", "")   # ✅ REMOVE .git

        parts = [p for p in url.split("/") if p]

        if len(parts) < 2:
            return None, None

        return parts[0], parts[1]
    except:
        return None, None


def get_repo_files(user, repo):
    url = f"https://api.github.com/repos/{user}/{repo}/contents"
    response = requests.get(url)

    if response.status_code != 200:
        return []

    try:
        data = response.json()
    except:
        return []

    if isinstance(data, str):
        return []

    return data


def get_code_files(files):
    if not isinstance(files, list):
        return []

    return [
        f for f in files
        if isinstance(f, dict)
        and f.get("type") == "file"
        and f.get("name", "").endswith((
            ".js", ".py", ".java", ".cpp", ".c", ".ts", ".jsx", ".tsx"
        ))
    ]


def get_file_content(url):
    try:
        res = requests.get(url)
        if res.status_code != 200:
            return ""
        return res.text
    except:
        return ""


def detect_language_from_filename(filename):
    if filename.endswith(".js"):
        return "javascript"
    elif filename.endswith(".py"):
        return "python"
    elif filename.endswith(".java"):
        return "java"
    elif filename.endswith(".cpp") or filename.endswith(".c"):
        return "cpp"
    else:
        return "text"