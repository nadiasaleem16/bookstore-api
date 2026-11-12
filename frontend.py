
import streamlit as st
import requests


# ==================================
# PAGE CONFIGURATION
# ==================================

st.set_page_config(
    page_title="My Bookstore",
    page_icon="📚",
    layout="wide"
)

API_URL = "http://127.0.0.1:8000"


# ==================================
# SESSION STATE
# ==================================

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if "admin_password" not in st.session_state:
    st.session_state.admin_password = ""


# ==================================
# DARK THEME
# ==================================

st.markdown("""
<style>

.stApp {
    background-color: #0E1117;
    color: #F1F5F9;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

[data-testid="stSidebar"] {
    background-color: #161B22;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #1C2330;
    border: 1px solid #303B4B;
    border-radius: 15px;
}

h1, h2, h3 {
    color: #FFFFFF !important;
}

p, label, span {
    color: #E2E8F0;
}

.stTextInput input,
.stNumberInput input {
    background-color: #1C2330;
    color: white;
    border: 1px solid #475569;
}

.stButton button {
    background-color: #2563EB;
    color: white;
    border-radius: 8px;
    border: none;
    font-weight: bold;
}

.stButton button:hover {
    background-color: #1D4ED8;
    color: white;
}

hr {
    border-color: #303B4B;
}

.metric-card {
    background-color: #1C2330;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #303B4B;
    text-align: center;
}

.metric-number {
    color: #60A5FA;
    font-size: 30px;
    font-weight: bold;
}

.metric-label {
    color: #CBD5E1;
    font-size: 15px;
}

</style>
""", unsafe_allow_html=True)


# ==================================
# HELPER FUNCTIONS
# ==================================

def get_books():

    response = requests.get(
        f"{API_URL}/books",
        timeout=5
    )

    response.raise_for_status()

    return response.json()


def get_admin_headers():

    return {
        "X-Admin-Password": st.session_state.admin_password
    }


# ==================================
# HEADER
# ==================================

st.markdown(
    "<h1 style='text-align:center;'>📚 MY BOOKSTORE</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center;color:#94A3B8;'>"
    "Discover your next favorite book!"
    "</p>",
    unsafe_allow_html=True
)

st.divider()


# ==================================
# SIDEBAR
# ==================================

st.sidebar.title("📚 Bookstore")

role = st.sidebar.radio(
    "Select Your Role",
    ["Buyer", "Admin"]
)


# ==================================
# BUYER NAVIGATION
# ==================================

if role == "Buyer":

    # Clear admin session when switching to Buyer

    st.session_state.admin_logged_in = False
    st.session_state.admin_password = ""

    page = st.sidebar.radio(
        "Navigation",
        [
            "Home",
            "Request a Book",
            "My Cart",
            "My Orders"
        ]
    )


# ==================================
# ADMIN LOGIN
# ==================================

else:

    if not st.session_state.admin_logged_in:

        page = "Admin Login"

    else:

        page = st.sidebar.radio(
            "Admin Navigation",
            [
                "Admin Dashboard",
                "Book Requests",
                "Manage Books"
            ]
        )

    if page == "Admin Login":

        st.header("🔐 Admin Login")

        st.write(
            "Only authorized administrators can access this dashboard."
        )

        with st.form("admin_login_form"):

            password = st.text_input(
                "Enter Admin Password",
                type="password"
            )

            login = st.form_submit_button(
                "Login as Admin",
                use_container_width=True
            )

            if login:

                try:

                    response = requests.post(
                        f"{API_URL}/admin/login",
                        json={"password": password},
                        timeout=5
                    )

                    if response.status_code == 200:

                        st.session_state.admin_logged_in = True
                        st.session_state.admin_password = password

                        st.success("Admin login successful!")

                        st.rerun()

                    else:

                        st.error("Incorrect admin password!")

                except requests.exceptions.RequestException:

                    st.error("Cannot connect to FastAPI backend.")


# ==================================
# BUYER HOME PAGE
# ==================================

if role == "Buyer" and page == "Home":

    st.header("🏠 Welcome to Our Bookstore")

    try:

        books = get_books()

        # TOTAL BOOKS

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-number">{len(books)}</div>
                <div class="metric-label">Total Books Available</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")

        # SEARCH BOOKS

        search = st.text_input(
            "🔍 Search Books",
            placeholder="Enter book name..."
        )

        filtered_books = [
            book for book in books
            if search.lower() in book["name"].lower()
        ]

        st.subheader("📖 All Available Books")

        st.write(
            f"Showing {len(filtered_books)} of {len(books)} books"
        )

        if len(filtered_books) == 0:

            st.info("No matching books found.")

        cols = st.columns(3)

        for index, book in enumerate(filtered_books):

            with cols[index % 3]:

                with st.container(border=True):

                    st.markdown("### 📕")

                    st.subheader(book["name"])

                    st.write(f"Book ID: {book['id']}")

                    st.markdown(
                        f"### Rs. {book['price']:,}"
                    )

                    if st.button(
                        "🛒 Add to Cart",
                        key=f"cart_{book['id']}",
                        use_container_width=True
                    ):

                        result = requests.post(
                            f"{API_URL}/cart",
                            json={"book_id": book["id"]},
                            timeout=5
                        )

                        if result.status_code == 200:

                            st.success("Added to cart!")

                        else:

                            st.error("Unable to add book.")

        # RECOMMENDATIONS

        st.divider()

        st.header("✨ Recommended Books")

        st.caption(
            "Explore some books from our collection."
        )

        recommendation_response = requests.get(
            f"{API_URL}/recommendations",
            timeout=5
        )

        recommendation_response.raise_for_status()

        recommendations = recommendation_response.json()

        rec_cols = st.columns(3)

        for index, book in enumerate(recommendations):

            with rec_cols[index]:

                with st.container(border=True):

                    st.markdown("### ⭐")

                    st.subheader(book["name"])

                    st.write(
                        f"Rs. {book['price']:,}"
                    )

                    st.caption("Recommended for you")

    except requests.exceptions.RequestException:

        st.error(
            "FastAPI server is not running. Please start your backend."
        )


# ==================================
# BUYER REQUEST A BOOK
# ==================================

elif role == "Buyer" and page == "Request a Book":

    st.header("📩 Request an Unavailable Book")

    st.write(
        "Can't find your favourite book? "
        "Tell us its name and our Admin will review your request."
    )

    try:

        with st.form("book_request_form"):

            requester_name = st.text_input(
                "Your Name",
                placeholder="Enter your name"
            )

            book_name = st.text_input(
                "Book Name",
                placeholder="Enter unavailable book name"
            )

            submit_request = st.form_submit_button(
                "📩 Submit Book Request",
                use_container_width=True
            )

            if submit_request:

                if requester_name.strip() == "" or book_name.strip() == "":

                    st.warning("Please fill in both fields.")

                else:

                    response = requests.post(
                        f"{API_URL}/book-requests",
                        json={
                            "requester_name": requester_name,
                            "book_name": book_name
                        },
                        timeout=5
                    )

                    if response.status_code == 200:

                        st.success(
                            "Your book request has been submitted!"
                        )

                    else:

                        try:
                            st.error(response.json()["detail"])
                        except:
                            st.error("Unable to submit request.")

        st.divider()

        st.subheader("📋 Your Book Request Status")

        status_response = requests.get(
            f"{API_URL}/book-requests",
            timeout=5
        )

        status_response.raise_for_status()

        all_requests = status_response.json()

        if len(all_requests) == 0:

            st.info("No book requests submitted yet.")

        else:

            for request in all_requests:

                with st.container(border=True):

                    st.subheader(request["book_name"])

                    st.write(
                        f"Requested by: {request['requester_name']}"
                    )

                    if request["status"] == "Pending":

                        st.warning("Status: Pending")

                    elif request["status"] == "Approved":

                        st.success("Status: Approved")

                    else:

                        st.error("Status: Rejected")

    except requests.exceptions.RequestException:

        st.error("Unable to connect to FastAPI backend.")


# ==================================
# BUYER CART PAGE
# ==================================

elif role == "Buyer" and page == "My Cart":

    st.header("🛒 My Shopping Cart")

    try:

        response = requests.get(
            f"{API_URL}/cart",
            timeout=5
        )

        response.raise_for_status()

        cart = response.json()

        if len(cart) == 0:

            st.info("Your cart is empty!")

        else:

            total = 0

            for book in cart:

                with st.container(border=True):

                    col1, col2, col3 = st.columns([3, 2, 1])

                    with col1:

                        st.subheader(book["name"])

                    with col2:

                        st.write(
                            f"Rs. {book['price']:,}"
                        )

                    with col3:

                        if st.button(
                            "🗑️ Remove",
                            key=f"remove_{book['id']}"
                        ):

                            requests.delete(
                                f"{API_URL}/cart/{book['id']}",
                                timeout=5
                            )

                            st.rerun()

                total += book["price"]

            st.divider()

            st.subheader(f"Total: Rs. {total:,}")

            if st.button(
                "Place My Order",
                type="primary",
                use_container_width=True
            ):

                result = requests.post(
                    f"{API_URL}/orders",
                    timeout=5
                )

                if result.status_code == 200:

                    st.success("🎉 Your order has been placed!")

                    st.json(result.json())

                else:

                    try:
                        st.error(result.json()["detail"])
                    except:
                        st.error("Unable to place order.")

    except requests.exceptions.RequestException:

        st.error("Unable to connect to FastAPI backend.")


# ==================================
# BUYER ORDERS PAGE
# ==================================

elif role == "Buyer" and page == "My Orders":

    st.header("📦 My Orders")

    try:

        response = requests.get(
            f"{API_URL}/orders",
            timeout=5
        )

        response.raise_for_status()

        orders = response.json()

        if len(orders) == 0:

            st.info("You haven't placed any orders yet.")

        else:

            for order in orders:

                with st.container(border=True):

                    st.subheader(
                        f"Order #{order['order_id']}"
                    )

                    st.write(
                        f"Status: {order['status']}"
                    )

                    for book in order["books"]:

                        st.write(
                            f"📕 {book['name']} - Rs. {book['price']:,}"
                        )

                    st.success("Order confirmed!")

    except requests.exceptions.RequestException:

        st.error("Unable to connect to FastAPI backend.")


# ==================================
# ADMIN DASHBOARD
# ==================================

elif role == "Admin" and page == "Admin Dashboard":

    st.header("⚙️ Admin Dashboard")

    st.success("Welcome, Admin!")

    try:

        books = get_books()

        requests_response = requests.get(
            f"{API_URL}/book-requests",
            timeout=5
        )

        requests_response.raise_for_status()

        all_requests = requests_response.json()

        pending_requests = [
            item for item in all_requests
            if item["status"] == "Pending"
        ]

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Total Books",
                len(books)
            )

        with col2:

            st.metric(
                "Pending Requests",
                len(pending_requests)
            )

        st.divider()

        st.subheader("➕ Add New Book")

        with st.form("admin_add_book"):

            new_name = st.text_input(
                "Book Name"
            )

            new_price = st.number_input(
                "Book Price (Rs.)",
                min_value=1,
                step=100
            )

            add_button = st.form_submit_button(
                "Add Book",
                use_container_width=True
            )

            if add_button:

                if new_name.strip() == "":

                    st.warning("Enter book name.")

                else:

                    result = requests.post(
                        f"{API_URL}/books",
                        json={
                            "name": new_name,
                            "price": int(new_price)
                        },
                        headers=get_admin_headers(),
                        timeout=5
                    )

                    if result.status_code == 200:

                        st.success("Book added successfully!")

                        st.rerun()

                    else:

                        st.error("Unable to add book.")

    except requests.exceptions.RequestException:

        st.error("Unable to connect to FastAPI backend.")


# ==================================
# ADMIN BOOK REQUESTS
# ==================================

elif role == "Admin" and page == "Book Requests":

    st.header("📩 Buyer Book Requests")

    st.write(
        "Review unavailable book requests submitted by buyers."
    )

    try:

        response = requests.get(
            f"{API_URL}/book-requests",
            timeout=5
        )

        response.raise_for_status()

        all_requests = response.json()

        if len(all_requests) == 0:

            st.info("No book requests available.")

        else:

            for request in all_requests:

                with st.container(border=True):

                    st.subheader(
                        request["book_name"]
                    )

                    st.write(
                        f"Request ID: {request['request_id']}"
                    )

                    st.write(
                        f"Requested by: {request['requester_name']}"
                    )

                    if request["status"] == "Pending":

                        st.warning("Pending Review")

                        price = st.number_input(
                            "Set Book Price (Rs.)",
                            min_value=1,
                            step=100,
                            key=f"price_{request['request_id']}"
                        )

                        col1, col2 = st.columns(2)

                        with col1:

                            if st.button(
                                "✅ Approve & Add Book",
                                key=f"approve_{request['request_id']}",
                                use_container_width=True
                            ):

                                result = requests.post(
                                    f"{API_URL}/book-requests/{request['request_id']}/approve",
                                    json={"price": int(price)},
                                    headers=get_admin_headers(),
                                    timeout=5
                                )

                                if result.status_code == 200:

                                    st.success(
                                        "Request approved! Book added to store."
                                    )

                                    st.rerun()

                                else:

                                    st.error("Unable to approve request.")

                        with col2:

                            if st.button(
                                "❌ Reject",
                                key=f"reject_{request['request_id']}",
                                use_container_width=True
                            ):

                                result = requests.post(
                                    f"{API_URL}/book-requests/{request['request_id']}/reject",
                                    headers=get_admin_headers(),
                                    timeout=5
                                )

                                if result.status_code == 200:

                                    st.warning("Request rejected.")

                                    st.rerun()

                                else:

                                    st.error("Unable to reject request.")

                    elif request["status"] == "Approved":

                        st.success("Approved — Book added to store.")

                    else:

                        st.error("Request rejected.")

    except requests.exceptions.RequestException:

        st.error("Unable to connect to FastAPI backend.")


# ==================================
# ADMIN MANAGE BOOKS
# ==================================

elif role == "Admin" and page == "Manage Books":

    st.header("📚 Manage Books")

    try:

        books = get_books()

        st.write(f"Total Books: {len(books)}")

        for book in books:

            with st.container(border=True):

                st.subheader(book["name"])

                st.write(f"Book ID: {book['id']}")

                st.write(f"Price: Rs. {book['price']:,}")

                with st.expander("Edit Book"):

                    updated_name = st.text_input(
                        "New Book Name",
                        value=book["name"],
                        key=f"name_{book['id']}"
                    )

                    updated_price = st.number_input(
                        "New Price",
                        min_value=1,
                        value=book["price"],
                        key=f"price_edit_{book['id']}"
                    )

                    if st.button(
                        "Update Book",
                        key=f"update_{book['id']}"
                    ):

                        result = requests.put(
                            f"{API_URL}/books/{book['id']}",
                            json={
                                "name": updated_name,
                                "price": int(updated_price)
                            },
                            headers=get_admin_headers(),
                            timeout=5
                        )

                        if result.status_code == 200:

                            st.success("Book updated!")

                            st.rerun()

                        else:

                            st.error("Unable to update book.")

                if st.button(
                    "🗑️ Delete Book",
                    key=f"delete_{book['id']}"
                ):

                    result = requests.delete(
                        f"{API_URL}/books/{book['id']}",
                        headers=get_admin_headers(),
                        timeout=5
                    )

                    if result.status_code == 200:

                        st.success("Book deleted!")

                        st.rerun()

                    else:

                        st.error("Unable to delete book.")

    except requests.exceptions.RequestException:

        st.error("Unable to connect to FastAPI backend.")


# ==================================
# ADMIN LOGOUT
# ==================================

if role == "Admin" and st.session_state.admin_logged_in:

    st.sidebar.divider()

    if st.sidebar.button("🔒 Admin Logout"):

        st.session_state.admin_logged_in = False
        st.session_state.admin_password = ""

        st.rerun()


# ==================================
# FOOTER
# ==================================

st.divider()

st.markdown(
    "<center>📚 My Bookstore | Python + FastAPI + Streamlit</center>",
    unsafe_allow_html=True
)
