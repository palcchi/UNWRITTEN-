# Handcrafted overrides

Before refining generated files, copy them here with their repository-relative paths.
Example: `source_overrides/blockbench/colossi/little_morrow.bbmodel`.

The build copies these files over generated outputs. If you change a Blockbench file,
also export the matching geometry, PNG and animation JSON into matching `packs/...`
override paths. The generator does not re-export arbitrary edited Blockbench files.
The validator detects mismatched texture or animation counts, but cannot prove that
hand-edited geometry and its runtime export are identical.
