"""Generate the self-contained source explorer from a clean build context."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from metadata import build_nodes

SKIP_FOLDERS = {".git", ".venv", "venv", "node_modules", "__pycache__",
                "staticfiles", "media", "work", "output", ".pytest_cache"}
SKIP_SUFFIXES = {".pyc", ".sqlite3", ".db", ".pem", ".key", ".p12", ".pfx"}
GENERATED = "SPDWEBAPP/railway_demo/static/railway_demo/file-tree.html"
REPOSITORY = "Rmorr2001/SPDWEBAPP_ENV"
DEFAULT_BRANCH = "demo/sebe-mizzou-railway"


def allowed(relative: str) -> bool:
    path = Path(relative)
    return (not any(part in SKIP_FOLDERS for part in path.parts)
            and not any(part.startswith(".env") for part in path.parts)
            and path.suffix.lower() not in SKIP_SUFFIXES and relative != GENERATED)


def source_paths(root: Path) -> list[str]:
    """Use Git's tracked list locally; Docker uses its clean, filtered context."""
    if (root / ".git").exists():
        result = subprocess.run(["git", "ls-files", "-z"], cwd=root,
                                capture_output=True, check=True)
        candidates = result.stdout.decode().split("\0")
    else:
        candidates = [path.relative_to(root).as_posix() for path in root.rglob("*")]
    return sorted(relative for relative in candidates if relative and allowed(relative)
                  and not (root / relative).is_symlink()
                  and (root / relative).resolve().is_relative_to(root.resolve())
                  and (root / relative).is_file())


def git_commit(root: Path) -> str:
    if not (root / ".git").exists():
        return ""
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                            capture_output=True, check=False)
    return result.stdout.decode().strip() if result.returncode == 0 else ""


def build_data(root: Path, commit: str = "", branch: str = DEFAULT_BRANCH) -> dict:
    """Create safe metadata, with an exact commit or an honest manifest digest."""
    commit = commit or git_commit(root)
    if commit and not re.fullmatch(r"[0-9a-fA-F]{40,64}", commit):
        raise ValueError("Commit must be a full hexadecimal Git object ID.")
    nodes = build_nodes(root, source_paths(root))
    digest = hashlib.sha256(json.dumps(nodes, sort_keys=True).encode()).hexdigest()
    return {"nodes": nodes, "repo": REPOSITORY, "branch": branch,
            "commit": commit, "snapshotId": commit or digest,
            "snapshotLabel": f"Commit {commit[:7]}" if commit else f"Build manifest {digest[:7]}",
            "sourceRef": commit or branch,
            "fileCount": sum(node["kind"] == "file" for node in nodes.values())}


def render(root: Path, output: Path, commit: str = "", branch: str = DEFAULT_BRANCH) -> dict:
    """Write a fresh viewer; generated output never enters its own manifest."""
    assets = Path(__file__).parent
    data = build_data(root, commit, branch)
    script = (assets / "viewer.js").read_text() + "\n" + (assets / "notes.js").read_text()
    script += "\nrenderTree(); renderDetail();"
    payload = json.dumps(data, ensure_ascii=True).replace("<", "\\u003c")
    script = script.replace("__DATA__", payload)
    html = (assets / "viewer.html").read_text().replace(
        "__STYLE__", (assets / "viewer.css").read_text() + (assets / "details.css").read_text()).replace("__SCRIPT__", script)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html)
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--commit", default="")
    parser.add_argument("--branch", default=DEFAULT_BRANCH)
    args = parser.parse_args()
    data = render(args.root.resolve(), args.output, args.commit, args.branch)
    print(f"Generated file explorer: {data['fileCount']} source files, {data['snapshotLabel']}.")


if __name__ == "__main__":
    main()
