
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel


app = FastAPI(title="My Online Bookstore")


# ==================================
# ADMIN PASSWORD
# ==================================

ADMIN_PASSWORD = "1234"


# ==================================
# BOOKS DATABASE
# ==================================

books = [
    {"id": 1, "name": "Python Basics", "price": 1500},
    {"id": 2, "name": "Atomic Habits", "price": 1800},
    {"id": 3, "name": "Rich Dad Poor Dad", "price": 1200},
    {"id": 4, "name": "Deep Work", "price": 2000}
]


# ==================================
# CART DATABASE
# ==================================

cart = []


# ==================================
# ORDERS DATABASE
# ==================================

orders = []


# ==================================
# BOOK REQUEST DATABASE
# ==================================

book_requests = []


# ==================================
# PYDANTIC MODELS
# ==================================

class Book(BaseModel):
    name: str
    price: int


class CartItem(BaseModel):
    book_id: int


class AdminLogin(BaseModel):
    password: str


class BookRequest(BaseModel):
    book_name: str
    requester_name: str


class ApproveRequest(BaseModel):
    price: int


# ==================================
# ADMIN ACCESS CHECK
# ==================================

def check_admin(admin_password):

    if admin_password != ADMIN_PASSWORD:

        raise HTTPException(
            status_code=403,
            detail="Admin access denied. Incorrect password."
        )


# ==================================
# ROOT
# ==================================

@app.get("/")
def root():

    return "Welcome to My Online Bookstore"


# ==================================
# ADMIN LOGIN
# ==================================

@app.post("/admin/login")
def admin_login(data: AdminLogin):

    if data.password == ADMIN_PASSWORD:

        return {
            "message": "Admin login successful",
            "success": True
        }

    raise HTTPException(
        status_code=401,
        detail="Incorrect admin password"
    )


# ==================================
# GET - SHOW ALL BOOKS
# ==================================

@app.get("/books")
def get_books():

    return books


# ==================================
# GET - TOTAL BOOKS
# ==================================

@app.get("/books/count")
def total_books():

    return {
        "total_books": len(books)
    }


# ==================================
# GET - SHOW BOOK BY ID
# ==================================

@app.get("/books/{book_id}")
def get_book(book_id: int):

    for book in books:

        if book["id"] == book_id:
            return book

    raise HTTPException(
        status_code=404,
        detail="Book not found"
    )


# ==================================
# POST - ADMIN ADD BOOK
# ==================================

@app.post("/books")
def add_book(
    book: Book,
    admin_password: str = Header(
        default="",
        alias="X-Admin-Password"
    )
):

    check_admin(admin_password)

    new_id = max(
        [book["id"] for book in books],
        default=0
    ) + 1

    new_book = {
        "id": new_id,
        "name": book.name,
        "price": book.price
    }

    books.append(new_book)

    return {
        "message": "Book added successfully",
        "book": new_book
    }


# ==================================
# PUT - ADMIN UPDATE BOOK
# ==================================

@app.put("/books/{book_id}")
def update_book(
    book_id: int,
    updated_book: Book,
    admin_password: str = Header(
        default="",
        alias="X-Admin-Password"
    )
):

    check_admin(admin_password)

    for book in books:

        if book["id"] == book_id:

            book["name"] = updated_book.name
            book["price"] = updated_book.price

            return {
                "message": "Book updated successfully",
                "book": book
            }

    raise HTTPException(
        status_code=404,
        detail="Book not found"
    )


# ==================================
# DELETE - ADMIN DELETE BOOK
# ==================================

@app.delete("/books/{book_id}")
def delete_book(
    book_id: int,
    admin_password: str = Header(
        default="",
        alias="X-Admin-Password"
    )
):

    check_admin(admin_password)

    for index, book in enumerate(books):

        if book["id"] == book_id:

            deleted_book = books.pop(index)

            return {
                "message": "Book deleted successfully",
                "book": deleted_book
            }

    raise HTTPException(
        status_code=404,
        detail="Book not found"
    )


# ==================================
# POST - BUYER ADD BOOK TO CART
# ==================================

@app.post("/cart")
def add_to_cart(item: CartItem):

    for book in books:

        if book["id"] == item.book_id:

            cart.append(book.copy())

            return {
                "message": "Book added to cart",
                "cart": cart
            }

    raise HTTPException(
        status_code=404,
        detail="Book not found"
    )


# ==================================
# GET - SHOW CART
# ==================================

@app.get("/cart")
def get_cart():

    return cart


# ==================================
# DELETE - REMOVE BOOK FROM CART
# ==================================

@app.delete("/cart/{book_id}")
def remove_from_cart(book_id: int):

    for index, book in enumerate(cart):

        if book["id"] == book_id:

            removed_book = cart.pop(index)

            return {
                "message": "Book removed from cart",
                "book": removed_book,
                "cart": cart
            }

    raise HTTPException(
        status_code=404,
        detail="Book not found in cart"
    )


# ==================================
# POST - BUYER REQUEST UNAVAILABLE BOOK
# ==================================

@app.post("/book-requests")
def request_book(data: BookRequest):

    if data.book_name.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="Book name cannot be empty"
        )

    if data.requester_name.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="Your name cannot be empty"
        )

    for book in books:

        if book["name"].lower() == data.book_name.strip().lower():

            raise HTTPException(
                status_code=400,
                detail="This book is already available in our store"
            )

    new_request = {
        "request_id": max(
            [item["request_id"] for item in book_requests],
            default=0
        ) + 1,
        "book_name": data.book_name.strip(),
        "requester_name": data.requester_name.strip(),
        "status": "Pending"
    }

    book_requests.append(new_request)

    return {
        "message": "Book request submitted successfully",
        "request": new_request
    }


# ==================================
# GET - SHOW BOOK REQUESTS
# ==================================

@app.get("/book-requests")
def get_book_requests():

    return book_requests


# ==================================
# POST - ADMIN APPROVE BOOK REQUEST
# ==================================

@app.post("/book-requests/{request_id}/approve")
def approve_book_request(
    request_id: int,
    data: ApproveRequest,
    admin_password: str = Header(
        default="",
        alias="X-Admin-Password"
    )
):

    check_admin(admin_password)

    for request in book_requests:

        if request["request_id"] == request_id:

            if request["status"] != "Pending":

                raise HTTPException(
                    status_code=400,
                    detail="This request has already been processed"
                )

            new_id = max(
                [book["id"] for book in books],
                default=0
            ) + 1

            new_book = {
                "id": new_id,
                "name": request["book_name"],
                "price": data.price
            }

            books.append(new_book)

            request["status"] = "Approved"

            return {
                "message": "Request approved and book added",
                "book": new_book,
                "request": request
            }

    raise HTTPException(
        status_code=404,
        detail="Book request not found"
    )


# ==================================
# POST - ADMIN REJECT BOOK REQUEST
# ==================================

@app.post("/book-requests/{request_id}/reject")
def reject_book_request(
    request_id: int,
    admin_password: str = Header(
        default="",
        alias="X-Admin-Password"
    )
):

    check_admin(admin_password)

    for request in book_requests:

        if request["request_id"] == request_id:

            if request["status"] != "Pending":

                raise HTTPException(
                    status_code=400,
                    detail="This request has already been processed"
                )

            request["status"] = "Rejected"

            return {
                "message": "Book request rejected",
                "request": request
            }

    raise HTTPException(
        status_code=404,
        detail="Book request not found"
    )


# ==================================
# GET - BOOK RECOMMENDATIONS
# ==================================

@app.get("/recommendations")
def recommendations():

    return books[:3]


# ==================================
# POST - PLACE ORDER
# ==================================

@app.post("/orders")
def place_order():

    if len(cart) == 0:

        raise HTTPException(
            status_code=400,
            detail="Your cart is empty"
        )

    new_order = {
        "order_id": max(
            [order["order_id"] for order in orders],
            default=0
        ) + 1,
        "books": cart.copy(),
        "status": "Confirmed"
    }

    orders.append(new_order)

    cart.clear()

    return {
        "message": "Order placed successfully",
        "order": new_order
    }


# ==================================
# GET - SHOW ALL ORDERS
# ==================================

@app.get("/orders")
def get_orders():

    return orders
