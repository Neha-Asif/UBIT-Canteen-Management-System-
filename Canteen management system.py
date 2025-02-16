import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import Image, ImageTk
from tkinter import font
import sqlite3
import random
import string
from io import BytesIO
import requests

# Database setup
conn = sqlite3.connect('canteen_management.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS shopkeeper (
    id TEXT PRIMARY KEY,
    password TEXT NOT NULL
)
''')

def create_menu_table():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT UNIQUE NOT NULL,
            category TEXT,
            quantity INTEGER NOT NULL,
            actual_price REAL NOT NULL,
            selling_price REAL NOT NULL,
            boycotted TEXT NOT NULL
        )
    ''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS student (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    cnic TEXT NOT NULL,
    major TEXT NOT NULL,
    section NOT NULL,
    password TEXT NOT NULL,
    first_login INTEGER NOT NULL DEFAULT 1
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS finance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    total_cost REAL,
    total_profit REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    items TEXT NOT NULL,
    total_price REAL NOT NULL,
    fulfilled INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY(student_id) REFERENCES student(id)
)
''')

# Insert shopkeeper data
cursor.execute("INSERT OR IGNORE INTO shopkeeper (id, password) VALUES ('675409', 'ubit2468'), ('676377', 'ubit2468')")

# Insert default menu items
def insert_sample_data():
    cursor.execute('''
        INSERT OR IGNORE INTO menu (item, category, quantity, actual_price, selling_price, boycotted) VALUES
        ('Chocolate', 'Chocolates', 100, 10.0, 12.0, 'no'),
        ('Paradise', 'Chocolates', 100, 15.0, 20.0, 'no'),
        ('Mars', 'Chocolates', 100, 20.0, 25.0, 'no'),
        ('Snickers', 'Chocolates', 100, 20.0, 25.0, 'yes'),
        ('Kitkat', 'Chocolates', 100, 30.0, 35.0, 'no'),
        ('Wavy', 'Snacks', 100, 25.0, 30.0, 'yes'),
        ('Lays', 'Snacks', 100, 20.0,25.0,'yes'),
        ('Kurkure', 'Snacks', 100,35.0,40.0, 'yes'),
        ('Cheetos', 'Snacks', 100, 25.0, 30.0, 'yes'),
        ('Doritos', 'Snacks', 100, 35.0, 40.0, 'no'),     
        ('Mirinda', 'Beverages', 100,20.0,25.0, 'yes'),
        ('Slice', 'Beverages', 100,15.0,20.0, 'no'),           
        ('Milo', 'Beverages', 100,10.0,15.0, 'yes'),      
        ('Cola Next', 'Beverages', 100, 35.0,40.0, 'no'),
        ('Pakola', 'Beverages', 100,25.0,30.0, 'no'),
        ('Malai boti Roll', 'Fast Food', 100, 30.0,35.0, 'no'),
        ('Veg Samosa', 'Fast Food', 100, 40.0,50.0, 'no'),
        ('Burger', 'Fast Food', 100, 35.0,40.0, 'no'),                                     
        ('Pizza', 'Fast Food', 100,70.0,80.0,'no'),
        ('Chowmein', 'Fast Food', 100,90.0,100.0, 'no')
    ''')

create_menu_table()
insert_sample_data()

conn.commit()
# Helper functions
def generate_random_password(length=8):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def validate_student_data(student_id, cnic):
    if len(student_id) != 6 or not student_id.isdigit():
        return False, "Student ID must be 6 digits."
    if len(cnic) != 13 or not cnic.isdigit():
        return False, "CNIC must be 13 digits."
    return True, ""

def clear_window():
    for widget in root.winfo_children():
        widget.destroy()

# Shopkeeper Functions
def shopkeeper_menu(shopkeeper_id):
    clear_window()

    # Create two frames to divide the window in half
    left_frame = tk.Frame(root, bg='light salmon', width=300, height=400)
    left_frame.pack(side="left", fill="both", expand=True)

    right_frame = tk.Frame(root, bg='white', width=300, height=400)
    right_frame.pack(side="right", fill="both", expand=True)

    # Add Welcome Label to the left frame
    welcome_label = tk.Label(left_frame, text=f"Welcome  \n\n{shopkeeper_id}!", font=("Helvetica", 40, "bold"), fg='white', bg='light salmon')
    welcome_label.pack(pady=250)  # Adjust padding as necessary

    # Custom style for buttons
    button_font = font.Font(family="Helvetica", size=18, weight="bold")
    button_style = {"font": button_font, "fg": "white", "bg": "light salmon", "activebackground": "brown", "bd": 0, "relief": "flat", "width": 20}

    tk.Frame(right_frame, bg='white').pack(side="top", expand=True)
    # Add buttons to the right frame
    tk.Button(right_frame, text="Update Menu", command=update_menu, **button_style).pack(pady=20)
    tk.Button(right_frame, text="Pending Orders", command=show_pending_orders, **button_style).pack(pady=20)
    tk.Button(right_frame, text="Finance", command=show_finance, **button_style).pack(pady=20)
    tk.Button(right_frame, text="Exit", command=main_screen, **button_style).pack(pady=20)
    tk.Frame(right_frame, bg='white').pack(side="bottom", expand=True)

def update_menu():
    clear_window()
    # Create a main frame that will contain the two sections
    main_frame = tk.Frame(root, bg="white")
    main_frame.pack(fill="both", expand=True)

    # Create the left frame for displaying items
    left_frame = tk.Frame(main_frame, bg='brown')
    left_frame.grid(row=0, column=0, sticky="nsew")

    # Create the right frame for adding new items
    right_frame = tk.Frame(main_frame, bg='peach puff')
    right_frame.grid(row=0, column=1, sticky="nsew")

    # Configure column weights to give more space to the left frame
    main_frame.columnconfigure(0, weight=3)
    main_frame.columnconfigure(1, weight=2)
    main_frame.rowconfigure(0, weight=1)

    # Update Menu Label on the left
    tk.Label(left_frame, text="Update Menu", font=("Helvetica", 28,"bold"), fg="peach puff", bg='brown').pack(pady=30)

    categories = ["Chocolates", "Snacks", "Beverages", "Fast Food"]

    category_var = tk.StringVar(root)
    category_var.set("Select Category")
    style = ttk.Style()
    style.theme_use('default')

    style.configure("TCombobox",
                    fieldbackground="white",
                    background="white",
                    selectbackground="white",
                    selectforeground="black",
                    arrowsize=20,
                    relief="flat")
                    
    category_dropdown = ttk.Combobox(left_frame, textvariable=category_var, values=categories, state="readonly", width=20, font=("Helvetica", 15), style="TCombobox")
    category_dropdown.pack(pady=10)

    items_frame = tk.Frame(left_frame, bg='brown') 
    items_frame.pack(pady=10)


    def load_items():
        for widget in items_frame.winfo_children():
            widget.destroy()

        selected_category = category_var.get()
        cursor.execute("SELECT item, quantity, actual_price, selling_price, boycotted FROM menu WHERE category=? LIMIT 10", (selected_category,))
        items = cursor.fetchall()

        for item in items:
            item_frame = tk.Frame(items_frame, bg='peach puff')  
            item_frame.pack(pady=5, fill="x", padx=5)
            
            item_info = f"{item[0]} - Qty: {item[1]}, Actual Price: {item[2]}, Selling Price: {item[3]}, Boycotted: {item[4]}"
            tk.Label(item_frame, text=item_info, bg='peach puff', font=("Helvetica", 12, "bold")).pack(side=tk.LEFT, padx=5)

            button_frame = tk.Frame(item_frame, bg='brown')  
            button_frame.pack(side=tk.RIGHT)

            tk.Button(button_frame, text="Remove", command=lambda i=item[0]: remove_item(i), fg="black", bg='peach puff').pack(padx=5, pady=2)

    def remove_item(item_name):
        default_items = ['Chocolate', 'Paradise', 'Mars', 'Wavy', 'Lays', 'Kurkure', 
                     'Pepsi', 'Cola Next', 'Pakola', 'Burger', 'Pizza', 'Chowmein']# List of default items that cannot be removed
    
    # Check if the item is a default item
        if item_name in default_items:
            tk.messagebox.showerror("Error", f"Cannot remove default item: {item_name}")
        else:
        # If not a default item, remove it from the database
            cursor.execute("DELETE FROM menu WHERE item=?", (item_name,))
            conn.commit()
            tk.messagebox.showinfo("Success", f"Item {item_name} removed successfully!")
            load_items()  # Reload items after removal

    conn.commit()
    load_items()

    tk.Button(left_frame, text="Load Items", command=load_items, bg='peach puff',font=("Helvetica", 10)).pack(pady=10)

    # Add New Item section on the right
    tk.Label(right_frame, text="Add New Item", font=("Helvetica", 28, "bold"),fg="brown", bg='peach puff').pack(pady=30)

    tk.Label(right_frame, text="Item Name", bg='peach puff').pack()
    item_name = tk.Entry(right_frame)
    item_name.pack(pady=5)
    
    tk.Label(right_frame, text="Quantity", bg='peach puff').pack()
    quantity = tk.Entry(right_frame)
    quantity.pack(pady=5)

    tk.Label(right_frame, text="Actual Price", bg='peach puff').pack()
    actual_price = tk.Entry(right_frame)
    actual_price.pack(pady=5)

    tk.Label(right_frame, text="Selling Price", bg='peach puff').pack()
    selling_price = tk.Entry(right_frame)
    selling_price.pack(pady=5)

    tk.Label(right_frame, text="Boycotted (yes/no)", bg='peach puff').pack()
    boycotted = tk.Entry(right_frame)
    boycotted.pack(pady=5)

    def save_menu_item():
        cursor.execute('''INSERT OR REPLACE INTO menu (item, category, quantity, actual_price, selling_price, boycotted)
                          VALUES (?, ?, ?, ?, ?, ?)''', (item_name.get(), category_var.get(), int(quantity.get()),
                                                      float(actual_price.get()), float(selling_price.get()), boycotted.get()))
        conn.commit()
        
        # Confirming the addition
        if cursor.rowcount == 0:
            print(f"Item '{item_name}' already exists and was not added.")
        else:
            print(f"Item '{item_name}' Menu item added successfully.")
            messagebox.showinfo("Success", "Menu item updated successfully!")
        shopkeeper_menu(current_shopkeeper_id)

    tk.Button(right_frame, text="Save", command=save_menu_item, bg='peach puff', font=("Helvetica", 10)).pack(pady=10)
    tk.Button(right_frame, text="Back", command=lambda: shopkeeper_menu(current_shopkeeper_id), bg='peach puff',font=("Helvetica", 10)).pack(pady=10)

def show_pending_orders():
    clear_window()
    root.configure(bg='peach puff')
    tk.Label(root, text="Pending Orders", font=("Helvetica", 30, "bold"), bg='light salmon', fg='brown').pack(pady=50)

    # Create a canvas for scrolling
    canvas = tk.Canvas(root, bg='peach puff')
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)

    scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Create a frame inside the canvas to hold the orders
    orders_frame = tk.Frame(canvas, bg='peach puff')
    canvas.create_window((0, 0), window=orders_frame, anchor="nw")

    # Configure the canvas to update its scroll region
    orders_frame.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.configure(yscrollcommand=scrollbar.set)

    cursor.execute("SELECT id, student_id, items, total_price FROM orders WHERE fulfilled=0")
    orders = cursor.fetchall()

    checkbuttons = []
    order_vars = []

    for order in orders:
        order_frame = tk.Frame(orders_frame, bg='peach puff')
        order_frame.pack(pady=5)

        order_var = tk.IntVar()
        order_vars.append(order_var)
        order_info = f"Order ID: {order[0]}, Student ID: {order[1]}, Items: {order[2]}, Total Price: {order[3]}"
        tk.Checkbutton(order_frame, text=order_info, variable=order_var, font=("Helvetica", 16, "bold"), bg='peach puff').pack(side=tk.LEFT)
        checkbuttons.append(order_var)

    def mark_orders_fulfilled():
        for i, order_var in enumerate(order_vars):
            if order_var.get() == 1:
                cursor.execute("UPDATE orders SET fulfilled=1 WHERE id=?", (orders[i][0],))
        conn.commit()
        messagebox.showinfo("Success", "Selected orders have been fulfilled!")
        show_pending_orders()

    tk.Button(root, text="Mark as Fulfilled", command=mark_orders_fulfilled, font=("Helvetica", 15), bg='peach puff', fg='brown').pack(pady=10, padx=10)
    tk.Button(root, text="Back", command=lambda: shopkeeper_menu(current_shopkeeper_id), font=("Helvetica", 15), bg='peach puff', fg='brown').pack(pady=10, padx=10)

def show_finance():
    # Calculate the total cost of items in the menu (investment by the shopkeeper)
    cursor.execute("SELECT quantity, actual_price FROM menu")
    menu_items = cursor.fetchall()

    total_cost = sum(quantity * actual_price for quantity, actual_price in menu_items)

    # Calculate the total profit from fulfilled orders
    cursor.execute("SELECT items FROM orders WHERE fulfilled=1")
    orders = cursor.fetchall()

    total_profit = 0

    for (items,) in orders:
        # Correctly split items by both commas and newlines
        items_list = [item.strip() for item in items.replace('\n', ',').split(',')]

        for item in items_list:
            try:
                # Split the item into name and quantity
                item_parts = item.rsplit(' x', 1)
                if len(item_parts) == 2:
                    item_name = item_parts[0].strip().lower()  # Normalize item name
                    quantity = int(item_parts[1].strip())

                    # Fetch the actual price and selling price for the item
                    cursor.execute("SELECT actual_price, selling_price FROM menu WHERE LOWER(TRIM(item))=?", (item_name,))
                    result = cursor.fetchone()

                    if result:
                        actual_price, selling_price = result
                        item_profit = (selling_price - actual_price) * quantity
                        total_profit += item_profit
                    else:
                        print(f"Warning: Item '{item_name}' not found in the menu.")
                else:
                    print(f"Warning: Item format incorrect '{item}'.")

            except ValueError as e:
                print(f"Error processing item '{item}': {e}")

    # Insert total cost and profit into the finance table (if you want to track history)
    cursor.execute("INSERT INTO finance (total_cost, total_profit) VALUES (?, ?)", (total_cost, total_profit))
    conn.commit()

    # Display the calculated finance information
    clear_window()
    root.configure(bg='peach puff')
    tk.Label(root, text="Finance", font=("Helvetica", 30, "bold"), bg='light salmon', fg='brown').pack(pady=50)
    tk.Label(root, text=f"Total Investment (Cost): {total_cost:.2f} PKR", font=("Helvetica", 18), bg='peach puff', fg='brown').pack(pady=20)
    tk.Label(root, text=f"Total Profit: {total_profit:.2f} PKR", font=("Helvetica", 18), bg='peach puff', fg='brown').pack(pady=20)
    tk.Button(root, text="Back", command=lambda: shopkeeper_menu(current_shopkeeper_id), font=("Helvetica", 18), bg='peach puff').pack(pady=20)


# Student Functions
def student_menu():
    clear_window()
    response = requests.get("https://img.freepik.com/free-vector/light-peach-background-design_23-2150315455.jpg")
    img_data = response.content
    img = Image.open(BytesIO(img_data))
    img = img.resize((root.winfo_screenwidth(), root.winfo_screenheight()))
    background_image = ImageTk.PhotoImage(img)

    background_label = tk.Label(root, image=background_image)
    background_label.image = background_image
    background_label.place(relwidth=1, relheight=1)

    tk.Label(root, text="Student Options", font=("Helvetica", 36,"bold"), fg="brown", bg='white').pack(pady=70)

    # Load and resize the signup image
    signup_image = Image.open("signup-icon.png")
    signup_image = signup_image.resize((50, 50))
    signup_image = ImageTk.PhotoImage(signup_image)

    # Load and resize the login image
    login_image = Image.open("logins-icon.png")
    login_image = login_image.resize((50, 50))
    login_image = ImageTk.PhotoImage(login_image)

    # Load and resize the exit image
    exit_image = Image.open("exit-icon.png")
    exit_image = exit_image.resize((50, 50))
    exit_image = ImageTk.PhotoImage(exit_image)

    # Create a frame to hold the signup image and button side by side
    signup_frame = tk.Frame(root, bg='white')
    signup_frame.pack(pady=20)
    tk.Label(signup_frame, image=signup_image, bg='white').pack(side="left")
    tk.Button(signup_frame, text="Student Sign-Up", command=student_signup, font=("Helvetica", 18), bg='white').pack(side="left", padx=20)

    # Create a frame to hold the login image and button side by side
    login_frame = tk.Frame(root, bg='white')
    login_frame.pack(pady=20)
    tk.Label(login_frame, image=login_image, bg='white').pack(side="left")
    tk.Button(login_frame, text="Student Login", command=student_login, font=("Helvetica", 18), bg='white').pack(side="left", padx=20)

    # Create a frame to hold the exit image and button side by side
    exit_frame = tk.Frame(root, bg='white')
    exit_frame.pack(pady=20)
    tk.Label(exit_frame, image=exit_image, bg='white').pack(side="left")
    tk.Button(exit_frame, text="Exit", command=main_screen, font=("Helvetica", 18), bg='white').pack(side="left", padx=20)

    # Keep a reference to the images to prevent garbage collection
    signup_frame.image = signup_image
    login_frame.image = login_image
    exit_frame.image = exit_image

def student_portal(student_id):
    clear_window()
    # Create two frames to divide the window in half
    left_frame = tk.Frame(root, bg='light salmon', width=300, height=400)
    left_frame.pack(side="left", fill="both", expand=True)

    right_frame = tk.Frame(root, bg='white', width=300, height=400)
    right_frame.pack(side="right", fill="both", expand=True)

    # Add Welcome Label to the left frame
    welcome_label = tk.Label(left_frame, text=f"Welcome  \n\n{student_id}!", font=("Helvetica", 40, "bold"), fg='white', bg='light salmon')
    welcome_label.pack(pady=250)  # Adjust padding as necessary

    # Custom style for buttons
    button_font = font.Font(family="Helvetica", size=18, weight="bold")
    button_style = {"font": button_font, "fg": "white", "bg": "light salmon", "activebackground": "brown", "bd": 0, "relief": "flat", "width": 20}

    tk.Frame(right_frame, bg='white').pack(side="top", expand=True)
    # Add buttons to the right frame
    tk.Button(right_frame, text="Show Menu", command=lambda: show_menu(student_id), **button_style).pack(pady=20)
    tk.Button(right_frame, text="Previous Orders", command=lambda: previous_orders(student_id), **button_style).pack(pady=20)
    tk.Button(right_frame, text="Change Password", command=lambda: change_password(student_id), **button_style).pack(pady=20)
    tk.Button(right_frame, text="Exit", command=student_menu, **button_style).pack(pady=20)
    tk.Frame(right_frame, bg='white').pack(side="bottom", expand=True)

def show_menu(student_id):
    clear_window()
    root.configure(bg='peachpuff')
    tk.Label(root, text="Menu", font=("Helvetica", 30, "bold"), fg='brown', bg='light salmon').pack(pady=30)

    categories = ["Chocolates", "Snacks", "Beverages", "Fast Food"]
    category_var = tk.StringVar(root)
    category_var.set("Select Category")
    
    style = ttk.Style()
    style.theme_use('default')
    style.configure("TCombobox",
                    fieldbackground="white",
                    background="white",
                    selectbackground="white",
                    selectforeground="black",
                    arrowsize=20,
                    relief="flat")

    category_dropdown = ttk.Combobox(root, textvariable=category_var, values=categories, state="readonly", width=20, font=("Helvetica", 15), style="TCombobox")
    category_dropdown.pack(pady=10)

    # Create a canvas for scrolling
    canvas = tk.Canvas(root, bg='peachpuff')
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)

    scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Create a frame inside the canvas to hold the items
    items_frame = tk.Frame(canvas, bg='peachpuff')
    canvas.create_window((0, 0), window=items_frame, anchor="nw")

    # Configure the canvas to update its scroll region
    items_frame.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.configure(yscrollcommand=scrollbar.set)

    cart_frame = tk.Frame(root, bg='peachpuff')
    cart_frame.pack(pady=10)

    cart = {}

    def update_cart_display():
        for widget in cart_frame.winfo_children():
            widget.destroy()
        total_price = 0
        total_items = 0  # Initialize total_items
        for item, details in cart.items():
            item_frame = tk.Frame(cart_frame, bg='peachpuff')
            item_frame.pack(pady=5)
            

            item_info = f"{item.capitalize()} - Qty: {details['quantity']}, Price: {details['price'] * details['quantity']}"
            total_price += details['price'] * details['quantity']
            total_items += details['quantity']  # Update total_items with the quantity
            tk.Label(item_frame, text=item_info, bg='peachpuff').pack(side=tk.LEFT)
        if total_items > 7:
            messagebox.showwarning("Order Limit Exceeded", "You can only order a maximum of 7 items.")
            return
        tk.Label(cart_frame, text=f"Total Price: {total_price}", bg='peachpuff').pack(pady=10)

    def add_to_cart(item, price):
        if item not in cart:
            cart[item] = {"quantity": 1, "price": price}
        else:
            cart[item]["quantity"] += 1
        update_cart_display()

    def remove_from_cart(item):
        if item in cart:
            cart[item]["quantity"] -= 1
            if cart[item]["quantity"] <= 0:
                del cart[item]
        update_cart_display()

    def load_items():
        for widget in items_frame.winfo_children():
            widget.destroy()

        cursor.execute("SELECT item, quantity, selling_price, boycotted FROM menu WHERE category=?", (category_var.get(),))
        items = cursor.fetchall()

        for item in items:
            item_frame = tk.Frame(items_frame, bg='peachpuff')
            item_frame.pack(pady=5, anchor='w')

            item_label = tk.Label(item_frame, text=f"{item[0]} - Qty: {item[1]}, Price: {item[2]}, Boycotted: {item[3]}", font=("Helvetica", 12, "bold"), bg='peachpuff')
            item_label.pack(side=tk.LEFT)

            add_button = tk.Button(item_frame, text="+", command=lambda i=item[0], p=item[2]: add_to_cart(i, p), bg='peachpuff')
            add_button.pack(side=tk.RIGHT)
            remove_button = tk.Button(item_frame, text="-", command=lambda i=item[0]: remove_from_cart(i), bg='peachpuff')
            remove_button.pack(side=tk.RIGHT)

    tk.Button(root, text="Load Items", command=load_items, font=("Helvetica", 18), bg='peach puff', fg='brown').pack(pady=20, padx=20)
    tk.Button(root, text="Go to Billing", command=lambda: billing(student_id, cart), font=("Helvetica", 18), bg='peach puff', fg='brown').pack(pady=20, padx=20)
    tk.Button(root, text="Back", command=lambda: student_portal(student_id), font=("Helvetica", 18), bg='peach puff', fg='brown').pack(pady=20, padx=20)

def billing(student_id, cart):
    clear_window()
    root.configure(bg='peachpuff')
    tk.Label(root, text="Billing", font=("Helvetica", 30, "bold"), fg='brown', bg='peachpuff').pack(pady=20)

    # Display a narrow receipt
    receipt_frame = tk.Frame(root, bg='white', relief="solid", borderwidth=2, width=1000)
    receipt_frame.pack(pady=10, padx=10)

    tk.Label(receipt_frame, text="UBIT Canteen", font=("Helvetica", 24), bg='white').pack(pady=20, padx=30)
    tk.Label(receipt_frame, text=f"Invoice to: {student_id}", font=("Helvetica", 12), bg='white').pack()

    items_frame = tk.Frame(receipt_frame, bg='white')
    items_frame.pack(pady=5, padx=5)

    tk.Label(items_frame, text="Sl. | Item | Price | Qty | Total", bg='white', anchor="w", justify=tk.LEFT).pack()

    total_price = 0

    for idx, (item, details) in enumerate(cart.items(), start=1):
        item_total = details['price'] * details['quantity']
        total_price += item_total
        tk.Label(items_frame, text=f"{idx}.  | {item.capitalize()} | {details['price']} | {details['quantity']} | {item_total}", bg='white', anchor="w", justify=tk.LEFT).pack()

    tk.Label(receipt_frame, text=f"Subtotal: {total_price}", font=("Helvetica", 12), bg='white').pack(pady=5)
    tk.Label(receipt_frame, text=f"Total: {total_price}", font=("Helvetica", 12, 'bold'), bg='white').pack(pady=20)

    def place_order():
        items_str = '\n'.join([f"{item} x {details['quantity']}" for item, details in cart.items()])
        cursor.execute('''INSERT INTO orders (student_id, items, total_price) VALUES (?, ?, ?)''', (student_id, items_str, total_price))
        conn.commit()
        messagebox.showinfo("Order Placed", "Your order has been placed successfully! Pick it from the canteen receptionist area")
        student_portal(student_id)

    tk.Button(root, text="Place Order", command=place_order, font=("Helvetica", 18), bg='peach puff', fg='brown').pack(pady=20)
    tk.Button(root, text="Back", command=lambda: show_menu(student_id),font=("Helvetica", 18), bg='peach puff', fg='brown').pack(pady=20)

def previous_orders(student_id):
    clear_window()
    root.configure(bg='peach puff')
    tk.Label(root, text="Previous Orders", font=("Helvetica", 30, "bold"),bg='light salmon', fg='brown').pack(pady=50)

    # Create a canvas to hold the orders frame
    canvas = tk.Canvas(root, bg='peach puff')
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Add a scrollbar to the canvas
    scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Create a frame inside the canvas to hold the orders
    orders_frame = tk.Frame(canvas, bg='peach puff')
    
    # Configure the canvas to scroll with the frame
    canvas.create_window((0, 0), window=orders_frame, anchor="nw")
    orders_frame.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.configure(yscrollcommand=scrollbar.set)

    # Fetch orders from the database
    cursor.execute("SELECT items, total_price FROM orders WHERE student_id=?", (student_id,))
    orders = cursor.fetchall()

    # Display each order in the orders_frame
    for order in orders:
        order_frame = tk.Frame(orders_frame, bg='peach puff')
        order_frame.pack(pady=5, padx=10, anchor='w')

        order_info = f"Items: {order[0]}, Total Price: {order[1]}"
        tk.Label(order_frame, text=order_info, font=("Helvetica", 18), bg='peach puff', fg='brown', wraplength=500, justify="left").pack(side=tk.LEFT)

    # Back button to return to the student portal
    tk.Button(root, text="Back", command=lambda: student_portal(student_id), font=("Helvetica", 18), bg='peach puff', fg='brown').pack(pady=20, padx=20)

def change_password(student_id):
    clear_window()
    root.configure(bg='peach puff')
    tk.Label(root, text="Change Password", font=("Helvetica", 30,"bold"), bg= 'light salmon', fg='brown').pack(pady=50)

    tk.Label(root, text="New Password", font=("Helvetica", 22), fg='brown').pack(pady=20)
    new_password = tk.Entry(root, show="*", width=40)
    new_password.pack(pady=5)

    def update_password():
        cursor.execute("UPDATE student SET password=? WHERE id=?", (new_password.get(), student_id))
        conn.commit()
        messagebox.showinfo("Success", "Password updated successfully!")
        student_portal(student_id)

    tk.Button(root, text="Change Password", command=update_password, font=("Helvetica", 18), bg='peach puff', fg='brown').pack(pady=30)
    tk.Button(root, text="Back", command=lambda: student_portal(student_id), font=("Helvetica", 18), bg='peach puff', fg='brown').pack(pady=20)

def student_signup():
    clear_window()
    root.configure(bg='peach puff')
    # Create a frame for the sign-up form
    signup_frame = tk.Frame(root, bg='white')
    signup_frame.pack(pady=50)

    # Create a label for the sign-up title
    tk.Label(signup_frame, text="Student Sign-Up", font=("Helvetica", 24), bg='#FFFFFF', fg='brown').pack(pady=20)

    # Create a frame for the input fields
    input_frame = tk.Frame(signup_frame, bg='white')
    input_frame.pack(pady=20)

    # Create labels and entries for student ID, name, CNIC, major, and photo
    tk.Label(input_frame, text="Student ID", bg='white', fg='black').grid(row=0, column=0, padx=10, pady=10)
    student_id = tk.Entry(input_frame, width=30, bg='#F7F7F7', fg='#808080')
    student_id.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(input_frame, text="Name", bg='white', fg='black').grid(row=1, column=0, padx=10, pady=10)
    name = tk.Entry(input_frame, width=30, bg='#F7F7F7', fg='#808080')
    name.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(input_frame, text="CNIC", bg='white', fg='black').grid(row=2, column=0, padx=10, pady=10)
    cnic = tk.Entry(input_frame, width=30, bg='#F7F7F7', fg='#808080')
    cnic.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(input_frame, text="Major", bg='white', fg='black').grid(row=3, column=0, padx=10, pady=10)
    major = tk.Entry(input_frame, width=30, bg='#F7F7F7', fg='#808080')
    major.grid(row=3, column=1, padx=10, pady=10)

    tk.Label(input_frame, text="Section", bg='white', fg='black').grid(row=4, column=0, padx=10, pady=10)
    section = tk.Entry(input_frame, width=30, bg='#F7F7F7', fg='#808080')
    section.grid(row=4, column=1, padx=10, pady=10)

    def register_student():
        validation_result, message = validate_student_data(student_id.get(), cnic.get())
        if not validation_result:
            messagebox.showerror("Error", message)
            return

        generated_password = generate_random_password()
        cursor.execute('''INSERT INTO student (id, name, cnic, major, section, password)
                          VALUES (?, ?, ?, ?, ?, ?)''',
                       (student_id.get(), name.get(), cnic.get(), major.get(), section.get(), generated_password))
        conn.commit()

        tk.Label(signup_frame, text="Password Generated:", font=("Helvetica", 18), bg='#FFFFFF', fg='#808080').pack(pady=10)
        password_label = tk.Label(signup_frame, text=generated_password, font=("Helvetica", 18), bg='#FFFFFF', fg='#808080')
        password_label.pack(pady=10)

        def copy_password():
            root.clipboard_clear()
            root.clipboard_append(generated_password)
            root.update()
            messagebox.showinfo("Copied", "Password copied to clipboard!")

        tk.Button(signup_frame, text="Copy Password", command=copy_password, bg='peach puff', fg='brown').pack(pady=10)
        tk.Button(signup_frame, text="Sign In", command=student_login, bg='peach puff', fg='brown').pack(pady=10)

    tk.Button(input_frame, text="Sign Up", command=register_student, bg='peach puff', fg='brown').grid(row=5, column=1, padx=10, pady=10)
    tk.Button(input_frame, text="Back", command=student_menu,bg='peach puff', fg='brown').grid(row=5, column=2, padx=10, pady=10)
    
def student_login():
    clear_window()
    root.configure(bg='peach puff')

    # Create a frame for the login form
    login_frame = tk.Frame(root, bg='white')
    login_frame.pack(pady=180, padx=180)

    # Create a label for the student login title
    tk.Label(login_frame, text="Student Login", font=("Helvetica", 24, "bold"), fg='brown', bg='white').pack(pady=20)

    # Create a frame for the input fields
    input_frame = tk.Frame(login_frame, bg='white')
    input_frame.pack(pady=20)

    # Create labels and entries for student ID and password
    tk.Label(input_frame, text="Student ID", font=("Helvetica", 18), fg='black', bg='white').grid(row=0, column=0, padx=10, pady=10)
    student_id = tk.Entry(input_frame, font=("Helvetica", 18), width=25)
    student_id.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(input_frame, text="Password", font=("Helvetica", 18), fg='black', bg='white').grid(row=1, column=0, padx=10, pady=10)
    student_password = tk.Entry(input_frame, font=("Helvetica", 18), width=25, show="*")
    student_password.grid(row=1, column=1, padx=10, pady=10)

    def login_student():
        cursor.execute("SELECT password FROM student WHERE id=?", (student_id.get(),))
        result = cursor.fetchone()
        if result and result[0] == student_password.get():
            student_portal(student_id.get())
        else:
            messagebox.showerror("Error", "Invalid student ID or password.")
    
    tk.Button(input_frame, text="Login", command=login_student, font=("Helvetica", 18), bg='peach puff', fg='brown', width=10).grid(row=2, column=1, padx=10, pady=20)
    tk.Button(input_frame, text="Back", command=student_menu, font=("Helvetica", 18), bg='peach puff', fg='brown', width=10).grid(row=2, column=0, padx=10, pady=20)

# Main Screen
def main_screen():
    clear_window()

    response = requests.get("https://i.ytimg.com/vi/j03xfrFeYhM/maxresdefault.jpg")
    img_data = response.content
    img = Image.open(BytesIO(img_data))
    img = img.resize((root.winfo_screenwidth(), root.winfo_screenheight()))
    background_image = ImageTk.PhotoImage(img)

    background_label = tk.Label(root, image=background_image)
    background_label.image = background_image
    background_label.place(relwidth=1, relheight=1)

    tk.Label(root, text="UBIT Canteen Management System", font=("Helvetica", 44, "bold"), fg='brown').pack(pady=70)

    tk.Button(root, text="Shopkeeper", command=shopkeeper_login, font=("Helvetica", 28), activebackground='lavender', activeforeground='brown', bg='peach puff', fg='brown').pack(pady=20)
    tk.Button(root, text="Student", command=student_menu, font=("Helvetica", 28), activebackground='lavender', activeforeground='brown', bg='peach puff', fg='brown').pack(pady=20)
    tk.Button(root, text="Exit", command=root.quit, font=("Helvetica", 28), activebackground='lavender', activeforeground='brown',  bg='peach puff', fg='brown').pack(pady=20)

def shopkeeper_login():
    clear_window()
    root.configure(bg='peach puff')

    # Create a frame for the login form
    login_frame = tk.Frame(root, bg='white')
    login_frame.pack(pady=180, padx=180)

    # Create a label for the shopkeeper login title
    tk.Label(login_frame, text="Shopkeeper Login", font=("Helvetica", 24, "bold"), fg='brown', bg='white').pack(pady=20)

    # Create a frame for the input fields
    input_frame = tk.Frame(login_frame, bg='white')
    input_frame.pack(pady=20)

    # Create labels and entries for shopkeeper ID and password
    tk.Label(input_frame, text="Shopkeeper ID", font=("Helvetica", 18), fg='black', bg='white').grid(row=0, column=0, padx=10, pady=10)
    shopkeeper_id = tk.Entry(input_frame, font=("Helvetica", 18), width=25)
    shopkeeper_id.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(input_frame, text="Password", font=("Helvetica", 18), fg='black', bg='white').grid(row=1, column=0, padx=10, pady=10)
    shopkeeper_password = tk.Entry(input_frame, font=("Helvetica", 18), width=25, show="*")
    shopkeeper_password.grid(row=1, column=1, padx=10, pady=10)

    def login_shopkeeper():
        global current_shopkeeper_id
        cursor.execute("SELECT password FROM shopkeeper WHERE id=?", (shopkeeper_id.get(),))
        result = cursor.fetchone()

        if result and result[0] == shopkeeper_password.get():
            current_shopkeeper_id = shopkeeper_id.get()
            shopkeeper_menu(current_shopkeeper_id)
        else:
            messagebox.showerror("Error", "Invalid shopkeeper ID or password.")

    tk.Button(input_frame, text="Login", command=login_shopkeeper, font=("Helvetica", 18), bg='peach puff', fg='brown', width=10).grid(row=2, column=1, padx=10, pady=20)

    # Create a button for back
    tk.Button(input_frame, text="Back", command=main_screen, font=("Helvetica", 18), bg='peach puff', fg='brown', width=10).grid(row=2, column=0, padx=20, pady=20)

# Initialize the main application window
root = tk.Tk()
root.title("Cafeteria Management System")
root.geometry("1200x1000")

# Launch the main screen
main_screen()

# Start the GUI event loop
root.mainloop()