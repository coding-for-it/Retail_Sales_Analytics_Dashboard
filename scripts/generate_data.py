"""
generate_data.py
----------------
Sample data generator for the Retail Sales Analytics project.

Generates realistic Indian retail data with intentional dirty rows for
validation testing.

Output:
  data/customers.csv  ~520 rows (500 clean + ~20 dirty)
  data/products.csv   ~110 rows (100 clean + ~10 dirty)
  data/orders.csv     ~5100 rows (5000 clean + ~100 dirty)

Run:
  python scripts/generate_data.py
"""

import os
import random
import sys
from datetime import date, timedelta

import pandas as pd

# ── Path Setup ────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR  = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

random.seed(42)

# ─────────────────────────────────────────────────────────────────────────────
# REFERENCE DATA
# ─────────────────────────────────────────────────────────────────────────────

FIRST_NAMES = [
    "Aarav", "Aditya", "Akash", "Amit", "Ananya", "Anjali", "Ankit", "Arjun",
    "Aryan", "Ayesha", "Chetan", "Deepa", "Deepak", "Divya", "Gaurav", "Harsha",
    "Ishaan", "Jatin", "Kavita", "Kiran", "Komal", "Krishna", "Lakshmi", "Manish",
    "Meera", "Mohan", "Nisha", "Nitin", "Palak", "Pooja", "Priya", "Rahul",
    "Raj", "Ravi", "Ritika", "Rohan", "Rohit", "Sakshi", "Sandeep", "Sanjay",
    "Sara", "Shreya", "Simran", "Sneha", "Suresh", "Swati", "Tanvi", "Uday",
    "Varun", "Vikas", "Vikram", "Vinita", "Yash", "Zara", "Nisha", "Karan",
    "Preeti", "Vivek", "Neeraj", "Payal", "Kunal", "Megha", "Asha", "Suraj",
]

LAST_NAMES = [
    "Sharma", "Verma", "Singh", "Kumar", "Patel", "Shah", "Mehta", "Gupta",
    "Joshi", "Mishra", "Agarwal", "Bansal", "Chopra", "Desai", "Rao", "Nair",
    "Reddy", "Iyer", "Pillai", "Menon", "Bhat", "Kaur", "Bose", "Das",
    "Chakraborty", "Mukherjee", "Ghosh", "Dey", "Sinha", "Tiwari",
]

CITIES_BY_STATE: dict = {
    "Maharashtra":    (["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad"],    "West"),
    "Delhi":          (["New Delhi", "Noida", "Dwarka", "Rohini", "Karol Bagh"],"North"),
    "Karnataka":      (["Bengaluru", "Mysuru", "Hubli", "Mangaluru", "Belagavi"],"South"),
    "Tamil Nadu":     (["Chennai", "Coimbatore", "Madurai", "Salem", "Trichy"], "South"),
    "Gujarat":        (["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Gandhinagar"],"West"),
    "Uttar Pradesh":  (["Lucknow", "Agra", "Kanpur", "Varanasi", "Prayagraj"], "North"),
    "Rajasthan":      (["Jaipur", "Jodhpur", "Udaipur", "Kota", "Bikaner"],    "North"),
    "West Bengal":    (["Kolkata", "Howrah", "Durgapur", "Asansol", "Siliguri"],"East"),
    "Telangana":      (["Hyderabad", "Warangal", "Nizamabad", "Khammam"],      "South"),
    "Punjab":         (["Chandigarh", "Ludhiana", "Amritsar", "Jalandhar"],    "North"),
    "Kerala":         (["Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur"],"South"),
    "Madhya Pradesh": (["Bhopal", "Indore", "Gwalior", "Jabalpur"],            "North"),
    "Bihar":          (["Patna", "Gaya", "Muzaffarpur", "Bhagalpur"],          "East"),
    "Odisha":         (["Bhubaneswar", "Cuttack", "Rourkela", "Berhampur"],    "East"),
    "Andhra Pradesh": (["Visakhapatnam", "Vijayawada", "Guntur", "Tirupati"],  "South"),
    "Haryana":        (["Gurugram", "Faridabad", "Ambala", "Panipat"],         "North"),
    "Assam":          (["Guwahati", "Dibrugarh", "Jorhat", "Silchar"],         "East"),
    "Goa":            (["Panaji", "Margao", "Vasco da Gama"],                  "West"),
    "Jharkhand":      (["Ranchi", "Jamshedpur", "Dhanbad", "Bokaro"],          "East"),
    "Uttarakhand":    (["Dehradun", "Haridwar", "Rishikesh", "Nainital"],      "North"),
}

PRODUCTS_DATA = [
    # Category, Product_Name, Brand, Price
    # Electronics
    ("Electronics", "Samsung Galaxy S24 Ultra",         "Samsung",  89999),
    ("Electronics", "Apple iPhone 15 Pro",              "Apple",    134999),
    ("Electronics", "OnePlus 12R",                      "OnePlus",  39999),
    ("Electronics", "Redmi Note 13 Pro",                "Xiaomi",   24999),
    ("Electronics", "Realme Narzo 60 Pro",              "Realme",   19999),
    ("Electronics", "Dell Inspiron 15 Laptop",          "Dell",     62999),
    ("Electronics", "HP Pavilion 14 Laptop",            "HP",       54999),
    ("Electronics", "Lenovo IdeaPad Slim 5",            "Lenovo",   47999),
    ("Electronics", "Asus VivoBook 15",                 "Asus",     44999),
    ("Electronics", "Samsung 55 Inch 4K Smart TV",      "Samsung",  59999),
    ("Electronics", "LG OLED 48 Inch TV",               "LG",       79999),
    ("Electronics", "Sony Bravia 43 Inch TV",           "Sony",     44999),
    ("Electronics", "boAt Airdopes 141",                "boAt",     1499),
    ("Electronics", "Sony WH-1000XM5 Headphones",      "Sony",     29990),
    ("Electronics", "JBL Charge 5 Speaker",             "JBL",     14999),
    ("Electronics", "Canon EOS R50 Camera",             "Canon",   54999),
    ("Electronics", "Nikon Z30 Mirrorless Camera",      "Nikon",   68999),
    ("Electronics", "iPad Air 5th Generation",          "Apple",   59900),
    ("Electronics", "Samsung Galaxy Tab S9",            "Samsung",  73999),
    ("Electronics", "Logitech MX Master 3 Mouse",       "Logitech", 8995),
    ("Electronics", "HP LaserJet Printer",              "HP",      14999),
    ("Electronics", "Epson EcoTank Printer",            "Epson",   12999),
    ("Electronics", "Seagate 2TB External Hard Drive",  "Seagate",  5999),
    ("Electronics", "SanDisk 512GB USB Drive",          "SanDisk",  2499),
    ("Electronics", "Dlink WiFi Router AC1200",         "Dlink",    2499),
    # Fashion
    ("Fashion", "Levi's 511 Slim Fit Jeans",            "Levi's",  3999),
    ("Fashion", "Wrangler Regular Fit Jeans",           "Wrangler", 2499),
    ("Fashion", "Allen Solly Formal Shirt",             "Allen Solly", 1699),
    ("Fashion", "Van Heusen Slim Fit Shirt",            "Van Heusen",  1999),
    ("Fashion", "Nike Air Max 270 Sneakers",            "Nike",    9999),
    ("Fashion", "Adidas Ultraboost Running Shoes",      "Adidas",  12999),
    ("Fashion", "Puma Softride Running Shoes",          "Puma",    4999),
    ("Fashion", "H&M Floral Kurta",                    "H&M",     1299),
    ("Fashion", "Global Desi Printed Saree",            "Global Desi", 2499),
    ("Fashion", "Biba Embroidered Salwar Suit",         "Biba",    3499),
    ("Fashion", "Fossil Gen 6 Smartwatch",              "Fossil",  22495),
    ("Fashion", "Titan Raga Watch",                    "Titan",    6995),
    ("Fashion", "Fastrack Sports Watch",               "Fastrack",  1995),
    ("Fashion", "Wildcraft Backpack 30L",              "Wildcraft",  2299),
    ("Fashion", "Lavie Laptop Bag",                    "Lavie",    1799),
    # Home & Kitchen
    ("Home & Kitchen", "Prestige Induction Cooktop",   "Prestige",  2999),
    ("Home & Kitchen", "Philips Air Fryer XXL",        "Philips",   9999),
    ("Home & Kitchen", "Instant Pot Duo 7-in-1",       "Instant Pot",7999),
    ("Home & Kitchen", "Bosch Mixer Grinder 750W",     "Bosch",     4999),
    ("Home & Kitchen", "Pigeon Stainless Steel Cookware Set","Pigeon",2999),
    ("Home & Kitchen", "Milton Thermosteel Flask 1L",  "Milton",     999),
    ("Home & Kitchen", "Cello Opalware Dinner Set",    "Cello",     2499),
    ("Home & Kitchen", "Whirlpool 265L Double Door Refrigerator","Whirlpool",28999),
    ("Home & Kitchen", "Samsung 7Kg Washing Machine",  "Samsung",  31999),
    ("Home & Kitchen", "Dyson V15 Vacuum Cleaner",     "Dyson",    44900),
    # Beauty
    ("Beauty", "Lakme 9to5 Foundation",                "Lakme",     699),
    ("Beauty", "Nykaa Cosmetics Lip Liner",            "Nykaa",     299),
    ("Beauty", "Maybelline Fit Me Foundation",         "Maybelline",499),
    ("Beauty", "L'Oreal Paris Revitalift Serum",       "L'Oreal",  1299),
    ("Beauty", "Biotique Bio Honey Gel Facewash",      "Biotique",  299),
    ("Beauty", "The Ordinary Niacinamide 10% Serum",   "The Ordinary",699),
    ("Beauty", "Dove Body Lotion 400ml",               "Dove",      299),
    ("Beauty", "Himalaya Herbals Face Cream",          "Himalaya",  199),
    ("Beauty", "Clinique Moisture Surge Moisturiser",  "Clinique", 3499),
    ("Beauty", "Forest Essentials Facial Cleanser",    "Forest Essentials",1295),
    # Sports
    ("Sports", "Yonex Badminton Racquet",              "Yonex",    2499),
    ("Sports", "DSC Cricket Bat Kashmir Willow",       "DSC",      1799),
    ("Sports", "Cosco Football Size 5",                "Cosco",     899),
    ("Sports", "Nivia Basketball",                     "Nivia",    1299),
    ("Sports", "Strauss Yoga Mat 6mm",                "Strauss",   699),
    ("Sports", "Decathlon Resistance Bands Set",       "Decathlon",  999),
    ("Sports", "Skybags Pro Cycling Helmet",           "Skybags",  2499),
    ("Sports", "Garmin Forerunner 255 GPS Watch",      "Garmin",  34999),
    ("Sports", "Fitbit Charge 6 Fitness Tracker",      "Fitbit",  14999),
    ("Sports", "Speedo Adult Swim Goggles",            "Speedo",    799),
    # Books
    ("Books", "Rich Dad Poor Dad by Robert Kiyosaki",  "Simon & Schuster",499),
    ("Books", "Atomic Habits by James Clear",          "Penguin",   499),
    ("Books", "The Alchemist by Paulo Coelho",         "HarperCollins",299),
    ("Books", "Zero to One by Peter Thiel",            "Virgin Books",399),
    ("Books", "Deep Work by Cal Newport",              "Piatkus",   399),
    ("Books", "Think and Grow Rich by Napoleon Hill",  "Fingerprint",299),
    ("Books", "Python Crash Course by Eric Matthes",   "No Starch Press",699),
    ("Books", "SQL for Data Analytics",               "Packt",     799),
    ("Books", "The Psychology of Money",              "Jaico",     399),
    ("Books", "Ikigai by Hector Garcia",              "Penguin",   299),
    # Furniture
    ("Furniture", "Wakefit Orthopaedic Memory Foam Mattress","Wakefit",12999),
    ("Furniture", "Pepperfry Fabric 3-Seater Sofa",   "Pepperfry",24999),
    ("Furniture", "Ikea Kallax Shelf Unit",            "Ikea",      7999),
    ("Furniture", "Nilkamal Study Table with Shelf",   "Nilkamal",  4999),
    ("Furniture", "Godrej Interio Wardrobe 3 Door",    "Godrej",   34999),
    ("Furniture", "Green Soul Ergonomic Office Chair", "Green Soul",12999),
    ("Furniture", "Durian Recliner Sofa Chair",        "Durian",   29999),
    ("Furniture", "Wooden Street King Size Bed",       "Wooden Street",28999),
    # Groceries
    ("Groceries", "Aashirvaad Atta 10Kg",              "Aashirvaad",  499),
    ("Groceries", "Fortune Sunflower Oil 5L",          "Fortune",   799),
    ("Groceries", "Tata Salt 1Kg",                    "Tata",        25),
    ("Groceries", "Amul Butter 500g",                 "Amul",       275),
    ("Groceries", "Nestle Maggi 12 Pack",              "Nestle",     299),
    ("Groceries", "Bru Gold Coffee 200g",              "Bru",        399),
    ("Groceries", "Britannia Good Day Cookies 400g",   "Britannia",  129),
    ("Groceries", "Haldiram Bhujia Sev 400g",          "Haldiram",   179),
    ("Groceries", "Dettol Handwash Liquid 500ml",      "Dettol",     179),
    ("Groceries", "Surf Excel Matic Liquid 2L",        "Surf Excel",  599),
]

ORDER_STATUSES   = ["Completed", "Pending", "Cancelled", "Returned"]
PAYMENT_METHODS  = ["UPI", "Card", "Cash", "Net Banking"]

# Status weights: ~70% Completed, 15% Pending, 10% Cancelled, 5% Returned
STATUS_WEIGHTS   = [0.70, 0.15, 0.10, 0.05]
# Payment method weights: UPI most popular
PAYMENT_WEIGHTS  = [0.40, 0.30, 0.15, 0.15]

DISCOUNTS = [0, 0, 0, 5, 5, 10, 10, 15, 20, 25, 30]  # 0 most common


def random_date(start: date, end: date) -> str:
    delta = (end - start).days
    return (start + timedelta(days=random.randint(0, delta))).isoformat()


# ─────────────────────────────────────────────────────────────────────────────
# GENERATE CUSTOMERS
# ─────────────────────────────────────────────────────────────────────────────

def generate_customers(n: int = 500) -> pd.DataFrame:
    """Generate n clean customer records + ~20 dirty records."""
    rows = []
    states = list(CITIES_BY_STATE.keys())

    for i in range(1, n + 1):
        first = random.choice(FIRST_NAMES)
        last  = random.choice(LAST_NAMES)
        name  = f"{first} {last}"
        cid   = f"C{i:04d}"
        state = random.choice(states)
        city  = random.choice(CITIES_BY_STATE[state][0])
        region = CITIES_BY_STATE[state][1]
        email = f"{first.lower()}.{last.lower()}{random.randint(1, 99)}@{random.choice(['gmail','yahoo','outlook'])}.com"
        phone = f"{random.randint(6, 9)}{random.randint(100000000, 999999999)}"
        jdate = random_date(date(2020, 1, 1), date(2024, 12, 31))
        rows.append([cid, name, email, phone, city, state, region, jdate])

    df = pd.DataFrame(rows, columns=[
        "Customer_ID", "Customer_Name", "Email",
        "Phone", "City", "State", "Region", "Join_Date"
    ])

    # ── Inject dirty rows ────────────────────────────────────────────────────
    dirty = []

    # Dirty 1-4: Duplicate Customer_IDs
    for _ in range(4):
        row = df.sample(1).iloc[0].tolist()
        dirty.append(row)

    # Dirty 5-7: Missing Customer_ID
    for _ in range(3):
        r = df.sample(1).iloc[0].tolist()
        r[0] = None
        dirty.append(r)

    # Dirty 8-10: Missing Customer_Name
    for _ in range(3):
        r = df.sample(1).iloc[0].tolist()
        r[1] = None
        dirty.append(r)

    # Dirty 11-14: Invalid Email
    for bad_email in ["notanemail", "missing@", "double@@gmail.com", "no_domain"]:
        r = df.sample(1).iloc[0].tolist()
        r[0] = f"C{n + len(dirty) + 1:04d}"
        r[2] = bad_email
        dirty.append(r)

    # Dirty 15-17: Invalid Phone
    for bad_phone in ["123", "abcdefghij", "00000000000"]:
        r = df.sample(1).iloc[0].tolist()
        r[0] = f"C{n + len(dirty) + 1:04d}"
        r[3] = bad_phone
        dirty.append(r)

    # Dirty 18-19: Invalid Region
    for bad_region in ["Central", "Unknown"]:
        r = df.sample(1).iloc[0].tolist()
        r[0] = f"C{n + len(dirty) + 1:04d}"
        r[6] = bad_region
        dirty.append(r)

    # Dirty 20: Missing City
    r = df.sample(1).iloc[0].tolist()
    r[0] = f"C{n + len(dirty) + 1:04d}"
    r[4] = None
    dirty.append(r)

    dirty_df = pd.DataFrame(dirty, columns=df.columns)
    result = pd.concat([df, dirty_df], ignore_index=True)

    # Shuffle to mix dirty rows throughout the file
    result = result.sample(frac=1, random_state=42).reset_index(drop=True)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# GENERATE PRODUCTS
# ─────────────────────────────────────────────────────────────────────────────

def generate_products() -> pd.DataFrame:
    """Generate ~100 clean product records + ~10 dirty records."""
    rows = []
    for i, (cat, name, brand, price) in enumerate(PRODUCTS_DATA, start=1):
        pid = f"P{i:03d}"
        rows.append([pid, name, cat, brand, float(price)])

    df = pd.DataFrame(rows, columns=[
        "Product_ID", "Product_Name", "Category", "Brand", "Price"
    ])

    # ── Inject dirty rows ────────────────────────────────────────────────────
    dirty = []
    n = len(df)

    # Dirty 1-2: Duplicate Product_IDs
    for _ in range(2):
        dirty.append(df.sample(1).iloc[0].tolist())

    # Dirty 3-4: Missing Product_ID
    for _ in range(2):
        r = df.sample(1).iloc[0].tolist()
        r[0] = None
        dirty.append(r)

    # Dirty 5: Missing Product_Name
    r = df.sample(1).iloc[0].tolist()
    r[0] = f"P{n + len(dirty) + 1:03d}"
    r[1] = None
    dirty.append(r)

    # Dirty 6-7: Invalid Category
    for bad_cat in ["Misc", "Unknown Category"]:
        r = df.sample(1).iloc[0].tolist()
        r[0] = f"P{n + len(dirty) + 1:03d}"
        r[2] = bad_cat
        dirty.append(r)

    # Dirty 8-9: Negative Price
    for bad_price in [-99.99, -1.0]:
        r = df.sample(1).iloc[0].tolist()
        r[0] = f"P{n + len(dirty) + 1:03d}"
        r[4] = bad_price
        dirty.append(r)

    # Dirty 10: Zero Price
    r = df.sample(1).iloc[0].tolist()
    r[0] = f"P{n + len(dirty) + 1:03d}"
    r[4] = 0.0
    dirty.append(r)

    dirty_df = pd.DataFrame(dirty, columns=df.columns)
    result   = pd.concat([df, dirty_df], ignore_index=True)
    result   = result.sample(frac=1, random_state=42).reset_index(drop=True)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# GENERATE ORDERS
# ─────────────────────────────────────────────────────────────────────────────

def generate_orders(
    n: int,
    customer_ids: list,
    product_ids: list,
    product_prices: dict,
) -> pd.DataFrame:
    """Generate n clean order records + ~100 dirty records."""
    rows = []
    start_date = date(2024, 1, 1)
    end_date   = date(2025, 6, 30)

    for i in range(1, n + 1):
        oid     = f"ORD{i:05d}"
        cid     = random.choice(customer_ids)
        pid     = random.choice(product_ids)
        odate   = random_date(start_date, end_date)
        qty     = random.randint(1, 10)
        price   = product_prices.get(pid, 999.0)
        disc    = random.choice(DISCOUNTS)
        total   = round(qty * price * (1 - disc / 100), 2)
        status  = random.choices(ORDER_STATUSES, weights=STATUS_WEIGHTS)[0]
        payment = random.choices(PAYMENT_METHODS, weights=PAYMENT_WEIGHTS)[0]
        rows.append([oid, cid, pid, odate, qty, price, disc, total, status, payment])

    df = pd.DataFrame(rows, columns=[
        "Order_ID", "Customer_ID", "Product_ID", "Order_Date",
        "Quantity", "Unit_Price", "Discount", "Total_Amount",
        "Order_Status", "Payment_Method"
    ])

    # ── Inject dirty rows ────────────────────────────────────────────────────
    dirty = []

    # Dirty 1-8: Duplicate Order_IDs
    for _ in range(8):
        dirty.append(df.sample(1).iloc[0].tolist())

    # Dirty 9-12: Missing Order_ID
    for _ in range(4):
        r = df.sample(1).iloc[0].tolist()
        r[0] = None
        dirty.append(r)

    # Dirty 13-15: Missing Customer_ID
    for _ in range(3):
        r = df.sample(1).iloc[0].tolist()
        r[0] = f"ORD{n + len(dirty) + 1:05d}"
        r[1] = None
        dirty.append(r)

    # Dirty 16-18: Invalid Customer_ID (FK violation)
    for fake_cid in ["C9999", "CXXXXX", "C0000"]:
        r = df.sample(1).iloc[0].tolist()
        r[0] = f"ORD{n + len(dirty) + 1:05d}"
        r[1] = fake_cid
        dirty.append(r)

    # Dirty 19-21: Missing Product_ID
    for _ in range(3):
        r = df.sample(1).iloc[0].tolist()
        r[0] = f"ORD{n + len(dirty) + 1:05d}"
        r[2] = None
        dirty.append(r)

    # Dirty 22-24: Invalid Product_ID (FK violation)
    for fake_pid in ["P999", "PXXX", "P000"]:
        r = df.sample(1).iloc[0].tolist()
        r[0] = f"ORD{n + len(dirty) + 1:05d}"
        r[2] = fake_pid
        dirty.append(r)

    # Dirty 25-30: Negative Quantity
    for bad_qty in [-1, -5, -3, 0, -2, -7]:
        r = df.sample(1).iloc[0].tolist()
        r[0] = f"ORD{n + len(dirty) + 1:05d}"
        r[4] = bad_qty
        dirty.append(r)

    # Dirty 31-34: Negative Unit_Price
    for bad_price in [-100, -999.9, -50, -1]:
        r = df.sample(1).iloc[0].tolist()
        r[0] = f"ORD{n + len(dirty) + 1:05d}"
        r[5] = bad_price
        dirty.append(r)

    # Dirty 35-38: Future Order_Date
    for future_days in [30, 60, 90, 365]:
        future_date_str = (date.today() + timedelta(days=future_days)).isoformat()
        r = df.sample(1).iloc[0].tolist()
        r[0] = f"ORD{n + len(dirty) + 1:05d}"
        r[3] = future_date_str
        dirty.append(r)

    # Dirty 39-41: Invalid Order_Status
    for bad_status in ["Dispatched", "Unknown", "Processing"]:
        r = df.sample(1).iloc[0].tolist()
        r[0] = f"ORD{n + len(dirty) + 1:05d}"
        r[8] = bad_status
        dirty.append(r)

    # Dirty 42-44: Invalid Payment_Method
    for bad_pay in ["Crypto", "Cheque", "EMI"]:
        r = df.sample(1).iloc[0].tolist()
        r[0] = f"ORD{n + len(dirty) + 1:05d}"
        r[9] = bad_pay
        dirty.append(r)

    # Dirty 45-47: Discount out of range
    for bad_disc in [-10, 95, 100]:
        r = df.sample(1).iloc[0].tolist()
        r[0] = f"ORD{n + len(dirty) + 1:05d}"
        r[6] = bad_disc
        dirty.append(r)

    dirty_df = pd.DataFrame(dirty, columns=df.columns)
    result   = pd.concat([df, dirty_df], ignore_index=True)
    result   = result.sample(frac=1, random_state=42).reset_index(drop=True)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 60)
    print("  Retail Sales Analytics — Sample Data Generator")
    print("=" * 60)

    # Customers
    print("\n[1/3] Generating customers...")
    customers_df = generate_customers(500)
    cust_path = os.path.join(DATA_DIR, "customers.csv")
    customers_df.to_csv(cust_path, index=False)
    print(f"      Saved {len(customers_df)} rows → {cust_path}")

    # Products
    print("[2/3] Generating products...")
    products_df = generate_products()
    prod_path = os.path.join(DATA_DIR, "products.csv")
    products_df.to_csv(prod_path, index=False)
    print(f"      Saved {len(products_df)} rows → {prod_path}")

    # Orders — use clean IDs for FK references
    print("[3/3] Generating orders...")
    # Use only the first 500 valid customer IDs (C0001–C0500)
    customer_ids  = [f"C{i:04d}" for i in range(1, 501)]
    product_ids   = [f"P{i:03d}" for i in range(1, len(PRODUCTS_DATA) + 1)]
    product_prices = {
        f"P{i:03d}": float(PRODUCTS_DATA[i - 1][3])
        for i in range(1, len(PRODUCTS_DATA) + 1)
    }

    orders_df = generate_orders(5000, customer_ids, product_ids, product_prices)
    ord_path = os.path.join(DATA_DIR, "orders.csv")
    orders_df.to_csv(ord_path, index=False)
    print(f"      Saved {len(orders_df)} rows -> {ord_path}")

    print("\n" + "=" * 60)
    print("  Data generation complete!")
    print(f"  Customers : {len(customers_df):,} rows")
    print(f"  Products  : {len(products_df):,} rows")
    print(f"  Orders    : {len(orders_df):,} rows")
    print("=" * 60)


if __name__ == "__main__":
    main()
