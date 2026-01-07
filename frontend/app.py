import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:5000"

st.set_page_config(page_title="Smart Support Desk", layout="wide")

st.title("🎧 Smart Support Desk")
st.header("📊 Dashboard Summary")

try:
    res = requests.get(f"{BASE_URL}/dashboard/summary")
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

st.header("🎫 Tickets")

status_filter = st.selectbox(
    "Status",
    ["All", "OPEN", "IN_PROGRESS", "CLOSED"]
)

priority_filter = st.selectbox(
    "Priority",
    ["All", "LOW", "MEDIUM", "HIGH"]
)

params = {}

if status_filter != "All":
    params["status"] = status_filter

if priority_filter != "All":
    params["priority"] = priority_filter

try:
    res = requests.get(f"{BASE_URL}/tickets", params=params)
    res.raise_for_status()
    tickets = res.json()

    st.subheader(f"Showing {len(tickets)} tickets")
    st.dataframe(tickets, use_container_width=True)

except Exception as e:
    st.error(f"Failed to load tickets: {e}")


st.subheader("Update Ticket Status")

ticket_id_input = st.number_input("Ticket ID", min_value=1, step=1)
new_status = st.selectbox("New Status", ["OPEN", "IN_PROGRESS", "CLOSED"])

if st.button("Update Status"):
    res = requests.put(
        f"{BASE_URL}/tickets/{ticket_id_input}/status",
        json={"status": new_status}
    )
    if res.status_code == 200:
        st.success("Status updated")
        st.rerun()
    else:
        st.error(res.text)







st.header("➕ Create Ticket")

with st.form("create_ticket"):
    customer_id = st.number_input("Customer ID", min_value=1, step=1)
    title = st.text_input("Title")
    description = st.text_area("Description")
    priority = st.selectbox("Priority", ["LOW", "MEDIUM", "HIGH"])

    submitted = st.form_submit_button("Create Ticket")

    if submitted:
        payload = {
            "customer_id": customer_id,
            "title": title,
            "description": description,
            "priority": priority
        }

        res = requests.post(f"{BASE_URL}/tickets", json=payload)

        if res.status_code == 201:
            st.success("Ticket created successfully")
            st.rerun()   # 🔥 refresh dashboard + tickets
        else:
            st.error(res.text)


