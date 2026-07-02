import json
import unittest
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

import new


class FakeVar:
	def __init__(self, value=""):
		self.value = value

	def get(self):
		return self.value

	def set(self, value):
		self.value = value


class ExpenseTrackerTests(unittest.TestCase):
	def _make_bare_app(self):
		app = new.ExpenseTrackerApp.__new__(new.ExpenseTrackerApp)
		app.expenses = []
		return app

	def test_get_current_month_expenses_filters_invalid_and_old_dates(self):
		app = self._make_bare_app()
		today = date.today()
		this_month = today.replace(day=1).isoformat()
		last_year = today.replace(year=today.year - 1).isoformat()

		app.expenses = [
			{"date": this_month, "category": "Food", "amount": 10},
			{"date": last_year, "category": "Travel", "amount": 20},
			{"date": "invalid", "category": "Bad", "amount": 30},
			{"category": "Missing date", "amount": 40},
		]

		result = app._get_current_month_expenses()

		self.assertEqual(len(result), 1)
		self.assertEqual(result[0]["category"], "Food")

	def test_calculate_current_month_total_ignores_bad_amounts_and_rounds(self):
		app = self._make_bare_app()
		app._get_current_month_expenses = MagicMock(
			return_value=[
				{"amount": "10.225"},
				{"amount": "bad"},
				{"other": 1},
				{"amount": 5},
			]
		)

		total = app._calculate_current_month_total()

		self.assertEqual(total, 15.22)

	@patch("new.messagebox.showerror")
	def test_add_expense_rejects_missing_category(self, showerror):
		app = self._make_bare_app()
		app.date_var = FakeVar(date.today().isoformat())
		app.category_var = FakeVar("")
		app.amount_var = FakeVar("12")
		app.note_var = FakeVar("note")
		app._save_expenses = MagicMock()
		app._refresh_view = MagicMock()
		app.clear_fields = MagicMock()

		app.add_expense()

		showerror.assert_called_once()
		self.assertEqual(app.expenses, [])
		app._save_expenses.assert_not_called()

	@patch("new.messagebox.showerror")
	def test_add_expense_rejects_invalid_date(self, showerror):
		app = self._make_bare_app()
		app.date_var = FakeVar("02-07-2026")
		app.category_var = FakeVar("Food")
		app.amount_var = FakeVar("12")
		app.note_var = FakeVar("note")
		app._save_expenses = MagicMock()
		app._refresh_view = MagicMock()
		app.clear_fields = MagicMock()

		app.add_expense()

		showerror.assert_called_once()
		self.assertEqual(app.expenses, [])

	@patch("new.messagebox.showerror")
	def test_add_expense_rejects_negative_amount(self, showerror):
		app = self._make_bare_app()
		app.date_var = FakeVar(date.today().isoformat())
		app.category_var = FakeVar("Fuel")
		app.amount_var = FakeVar("-1")
		app.note_var = FakeVar("note")
		app._save_expenses = MagicMock()
		app._refresh_view = MagicMock()
		app.clear_fields = MagicMock()

		app.add_expense()

		showerror.assert_called_once()
		self.assertEqual(app.expenses, [])

	@patch("new.messagebox.showerror")
	def test_add_expense_saves_and_refreshes_on_success(self, showerror):
		app = self._make_bare_app()
		app.date_var = FakeVar("2026-07-02")
		app.category_var = FakeVar("Rent")
		app.amount_var = FakeVar("2750")
		app.note_var = FakeVar("PG")
		app._save_expenses = MagicMock()
		app._refresh_view = MagicMock()
		app.clear_fields = MagicMock()

		app.add_expense()

		showerror.assert_not_called()
		self.assertEqual(len(app.expenses), 1)
		self.assertEqual(app.expenses[0]["amount"], 2750.0)
		app._save_expenses.assert_called_once()
		app._refresh_view.assert_called_once()
		app.clear_fields.assert_called_once_with(reset_date=False)

	def test_load_expenses_sets_empty_when_file_missing(self):
		app = self._make_bare_app()
		with TemporaryDirectory() as tmp_dir:
			target = Path(tmp_dir) / "missing.json"
			with patch("new.DATA_FILE", target):
				app._load_expenses()

		self.assertEqual(app.expenses, [])

	def test_load_expenses_reads_list_data(self):
		app = self._make_bare_app()
		data = [{"date": "2026-07-02", "category": "A", "amount": 1}]

		with TemporaryDirectory() as tmp_dir:
			target = Path(tmp_dir) / "expenses.json"
			target.write_text(json.dumps(data), encoding="utf-8")
			with patch("new.DATA_FILE", target):
				app._load_expenses()

		self.assertEqual(app.expenses, data)

	def test_load_expenses_sets_empty_for_non_list_or_bad_json(self):
		app = self._make_bare_app()

		with TemporaryDirectory() as tmp_dir:
			target = Path(tmp_dir) / "expenses.json"
			target.write_text('{"not": "a list"}', encoding="utf-8")
			with patch("new.DATA_FILE", target):
				app._load_expenses()
			self.assertEqual(app.expenses, [])

			target.write_text("{bad-json", encoding="utf-8")
			with patch("new.DATA_FILE", target):
				app._load_expenses()
			self.assertEqual(app.expenses, [])

	def test_save_expenses_writes_json_file(self):
		app = self._make_bare_app()
		app.expenses = [{"date": "2026-07-02", "category": "X", "amount": 99.5, "note": "ok"}]

		with TemporaryDirectory() as tmp_dir:
			target = Path(tmp_dir) / "expenses.json"
			with patch("new.DATA_FILE", target):
				app._save_expenses()
			content = json.loads(target.read_text(encoding="utf-8"))

		self.assertEqual(content, app.expenses)


if __name__ == "__main__":
	unittest.main()