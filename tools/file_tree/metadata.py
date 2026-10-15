"""Describe source files without executing modules or exposing configuration."""
import ast
from pathlib import Path
from descriptions import domains, rootdesc, generic

CONFIG_NAMES = {"secret_config.py", "secrets_config.py", "settings.py"}
TEXT_SUFFIXES = {".py", ".html", ".css", ".md", ".txt", ".json", ".js"}
FOLDERS = {
    "templates": "Server-rendered HTML templates owned by this area.",
    "migrations": "Versioned database schema history, including generated migrations.",
    "management": "Custom Django management commands.",
    "commands": "Commands callable through manage.py.",
    "templatetags": "Custom Django template tags and filters.",
    "css": "Stylesheets used by the site.",
    "images": "Public image assets from the original repository.",
    "tools": "Build and maintenance tools, separate from business domains.",
    "file_tree": "Build-time file explorer generator, viewer sources, and tests.",
}


def python_contracts(source: str, name: str) -> tuple[list[str], list[str]]:
    """Extract names and literal route patterns without importing source code."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return [], []
    definitions = (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
    exports = [node.name for node in tree.body if isinstance(node, definitions)]
    routes = []
    if name == "urls.py":
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id in {"path", "re_path"} and node.args
                    and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, str)):
                routes.append(node.args[0].value)
    return exports, routes


def describe_file(root: Path, relative: str) -> dict:
    """Return safe metadata; configuration files are listed but never read."""
    path = root / relative
    description = rootdesc.get(relative, generic.get(path.name, ""))
    lines, exports, routes = None, [], []
    if path.name not in CONFIG_NAMES and (path.suffix.lower() in TEXT_SUFFIXES
            or path.name in {"Dockerfile", ".gitignore", ".dockerignore"}):
        source = path.read_text(errors="replace")
        lines = len(source.splitlines())
        if path.suffix == ".py":
            exports, routes = python_contracts(source, path.name)
    if "/migrations/" in relative and path.name != "__init__.py":
        description = "Existing generated Django database migration."
    elif path.name == "tests.py" and not exports:
        description = "Existing test scaffold; no test classes or functions are defined here."
    elif path.suffix == ".html":
        description = f"Django HTML template for {path.stem.replace('_', ' ')}."
    elif path.suffix.lower() == ".css":
        description = f"Styles for {path.stem.replace('_', ' ')}."
    elif path.suffix.lower() in {".png", ".webp", ".jpg", ".jpeg"}:
        description = "Public image asset; image data is not included in this explorer."
    if path.name == "seed_railway_demo.py":
        description = "Seeds real app models with fictional members and workflow records."
    if relative == "SPDWEBAPP/railway_demo/tests.py":
        description = "Implemented demo tests covering routes, roles, seeding, and interactions."
    return {"path": relative, "name": path.name, "kind": "file",
            "description": description or "Project source file.", "lines": lines,
            "bytes": path.stat().st_size, "exports": exports, "routes": routes}


def build_nodes(root: Path, paths: list[str]) -> dict:
    nodes = {".": {"path": ".", "name": "SPDWEBAPP_ENV", "kind": "folder",
                   "description": "The source tree included in this deployment build.",
                   "children": []}}
    for relative in paths:
        parts = relative.split("/")
        for index in range(1, len(parts)):
            folder = "/".join(parts[:index])
            name = parts[index - 1]
            nodes.setdefault(folder, {"path": folder, "name": name, "kind": "folder",
                "description": domains.get(name, FOLDERS.get(name, "Application folder.")),
                "children": []})
        nodes[relative] = describe_file(root, relative)
    for relative in paths + [p for p, n in nodes.items() if n["kind"] == "folder" and p != "."]:
        parent = relative.rsplit("/", 1)[0] if "/" in relative else "."
        nodes[parent]["children"].append(relative)
    for node in nodes.values():
        if node["kind"] == "folder":
            node["children"].sort(key=lambda p: (nodes[p]["kind"] != "folder", nodes[p]["name"].lower()))
    return nodes
