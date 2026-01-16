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
    ["Dashboard", "Tickets", "Create Ticket", "Customers", "Create Customer", "Assign Ticket","Update Ticket"],
    index=["Dashboard", "Tickets", "Create Ticket", "Customers", "Create Customer", "Assign Ticket","Update Ticket"].index(st.session_state.menu)
)

# update state immediately
if menu != st.session_state.menu:
    st.session_state.menu = menu
    st.rerun() 

# -------------------------------
# DASHBOARD
# -------------------------------
if menu == "Dashboard":
    st.header("Dashboard Summary")
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

    # if redirected from customer table
    customer_filter = st.session_state.get("filter_customer_idz", None)

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
        st.dataframe(tickets, use_container_width=True)
    except Exception as e:
        st.error(f"Failed to load tickets: {e}")

    # Clear filter button
    if customer_filter and st.button("Show All Tickets"):
        st.session_state.filter_customer_id = None
        st.rerun()



    flag4 = st.button("Update Ticket Status")
    if flag4:
        st.session_state.menu = "Update Ticket"
        st.rerun()
        
    
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

# -------------------------------
# ASSIGN TICKET TO ANY USER
# -------------------------------
elif menu == "Assign Ticket":
    st.subheader("Assign Ticket")

    ticket_id_sel = st.number_input("Ticket ID to Assign", min_value=1)

    agents_res = requests.get(f"{BASE_URL}/users", headers=headers)
    agents = agents_res.json() if agents_res.status_code == 200 else []

    if agents:
        agent_dict = {a["name"]: a["id"] for a in agents}
        agent_name = st.selectbox("Assign To", list(agent_dict.keys()))
        assigned_to_id = agent_dict[agent_name]

        if st.button("Assign Ticket"):
            res = requests.put(
                f"{BASE_URL}/tickets/{ticket_id_sel}/assign",
                json={"assigned_to": assigned_to_id},
                headers=headers
            )
            if res.status_code == 200:
                st.success("Ticket assigned")
                st.rerun()
            else:
                st.error(res.text)
    else:
        st.info("No users available")

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

            new_status = st.selectbox("New Status", ["OPEN", "IN_PROGRESS", "CLOSED"], )
            
            agents_res = requests.get(f"{BASE_URL}/users", params = params,headers=headers)

            agents = agents_res.json() if agents_res.status_code == 200 else []

            options = [None] + [f"{a['id']}-{a['name']} - {a['email']}" for a in agents]

            default_index = (
                next((i+1 for i, a in enumerate(agents) if a['id'] == st.session_state.user['id']), 0)
                if st.session_state.user['role'] == 'agent'
                else 0
            )

            agent_name = st.selectbox("Assign To", options, index=default_index)

            
            if st.button("Update Status"):
                
                if agent_name != None:
                    assigned_to_id = int(agent_name.split("-")[0])
                else:
                    assigned_to_id = None
                    
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