import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime


# Database operations
def create_connection():
    conn = sqlite3.connect("coffee.db")
    return conn


def create_table():
    conn = create_connection()
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS coffee_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Body TEXT,
                    Acidity TEXT,
                    Flavor TEXT,
                    Aroma TEXT,
                    Roast TEXT,
                    Roastery TEXT,
                    RoastDate TEXT,
                    Country TEXT,
                    Blend TEXT,
                    Sold INTEGER)"""
    )
    conn.commit()
    conn.close()


# Seller functions
def add_item(item_data):
    conn = create_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO coffee_data (Body, Acidity, Flavor, Aroma, Roast, Roastery, RoastDate, Country, Blend, Sold) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        item_data,
    )
    conn.commit()
    conn.close()


def delete_item(item_id):
    conn = create_connection()
    c = conn.cursor()
    c.execute("DELETE FROM coffee_data WHERE id=?", (item_id,))
    conn.commit()
    conn.close()


# Buyer functions
def search_items(column, value):
    conn = create_connection()
    c = conn.cursor()
    c.execute(f"SELECT * FROM coffee_data WHERE {column} LIKE ?", ("%" + value + "%",))
    result = c.fetchall()
    conn.close()
    return result


def sort_items(column):
    conn = create_connection()
    c = conn.cursor()
    c.execute(f"SELECT * FROM coffee_data ORDER BY {column}")
    result = c.fetchall()
    conn.close()
    return result


def purchase_bean(item_id, quantity):
    conn = create_connection()
    c = conn.cursor()
    c.execute("UPDATE coffee_data SET Sold = Sold + ? WHERE id=?", (quantity, item_id))
    conn.commit()
    conn.close()


# GUI components
class CoffeeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Coffee Database Management")
        self.geometry("825x325")
        self.create_widgets()

    def create_widgets(self):
        mode_label = ttk.Label(self, text="Select Mode")
        mode_label.grid(column=0, row=0)

        self.mode_var = tk.StringVar()
        mode_combobox = ttk.Combobox(
            self, textvariable=self.mode_var, values=["Seller", "Buyer"]
        )
        mode_combobox.grid(column=1, row=0)
        mode_combobox.bind("<<ComboboxSelected>>", self.mode_selected)

        self.mode_var.trace("w", self.mode_selected)

    def create_results_tree(self):
        headings = [
            "ID",
            "Body",
            "Acidity",
            "Flavor",
            "Aroma",
            "Roast",
            "Roastery",
            "RoastDate",
            "Country",
            "Blend",
            "Sold",
        ]
        self.results_tree = ttk.Treeview(
            self.tree_frame, columns=headings, show="headings"
        )
        for i, heading in enumerate(headings):
            self.results_tree.heading(i, text=heading)
            self.results_tree.column(i, width=75)
        self.results_tree.pack(fill=tk.BOTH, expand=True)

    def mode_selected(self, event=None):
        mode = self.mode_var.get()
        if mode == "Seller":
            self.show_seller_interface()
        elif mode == "Buyer":
            self.show_buyer_interface()

        self.display_all_items()

    def switch_mode(self):
        current_mode = self.mode_var.get()
        if current_mode == "Seller":
            self.mode_var.set("Buyer")
        elif current_mode == "Buyer":
            self.mode_var.set("Seller")
        self.mode_selected()

    def show_seller_interface(self):
        self.clear_interface()

        # Create labels and entries for coffee data
        labels = [
            "Body",
            "Acidity",
            "Flavor",
            "Aroma",
            "Roast",
            "Roastery",
            "RoastDate",
            "Country",
            "Blend",
        ]
        for i, label in enumerate(labels):
            ttk.Label(self, text=label).grid(column=0, row=i + 1)

        self.entries = [ttk.Entry(self) for _ in range(9)]
        for i, entry in enumerate(self.entries):
            entry.grid(column=1, row=i + 1)

        # Add and delete buttons
        add_button = ttk.Button(self, text="Add Item", command=self.add_item_clicked)
        add_button.grid(column=2, row=1)

        delete_label = ttk.Label(self, text="Item ID to delete:")
        delete_label.grid(column=2, row=2)
        self.delete_entry = ttk.Entry(self)
        self.delete_entry.grid(column=2, row=3)

        delete_button = ttk.Button(
            self, text="Delete Item", command=self.delete_item_clicked
        )
        delete_button.grid(column=2, row=4)

        # Switch Mode button
        switch_mode_button = ttk.Button(
            self, text="Switch Mode", command=self.switch_mode
        )
        switch_mode_button.grid(column=2, row=5)

        # Create a new frame for the results_tree
        self.tree_frame = tk.Frame(self)
        self.tree_frame.grid(
            column=0, row=11, rowspan=11, columnspan=4, padx=(0, 0), pady=(10, 0)
        )

        self.create_results_tree()
        self.display_all_items()

    def show_buyer_interface(self):
        self.clear_interface()

        # Create sort and search options
        ttk.Label(self, text="Sort by:").grid(column=0, row=1)
        self.sort_var = tk.StringVar()
        sort_combobox = ttk.Combobox(
            self,
            textvariable=self.sort_var,
            values=[
                "Body",
                "Acidity",
                "Flavor",
                "Aroma",
                "Roast",
                "Roastery",
                "Country",
                "Blend",
                "Sold",
            ],
        )
        sort_combobox.grid(column=1, row=1)
        sort_combobox.bind("<<ComboboxSelected>>", self.sort_items_clicked)

        sort_button = ttk.Button(self, text="Sort", command=self.sort_items_clicked)
        sort_button.grid(column=2, row=1)

        ttk.Label(self, text="Search:").grid(column=0, row=0)
        self.search_var = tk.StringVar()
        search_combobox = ttk.Combobox(
            self,
            textvariable=self.search_var,
            values=[
                "Body",
                "Acidity",
                "Flavor",
                "Aroma",
                "Roast",
                "Roastery",
                "Country",
                "Blend",
            ],
        )
        search_combobox.grid(column=1, row=0)

        self.search_entry = ttk.Entry(self)
        self.search_entry.grid(column=2, row=0)

        search_button = ttk.Button(
            self, text="Search", command=self.search_items_clicked
        )
        search_button.grid(column=3, row=0)

        ttk.Label(self, text="Item ID:").grid(column=0, row=2)
        self.item_id_entry = ttk.Entry(self)
        self.item_id_entry.grid(column=1, row=2)

        select_item_button = ttk.Button(
            self, text="Select Item", command=self.select_item_clicked
        )
        select_item_button.grid(column=2, row=2)

        # Purchase button and quantity entry
        ttk.Label(self, text="Quantity:").grid(column=0, row=3)
        self.quantity_entry = ttk.Entry(self)
        self.quantity_entry.grid(column=1, row=3)

        purchase_button = ttk.Button(
            self, text="Purchase", command=self.purchase_bean_clicked
        )
        purchase_button.grid(column=2, row=3)

        # Switch Mode button
        switch_mode_button = ttk.Button(
            self, text="Switch Mode", command=self.switch_mode
        )
        switch_mode_button.grid(column=3, row=3)

        # Create a new frame for the results_tree
        self.tree_frame = tk.Frame(self)
        self.tree_frame.grid(
            column=0, row=5, rowspan=11, columnspan=4, padx=(0, 0), pady=(10, 0)
        )

        self.create_results_tree()

    def clear_interface(self):
        for widget in self.grid_slaves():
            widget.destroy()

    def display_all_items(self):
        conn = create_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM coffee_data")
        results = c.fetchall()
        conn.close()
        self.update_results_tree(results)

    def add_item_clicked(self):
        item_data = [entry.get() for entry in self.entries]
        item_data.append(0)  # Set Sold feature to 0
        add_item(item_data)
        messagebox.showinfo("Success", "Item added successfully.")
        self.display_all_items()  # Update the treeview after adding an item

    def delete_item_clicked(self):
        item_id = self.delete_entry.get()
        if not item_id:
            messagebox.showerror("Error", "Please enter an item ID to delete.")
            return

        delete_item(item_id)
        messagebox.showinfo("Success", "Item deleted successfully.")
        self.display_all_items()  # Update the treeview after deleting an item

    def sort_items_clicked(self):
        column = self.sort_var.get()
        results = sort_items(column)
        self.update_results_tree(results)

    def search_items_clicked(self):
        column = self.search_var.get()
        value = self.search_entry.get()
        results = search_items(column, value)
        self.update_results_tree(results)

    def purchase_bean_clicked(self):
        item_id = self.item_id_entry.get()
        if not item_id:
            messagebox.showerror("Error", "Please select an item to purchase.")
            return
        item_id = int(item_id)
        quantity = int(self.quantity_entry.get())
        purchase_bean(item_id, quantity)
        messagebox.showinfo("Success", "Bean purchased successfully.")
        self.display_all_items()

    def get_selected_item_id(self):
        selected_item = self.results_tree.selection()
        if selected_item:
            return selected_item[0]
        else:
            return None

    def select_item_clicked(self):
        item_id = self.get_selected_item_id()
        if item_id is None:
            messagebox.showerror("Sucess", "Item Successfully Selected.")
            pass
        else:
            self.item_id_entry.delete(0, tk.END)
            self.item_id_entry.insert(0, str(item_id))

    def update_results_tree(self, results):
        self.results_tree.delete(*self.results_tree.get_children())
        for row in results:
            self.results_tree.insert("", "end", iid=row[0], values=row)


# Main
if __name__ == "__main__":
    create_table()
    app = CoffeeApp()
    app.mainloop()
