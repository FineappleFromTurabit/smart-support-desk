# 🎧 Smart Support Desk
### A Full-Stack Ticket Management System (Zendesk-Inspired)

Smart Support Desk is a **production-style customer support system** built to demonstrate real-world backend logic, role-based access control, audit trails, and a modern interactive UI.

Designed for **learning, scaling, and real usage** — not just demos.

---

## 🌟 Why This Project Stands Out

✔ End-to-end system (**Frontend + Backend**)  
✔ Role-based access (**Admin / Agent**)  
✔ Full ticket lifecycle tracking  
✔ Immutable ticket history (**Audit Trail**)  
✔ Clean architecture & defensive coding  
✔ Built with real production problems in mind  

---

## 🚀 Core Features

### 🔐 Authentication & Roles
- Secure login system
- Roles:
  - **ADMIN**
  - **AGENT**
- Role-based UI & permissions
- Admins can create/delete other users

---

### 🎫 Ticket Management
- Create, update, assign, and delete tickets
- Ticket states:
  - `OPEN`
  - `IN_PROGRESS`
  - `CLOSED`

**Business rules enforced:**
- Closed tickets cannot be reopened
- Invalid transitions blocked
- Simple, predictable logic (no over-engineering)

---

### 📜 Ticket Journey (Audit Trail)

Every ticket maintains a **complete history** of actions:

- Ticket creation
- Status changes
- Agent assignments
- Who performed the action (**Admin / Agent**)
- Exact timestamp

✅ Provides **full transparency and accountability**, just like real support systems.

---

### 👥 Customer Management
- Create customers
- View customers
- Delete customers
- Cascade delete enabled

> Deleting a customer automatically deletes related tickets & history

---

## 📊 Dashboard (Role-Aware)

### 👑 Admin Dashboard
- Total tickets in system
- Ticket distribution by status
- Ticket distribution by priority

### 👤 Agent Dashboard
- Tickets assigned to me
- My open tickets
- My priority & status breakdown

---

## 🖥️ Frontend (Streamlit)
- Sidebar-driven navigation
- Role-aware menus
- Ticket filters
- Ticket detail page with timeline view
- Safe session handling (no crashes on refresh)

---

## 🏗️ Tech Stack

### Backend
- Python
- Flask
- MySQL
- Pydantic (request validation)
- Transaction-safe DB operations
- Modular Blueprint architecture

### Frontend
- Streamlit
- Requests
- Pandas & Matplotlib (analytics & charts)

---

## 🗄️ Database Design

### Core Tables
- `users`
- `customers`
- `tickets`
- `ticket_history`

### Ticket History Example
```text
CREATED → OPEN
ASSIGNED → Agent A
STATUS_CHANGED → IN_PROGRESS
STATUS_CHANGED → CLOSED




📂 PROJECT STRUCTURE

smart-support-desk/
│
├── backend/
│   ├── app.py
│   ├── db.py
│   ├── routes/
│   │   ├── tickets.py
│   │   ├── customers.py
│   │   └── users.py
│   └── schemas/
│
├── frontend/
│   └── app.py   # Streamlit UI
│
├── requirements.txt
└── README.md
--
▶️ How to Run

1️⃣ Backend
cd backend
python app.py

Runs on:
http://127.0.0.1:5000


2️⃣ Frontend

cd frontend
streamlit run app.py

Runs on:
http://localhost:8501


🔌 API Highlights

-POST /login

-POST /register

-GET /tickets

-POST /tickets

-PUT /tickets/<id>/update

-GET /tickets/<id>/detail

-DELETE /tickets/<id>

-GET /customers

-DELETE /customers/<id>

-GET /dashboard/summary

🧠 What This Project Demonstrates:
Real-world ticket lifecycle handling
Role-based authorization
Backend-driven audit trails
Defensive API design
Streamlit session safety
Debugging complex frontend-backend flows
This is not a toy CRUD app — it’s an engineering-focused system.

👨‍💻 Author
Smit Panchal
Built to learn how real support systems work — and how they break.