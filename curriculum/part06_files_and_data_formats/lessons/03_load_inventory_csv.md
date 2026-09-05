# Loading CSV

--- teach #card-c56a34e473be57bb
### Never split CSV on commas by hand
A quoted cell can contain a comma: `"mbp-quoted, with comma"`. `split(",")` would cut it in two. The `csv` module knows the rules. `csv.reader` gives a list per row; it works on a file or on any list of strings.
```python
>>> import csv
>>> list(csv.reader(['serial,hostname', '"C02","lab, box"']))
[['serial', 'hostname'], ['C02', 'lab, box']]
```

--- predict #card-f6a58a9705c354a9
What does this print?
```python
import csv
rows = list(csv.reader(['a,b', '"x, y",1']))
print(rows[1])
```
answer: ['x, y', '1']
> The quoted cell stays one value, comma and all. Note that `1` came back as the string `'1'`.

--- teach #card-e5245f5b8a8a54d3
### `DictReader` uses the header row as keys
`csv.DictReader` reads the first row as column names and gives you a dict per data row. `reader.fieldnames` is the header list, or `None` for an empty file. Every cell is a `str`, even the numbers.
```python
>>> reader = csv.DictReader(['serial,ram_gb', 'C02XG,16'])
>>> reader.fieldnames
['serial', 'ram_gb']
>>> next(reader)
{'serial': 'C02XG', 'ram_gb': '16'}
```
Open CSV files with `encoding="utf-8"` and `newline=""`; the second one stops Windows from mangling line endings inside quoted cells.

--- predict #card-9dcf03167ac352da
What does this print?
```python
import csv
row = next(csv.DictReader(['serial,ram_gb', 'C02XG,16']))
print(type(row["ram_gb"]).__name__)
```
answer: str
> CSV has no types. `'16'` is text until you call `int()` on it yourself.

--- teach #card-0459a0ab4f6c55e9
### Short and long rows
`DictReader` does not complain about rows of the wrong length. A short row fills the missing columns with `None`. A long row puts the extra cells in a list under the key `None`. Both are your "malformed row" signal.
```python
>>> list(csv.DictReader(['a,b,c', '1,2']))
[{'a': '1', 'b': '2', 'c': None}]
>>> list(csv.DictReader(['a,b', '1,2,3']))
[{'a': '1', 'b': '2', None: ['3']}]
```
So: `if None in row` catches long rows, and `row.get(key) is None` catches short ones.

--- quiz #card-2290d5178d325804
A CSV header has three columns and a data row has two cells. What does `DictReader` produce for that row?
- [x] A dict where the third column's value is `None`
- [ ] A dict with only two keys
- [ ] It raises `ValueError`
> `DictReader` keeps every header key and fills missing cells with `None`. It never raises for row length; that check is yours.

--- teach #card-07c7d59a157e5ac0
### Converting cells, and surviving when it fails
`int("sixteen")` raises `ValueError`. To skip that row instead of crashing, wrap the conversion in `try` / `except`: run the `try` block, and if a `ValueError` is raised, jump to the `except` block.
```python
try:
    ram_gb = int(cells["ram_gb"])
    disk_pct = float(cells["disk_pct"])
except ValueError:
    continue                 # malformed row: skip it
```
Keep only the conversions inside `try`, so you know exactly which line can fail. Strip each cell first: `int(" 8 ")` works, but the spec asks for stripped text in the output too.

--- code #card-0facd3c7c9635ee9
Append `int()` of each row's stripped `ram_gb` cell to `values`, skipping rows where the conversion raises `ValueError`.
```python
raw_rows = [{"ram_gb": "16"}, {"ram_gb": "sixteen"}, {"ram_gb": " 8 "}]
values = []
```
check: values == [16, 8]
solution: for raw in raw_rows:
solution:     try:
solution:         values.append(int(raw["ram_gb"].strip()))
solution:     except ValueError:
solution:         continue
> Only the conversion sits inside `try`. `"sixteen"` raises `ValueError`, the `except` runs `continue`, and the loop carries on with the next row.

--- fill #card-0a3bc9d4844656c0
Complete the code so a bad number skips the row instead of crashing.
```python
try:
    ram_gb = int(cells["ram_gb"])
except ___:
    continue
```
answer: ValueError
> `int()` on text that is not a whole number raises `ValueError`. Naming that one exception keeps other bugs visible.

--- teach #card-5802e395497659c5
### Check the header once, before the loop
The header may have extra columns (ignore them) or be missing a required one (raise `ValueError`). An empty file has `fieldnames` of `None`; treat that as "no rows" and return `[]`.
```python
header = reader.fieldnames or []
if header:
    missing = [c for c in REQUIRED if c not in header]
    if missing:
        raise ValueError(f"missing columns: {missing}")
```

--- exercise 6.3 #card-8c0696a815f75b95

--- recap #card-c87bc8ab076b51fd
- `csv.DictReader` handles quoting and gives a dict per row; every cell is a `str`.
- Open with `encoding="utf-8", newline=""`.
- Short rows have `None` values; long rows have a `None` key.
- `try: int(...) except ValueError: continue` skips rows that will not convert.
- Validate the header with `reader.fieldnames` before looping.
