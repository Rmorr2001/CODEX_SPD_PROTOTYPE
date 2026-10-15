# Build-time file explorer

Owns the generated source-tree viewer published at
`/static/railway_demo/file-tree.html`. The Docker build runs `build.py` in a
separate source stage, then copies only the generated HTML into the app stage
before `collectstatic`. No generator dependency is added to the runtime.

## Boundaries and entry points

- `build.py`: Git-tracked inventory locally; clean build-context inventory when
  Docker excludes `.git`. Excludes generated output, runtime/private data,
  environment files, keys, virtualenv/cache folders, and outside symlinks.
- `metadata.py` / `descriptions.py`: purpose labels, physical line counts,
  Python definitions, and literal route names. Configuration contents are never
  read. Source modules are parsed, never executed. No file contents are embedded.
- `viewer.html`, `viewer.css`, `details.css`, `viewer.js`: responsive tree,
  selection details, search, and review UI.
- `notes.js`: versioned browser/widget state, migration from snapshot-specific
  storage, and export including notes for removed files.
- `test_build.py`: standalone standard-library generator checks.

The repository/branch defaults identify this demo. `--commit` accepts a full Git
object ID. In Docker, `RAILWAY_GIT_COMMIT_SHA` supplies it when available; without
it the display clearly labels a manifest digest instead. No credential binding
is needed to generate the tree. This is refreshed at build time, not on every
request, and does not expose a live filesystem endpoint.

## Generate and verify

From the repository root:

```sh
python tools/file_tree/build.py --root . --output SPDWEBAPP/railway_demo/static/railway_demo/file-tree.html
python -m unittest discover -s tools/file_tree -p 'test_*.py'
node --check tools/file_tree/viewer.js
node --check tools/file_tree/notes.js
```

Run `collectstatic` afterward for local Gunicorn/WhiteNoise serving, as documented
in the [demo README](../../SPDWEBAPP/railway_demo/README.md). Generated HTML is
ignored by Git and excluded from its own source manifest. Browser review state
belongs to the viewer's origin/browser. Migration keeps the old stored copy and
only writes the repository-scoped key when a user changes a note or review mark.
The static header callback in the demo layer revalidates this HTML on reload.
