"""MOCK DATA for the FreshCart ELT (Part B).

ASSUMPTION / PROVENANCE: there are no real FreshCart APIs. This is the sample data from the course's
reference notebook (`freshcart_elt_simple_(1).ipynb`, section 3), copied unchanged. It stands in for
what the website API, mobile API, CRM, FX API and India Post pincode API would have sent.
The mess in it (spaces, symbols, wrong dates, duplicates, bad rows) is deliberate: the SQL cleans it.
B4 later adds one extra event to MOCK_CRM_TIER_EVENTS.
"""

# ---- Website orders: flat JSON ----
MOCK_WEB_ORDERS = [
    # ORD-1001: email has spaces and capitals, amount has a comma
    {"order_id": "ORD-1001", "cust_email": " Priya.R@Gmail.com ", "cust_name": "priya r",
     "order_date": "2026-09-01", "amount": "1,250.00", "currency": "INR", "pincode": "600041",
     "updated_at": "2026-09-01 10:02:00"},
    # ORD-1003: amount is missing (the mobile copy below has it)
    {"order_id": "ORD-1003", "cust_email": "meera@outlook.com", "cust_name": "MEERA S",
     "order_date": "2026-09-02", "amount": None, "currency": "INR", "pincode": "400050",
     "updated_at": "2026-09-02 09:10:00"},
    # ORD-1002: a dollar order (also sent by the mobile app = duplicate)
    {"order_id": "ORD-1002", "cust_email": "Arjun.K@Yahoo.in ", "cust_name": "Arjun K",
     "order_date": "2026-09-01", "amount": "42.50", "currency": "USD", "pincode": "560034",
     "updated_at": "2026-09-01 11:15:00"},
    # ORD-1004: negative amount -> will be rejected
    {"order_id": "ORD-1004", "cust_email": "rahul.m@gmail.com", "cust_name": "Rahul M",
     "order_date": "Sep 3, 2026", "amount": "-500", "currency": "INR", "pincode": "110001",
     "updated_at": "2026-09-03 12:00:00"},
    # ORD-1005: rupee sign in the amount, lowercase currency, dot after the name
    {"order_id": "ORD-1005", "cust_email": "priya.r@gmail.com", "cust_name": "Priya R.",
     "order_date": "2026-09-03", "amount": "₹ 899", "currency": "inr", "pincode": "600041",
     "updated_at": "2026-09-03 16:45:00"},
    # ORD-1006: bad email and 5-digit pincode -> will be rejected
    {"order_id": "ORD-1006", "cust_email": "vikram@@mail", "cust_name": "Vikram",
     "order_date": "2026-09-04", "amount": 30, "currency": "EUR", "pincode": "99999",
     "updated_at": "2026-09-04 08:30:00"},
]

# ---- Mobile app orders: nested JSON, different field names, day-first dates ----
MOCK_MOBILE_ORDERS = [
    # ORD-1002 again (same as the web copy)
    {"orderId": "ORD-1002", "customer": {"email": "arjun.k@yahoo.in", "name": "Arjun K"},
     "orderDate": "01/09/2026", "total": {"value": "42.50", "currency": "usd"},
     "deliveryPin": "560034", "updatedAt": "2026-09-01T11:15:00"},
    # ORD-1003 again, newer and with the amount filled in
    {"orderId": "ORD-1003", "customer": {"email": "Meera@Outlook.com", "name": "Meera S"},
     "orderDate": "02/09/2026", "total": {"value": "2,100.00", "currency": "INR"},
     "deliveryPin": "400050", "updatedAt": "2026-09-02T18:40:00"},
]

# ---- Customer tier changes (Priya moves from Silver to Gold on 3 Sept) ----
MOCK_CRM_TIER_EVENTS = [
    {"cust_id": "CUST-01", "email": "priya.r@gmail.com", "tier": "Silver", "effective_from": "2023-04-10"},
    {"cust_id": "CUST-01", "email": "priya.r@gmail.com", "tier": "Gold", "effective_from": "2026-09-03"},
    {"cust_id": "CUST-02", "email": "arjun.k@yahoo.in", "tier": "Silver", "effective_from": "2024-01-15"},
    {"cust_id": "CUST-03", "email": "meera@outlook.com", "tier": "Platinum", "effective_from": "2022-11-01"},
]

# ---- Exchange rates: rupees per 1 US dollar, per day ----
MOCK_FX_RESPONSES = [
    {"amount": 1.0, "base": "USD", "start_date": "2026-09-01", "end_date": "2026-09-03",
     "rates": {"2026-09-01": {"INR": 83.20}, "2026-09-02": {"INR": 83.35}, "2026-09-03": {"INR": 83.10}}},
]

# ---- Pincodes: pincode -> (city, state) ----
MOCK_PINCODES = {"600041": ("Chennai", "Tamil Nadu"), "560034": ("Bengaluru", "Karnataka"),
                 "400050": ("Mumbai", "Maharashtra")}


def mock_pincode_response(pin):
    """Reply in the same shape the India Post API uses."""
    if pin not in MOCK_PINCODES:
        return [{"Message": "No records found", "Status": "Error", "PostOffice": None}]
    district, state = MOCK_PINCODES[pin]
    return [{"Message": "Number of pincode(s) found:1", "Status": "Success",
             "PostOffice": [{"Name": district, "District": district, "State": state,
                             "Country": "India", "Pincode": pin}]}]
