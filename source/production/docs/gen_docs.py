from pathlib import Path

import mkdocs_gen_files

SRC_ROOT = Path("arb")

def generate_docs() -> None:
  """
  Generate documentation files for all Python modules in the arb package.
  
  This function walks through all Python files in the arb directory and creates
  corresponding markdown documentation files with mkdocs-gen-files directives.
  
  Returns:
      None: This function generates files but doesn't return anything.
      
  Examples:
      # Called automatically by mkdocs-gen-files
      # Generates documentation for all Python modules
  """
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
