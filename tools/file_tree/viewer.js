const DATA = __DATA__;
const nodes = DATA.nodes,
  $ = (id) => document.getElementById(id);
let selected = ".",
  opened = new Set([".", "SPDWEBAPP"]),
  notes = {},
  reviewed = {};
function elem(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined) e.textContent = text;
  return e;
}
const descendants = {};
function fileCount(path) {
  if (descendants[path] !== undefined) return descendants[path];
  const n = nodes[path];
  return (descendants[path] =
    n.kind === "file"
      ? 1
      : n.children.reduce((sum, p) => sum + fileCount(p), 0));
}
function fits(path) {
  const n = nodes[path],
    q = $("search").value.trim().toLowerCase();
  const self =
    (!q || (path + " " + n.description).toLowerCase().includes(q)) &&
    (!$("noted-only").checked || !!String(notes[path] || "").trim());
  return self || (n.kind === "folder" && n.children.some(fits));
}
function marker(path) {
  const m = elem("span", "marks");
  m.dataset.markPath = path;
  if (String(notes[path] || "").trim()) m.append(elem("span", "note-dot", "●"));
  if (reviewed[path]) m.append(elem("span", "", "👍"));
  return m;
}
function build(path) {
  if (!fits(path)) return null;
  const n = nodes[path];
  if (n.kind === "folder") {
    const d = elem("details");
    d.open =
      $("search").value.trim() !== "" ||
      $("noted-only").checked ||
      opened.has(path);
    const s = elem("summary", path === selected ? "selected" : "");
    s.dataset.path = path;
    s.append(
      elem("span", "arrow", "▸"),
      elem("span", "folder-icon", "▣"),
      elem("span", "node-name", n.name),
      marker(path),
    );
    s.addEventListener("click", () => select(path));
    d.append(s);
    const children = elem("div", "children");
    n.children.forEach((child) => {
      const item = build(child);
      if (item) children.append(item);
    });
    d.append(children);
    d.addEventListener("toggle", () => {
      if (d.open) opened.add(path);
      else opened.delete(path);
    });
    return d;
  }
  const b = elem("button", "file" + (path === selected ? " selected" : ""));
  b.type = "button";
  b.dataset.path = path;
  b.append(
    elem(
      "span",
      "file-icon",
      n.name.endsWith(".py") ? "py" : n.name.endsWith(".html") ? "<>" : "·",
    ),
    elem("span", "node-name", n.name),
    marker(path),
  );
  b.addEventListener("click", () => select(path));
  return b;
}
function renderTree() {
  const tree = $("tree");
  tree.replaceChildren();
  const item = build(".");
  if (item) tree.append(item);
  else
    tree.append(
      elem(
        "p",
        "empty",
        "No files match. Try another search or clear the notes filter.",
      ),
    );
  updateTally();
}
function reveal(path) {
  const parts = path === "." ? [] : path.split("/");
  opened.add(".");
  for (let i = 1; i < parts.length; i++)
    opened.add(parts.slice(0, i).join("/"));
  renderTree();
}
function select(path) {
  selected = path;
  renderDetail();
  document.querySelectorAll("[data-path]").forEach((el) => {
    el.classList.toggle("selected", el.dataset.path === path);
  });
}
function renderCrumbs() {
  const crumbs = $("crumbs");
  crumbs.replaceChildren();
  const home = elem("button", "", nodes["."].name);
  home.onclick = () => {
    select(".");
    reveal(".");
  };
  crumbs.append(home);
  if (selected !== ".") {
    const parts = selected.split("/");
    parts.forEach((part, i) => {
      crumbs.append(document.createTextNode(" / "));
      const b = elem("button", "", part);
      b.onclick = () => {
        select(parts.slice(0, i + 1).join("/"));
        reveal(selected);
      };
      crumbs.append(b);
    });
  }
}
function renderMetrics(n) {
  const metrics = $("metrics");
  metrics.replaceChildren();
  [
    n.kind === "folder" ? "Folder" : "File",
    n.kind === "folder"
      ? fileCount(selected) + " source files"
      : n.lines !== null
        ? n.lines + " physical lines"
        : Math.round(n.bytes / 1024) + " KB",
    selected.startsWith("SPDWEBAPP/railway_demo")
      ? "Demo layer"
      : selected.startsWith("SPDWEBAPP/")
        ? "Application"
        : "Repository root",
  ].forEach((text) => metrics.append(elem("span", "", text)));
}
function renderChildren(n, specifics) {
  specifics.append(elem("h3", "", "Inside this folder"));
  const list = elem("div", "entry-list");
  n.children.forEach((path) => {
    const child = nodes[path],
      b = elem("button", "entry");
    b.append(
      elem("span", "", child.kind === "folder" ? "▣" : "·"),
      elem("span", "node-name", child.name),
      elem(
        "small",
        "",
        child.kind === "folder"
          ? fileCount(path) + " files"
          : child.lines !== null
            ? child.lines + " lines"
            : "",
      ),
    );
    b.onclick = () => {
      select(path);
      reveal(path);
    };
    list.append(b);
  });
  specifics.append(list);
}
function renderContracts(n, specifics) {
  if (n.exports?.length) {
    specifics.append(elem("h3", "", "Defined here"));
    const list = elem("div", "code-list");
    n.exports.forEach((name) => list.append(elem("code", "", name)));
    specifics.append(list);
  }
  if (n.routes?.length) {
    specifics.append(elem("h3", "", "Local route patterns"));
    const list = elem("div", "code-list");
    n.routes.forEach((route) =>
      list.append(elem("code", "", route || "(empty path)")),
    );
    specifics.append(list);
  }
}
function renderDetail(keepDraft = false) {
  const n = nodes[selected];
  $("title").textContent = n.name;
  $("description").textContent = n.description;
  renderCrumbs();
  renderMetrics(n);
  $("source").href =
    "https://github.com/" +
    DATA.repo +
    "/" +
    (n.kind === "folder" ? "tree" : "blob") +
    "/" +
    DATA.sourceRef +
    (selected === "."
      ? ""
      : "/" + selected.split("/").map(encodeURIComponent).join("/"));
  const specifics = $("specifics");
  specifics.replaceChildren();
  if (n.kind === "folder") renderChildren(n, specifics);
  else renderContracts(n, specifics);
  if (!keepDraft) $("notes").value = String(notes[selected] || "");
  updateReview();
  updateTally();
}
function updateReview() {
  $("review").textContent = reviewed[selected]
    ? "👍 Reviewed"
    : "👍 Mark reviewed";
  $("review").classList.toggle("reviewed", !!reviewed[selected]);
  $("review").setAttribute("aria-pressed", String(!!reviewed[selected]));
}
function updateTally() {
  const nc = Object.keys(notes).filter(
      (k) => nodes[k] && String(notes[k]).trim(),
    ).length,
    rc = Object.keys(reviewed).filter((k) => nodes[k] && reviewed[k]).length;
  $("tally").textContent = nc + " selections with notes · " + rc + " reviewed";
}
function updateMarks() {
  document.querySelectorAll("[data-mark-path]").forEach((m) => {
    const path = m.dataset.markPath;
    m.replaceChildren();
    if (String(notes[path] || "").trim())
      m.append(elem("span", "note-dot", "●"));
    if (reviewed[path]) m.append(elem("span", "", "👍"));
  });
}
$("repo").textContent = DATA.repo;
$("branch").textContent = DATA.branch;
$("snapshot").textContent = DATA.snapshotLabel;
$("file-total").textContent = DATA.fileCount + " source files";
$("search").addEventListener("input", renderTree);
$("noted-only").onchange = renderTree;
$("expand").onclick = () => {
  Object.keys(nodes).forEach((p) => {
    if (nodes[p].kind === "folder") opened.add(p);
  });
  renderTree();
};
$("collapse").onclick = () => {
  opened = new Set([".", "SPDWEBAPP"]);
  renderTree();
};
$("notes").addEventListener("input", () => {
  notes[selected] = $("notes").value;
  persist();
});
$("review").onclick = () => {
  reviewed[selected] = !reviewed[selected];
  persist();
  updateReview();
};
