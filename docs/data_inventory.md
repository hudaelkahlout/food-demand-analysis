# Data inventory

Inspected on 2026-10-27 (Asia/Hebron). All four required source files are present under `data/raw/` and were inspected in full without modification.

## Reproduction and scope

Run `python docs/inspect_phase1.py` from the project root (Python 3, standard library only). The read-only script emits JSON to stdout and does not write datasets. This run used the bundled Python 3 runtime. Counts exclude the CSV header. Types below are inferred from every non-missing field, since CSV files carry no declared types: integer means integer-formatted numeric values, decimal means finite numeric values including fractional values, and string means text. Identifier and location-code integers represent labels rather than continuous measurements.

Inspection used strict comma-delimited CSV parsing with UTF-8/BOM support, record-width checks, missing-marker checks (empty/whitespace, NA, NaN, null, none, N/A), numeric checks, key uniqueness, and reference-set comparisons. Reference checks do not merge tables. No cleaning, row deletion, analytical merge, statistical analysis, or modeling was performed.

## Files and dimensions

| File | Purpose | Rows | Columns | Primary / join keys | Important fields and notes |
| --- | --- | ---: | ---: | --- | --- |
| `train.csv` | Historical weekly demand | 456,548 | 9 | Unique non-missing `id`; unique (`week`, `center_id`, `meal_id`); join on `meal_id` and `center_id` | Target `num_orders`; pricing and promotion inputs; 145 distinct weeks, 1–145 |
| `test.csv` | Future prediction inputs | 32,573 | 8 | Unique non-missing `id`; unique (`week`, `center_id`, `meal_id`); same join keys | No target; 10 distinct weeks, 146–155 |
| `meal_info.csv` | Meal attributes | 51 | 3 | Unique non-missing `meal_id` | 14 categories and 4 cuisines |
| `fulfilment_center_info.csv` | Center attributes | 77 | 5 | Unique non-missing `center_id` | 51 city codes, 8 region codes, 3 center types; `op_area` ranges 0.9–7.0 |

All four filenames match the plan. Both demand files contain 77 distinct centers and 51 distinct meals. All observed `meal_id` and `center_id` values in both demand files exist in the corresponding lookup table: zero unmatched distinct keys. Each lookup has exactly one row per join key, supporting future many-to-one joins. No joins were performed in Phase 1.

## Columns and inferred data types

Columns are listed in source order. Every column in every file has zero detected missing values.

### `train.csv`

| Column | Inferred type | Role / note |
| --- | --- | --- |
| `id` | integer | Row identifier, unique and non-missing |
| `week` | integer | Sequential week index, 1–145; no calendar dates supplied |
| `center_id` | integer | Foreign key to center lookup |
| `meal_id` | integer | Foreign key to meal lookup |
| `checkout_price` | decimal | Observed price field, 2.97–866.27 |
| `base_price` | decimal | Reference price field, 55.35–866.27 |
| `emailer_for_promotion` | integer | Binary flag; observed values exactly 0 and 1 |
| `homepage_featured` | integer | Binary flag; observed values exactly 0 and 1 |
| `num_orders` | integer | Demand target, 13–24,299 |

### `test.csv`

| Column | Inferred type | Role / note |
| --- | --- | --- |
| `id` | integer | Row identifier, unique and non-missing |
| `week` | integer | Sequential week index, 146–155 |
| `center_id` | integer | Foreign key to center lookup |
| `meal_id` | integer | Foreign key to meal lookup |
| `checkout_price` | decimal | Observed price field, 67.90–1,113.62 |
| `base_price` | decimal | Reference price field, 89.24–1,112.62 |
| `emailer_for_promotion` | integer | Binary flag; observed values exactly 0 and 1 |
| `homepage_featured` | integer | Binary flag; observed values exactly 0 and 1 |

### `meal_info.csv`

| Column | Inferred type | Role / note |
| --- | --- | --- |
| `meal_id` | integer | Primary key and meal join key |
| `category` | string | Meal category label |
| `cuisine` | string | Cuisine label |

### `fulfilment_center_info.csv`

| Column | Inferred type | Role / note |
| --- | --- | --- |
| `center_id` | integer | Primary key and center join key |
| `city_code` | integer | Coded city label |
| `region_code` | integer | Coded region label |
| `center_type` | string | Center classification label |
| `op_area` | decimal | Operating-area field; unit not established from CSV alone |

## Train/test schema comparison

- Training has 9 columns; test has 8.
- `num_orders` is the only training-only column. There are no test-only columns.
- All eight shared column names, their order, and inferred types match exactly.
- Training covers weeks 1–145; test covers weeks 146–155. Week ranges do not overlap.
- Zero overlapping `id` values between training and test.
- Test price maxima exceed training price maxima. This is an observed range difference, not a parsing error.

## Basic integrity findings and relevant notes

| Check | train.csv | test.csv | meal_info.csv | fulfilment_center_info.csv |
| --- | ---: | ---: | ---: | ---: |
| Malformed field-count records | 0 | 0 | 0 | 0 |
| Detected missing cells (all columns) | 0 | 0 | 0 | 0 |
| Invalid/non-finite numeric fields | 0 | 0 | 0 | 0 |
| Duplicate primary-key rows beyond first occurrence | 0 | 0 | 0 | 0 |
| Duplicate logical-key rows beyond first occurrence | 0 | 0 | 0 | 0 |

No CSV parse errors or duplicate header names were encountered. Logical keys for demand files are (`week`, `center_id`, `meal_id`); for lookup files they equal the primary key. Unique primary keys also rule out exact duplicate full records in these files.

`checkout_price > base_price` occurs in 116,101 training rows and 8,937 test rows. These observations remain intact and need investigation in the later data-quality phase; they are not automatically errors. Both price fields are strictly positive in both files. Promotion flags are binary, and observed training order counts are positive integers.

Currency, the operating-area unit, actual calendar dates, and the meaning of absent center-meal-week observations are not established from these CSVs alone. Phase 1 does not claim that all business-level data-quality questions are resolved.

## Source integrity and Git exclusion

SHA-256 hashes matched before and after full inspection and were independently rechecked with PowerShell. File sizes are included for traceability.

| File | Bytes | SHA-256 (before = after) |
| --- | ---: | --- |
| `train.csv` | 18,733,819 | `a2ed2d7c6905d63a9361d8dd35bc06c8a597831f7185644e0f33ad7bfe20cc81` |
| `test.csv` | 1,266,196 | `71a929bf2f043bf98748acb9d274258fe4c68c19592be1e26aca7dc1f1c8eda5` |
| `meal_info.csv` | 1,096 | `9d8045af391c492f531c928d7f3d58581c80d0594776d1f4e53c8b29bbff8f75` |
| `fulfilment_center_info.csv` | 1,661 | `c874f74fa392b2c4dd24a167f32a5bee68a444b8bf151acf295cd5d66aa0517f` |

Real `git check-ignore --no-index -v` checks matched `.gitignore` line 2 (`/data/`) for all four actual CSV paths and arbitrary-format probes in raw and processed data. The project has no `.git` directory, so the checks used isolated temporary Git metadata with this workspace as the work tree. No project Git initialization, commit, or push occurred. Tracking/staging checks are not applicable until a repository exists; ignore rules do not remove previously tracked files.
