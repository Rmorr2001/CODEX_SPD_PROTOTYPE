"""Small explicit state snapshots; never copy a real database or inspect secrets."""
from copy import deepcopy
from pathlib import Path


def _row_state(model, pk):
    fresh = model.objects.filter(pk=pk).values().first()
    return deepcopy(fresh)


def _relation_state(relation):
    return tuple(sorted(relation.values_list("pk", flat=True)))


def snapshot_scope(named_rows, *, relations=(), files=()):
    """Capture selected saved rows, managers, and synthetic file bytes before action."""
    if isinstance(named_rows, dict):
        named_rows = named_rows.values()
    rows = [(row, type(row), row.pk, _row_state(type(row), row.pk)) for row in named_rows]
    relation_items = relations.items() if isinstance(relations, dict) else enumerate(relations)
    relation_values = []
    for key, relation in relation_items:
        if isinstance(relation, tuple) and len(relation) == 2 and isinstance(relation[1], str):
            relation = getattr(relation[0], relation[1])
        relation_values.append((key, relation, _relation_state(relation)))
    file_items = files.items() if isinstance(files, dict) else enumerate(files)
    file_values = []
    for key, file in file_items:
        path = Path(file.path if hasattr(file, "path") else file)
        file_values.append((key, path, path.read_bytes() if path.is_file() else None))
    return {"rows": rows, "relations": relation_values, "files": file_values}


def assert_unchanged(before, *, except_fields=None):
    """Assert fresh state, allowing only explicit row fields or relation/file keys."""
    exceptions = except_fields or {}
    for row, model, pk, previous in before["rows"]:
        current = _row_state(model, pk)
        try:
            allowed = exceptions.get(row, exceptions.get((model, pk), set()))
        except TypeError:  # Django clears an instance's PK after delete().
            allowed = exceptions.get((model, pk), set())
        if previous is None or current is None:
            if previous != current and "__deleted__" not in allowed:
                raise AssertionError(f"Row existence changed: {row._meta.label} pk={pk}")
            continue
        changes = {name for name in previous if previous[name] != current[name]}
        unexpected = changes - set(allowed)
        if unexpected:
            raise AssertionError(f"Unexpected changes in {row._meta.label} pk={pk}: {sorted(unexpected)}")
    for key, relation, previous in before["relations"]:
        if key not in exceptions.get("relations", ()) and _relation_state(relation) != previous:
            raise AssertionError(f"Relation changed: {key}")
    for key, path, previous in before["files"]:
        current = path.read_bytes() if path.is_file() else None
        if key not in exceptions.get("files", ()) and current != previous:
            raise AssertionError(f"Synthetic file changed: {key}")
