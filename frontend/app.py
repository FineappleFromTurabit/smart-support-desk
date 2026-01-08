import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:5000"
st.set_page_config(page_title="Smart Support Desk", layout="wide")

# Session State Setup
if "token" not in st.session_state:
    st.session_state.token = None

# Title
st.title("🎧 Smart Support Desk")

# -------------------------------
# AUTH BLOCK (Login + Register)
# -------------------------------
if not st.session_state.token:
    auth_mode = st.sidebar.radio("Auth", ["Login", "Register"])

    # LOGIN
    if auth_mode == "Login":
        st.header("🔐 Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            try:
                res = requests.post(f"{BASE_URL}/login",
                                    json={"email": email, "password": password})
                if res.status_code == 200:
                    st.session_state.token = res.json()["token"]
                    st.session_state.user = res.json()["user"]
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error(res.text)
            except Exception as e:
                st.error(f"Login failed: {e}")
        st.stop()

    # REGISTER
    else:
        st.header("🆕 Register")
        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Create Account"):
            try:
                res = requests.post(f"{BASE_URL}/register",
                                    json={"name": name, "email": email, "password": password})
                if res.status_code == 201:
                    st.success("Account created! Please login now.")
                else:
                    st.error(res.text)
            except Exception as e:
                st.error(f"Registration failed: {e}")
        st.stop()

# -------------------------------
# If logged in, show menu
# -------------------------------
# st.sidebar.success("Logged in")
st.sidebar.success(f"Logged in as {st.session_state.user['name']} ({st.session_state.user['role']})")

if st.sidebar.button("Logout"):
    st.session_state.token = None
    st.rerun()

headers = {"Authorization": f"Bearer {st.session_state.token}"}

role = st.session_state.user["role"]

if role == "admin":
    menu = st.sidebar.radio(
        "📌 Select Page",
        ["Dashboard", "Tickets", "Create Ticket", "Customers", "Create Customer"]
    )
else:  # agent
    menu = st.sidebar.radio(
        "📌 Select Page",
        ["Dashboard", "Tickets", "Create Ticket","Customers"
        ]
    )


# -------------------------------
# DASHBOARD
# -------------------------------
if menu == "Dashboard":
    st.header("📊 Dashboard Summary")
    try:
        res = requests.get(f"{BASE_URL}/dashboard/summary", headers=headers)
        res.raise_for_status()
        data = res.json()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("By Status")
            for item in data["by_status"]:
                st.metric(item["status"], item["count"])

        with col2:
            st.subheader("By Priority")
            for item in data["by_priority"]:
                st.metric(item["priority"], item["count"])

    except Exception as e:
        st.error(f"Failed to load dashboard: {e}")

# -------------------------------
# TICKETS LIST + UPDATE
# -------------------------------
elif menu == "Tickets":
    st.header("🎫 Tickets")

    status = st.selectbox("Status", ["All", "OPEN", "IN_PROGRESS", "CLOSED"])
    priority = st.selectbox("Priority", ["All", "LOW", "MEDIUM", "HIGH"])

    params = {}
    if status != "All": params["status"] = status
    if priority != "All": params["priority"] = priority

    try:
        res = requests.get(f"{BASE_URL}/tickets", params=params, headers=headers)
        tickets = res.json()
        st.dataframe(tickets, use_container_width=True)
    except Exception as e:
        st.error("Failed to load tickets")

    st.subheader("Update Ticket Status")
    ticket_id = st.number_input("Ticket ID", min_value=1)
    new_status = st.selectbox("New Status", ["OPEN", "IN_PROGRESS", "CLOSED"])

    if st.button("Update Status"):
        r = requests.put(
            f"{BASE_URL}/tickets/{ticket_id}/status",
            json={"status": new_status},
            headers=headers
        )
        if r.status_code == 200:
            st.success("Status updated")
            st.rerun()
        else:
            st.error(r.text)

# -------------------------------
# CREATE TICKET
# -------------------------------
elif menu == "Create Ticket":
    st.header("➕ Create Ticket")
    with st.form("ticket_form"):
        customer_id = st.number_input("Customer ID", min_value=1)
        title = st.text_input("Title")
        desc = st.text_area("Description")
        priority = st.selectbox("Priority", ["LOW", "MEDIUM", "HIGH"])

        submit = st.form_submit_button("Create Ticket")

        if submit:
            payload = {
                "customer_id": customer_id,
                "title": title,
                "description": desc,
                "priority": priority
            }
            r = requests.post(f"{BASE_URL}/tickets", json=payload, headers=headers)
            if r.status_code == 201:
                st.success("Ticket created")
                st.rerun()
            else:
                st.error(r.text)

# -------------------------------
# LIST CUSTOMERS
# -------------------------------
elif menu == "Customers":
    if role != "admin":
        st.error("Access denied: Admin only")
        st.stop()
    st.header("👥 Customers")
    try:
        res = requests.get(f"{BASE_URL}/customers", headers=headers)
        customers = res.json()
        st.dataframe(customers, use_container_width=True)
    except:
        st.error("Failed to load customers")

# -------------------------------
# CREATE CUSTOMER
# -------------------------------
elif menu == "Create Customer":
    if role != "admin":
        st.error("Access denied")
        st.stop()
    st.header("🏢 Create Customer")
    with st.form("cust_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        company = st.text_input("Company")

        submit = st.form_submit_button("Add Customer")

        if submit:
            payload = {"name": name, "email": email, "company": company}
            r = requests.post(f"{BASE_URL}/customers", json=payload, headers=headers)
            if r.status_code == 201:
                st.success("Customer created")
                st.rerun()
            else:
                st.error(r.text)
