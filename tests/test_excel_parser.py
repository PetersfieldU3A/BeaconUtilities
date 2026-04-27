"""Tests for beaconutilities.excel_parser."""

from __future__ import annotations

import pytest

from beaconutilities.excel_parser import list_sheets, parse_sheet


class TestListSheets:
    def test_returns_sheet_names(self, make_excel):
        path = make_excel({"Members": [["A"]], "Groups": [["B"]]})
        assert list_sheets(path) == ["Members", "Groups"]

    def test_single_sheet(self, make_excel):
        path = make_excel({"Data": [["X"]]})
        assert list_sheets(path) == ["Data"]

    def test_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="Excel file not found"):
            list_sheets(tmp_path / "missing.xlsx")


class TestParseSheet:
    def test_basic_rows(self, make_excel):
        path = make_excel({
            "Sheet1": [
                ["Name", "Email"],
                ["Alice", "alice@example.com"],
                ["Bob", "bob@example.com"],
            ]
        })
        rows = parse_sheet(path, "Sheet1")
        assert len(rows) == 2
        assert rows[0] == {"Name": "Alice", "Email": "alice@example.com"}
        assert rows[1] == {"Name": "Bob", "Email": "bob@example.com"}

    def test_index_access(self, make_excel):
        path = make_excel({"First": [["X", "Y"], [1, 2]]})
        rows = parse_sheet(path, 0)
        assert rows[0]["X"] == 1

    def test_skips_empty_rows(self, make_excel):
        path = make_excel({
            "Sheet1": [
                ["Name"],
                ["Alice"],
                [None],
                ["Bob"],
            ]
        })
        rows = parse_sheet(path, "Sheet1")
        assert len(rows) == 2

    def test_empty_sheet_returns_empty_list(self, make_excel):
        path = make_excel({"Empty": []})
        assert parse_sheet(path, "Empty") == []

    def test_header_only_returns_empty_list(self, make_excel):
        path = make_excel({"Sheet1": [["Name", "Email"]]})
        assert parse_sheet(path, "Sheet1") == []

    def test_missing_sheet_name_raises(self, make_excel):
        path = make_excel({"Sheet1": [["A"]]})
        with pytest.raises(KeyError, match="NoSuchSheet"):
            parse_sheet(path, "NoSuchSheet")

    def test_index_out_of_range_raises(self, make_excel):
        path = make_excel({"Sheet1": [["A"]]})
        with pytest.raises(IndexError):
            parse_sheet(path, 5)

    def test_file_not_found_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            parse_sheet(tmp_path / "missing.xlsx")

    def test_none_header_gets_generated_name(self, make_excel):
        path = make_excel({"Sheet1": [[None, "Name"], ["val", "Alice"]]})
        rows = parse_sheet(path, "Sheet1")
        assert "_col_0" in rows[0]
        assert rows[0]["Name"] == "Alice"

    def test_short_row_padded_with_none(self, tmp_path):
        """Rows shorter than header should not raise; missing values become None."""
        import openpyxl

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Sheet1"
        ws.append(["A", "B", "C"])
        ws.append(["only_a"])      # shorter than header
        path = tmp_path / "short.xlsx"
        wb.save(path)
        rows = parse_sheet(path, "Sheet1")
        assert rows[0]["A"] == "only_a"
        assert rows[0]["B"] is None
        assert rows[0]["C"] is None
