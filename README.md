# 2DES_CSV_Automator

This Python script extracts fluorescence scan data from a Tecan Excel workbook and exports one `csv` file per sample in a format compatible with **2DES_Studio**.

## What it does

- Prompts you to select:
  - the input Excel file
  - the output folder
- Prompts you for experiment-specific variables such as:
  - first sample row
  - last sample row
  - rows per scan
  - emission point count
  - points discarded per scan
  - first excitation row
  - last excitation row
  - emission wavelength row
- Lets you choose:
  - the plate map sheet
  - the raw data sheet
- Uses sample names from the plate map sheet if present - Format Sheet1 so that each sample name is entered into the Excel cell corresponding to its well position on the plate (e.g. A1, B1, etc.)
- Falls back to the well position (e.g. `A1`, `B3`) if no plate map name is provided
- Replaces `OVER` values with `1000000`
- Replaces negative values with `0`
- Saves one CSV per sample
- Remembers the last-used settings for the next run

---

## Requirements

- Python 3
- openpyxl
---
