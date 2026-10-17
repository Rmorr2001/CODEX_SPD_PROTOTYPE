const stableKey = "spd-tree-notes:" + DATA.repo;
const repositoryNames = [DATA.repo, ...(DATA.repositoryAliases || [])];
const validState = (s) =>
  s &&
  (s.version === 1 || s.version === 2) &&
  (!s.repository || repositoryNames.includes(s.repository));
function applyState(s) {
  if (!validState(s)) return;
  notes = s.notes && typeof s.notes === "object" ? s.notes : {};
  reviewed = s.reviewed && typeof s.reviewed === "object" ? s.reviewed : {};
}
let shared = false;
try {
  if (validState(window.openai?.widgetState)) {
    applyState(window.openai.widgetState);
    shared = true;
  } else {
    // A repository rename must not discard existing browser review notes.
    const prior = repositoryNames
      .map((name) => JSON.parse(localStorage.getItem("spd-tree-notes:" + name) || "null"))
      .find(validState);
    if (validState(prior)) {
      applyState(prior);
    } else {
      // Migrate the original snapshot's notes without deleting that saved copy.
      const legacy = [];
      for (let i = 0; i < localStorage.length; i++) {
        const k = localStorage.key(i);
        if (k.startsWith("spd-tree-") && !k.startsWith("spd-tree-notes:")) {
          try {
            const old = JSON.parse(localStorage.getItem(k));
            if (validState(old)) legacy.push(old);
          } catch (e) {}
        }
      }
      legacy.forEach((old) => {
        Object.assign(notes, old.notes || {});
        Object.assign(reviewed, old.reviewed || {});
      });
    }
  }
} catch (e) {}
function persist() {
  const state = {
    version: 2,
    repository: DATA.repo,
    commit: DATA.commit,
    notes,
    reviewed,
  };
  let local = false;
  try {
    localStorage.setItem(stableKey, JSON.stringify(state));
    local = true;
  } catch (e) {}
  if (typeof window.openai?.setWidgetState === "function") {
    try {
      const result = window.openai.setWidgetState(state);
      shared = true;
      Promise.resolve(result).catch(() => {
        $("save-state").textContent = "Keep a copy via export";
      });
    } catch (e) {
      shared = false;
    }
  }
  $("save-state").textContent = shared
    ? "Saved with this visualization"
    : local
      ? "Saved in this browser"
      : "Kept in this view · export to keep";
  updateTally();
  updateMarks();
}
window.addEventListener("openai:set_globals", (e) => {
  const s = e.detail?.globals?.widgetState;
  if (!validState(s)) return;
  applyState(s);
  shared = true;
  renderTree();
  renderDetail(document.activeElement === $("notes"));
});
function exportData() {
  return {
    repository: DATA.repo,
    branch: DATA.branch,
    commit: DATA.commit,
    entries: [
      ...new Set([
        ...Object.keys(nodes),
        ...Object.keys(notes),
        ...Object.keys(reviewed),
      ]),
    ]
      .filter((path) => String(notes[path] || "").trim() || reviewed[path])
      .map((path) => ({
        path,
        removed: !nodes[path],
        reviewed: !!reviewed[path],
        notes: String(notes[path] || ""),
      })),
  };
}
function exportText() {
  const d = exportData();
  return (
    "# CODEX-SPD-PROTOTYPE review notes\n\nRepository: " +
    d.repository +
    "\nBranch: " +
    d.branch +
    "\nBuild: " +
    DATA.snapshotLabel +
    "\n\n" +
    (d.entries.length
      ? d.entries
          .map(
            (n) =>
              "## " +
              n.path +
              (n.removed ? " (removed from this build)" : "") +
              "\n" +
              (n.reviewed ? "Reviewed: yes\n" : "") +
              (n.notes || "(Reviewed, no notes yet)"),
          )
          .join("\n\n")
      : "No notes or review marks yet.")
  );
}
let previousFocus = null;
$("export").onclick = () => {
  previousFocus = document.activeElement;
  $("export-text").value = exportText();
  $("modal").classList.add("open");
  $("close").focus();
};
function closeModal() {
  $("modal").classList.remove("open");
  previousFocus?.focus();
}
$("close").onclick = closeModal;
$("modal").onclick = (e) => {
  if (e.target === $("modal")) closeModal();
};
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeModal();
});
$("copy").onclick = async () => {
  try {
    await navigator.clipboard.writeText($("export-text").value);
    $("copy").textContent = "Copied";
  } catch (e) {
    $("export-text").focus();
    $("export-text").select();
    $("copy").textContent = "Select & copy text";
  }
};
$("download").onclick = () => {
  const blob = new Blob([JSON.stringify(exportData(), null, 2)], {
      type: "application/json",
    }),
    url = URL.createObjectURL(blob),
    a = document.createElement("a");
  a.href = url;
  a.download = "codex-spd-prototype-review-notes.json";
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
};
