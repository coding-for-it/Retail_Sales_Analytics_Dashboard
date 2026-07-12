"""
test_transform.py
-----------------
Unit tests for the transformation layer (src/transform.py).

Tests cover:
  - transform_customers() → name/state standardization, date parsing
  - transform_products()  → price casting, ID formatting
  - transform_orders()    → date parsing, type casting, Total_Amount calculation
"""

import pandas as pd
import pytest

from src.transform import transform_customers, transform_products, transform_orders


# ─────────────────────────────────────────────────────────────────────────────
# CUSTOMER TRANSFORM TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestTransformCustomers:

    def _base_df(self, **kwargs) -> pd.DataFrame:
        data = {
            "Customer_ID"  : "c0001",
            "Customer_Name": "  rahul sharma  ",
            "Email"        : "rahul@gmail.com",
            "Phone"        : "9876543210",
            "City"         : "  mumbai  ",
            "State"        : "MH",
            "Region"       : "West",
            "Join_Date"    : "2023-01-15",
        }
        data.update(kwargs)
        return pd.DataFrame([data])

    def test_customer_id_uppercased(self):
        """Customer_ID should be converted to uppercase."""
        result = transform_customers(self._base_df(Customer_ID="c0001"))
        assert result["Customer_ID"].iloc[0] == "C0001"

    def test_customer_name_title_cased(self):
        """Customer_Name should be title-cased and stripped."""
        result = transform_customers(self._base_df(Customer_Name="  rahul kumar sharma  "))
        assert result["Customer_Name"].iloc[0] == "Rahul Kumar Sharma"

    def test_state_abbreviation_expanded(self):
        """State abbreviation 'MH' should expand to 'Maharashtra'."""
        result = transform_customers(self._base_df(State="MH"))
        assert result["State"].iloc[0] == "Maharashtra"

    def test_state_unknown_abbreviation_title_cased(self):
        """Unknown state code should be title-cased as-is."""
        result = transform_customers(self._base_df(State="XX"))
        assert result["State"].iloc[0] == "Xx"  # title case

    def test_city_stripped_and_title_cased(self):
        """City with extra spaces should be stripped and title-cased."""
        result = transform_customers(self._base_df(City="  new delhi  "))
        assert result["City"].iloc[0] == "New Delhi"

    def test_join_date_parsed_to_date(self):
        """Join_Date string should be parsed to a Python date object."""
        from datetime import date
        result = transform_customers(self._base_df(Join_Date="2023-06-15"))
        assert result["Join_Date"].iloc[0] == date(2023, 6, 15)

    def test_invalid_join_date_becomes_none(self):
        """Unparseable Join_Date should produce NaT/None without error."""
        result = transform_customers(self._base_df(Join_Date="not-a-date"))
        assert pd.isna(result["Join_Date"].iloc[0])

    def test_all_state_abbreviations_expand(self):
        """All known state abbreviations should map to full names."""
        from src.config import STATE_MAP
        for abbr, full_name in STATE_MAP.items():
            result = transform_customers(self._base_df(State=abbr))
            assert result["State"].iloc[0] == full_name, \
                f"Expected '{full_name}' for abbreviation '{abbr}'"


# ─────────────────────────────────────────────────────────────────────────────
# PRODUCT TRANSFORM TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestTransformProducts:

    def _base_df(self, **kwargs) -> pd.DataFrame:
        data = {
            "Product_ID"  : "p001",
            "Product_Name": "  samsung galaxy s24  ",
            "Category"    : "Electronics",
            "Brand"       : "  samsung  ",
            "Price"       : "89999.999",
        }
        data.update(kwargs)
        return pd.DataFrame([data])

    def test_product_id_uppercased(self):
        """Product_ID should be converted to uppercase."""
        result = transform_products(self._base_df(Product_ID="p001"))
        assert result["Product_ID"].iloc[0] == "P001"

    def test_product_name_title_cased(self):
        """Product_Name should be title-cased and stripped."""
        result = transform_products(self._base_df())
        assert result["Product_Name"].iloc[0] == "Samsung Galaxy S24"

    def test_brand_title_cased_and_stripped(self):
        """Brand should be title-cased and whitespace stripped."""
        result = transform_products(self._base_df(Brand="  apple  "))
        assert result["Brand"].iloc[0] == "Apple"

    def test_price_cast_to_float(self):
        """Price should be a float after transformation."""
        result = transform_products(self._base_df(Price="1299.50"))
        assert isinstance(result["Price"].iloc[0], float)

    def test_price_rounded_to_2dp(self):
        """Price should be rounded to 2 decimal places."""
        result = transform_products(self._base_df(Price="89999.999"))
        assert result["Price"].iloc[0] == 90000.00


# ─────────────────────────────────────────────────────────────────────────────
# ORDERS TRANSFORM TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestTransformOrders:

    def _base_df(self, **kwargs) -> pd.DataFrame:
        data = {
            "Order_ID"      : "ord00001",
            "Customer_ID"   : "c0001",
            "Product_ID"    : "p001",
            "Order_Date"    : "2024-06-15",
            "Quantity"      : "2",
            "Unit_Price"    : "1000",
            "Discount"      : "10",
            "Total_Amount"  : "1800",
            "Order_Status"  : "Completed",
            "Payment_Method": "UPI",
        }
        data.update(kwargs)
        return pd.DataFrame([data])

    def test_order_id_uppercased(self):
        """Order_ID should be converted to uppercase."""
        result = transform_orders(self._base_df())
        assert result["Order_ID"].iloc[0] == "ORD00001"

    def test_customer_id_uppercased(self):
        """Customer_ID should be converted to uppercase."""
        result = transform_orders(self._base_df())
        assert result["Customer_ID"].iloc[0] == "C0001"

    def test_order_date_parsed(self):
        """Order_Date should be parsed to a Python date object."""
        from datetime import date
        result = transform_orders(self._base_df(Order_Date="2024-06-15"))
        assert result["Order_Date"].iloc[0] == date(2024, 6, 15)

    def test_quantity_cast_to_int(self):
        """Quantity should be cast to integer."""
        import numpy as np
        result = transform_orders(self._base_df(Quantity="3"))
        assert result["Quantity"].iloc[0] == 3
        assert isinstance(result["Quantity"].iloc[0], (int, np.integer))


    def test_unit_price_rounded(self):
        """Unit_Price should be cast to float and rounded to 2 dp."""
        result = transform_orders(self._base_df(Unit_Price="1299.999"))
        assert result["Unit_Price"].iloc[0] == 1300.00

    def test_null_discount_defaults_to_zero(self):
        """Null Discount should default to 0.0."""
        result = transform_orders(self._base_df(Discount=None))
        assert result["Discount"].iloc[0] == 0.0

    def test_total_amount_computed_correctly(self):
        """Total_Amount = Qty * Unit_Price * (1 - Discount/100)."""
        # 2 * 1000 * (1 - 10/100) = 2000 * 0.90 = 1800.00
        result = transform_orders(self._base_df(
            Quantity="2", Unit_Price="1000", Discount="10"
        ))
        assert result["Total_Amount"].iloc[0] == 1800.00

    def test_total_amount_with_zero_discount(self):
        """With 0% discount, Total_Amount = Qty * Unit_Price."""
        result = transform_orders(self._base_df(
            Quantity="3", Unit_Price="500", Discount="0"
        ))
        assert result["Total_Amount"].iloc[0] == 1500.00

    def test_total_amount_with_25_percent_discount(self):
        """With 25% discount, Total_Amount = Qty * Unit_Price * 0.75."""
        result = transform_orders(self._base_df(
            Quantity="4", Unit_Price="2000", Discount="25"
        ))
        assert result["Total_Amount"].iloc[0] == 6000.00  # 4 * 2000 * 0.75

    def test_total_amount_column_exists(self):
        """Total_Amount column must exist in the output."""
        result = transform_orders(self._base_df())
        assert "Total_Amount" in result.columns