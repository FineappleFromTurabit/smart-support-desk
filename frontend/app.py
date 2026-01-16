import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:5000"
st.set_page_config(page_title="Smart Support Desk", layout="wide")

# -------------------------------
# Session State Setup
# -------------------------------
if "token" not in st.session_state:
    st.session_state.token = None
headers = {"Authorization": f"Bearer {st.session_state.token}"}

if "user" not in st.session_state:
    st.session_state.user = None

if "menu" not in st.session_state:
    st.session_state.menu = "Dashboard"

# if "customer_data" not in st.session_state:
#     st.session_state.customer_data = {}

if "customers" not in st.session_state:
    res = requests.get(f"{BASE_URL}/customers") 
    st.session_state.customers = res.json() if res.status_code == 200 else []

if "agents" not in st.session_state:
    res = requests.get(f"{BASE_URL}/users") 
    st.session_state.agents = res.json() if res.status_code == 200 else []


if "agent_workload" not in st.session_state:
    st.session_state.agent_workload = [{}]
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
                    data = res.json()
                    st.session_state.token = data["token"]
                    st.session_state.user = data["user"]
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
# Sidebar: logged in user info + menu
# -------------------------------
st.sidebar.success(f"Logged in as {st.session_state.user['name']}")

if st.sidebar.button("Logout"):
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.filter_customer_id = None
    st.session_state.filter_customer_name = None
    st.session_state.menu = None
    # st.session_state.customer_data = {}
    
    st.session_state.menu = "Dashboard"
    st.rerun()


menu = st.sidebar.radio(
    "📌 Select Page",
    ["Dashboard", "Tickets", "Create Ticket", "Customers", "Create Customer","Update Ticket"],
    index=["Dashboard", "Tickets", "Create Ticket", "Customers", "Create Customer","Update Ticket"].index(st.session_state.menu)
)

# update state immediately
if menu != st.session_state.menu:
    st.session_state.menu = menu
    st.rerun() 

# -------------------------------
# DASHBOARD
# -------------------------------
import matplotlib.pyplot as plt
import pandas as pd

# -------------------------------
# DASHBOARD with charts
# -------------------------------
import matplotlib.pyplot as plt
import pandas as pd

# -------------------------------
# DASHBOARD with admin/agent summary
# -------------------------------
if menu == "Dashboard":
    st.header("📊 Dashboard Summary")

    try:
        # Load full summary for Admin always
        res_sum = requests.get(f"{BASE_URL}/dashboard/summary", headers=headers)
        res_sum.raise_for_status()
        data = res_sum.json()

        by_status = pd.DataFrame(data.get("by_status", []))
        by_priority = pd.DataFrame(data.get("by_priority", []))

        # LOAD user-specific tickets (if agent)
        res_my = requests.get(
            f"{BASE_URL}/tickets",
            params={"assigned_to": st.session_state.user["id"]},
            headers=headers
        )
        my_tickets = res_my.json() if res_my.status_code == 200 else []

        # Count
        my_df = pd.DataFrame(my_tickets)

        is_agent = st.session_state.user.get("role") == "agent"

        # ======================
        # TOP SUMMARY COUNTERS
        # ======================
        st.subheader("📌 Summary Highlights")

        col1, col2, col3 = st.columns(3)
        total = sum(by_status['count']) if not by_status.empty else 0
        col1.metric("Total Tickets (System)", total)

        if is_agent:
            col2.metric("My Tickets", len(my_tickets))
            col3.metric(
                "My Open Tickets",
                len([t for t in my_tickets if t["status"] == "OPEN"])
            )
        else:
            col2.metric("Open Tickets",
                        next((x["count"] for x in data["by_status"] if x["status"] == "OPEN"), 0))
            col3.metric("Closed Tickets",
                        next((x["count"] for x in data["by_status"] if x["status"] == "CLOSED"), 0))

        st.write("---")

        # ======================
        # ADMIN: SYSTEM CHARTS
        # ======================
        if not is_agent:
            st.subheader("🌍 Whole System Overview")

            colA, colB = st.columns(2)

            with colA:
                st.write("📍 Tickets by Status")
                if not by_status.empty:
                    fig, ax = plt.subplots()
                    ax.bar(by_status['status'], by_status['count'])
                    st.pyplot(fig)
                else:
                    st.info("No status data available")

            with colB:
                st.write("🎯 Priority Distribution")
                if not by_priority.empty:
                    fig2, ax2 = plt.subplots()
                    ax2.pie(
                        by_priority['count'],
                        labels=by_priority['priority'],
                        autopct='%1.1f%%'
                    )
                    ax2.axis('equal')
                    st.pyplot(fig2)
                else:
                    st.info("No priority data available")

        # ======================
        # AGENT MODE: MY OWN DATA
        # ======================
        if is_agent:
            st.subheader("👤 My Personal Ticket Stats")

            if my_df.empty:
                st.info("No tickets assigned to you yet 😎")
            else:
                colX, colY = st.columns(2)

                # My status chart
                with colX:
                    my_status_counts = my_df['status'].value_counts()
                    fig3, ax3 = plt.subplots()
                    ax3.bar(my_status_counts.index, my_status_counts.values)
                    st.write("Status Table")

                    st.write(my_status_counts)
                    st.write("📍 My Tickets by Status")
                    st.pyplot(fig3)

                # My priority chart
                with colY:
                    if 'priority' in my_df.columns:
                        my_priority_counts = my_df['priority'].value_counts()
                        fig4, ax4 = plt.subplots()
                        ax4.pie(
                            my_priority_counts.values,
                            labels=my_priority_counts.index,
                            autopct='%1.1f%%'
                        )
                        ax4.axis('equal')
                        st.write("Priority Table")
                        st.table(my_priority_counts)
                        st.write("🎯 My Priority Breakdown")
                        st.pyplot(fig4)

                if st.button("Go to Tickets"):
                    st.session_state.menu = "Tickets"
                    st.session_state.filter_customer_id = None
                    st.rerun()

        st.write("---")

        # Raw data tables (Bottom)
        st.subheader("📋 Raw Summary Data")
        admin1, admin2 = st.columns(2)
        admin1.write("Status Table")
        admin1.dataframe(by_status if not by_status.empty else pd.DataFrame())
        admin2.write("Priority Table")
        admin2.dataframe(by_priority if not by_priority.empty else pd.DataFrame())

    except Exception as e:
        st.error(f"Failed to load dashboard: {e}")


# -------------------------------
# TICKETS LIST + UPDATE
# -------------------------------
elif menu == "Tickets":
    st.header("🎫 Tickets")

    # if redirected from customer table
    customer_filter = st.session_state.get("filter_customer_id", None)

    with st.expander("🔍 Filters"):
        status = st.selectbox("Status", ["All", "OPEN", "IN_PROGRESS", "CLOSED"])
        priority = st.selectbox("Priority", ["All", "LOW", "MEDIUM", "HIGH"])
        assign_to_me = st.checkbox("Assigned to Me", value=False)

    params = {}

    # If user clicked "View Tickets" for a customer
    if customer_filter:
        params["customer_id"] = customer_filter
        st.info(f"Showing tickets for Customer ID: {st.session_state.get('filter_customer_id')} - {st.session_state.get('filter_customer_name','')}")

    # Filters
    if status != "All":
        params["status"] = status
    if priority != "All":
        params["priority"] = priority
    if assign_to_me:
        params["assigned_to"] = st.session_state.user["id"]
    
    try:
        res = requests.get(f"{BASE_URL}/tickets", params=params, headers=headers)
        tickets = res.json()
        st.session_state.tickets = tickets  # Store tickets in session state
        # Build a tiny id→name map once
        agent_map = {a["id"]:  a["email"] for a in st.session_state.agents}

        # Replace assigned_to id with the name
        for t in tickets:
            t["assigned_to"] = agent_map.get(t["assigned_to"], "Unassigned")

        st.dataframe(tickets,use_container_width=True)
    except Exception as e:
        st.error(f"Failed to load tickets: {e}")

    # Clear filter button
    if customer_filter and st.button("Show All Tickets"):
        st.session_state.filter_customer_id = None
        st.rerun()



    flag4 = st.button("Update Ticket Status")
    if flag4 :
        st.session_state.menu = "Update Ticket"
        st.rerun()
        
    with st.expander("Delete Ticket"):
        ticket_options = {f"{t['id']} - {t['title']}": t['id'] for t in tickets}
        selected_ticket_del = st.selectbox(
            "Select a Ticket to Delete",
            list(ticket_options.keys())
        )
        if selected_ticket_del == None:
            st.info("No tickets available to delete")
        else:
            ticket_id_del = ticket_options[selected_ticket_del]
        if st.button("Delete Ticket"):
            try:
                res_del = requests.delete(f"{BASE_URL}/tickets/{ticket_id_del}", headers=headers)
                if res_del.status_code == 200:
                    st.success(f"Ticket {ticket_id_del} deleted successfully")
                    st.rerun()
                else:
                    st.error(res_del.text)
            except Exception as e:
                st.error(f"Failed to delete ticket: {e}")
    if st.button("Create New Ticket"):
        st.session_state.menu = "Create Ticket"
        st.rerun()


# -------------------------------
# CREATE TICKET
# -------------------------------
elif menu == "Create Ticket":
    st.header("➕ Create Ticket")
    # st.text(f"Customer Name : ",st.session_state.user['name'])
    params = {}
    params['role'] = 'agent'
    with st.form("ticket_form"):
        # customer_id = st.number_input("Customer ID", min_value=1 , value=st.session_state.get("filter_customer_id", 1))
        # customer_id = st.selectbox("Customer", options=list(st.session_state.customer_data.keys()), format_func=lambda x: f"{x} - {st.session_state.customer_data[x]}",index = (len(st.session_state.customer_data) - int(st.session_state.get("filter_customer_id", 5))))
        # customer_id = st.selectbox("Customer", options=list(st.session_state.customer_data.keys()), format_func=lambda x: f"{x} - {st.session_state.customer_data[x]}",index = 0 if not st.session_state.get("filter_customer_id", None) else list(st.session_state.customer_data.keys()).index(st.session_state.get("filter_customer_id")))
        customer_id = st.selectbox("Customer", options=st.session_state.customers, format_func=lambda x: f"{x['id']} - {x['name']} - {x['email']}", index=0 if not st.session_state.get("filter_customer_id", None) else next((i for i, c in enumerate(st.session_state.customers) if c['id'] == st.session_state.get("filter_customer_id")), 0)).get('id')
        
        title = st.text_input("Title")
        desc = st.text_area("Description")
        priority = st.selectbox("Priority", ["LOW", "MEDIUM", "HIGH"])
        
        agents_res = requests.get(f"{BASE_URL}/users", params = params,headers=headers)
        agents = agents_res.json() if agents_res.status_code == 200 else []
        
        # agent_name = st.selectbox("Assign To", list(agent_dict.keys()),list)
        
            
         
        options = [None] + [f"{a['id']}-{a['name']} - {a['email']}" for a in agents]

        default_index = (
            next((i+1 for i, a in enumerate(agents) if a['id'] == st.session_state.user['id']), 0)
            if st.session_state.user['role'] == 'agent'
            else 0
        )

        agent_name = st.selectbox("Assign To", options, index=default_index)

        #do something like that so it will on the agent who logged in by default
        
        
        submit = st.form_submit_button("Create Ticket")

        

        customer_data = dict(st.session_state.get('customer_data', {}))
        # st.text(f"Customer Name : {customer_data.get(customer_id, 'N/A')}") 
        if submit:
            if agent_name != None:
                assigned_to_id = int(agent_name.split("-")[0])
            else:
                assigned_to_id = None
            payload = {
                "customer_id": customer_id,
                "title": title,
                "description": desc,
                "priority": priority,
                "assigned_to": assigned_to_id
            }
            
            r = requests.post(f"{BASE_URL}/tickets", json=payload, headers=headers)
            if r.status_code == 201:
                st.success("Ticket created")
                st.session_state.menu = "Tickets"
                st.rerun()
            else:
                st.error(r.text)

# -------------------------------
# LIST CUSTOMERS
# -------------------------------
elif menu == "Customers":
    st.header("👥 Customers")
    try:
        name_filter = st.text_input("Search by Name ")

        params = {}
        if name_filter:
            params["customer_name"] = name_filter
        
        res = requests.get(f"{BASE_URL}/customers", params=params, headers=headers)
        res.raise_for_status()
        customers = res.json()
       
        # st.session_state.customer_data = customers 
        # for cust in customers:
        #  st.session_state.customer_data[cust['id']] = cust['name']
        # Add dynamic link to each row
        

        # Show table with a View column
        st.dataframe(
            customers,
            use_container_width=True,
           
        )

        # Detect click by row selection
        selected = st.selectbox(
            "Select Customer to View Tickets",
            [f"{c['id']} - {c['name']} - {c['email']}"  for c in customers]
        )


        if st.button("View Tickets"):
            cust_id = int(selected.split(" - ")[0])
            
            st.session_state.filter_customer_id = cust_id
            st.session_state.filter_customer_name = selected.split(" - ")[1]
            st.session_state.menu = "Tickets"
            st.rerun()

        if st.button("Delete This Customer"):
            cust_id = int(selected.split(" - ")[0])
            try:
                res_del = requests.delete(f"{BASE_URL}/customers/{cust_id}", headers=headers)
                if res_del.status_code == 200:
                    st.success(f"Customer {cust_id} deleted successfully")
                    st.session_state.filter_customer_id = None
                    st.rerun()
                else:
                    st.error(res_del.text)
            except Exception as e:
                st.error(f"Failed to delete customer: {e}")
        
        
        if st.button("➕ Create New Customer"):
            st.session_state.menu = "Create Customer"
            st.rerun()

    except Exception as e:
        st.error(f"Failed to load customers: {e}")

# -------------------------------
# CREATE CUSTOMER
# -------------------------------
elif menu == "Create Customer":
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
                st.session_state.filter_customer_id = None #empty the customer filter
                res = requests.get(f"{BASE_URL}/customers", headers=headers)
                st.session_state.customers = res.json() if res.status_code == 200 else []
                st.success("Customer created")
                st.rerun()
            else:
                st.error(r.text)

elif menu == "Update Ticket":
    st.header("Update Ticket")
    tickets = st.session_state.get('tickets', [])
    if len(tickets) > 0:
            # Build selector from actual tickets shown
            ticket_options = {f"{t['id']} - {t['title']}": t['id'] for t in tickets}

            selected_ticket = st.selectbox(
                "Select a Ticket to Update",
                list(ticket_options.keys())
            )
            params = {}
            params['role'] = 'agent'
            ticket_id = ticket_options[selected_ticket]
            params['ticket_id'] = ticket_id
            res = requests.get(f"{BASE_URL}/tickets", params=params, headers=headers)
            ticket = res.json()
            for t in ticket:
                status_current = t['status']
                current_agent = t['assigned_to']
            new_status = st.selectbox("New Status", ["OPEN", "IN_PROGRESS", "CLOSED"], index=0 if not status_current else next((i for i, c in enumerate(["OPEN", "IN_PROGRESS", "CLOSED"]) if c == status_current), 0))

            agents_res = requests.get(f"{BASE_URL}/users", params = params,headers=headers)

            agents = agents_res.json() if agents_res.status_code == 200 else []

            options = [None] + [f"{a['id']}-{a['name']} - {a['email']}" for a in agents]

            default_index = (
                next((i+1 for i, a in enumerate(agents) if a['id'] == current_agent), 0)
                if st.session_state.user['role'] == 'agent'
                else 0
            )

            agent_name = st.selectbox("Assign To", options, index=default_index)

            
            if st.button("Update Status"):
                
                if agent_name != None:
                    assigned_to_id = int(agent_name.split("-")[0])
                else:
                    assigned_to_id = None
                if status_current.upper() == 'CLOSED':
                    st.warning("you can not update closed ticket")
                elif new_status.upper() == 'CLOSED':
                    st.warning("you can not assign agent while closing the ticket")
                else:
                    r = requests.put(
                        f"{BASE_URL}/tickets/{ticket_id}/update",
                        json={"status": new_status, "assigned_to": assigned_to_id},
                        headers=headers
                    )
                    if r.status_code == 200:
                        st.success(f"Ticket {ticket_id} updated!")
                        st.session_state.menu = "Tickets"
                        st.rerun()

                    else:
                        st.error(r.text)
    else:
        st.info("No tickets found")