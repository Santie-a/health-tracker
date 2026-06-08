# nutrition_core

Shared, in-repo package: the food-name matcher (`MacroTable`) + the bundled
per-100g macro table (`data/macros.csv`). One matcher, two consumers
(image-svc photo estimation and the server's manual/serving entry) so a name like
"rice" resolves identically on both paths and the data has a single
`TABLE_VERSION`.

## Use

```python
from nutrition_core import MacroTable, TABLE_VERSION, default_macro_csv

table = MacroTable.from_csv(default_macro_csv())
row = table.lookup("grilled chicken breast")   # -> MacroRow | None
```

## Install (editable, per service venv)

```bash
# from the consuming service's directory, into its venv
pip install -e ../packages/nutrition_core
```

Both `server/requirements.txt` and `image-svc/requirements.txt` list it as an
editable path dependency. Because it's installed (not fetched), the bundled CSV is
always on local disk — the services stay network-independent, and the Docker
images bake the data in at build time.

## Updating the macro data

Edit `nutrition_core/data/macros.csv` (columns: `name,aliases,kcal,protein_g,
carbs_g,fat_g`; `aliases` is `;`-separated), then bump `TABLE_VERSION` in
`nutrition_core/__init__.py`. Both services pick up the change after reinstall.
