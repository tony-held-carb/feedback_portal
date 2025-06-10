from pathlib import Path

import mkdocs_gen_files

SRC_ROOT = Path("arb")

for path in sorted(SRC_ROOT.rglob("*.py")):
    if path.name == "__init__.py":
        continue

    # Convert path to module path (e.g., arb/utils/json.py -> arb.utils.json)
    module_path = path.with_suffix("").as_posix().replace("/", ".")
    doc_path = path.with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    # Write the ::: directive into the markdown file
    with mkdocs_gen_files.open(full_doc_path, "w") as f:
        f.write(f"# `{module_path}`\n\n")
        f.write(f"::: {module_path}\n")

    mkdocs_gen_files.set_edit_path(full_doc_path, path)
