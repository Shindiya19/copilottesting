import json
from datetime import date, datetime
from pathlib import Path
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk


DATA_FILE = Path(__file__).with_name("expenses.json")


class ExpenseTrackerApp:
	def __init__(self, root: tk.Tk) -> None:
		self.root = root
		self.root.title("Expense Tracker Dashboard")
		self.root.geometry("1280x760")
		self.root.minsize(1120, 700)
		self.root.configure(bg="#eef3fb")

		self.expenses = []
		self.chart_palette = [
			"#00c2c7",
			"#ff9f43",
			"#6c5ce7",
			"#00b894",
			"#0984e3",
			"#fd79a8",
			"#e17055",
			"#2ecc71",
		]

		self._build_styles()
		self._build_ui()
		self._load_expenses()
		self._refresh_view()

	def _build_styles(self) -> None:
		style = ttk.Style(self.root)
		style.theme_use("clam")

		style.configure("App.TFrame", background="#eef3fb")
		style.configure("Sidebar.TFrame", background="#1f2a44")
		style.configure("Card.TFrame", background="#ffffff")
		style.configure("CardTitle.TLabel", background="#ffffff", foreground="#1f2937", font=("Segoe UI", 11, "bold"))
		style.configure("SectionTitle.TLabel", background="#eef3fb", foreground="#1f2937", font=("Segoe UI", 19, "bold"))
		style.configure("Subtle.TLabel", background="#eef3fb", foreground="#6b7280", font=("Segoe UI", 10))
		style.configure("SidebarTitle.TLabel", background="#1f2a44", foreground="#ffffff", font=("Segoe UI", 16, "bold"))
		style.configure("SidebarItem.TLabel", background="#1f2a44", foreground="#a9b6d3", font=("Segoe UI", 11))
		style.configure("SidebarActive.TLabel", background="#1f2a44", foreground="#ffffff", font=("Segoe UI", 11, "bold"))
		style.configure("BigNumber.TLabel", background="#ffffff", foreground="#0f172a", font=("Segoe UI", 20, "bold"))
		style.configure("MetricHint.TLabel", background="#ffffff", foreground="#64748b", font=("Segoe UI", 9))
		style.configure("FieldLabel.TLabel", background="#ffffff", foreground="#334155", font=("Segoe UI", 10))

		style.configure(
			"Primary.TButton",
			font=("Segoe UI", 10, "bold"),
			padding=(12, 8),
		)
		style.map(
			"Primary.TButton",
			background=[("!disabled", "#1f7af9")],
			foreground=[("!disabled", "#ffffff")],
		)

		style.configure(
			"Secondary.TButton",
			font=("Segoe UI", 10),
			padding=(10, 9),
		)

		style.configure(
			"Treeview",
			background="#ffffff",
			fieldbackground="#ffffff",
			rowheight=29,
			font=("Segoe UI", 10),
		)
		style.configure(
			"Treeview.Heading",
			background="#f1f5f9",
			foreground="#1f2937",
			font=("Segoe UI", 10, "bold"),
		)

	def _build_ui(self) -> None:
		self.root.columnconfigure(1, weight=1)
		self.root.rowconfigure(0, weight=1)

		sidebar = ttk.Frame(self.root, style="Sidebar.TFrame", width=220)
		sidebar.grid(row=0, column=0, sticky="ns")
		sidebar.grid_propagate(False)

		ttk.Label(sidebar, text="Penta", style="SidebarTitle.TLabel").grid(row=0, column=0, sticky="w", padx=24, pady=(28, 18))

		menu_frame = ttk.Frame(sidebar, style="Sidebar.TFrame")
		menu_frame.grid(row=1, column=0, sticky="nsew", padx=24)
		sidebar.rowconfigure(1, weight=1)

		ttk.Label(menu_frame, text="Dashboard", style="SidebarActive.TLabel").grid(row=0, column=0, sticky="w", pady=8)
		ttk.Label(menu_frame, text="Expenses", style="SidebarItem.TLabel").grid(row=1, column=0, sticky="w", pady=8)
		ttk.Label(menu_frame, text="Statistics", style="SidebarItem.TLabel").grid(row=2, column=0, sticky="w", pady=8)
		ttk.Label(menu_frame, text="Reports", style="SidebarItem.TLabel").grid(row=3, column=0, sticky="w", pady=8)

		profile = tk.Frame(sidebar, bg="#1f2a44", pady=24)
		profile.grid(row=2, column=0, sticky="ew", padx=24)
		tk.Label(profile, text="U", bg="#2f4f7b", fg="#ffffff", font=("Segoe UI", 12, "bold"), width=2, height=1).grid(row=0, column=0, sticky="w")
		ttk.Label(profile, text="Your Workspace", style="SidebarItem.TLabel").grid(row=0, column=1, sticky="w", padx=10)

		main = ttk.Frame(self.root, style="App.TFrame", padding=18)
		main.grid(row=0, column=1, sticky="nsew")
		main.columnconfigure(0, weight=1)
		main.rowconfigure(2, weight=1)
		main.rowconfigure(3, weight=1)

		header = ttk.Frame(main, style="App.TFrame")
		header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
		header.columnconfigure(0, weight=1)
		ttk.Label(header, text="Expense Dashboard", style="SectionTitle.TLabel").grid(row=0, column=0, sticky="w")
		ttk.Label(header, text="Monitor current month expenses and category split", style="Subtle.TLabel").grid(row=1, column=0, sticky="w")

		metrics = ttk.Frame(main, style="App.TFrame")
		metrics.grid(row=1, column=0, sticky="ew", pady=(0, 10))
		for col in range(3):
			metrics.columnconfigure(col, weight=1)

		self.monthly_total_var = tk.StringVar(value="0.00")
		self.monthly_count_var = tk.StringVar(value="0")
		self.avg_var = tk.StringVar(value="0.00")

		self._build_metric_card(metrics, 0, "Monthly Total", self.monthly_total_var, "Current month")
		self._build_metric_card(metrics, 1, "Expenses Added", self.monthly_count_var, "Current month")
		self._build_metric_card(metrics, 2, "Average Expense", self.avg_var, "Current month")

		middle = ttk.Frame(main, style="App.TFrame")
		middle.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
		middle.columnconfigure(0, weight=2)
		middle.columnconfigure(1, weight=1)
		middle.rowconfigure(0, weight=1)

		table_card = ttk.Frame(middle, style="Card.TFrame", padding=14)
		table_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
		table_card.columnconfigure(0, weight=1)
		table_card.rowconfigure(1, weight=1)
		ttk.Label(table_card, text="Recent Transactions", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))

		columns = ("date", "category", "amount", "note")
		self.table = ttk.Treeview(table_card, columns=columns, show="headings")
		self.table.heading("date", text="Date")
		self.table.heading("category", text="Category")
		self.table.heading("amount", text="Amount")
		self.table.heading("note", text="Note")
		self.table.column("date", width=110, anchor="center")
		self.table.column("category", width=130)
		self.table.column("amount", width=95, anchor="e")
		self.table.column("note", width=260)

		scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.table.yview)
		self.table.configure(yscrollcommand=scrollbar.set)
		self.table.grid(row=1, column=0, sticky="nsew")
		scrollbar.grid(row=1, column=1, sticky="ns")

		chart_card = ttk.Frame(middle, style="Card.TFrame", padding=14)
		chart_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
		chart_card.columnconfigure(0, weight=1)
		chart_card.rowconfigure(1, weight=1)
		ttk.Label(chart_card, text="Expense by Category", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))
		self.chart_canvas = tk.Canvas(chart_card, width=340, height=260, bg="#ffffff", highlightthickness=0)
		self.chart_canvas.grid(row=1, column=0, sticky="nsew")

		form_card = ttk.Frame(main, style="Card.TFrame", padding=14)
		form_card.grid(row=3, column=0, sticky="nsew")
		for col in range(5):
			form_card.columnconfigure(col, weight=1)

		ttk.Label(form_card, text="Add Expense", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=5, sticky="w", pady=(0, 8))

		self.date_var = tk.StringVar(value=date.today().isoformat())
		self.category_var = tk.StringVar()
		self.amount_var = tk.StringVar()
		self.note_var = tk.StringVar()

		ttk.Label(form_card, text="Date (YYYY-MM-DD)", style="FieldLabel.TLabel").grid(row=1, column=0, sticky="w")
		ttk.Label(form_card, text="Category", style="FieldLabel.TLabel").grid(row=1, column=1, sticky="w")
		ttk.Label(form_card, text="Amount", style="FieldLabel.TLabel").grid(row=1, column=2, sticky="w")
		ttk.Label(form_card, text="Note", style="FieldLabel.TLabel").grid(row=1, column=3, sticky="w")

		self.date_entry = tk.Entry(form_card, textvariable=self.date_var, relief="flat", bg="#f8fafc", fg="#111827", font=("Segoe UI", 10))
		self.date_entry.grid(row=2, column=0, sticky="ew", padx=(0, 8), ipady=7)
		self.category_entry = tk.Entry(form_card, textvariable=self.category_var, relief="flat", bg="#f8fafc", fg="#111827", font=("Segoe UI", 10))
		self.category_entry.grid(row=2, column=1, sticky="ew", padx=(0, 8), ipady=7)
		self.amount_entry = tk.Entry(form_card, textvariable=self.amount_var, relief="flat", bg="#f8fafc", fg="#111827", font=("Segoe UI", 10))
		self.amount_entry.grid(row=2, column=2, sticky="ew", padx=(0, 8), ipady=7)
		self.note_entry = tk.Entry(form_card, textvariable=self.note_var, relief="flat", bg="#f8fafc", fg="#111827", font=("Segoe UI", 10))
		self.note_entry.grid(row=2, column=3, sticky="ew", padx=(0, 8), ipady=7)

		actions = ttk.Frame(form_card, style="Card.TFrame")
		actions.grid(row=2, column=4, sticky="ew")
		actions.columnconfigure(0, weight=1)
		actions.columnconfigure(1, weight=1)
		ttk.Button(actions, text="Add", style="Primary.TButton", command=self.add_expense).grid(row=0, column=0, sticky="ew", padx=(0, 5))
		ttk.Button(actions, text="Clear", style="Secondary.TButton", command=self.clear_fields).grid(row=0, column=1, sticky="ew")

	def _build_metric_card(self, parent: ttk.Frame, column: int, title: str, value_var: tk.StringVar, hint: str) -> None:
		card = ttk.Frame(parent, style="Card.TFrame", padding=14)
		card.grid(row=0, column=column, sticky="ew", padx=(0, 8) if column < 2 else (0, 0))
		card.columnconfigure(1, weight=1)

		dot_color = ["#1f7af9", "#00b894", "#6c5ce7"][column]
		dot = tk.Canvas(card, width=20, height=20, bg="#ffffff", highlightthickness=0)
		dot.grid(row=0, column=0, sticky="w", padx=(0, 10))
		dot.create_oval(3, 3, 17, 17, fill=dot_color, outline=dot_color)

		ttk.Label(card, text=title, style="CardTitle.TLabel").grid(row=0, column=1, sticky="w")
		ttk.Label(card, textvariable=value_var, style="BigNumber.TLabel").grid(row=1, column=1, sticky="w", pady=(6, 0))
		ttk.Label(card, text=hint, style="MetricHint.TLabel").grid(row=2, column=1, sticky="w")

	def add_expense(self) -> None:
		raw_date = self.date_var.get().strip()
		raw_category = self.category_var.get().strip()
		raw_amount = self.amount_var.get().strip()
		raw_note = self.note_var.get().strip()

		if not raw_category:
			messagebox.showerror("Missing category", "Please enter a category.")
			return

		try:
			parsed_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
		except ValueError:
			messagebox.showerror("Invalid date", "Use date format YYYY-MM-DD.")
			return

		try:
			amount = float(raw_amount)
			if amount < 0:
				raise ValueError
		except ValueError:
			messagebox.showerror("Invalid amount", "Amount must be a positive number.")
			return

		expense = {
			"date": parsed_date.isoformat(),
			"category": raw_category,
			"amount": round(amount, 2),
			"note": raw_note,
		}

		self.expenses.append(expense)
		self._save_expenses()
		self._refresh_view()
		self.clear_fields(reset_date=False)

	def clear_fields(self, reset_date: bool = True) -> None:
		if reset_date:
			self.date_var.set(date.today().isoformat())
		self.category_var.set("")
		self.amount_var.set("")
		self.note_var.set("")

	def _refresh_view(self) -> None:
		for row_id in self.table.get_children():
			self.table.delete(row_id)

		for item in sorted(self.expenses, key=lambda x: x.get("date", ""), reverse=True):
			amount_value = item.get("amount", 0.0)
			try:
				formatted_amount = f"{float(amount_value):.2f}"
			except (ValueError, TypeError):
				formatted_amount = "0.00"
			self.table.insert(
				"",
				"end",
				values=(
					item.get("date", ""),
					item.get("category", ""),
					formatted_amount,
					item.get("note", ""),
				),
			)

		monthly_items = self._get_current_month_expenses()
		total = self._calculate_current_month_total()
		count = len(monthly_items)
		avg = (total / count) if count else 0.0

		self.monthly_total_var.set(f"{total:.2f}")
		self.monthly_count_var.set(str(count))
		self.avg_var.set(f"{avg:.2f}")
		self._draw_pie_chart()

	def _get_current_month_expenses(self) -> list[dict]:
		today = date.today()
		result = []
		for item in self.expenses:
			try:
				item_date = datetime.strptime(item["date"], "%Y-%m-%d").date()
			except (ValueError, KeyError, TypeError):
				continue
			if item_date.year == today.year and item_date.month == today.month:
				result.append(item)
		return result

	def _calculate_current_month_total(self) -> float:
		total = 0.0
		for item in self._get_current_month_expenses():
			try:
				total += float(item["amount"])
			except (ValueError, TypeError, KeyError):
				continue
		return round(total, 2)

	def _draw_pie_chart(self) -> None:
		self.chart_canvas.delete("all")
		monthly_items = self._get_current_month_expenses()

		category_totals: dict[str, float] = {}
		for item in monthly_items:
			category = str(item.get("category", "Other")).strip() or "Other"
			try:
				amount = float(item.get("amount", 0.0))
			except (ValueError, TypeError):
				continue
			category_totals[category] = category_totals.get(category, 0.0) + amount

		total = sum(category_totals.values())
		if total <= 0:
			self.chart_canvas.create_text(
				170,
				130,
				text="No current-month expenses yet",
				fill="#6b7280",
				font=("Segoe UI", 12, "bold"),
			)
			return

		start_angle = 0.0
		x0, y0, x1, y1 = 12, 20, 198, 206

		sorted_items = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
		for index, (category, value) in enumerate(sorted_items):
			extent = (value / total) * 360.0
			color = self.chart_palette[index % len(self.chart_palette)]
			self.chart_canvas.create_arc(
				x0,
				y0,
				x1,
				y1,
				start=start_angle,
				extent=extent,
				fill=color,
				outline="#ffffff",
				width=2,
			)
			start_angle += extent

		self.chart_canvas.create_oval(72, 80, 138, 146, fill="#ffffff", outline="#ffffff")
		self.chart_canvas.create_text(105, 105, text=f"{total:.0f}", fill="#111827", font=("Segoe UI", 11, "bold"))
		self.chart_canvas.create_text(105, 123, text="Total", fill="#6b7280", font=("Segoe UI", 8))

		legend_x = 210
		legend_y = 30
		for index, (category, value) in enumerate(sorted_items[:7]):
			color = self.chart_palette[index % len(self.chart_palette)]
			pct = (value / total) * 100
			self.chart_canvas.create_rectangle(legend_x, legend_y, legend_x + 14, legend_y + 14, fill=color, outline=color)
			self.chart_canvas.create_text(
				legend_x + 20,
				legend_y + 7,
				anchor="w",
				text=f"{category} ({pct:.1f}%)",
				fill="#374151",
				font=("Segoe UI", 9),
			)
			legend_y += 25

	def _load_expenses(self) -> None:
		if not DATA_FILE.exists():
			self.expenses = []
			return

		try:
			with DATA_FILE.open("r", encoding="utf-8") as file:
				data = json.load(file)
			if isinstance(data, list):
				self.expenses = data
			else:
				self.expenses = []
		except (json.JSONDecodeError, OSError):
			self.expenses = []

	def _save_expenses(self) -> None:
		with DATA_FILE.open("w", encoding="utf-8") as file:
			json.dump(self.expenses, file, indent=2)


def main() -> None:
	root = tk.Tk()
	ExpenseTrackerApp(root)
	root.mainloop()


if __name__ == "__main__":
	main()
