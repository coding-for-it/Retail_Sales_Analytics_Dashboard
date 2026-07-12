"""
test_validate.py
----------------
Unit tests for the validation layer (src/validate.py).

Tests cover all 3 entity validators:
  - validate_customers() — 8 rules
  - validate_products()  — 6 rules
  - validate_orders()    — 10+ rules

Each test focuses on a single validation rule in isolation.
"""

import pandas as pd
import pytest

from src.validate import validate_customers, validate_products, validate_orders


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def make_customer(**kwargs) -> pd.DataFrame:
    """Return a one-row customer DataFrame with sensible defaults."""
    defaults = {
        "Customer_ID"  : "C0001",
        "Customer_Name": "Rahul Sharma",
        "Email"        : "rahul.sharma1@gmail.com",
        "Phone"        : "9876543210",
        "City"         : "Mumbai",
        "State"        : "Maharashtra",
        "Region"       : "West",
        "Join_Date"    : "2023-01-15",
    }
    defaults.update(kwargs)
    return pd.DataFrame([defaults])


def make_product(**kwargs) -> pd.DataFrame:
    """Return a one-row product DataFrame with sensible defaults."""
    defaults = {
        "Product_ID"  : "P001",
        "Product_Name": "Samsung Galaxy S24",
        "Category"    : "Electronics",
        "Brand"       : "Samsung",
        "Price"       : "89999",
    }
    defaults.update(kwargs)
    return pd.DataFrame([defaults])


def make_order(**kwargs) -> pd.DataFrame:
    """Return a one-row order DataFrame with sensible defaults."""
    defaults = {
        "Order_ID"      : "ORD00001",
        "Customer_ID"   : "C0001",
        "Product_ID"    : "P001",
        "Order_Date"    : "2024-06-15",
        "Quantity"      : "2",
        "Unit_Price"    : "89999",
        "Discount"      : "10",
        "Total_Amount"  : "161998.20",
        "Order_Status"  : "Completed",
        "Payment_Method": "UPI",
    }
    defaults.update(kwargs)
    return pd.DataFrame([defaults])


VALID_CIDS = {"C0001"}
VALID_PIDS = {"P001"}


# ─────────────────────────────────────────────────────────────────────────────
# CUSTOMER VALIDATION TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestValidateCustomers:

    def test_valid_customer_passes(self):
        """A well-formed customer row should pass all validation rules."""
        clean, rejected = validate_customers(make_customer())
        assert len(clean) == 1
        assert len(rejected) == 0

    def test_missing_customer_id_rejected(self):
        """Customer with null Customer_ID should be rejected."""
        df = make_customer(Customer_ID=None)
        clean, rejected = validate_customers(df)
        assert len(clean) == 0
        assert len(rejected) == 1
        assert "Missing Customer_ID" in rejected.iloc[0]["REJECT_REASON"]

    def test_duplicate_customer_id_rejected(self):
        """Duplicate Customer_ID (same ID twice) — second row rejected."""
        df = pd.concat([make_customer(), make_customer()], ignore_index=True)
        clean, rejected = validate_customers(df)
        assert len(clean) == 1
        assert len(rejected) == 1
        assert "Duplicate Customer_ID" in rejected.iloc[0]["REJECT_REASON"]

    def test_missing_customer_name_rejected(self):
        """Customer with null name should be rejected."""
        df = make_customer(Customer_Name=None)
        clean, rejected = validate_customers(df)
        assert len(clean) == 0
        assert "Missing Customer_Name" in rejected.iloc[0]["REJECT_REASON"]

    def test_invalid_email_rejected(self):
        """Malformed email addresses should be rejected."""
        for bad_email in ["notanemail", "missing@", "no_at_sign", "double@@gmail.com"]:
            df = make_customer(Email=bad_email)
            clean, rejected = validate_customers(df)
            assert len(clean) == 0, f"Expected rejection for email: {bad_email}"
            assert "Invalid Email" in rejected.iloc[0]["REJECT_REASON"]

    def test_valid_email_passes(self):
        """Standard email formats should pass."""
        for good_email in ["user@gmail.com", "name.last@company.co.in", "test123@yahoo.com"]:
            df = make_customer(Email=good_email)
            clean, rejected = validate_customers(df)
            assert len(clean) == 1, f"Expected clean for email: {good_email}"

    def test_invalid_phone_rejected(self):
        """Non-10-digit phones should be rejected."""
        for bad_phone in ["123", "abcdefghij", "123456789012"]:
            df = make_customer(Phone=bad_phone)
            clean, rejected = validate_customers(df)
            assert len(clean) == 0, f"Expected rejection for phone: {bad_phone}"
            assert "Invalid Phone" in rejected.iloc[0]["REJECT_REASON"]

    def test_valid_phone_passes(self):
        """Exactly 10-digit phones should pass."""
        df = make_customer(Phone="9876543210")
        clean, rejected = validate_customers(df)
        assert len(clean) == 1

    def test_invalid_region_rejected(self):
        """Region not in {North, South, East, West} should be rejected."""
        for bad_region in ["Central", "Unknown", "Northwest"]:
            df = make_customer(Region=bad_region)
            clean, rejected = validate_customers(df)
            assert len(clean) == 0
            assert "Invalid Region" in rejected.iloc[0]["REJECT_REASON"]

    def test_missing_city_rejected(self):
        """Customer without a city should be rejected."""
        df = make_customer(City=None)
        clean, rejected = validate_customers(df)
        assert len(clean) == 0
        assert "Missing City" in rejected.iloc[0]["REJECT_REASON"]

    def test_multiple_failures_captured(self):
        """A row with multiple issues should have all reasons in REJECT_REASON."""
        df = make_customer(Email="bad_email", Phone="123")
        clean, rejected = validate_customers(df)
        assert len(clean) == 0
        reason = rejected.iloc[0]["REJECT_REASON"]
        assert "Invalid Email" in reason
        assert "Invalid Phone" in reason


# ─────────────────────────────────────────────────────────────────────────────
# PRODUCT VALIDATION TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestValidateProducts:

    def test_valid_product_passes(self):
        """A well-formed product row should pass all validation rules."""
        clean, rejected = validate_products(make_product())
        assert len(clean) == 1
        assert len(rejected) == 0

    def test_missing_product_id_rejected(self):
        """Product with null Product_ID should be rejected."""
        df = make_product(Product_ID=None)
        clean, rejected = validate_products(df)
        assert len(clean) == 0
        assert "Missing Product_ID" in rejected.iloc[0]["REJECT_REASON"]

    def test_duplicate_product_id_rejected(self):
        """Duplicate Product_ID — second row should be rejected."""
        df = pd.concat([make_product(), make_product()], ignore_index=True)
        clean, rejected = validate_products(df)
        assert len(clean) == 1
        assert len(rejected) == 1

    def test_missing_product_name_rejected(self):
        """Product without a name should be rejected."""
        df = make_product(Product_Name=None)
        clean, rejected = validate_products(df)
        assert len(clean) == 0
        assert "Missing Product_Name" in rejected.iloc[0]["REJECT_REASON"]

    def test_invalid_category_rejected(self):
        """Category not in the approved list should be rejected."""
        for bad_cat in ["Misc", "Unknown", "Other"]:
            df = make_product(Category=bad_cat)
            clean, rejected = validate_products(df)
            assert len(clean) == 0, f"Expected rejection for category: {bad_cat}"

    def test_valid_categories_pass(self):
        """All approved categories should pass validation."""
        valid_cats = [
            "Electronics", "Fashion", "Home & Kitchen",
            "Beauty", "Sports", "Books", "Furniture", "Groceries"
        ]
        for cat in valid_cats:
            df = make_product(Category=cat)
            clean, rejected = validate_products(df)
            assert len(clean) == 1, f"Expected clean for category: {cat}"

    def test_negative_price_rejected(self):
        """Negative price should be rejected."""
        df = make_product(Price="-100")
        clean, rejected = validate_products(df)
        assert len(clean) == 0
        assert "Negative or zero Price" in rejected.iloc[0]["REJECT_REASON"]

    def test_zero_price_rejected(self):
        """Zero price should be rejected."""
        df = make_product(Price="0")
        clean, rejected = validate_products(df)
        assert len(clean) == 0

    def test_positive_price_passes(self):
        """Any positive price should pass."""
        for price in ["1", "99.99", "150000"]:
            df = make_product(Price=price)
            clean, rejected = validate_products(df)
            assert len(clean) == 1, f"Expected clean for price: {price}"


# ─────────────────────────────────────────────────────────────────────────────
# ORDERS VALIDATION TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestValidateOrders:

    def test_valid_order_passes(self):
        """A well-formed order should pass all validation rules."""
        clean, rejected = validate_orders(make_order(), VALID_CIDS, VALID_PIDS)
        assert len(clean) == 1
        assert len(rejected) == 0

    def test_missing_order_id_rejected(self):
        """Order with null Order_ID should be rejected."""
        df = make_order(Order_ID=None)
        clean, rejected = validate_orders(df, VALID_CIDS, VALID_PIDS)
        assert len(clean) == 0
        assert "Missing Order_ID" in rejected.iloc[0]["REJECT_REASON"]

    def test_duplicate_order_id_rejected(self):
        """Duplicate Order_ID — second row should be rejected."""
        df = pd.concat([make_order(), make_order()], ignore_index=True)
        clean, rejected = validate_orders(df, VALID_CIDS, VALID_PIDS)
        assert len(clean) == 1
        assert len(rejected) == 1

    def test_invalid_customer_id_fk_rejected(self):
        """Customer_ID not in valid set should trigger FK violation."""
        df = make_order(Customer_ID="C9999")
        clean, rejected = validate_orders(df, VALID_CIDS, VALID_PIDS)
        assert len(clean) == 0
        assert "FK violation" in rejected.iloc[0]["REJECT_REASON"]

    def test_invalid_product_id_fk_rejected(self):
        """Product_ID not in valid set should trigger FK violation."""
        df = make_order(Product_ID="P999")
        clean, rejected = validate_orders(df, VALID_CIDS, VALID_PIDS)
        assert len(clean) == 0
        assert "FK violation" in rejected.iloc[0]["REJECT_REASON"]

    def test_negative_quantity_rejected(self):
        """Negative quantity should be rejected."""
        df = make_order(Quantity="-5")
        clean, rejected = validate_orders(df, VALID_CIDS, VALID_PIDS)
        assert len(clean) == 0
        assert "Negative or zero Quantity" in rejected.iloc[0]["REJECT_REASON"]

    def test_zero_quantity_rejected(self):
        """Zero quantity should be rejected."""
        df = make_order(Quantity="0")
        clean, rejected = validate_orders(df, VALID_CIDS, VALID_PIDS)
        assert len(clean) == 0

    def test_negative_unit_price_rejected(self):
        """Negative unit price should be rejected."""
        df = make_order(Unit_Price="-100")
        clean, rejected = validate_orders(df, VALID_CIDS, VALID_PIDS)
        assert len(clean) == 0
        assert "Negative Unit_Price" in rejected.iloc[0]["REJECT_REASON"]

    def test_future_order_date_rejected(self):
        """Order with a future date should be rejected."""
        df = make_order(Order_Date="2099-01-01")
        clean, rejected = validate_orders(df, VALID_CIDS, VALID_PIDS)
        assert len(clean) == 0
        assert "Future or invalid Order_Date" in rejected.iloc[0]["REJECT_REASON"]

    def test_invalid_date_format_rejected(self):
        """Unparseable date strings should be rejected."""
        df = make_order(Order_Date="not-a-date")
        clean, rejected = validate_orders(df, VALID_CIDS, VALID_PIDS)
        assert len(clean) == 0

    def test_invalid_order_status_rejected(self):
        """Order status not in allowed values should be rejected."""
        for bad_status in ["Dispatched", "Processing", "Unknown"]:
            df = make_order(Order_Status=bad_status)
            clean, rejected = validate_orders(df, VALID_CIDS, VALID_PIDS)
            assert len(clean) == 0, f"Expected rejection for status: {bad_status}"

    def test_valid_order_statuses_pass(self):
        """All 4 valid statuses should pass."""
        for status in ["Completed", "Pending", "Cancelled", "Returned"]:
            df = make_order(Order_Status=status)
            clean, rejected = validate_orders(df, VALID_CIDS, VALID_PIDS)
            assert len(clean) == 1, f"Expected clean for status: {status}"

    def test_invalid_payment_method_rejected(self):
        """Payment method not in allowed values should be rejected."""
        for bad_pay in ["Crypto", "Cheque", "EMI"]:
            df = make_order(Payment_Method=bad_pay)
            clean, rejected = validate_orders(df, VALID_CIDS, VALID_PIDS)
            assert len(clean) == 0, f"Expected rejection for payment: {bad_pay}"

    def test_discount_out_of_range_rejected(self):
        """Discount below 0 or above 90 should be rejected."""
        for bad_disc in ["-5", "95", "100"]:
            df = make_order(Discount=bad_disc)
            clean, rejected = validate_orders(df, VALID_CIDS, VALID_PIDS)
            assert len(clean) == 0, f"Expected rejection for discount: {bad_disc}"

    def test_zero_discount_passes(self):
        """Zero discount is valid."""
        df = make_order(Discount="0")
        clean, rejected = validate_orders(df, VALID_CIDS, VALID_PIDS)
        assert len(clean) == 1
