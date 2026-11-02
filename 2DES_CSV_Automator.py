import csv
import json
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from openpyxl import load_workbook

OVER_VALUE = 1000000
SETTINGS_FILE = Path("tecan_export_settings.json")


def load_settings():
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def pick_file(title, filetypes, initial_dir=""):
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askopenfilename(title=title, filetypes=filetypes, initialdir=initial_dir)
    root.destroy()
    return path


def pick_folder(title, initial_dir=""):
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askdirectory(title=title, initialdir=initial_dir)
    root.destroy()
    return path


def ask_string(title, prompt, initial=""):
    root = tk.Tk()
    root.withdraw()
    value = simpledialog.askstring(title, prompt, initialvalue=str(initial), parent=root)
    root.destroy()
    return value


def ask_int(title, prompt, initial):
    while True:
        root = tk.Tk()
        root.withdraw()
        value = simpledialog.askstring(title, prompt, initialvalue=str(initial), parent=root)
        root.destroy()

        if value is None:
            raise SystemExit("Cancelled by user.")

        try:
            return int(value)
        except ValueError:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Invalid input", f"Please enter an integer for:\n{prompt}", parent=root)
            root.destroy()


def clean_value(value):
    if value == "OVER":
        return OVER_VALUE
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        return 0 if value < 0 else value
    try:
        num = float(value)
        return 0 if num < 0 else num
    except Exception:
        return value


def get_plate_name(plate_sheet, well_id):
    try:
        value = plate_sheet[well_id].value
    except Exception:
        return well_id

    if value is None:
        return well_id

    value = str(value).strip()
    return value if value else well_id


def choose_sheet_name(sheetnames, prompt, default_name):
    sheet_list = "\n".join(sheetnames)
    while True:
        chosen = ask_string(
            "Sheet Selection",
            f"{prompt}\n\nAvailable sheets:\n{sheet_list}",
            default_name
        )
        if chosen is None:
            raise SystemExit("Cancelled by user.")
        if chosen in sheetnames:
            return chosen

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Invalid sheet name",
            f"'{chosen}' is not one of the workbook sheets.\n\nAvailable sheets:\n{sheet_list}",
            parent=root
        )
        root.destroy()


def main():
    settings = load_settings()

    last_excel_dir = settings.get("last_excel_dir", "")
    last_output_dir = settings.get("last_output_dir", "")

    excel_path = pick_file(
        "Select the Tecan Excel file",
        [("Excel files", "*.xlsx *.xlsm")],
        initial_dir=last_excel_dir
    )
    if not excel_path:
        raise SystemExit("No Excel file selected.")

    output_folder = pick_folder(
        "Select the output folder for CSV files",
        initial_dir=last_output_dir
    )
    if not output_folder:
        raise SystemExit("No output folder selected.")

    first_sample_row = ask_int("Flow Variables", "First sample row", settings.get("first_sample_row", 36))
    last_sample_row = ask_int("Flow Variables", "Last sample row", settings.get("last_sample_row", 75))
    rows_per_scan = ask_int("Flow Variables", "Rows per scan", settings.get("rows_per_scan", 69))
    emission_point_count = ask_int("Flow Variables", "Emission point count", settings.get("emission_point_count", 115))
    points_discarded_per_scan = ask_int("Flow Variables", "Points discarded per scan", settings.get("points_discarded_per_scan", 3))
    first_excitation_row = ask_int("Flow Variables", "First excitation row", settings.get("first_excitation_row", 21))
    last_excitation_row = ask_int("Flow Variables", "Last excitation row", settings.get("last_excitation_row", 2643))
    emission_row = ask_int("Flow Variables", "Emission wavelength row", settings.get("emission_row", 35))

    number_of_scans = ((last_excitation_row - first_excitation_row) // rows_per_scan) + 1

    wb = load_workbook(excel_path, data_only=True)

    print("Workbook sheets:", wb.sheetnames)
    if len(wb.sheetnames) < 2:
        raise SystemExit("Workbook does not contain at least two worksheets.")

    default_plate_sheet = settings.get("plate_sheet_name", wb.sheetnames[0])
    default_raw_sheet = settings.get("raw_sheet_name", wb.sheetnames[1] if len(wb.sheetnames) > 1 else wb.sheetnames[0])

    plate_sheet_name = choose_sheet_name(wb.sheetnames, "Enter the plate map sheet name", default_plate_sheet)
    raw_sheet_name = choose_sheet_name(wb.sheetnames, "Enter the raw data sheet name", default_raw_sheet)

    plate_sheet = wb[plate_sheet_name]
    raw_sheet = wb[raw_sheet_name]

    print("Using plate map sheet:", plate_sheet.title)
    print("Using raw data sheet:", raw_sheet.title)
    print("First sample row:", first_sample_row)
    print("Last sample row:", last_sample_row)
    print("Rows per scan:", rows_per_scan)
    print("Emission point count:", emission_point_count)
    print("Points discarded per scan:", points_discarded_per_scan)
    print("First excitation row:", first_excitation_row)
    print("Last excitation row:", last_excitation_row)
    print("Emission wavelength row:", emission_row)
    print("Calculated number of scans:", number_of_scans)
    print("Output folder:", output_folder)

    emission_wavelengths = []
    for col in range(2, 2 + emission_point_count):
        emission_wavelengths.append(raw_sheet.cell(row=emission_row, column=col).value)

    excitation_wavelengths = []
    for scan_index in range(number_of_scans):
        excitation_row = first_excitation_row + scan_index * rows_per_scan
        excitation_wavelengths.append(raw_sheet.cell(row=excitation_row, column=5).value)

    output_folder = Path(output_folder)
    files_written = 0

    for sample_row in range(first_sample_row, last_sample_row + 1):
        well_id = raw_sheet.cell(row=sample_row, column=1).value
        print(f"Row {sample_row}, col A raw value: {well_id!r}")

        if well_id is None:
            print(f"Skipping row {sample_row}: empty well id")
            continue

        well_id = str(well_id).strip()
        if not well_id:
            print(f"Skipping row {sample_row}: blank well id after strip")
            continue

        sample_name = get_plate_name(plate_sheet, well_id)
        output_path = output_folder / f"{sample_name}.csv"
        print(f"About to save: {output_path}")

        matrix_columns = []
        for scan_index in range(number_of_scans):
            current_row = sample_row + scan_index * rows_per_scan
            current_points_to_read = emission_point_count - scan_index * points_discarded_per_scan

            if current_points_to_read <= 0:
                print(f"Stopping scans for row {sample_row}: no points left to read")
                break

            column_values = []
            for col in range(2, 2 + current_points_to_read):
                raw_value = raw_sheet.cell(row=current_row, column=col).value
                column_values.append(clean_value(raw_value))

            matrix_columns.append(column_values)

        if not matrix_columns:
            print(f"Skipping row {sample_row}: no scan data collected")
            continue

        table = []

        header_row = [""]
        for value in excitation_wavelengths[:len(matrix_columns)]:
            header_row.append(value)
        table.append(header_row)

        for i in range(emission_point_count):
            row = [emission_wavelengths[i] if i < len(emission_wavelengths) else ""]
            for scan_index, column_values in enumerate(matrix_columns):
                if i < scan_index * points_discarded_per_scan:
                    row.append("")
                else:
                    shifted_index = i - scan_index * points_discarded_per_scan
                    if 0 <= shifted_index < len(column_values):
                        row.append(column_values[shifted_index])
                    else:
                        row.append("")
            table.append(row)

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(table)

        files_written += 1
        print(f"Saved: {output_path.name}")

    settings["last_excel_dir"] = str(Path(excel_path).parent)
    settings["last_output_dir"] = str(Path(output_folder))
    settings["first_sample_row"] = first_sample_row
    settings["last_sample_row"] = last_sample_row
    settings["rows_per_scan"] = rows_per_scan
    settings["emission_point_count"] = emission_point_count
    settings["points_discarded_per_scan"] = points_discarded_per_scan
    settings["first_excitation_row"] = first_excitation_row
    settings["last_excitation_row"] = last_excitation_row
    settings["emission_row"] = emission_row
    settings["plate_sheet_name"] = plate_sheet_name
    settings["raw_sheet_name"] = raw_sheet_name
    save_settings(settings)

    print(f"Done. Files written: {files_written}")

    root = tk.Tk()
    root.withdraw()
    if files_written == 0:
        messagebox.showwarning(
            "No files written",
            "CSV export completed, but zero files were written.\n\n"
            "Check the console output for:\n"
            "- workbook sheet names\n"
            "- selected plate/raw sheets\n"
            "- the values in column A of your sample rows",
            parent=root
        )
    else:
        messagebox.showinfo("Complete", f"CSV export complete.\nFiles written: {files_written}", parent=root)
    root.destroy()


if __name__ == "__main__":
    main()