import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import psycopg2

app = FastAPI(title="GharZaika")


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        return psycopg2.connect(database_url)

    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="gharzaika_db",
        user="postgres",
        password="Vidisha@123"
    )


# =========================================================
# DISCOUNT SETTINGS
# =========================================================

DISCOUNT_PERCENT = 5
MAX_DISCOUNT_AMOUNT = 50
REQUIRED_ORDER_DAYS = 4
CHECKING_DAYS = 7


# =========================================================
# MODELS
# =========================================================

class OrderItem(BaseModel):
    food_id: int
    quantity: int
    price: float


class OrderRequest(BaseModel):
    name: str
    phone: str
    email: Optional[str] = ""
    address: str
    total_amount: float
    payment_method: str
    items: List[OrderItem]


class FoodRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    price: float
    category: str
    available: bool = True


class AvailabilityRequest(BaseModel):
    available: bool


class OrderStatusRequest(BaseModel):
    order_status: str


# =========================================================
# REGULAR CUSTOMER DISCOUNT CALCULATION
# =========================================================

def calculate_customer_discount(
    cursor,
    customer_id: int,
    bill_amount: float
):
    """
    Regular customer rule:

    Previous 7 calendar days:
    - Count distinct days on which customer ordered
    - Cancelled orders are ignored
    - If customer ordered on 4 or more different days,
      customer gets 5% discount
    - Maximum discount = ₹50
    """

    if bill_amount <= 0:
        return {
            "eligible": False,
            "discount_percent": 0,
            "discount_amount": 0,
            "final_amount": bill_amount,
            "order_days": 0,
            "message": "No discount available."
        }

    cursor.execute("""
        SELECT COUNT(DISTINCT DATE(created_at))
        FROM orders
        WHERE customer_id = %s
          AND order_status <> 'cancelled'
          AND created_at >= CURRENT_DATE - INTERVAL '6 days'
          AND created_at < CURRENT_DATE + INTERVAL '1 day';
    """, (customer_id,))

    result = cursor.fetchone()

    order_days = result[0] if result and result[0] is not None else 0

    # -----------------------------------------------------
    # CUSTOMER ELIGIBILITY
    # -----------------------------------------------------

    if order_days >= REQUIRED_ORDER_DAYS:

        calculated_discount = (
            bill_amount * DISCOUNT_PERCENT / 100
        )

        discount_amount = min(
            calculated_discount,
            MAX_DISCOUNT_AMOUNT
        )

        final_amount = bill_amount - discount_amount

        return {
            "eligible": True,
            "discount_percent": DISCOUNT_PERCENT,
            "discount_amount": round(discount_amount, 2),
            "final_amount": round(final_amount, 2),
            "order_days": order_days,
            "message": (
                f"Regular customer discount applied. "
                f"{DISCOUNT_PERCENT}% OFF."
            )
        }

    # -----------------------------------------------------
    # NOT ELIGIBLE
    # -----------------------------------------------------

    return {
        "eligible": False,
        "discount_percent": 0,
        "discount_amount": 0,
        "final_amount": round(bill_amount, 2),
        "order_days": order_days,
        "message": (
            f"Customer ordered on {order_days} different "
            f"day(s) in the last {CHECKING_DAYS} days. "
            f"{REQUIRED_ORDER_DAYS} days are required."
        )
    }


# =========================================================
# CUSTOMER - AVAILABLE FOODS
# =========================================================

@app.get("/api/foods")
def get_foods():

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                name,
                description,
                price,
                category,
                available
            FROM food_items
            WHERE available = TRUE
            ORDER BY id ASC;
        """)

        rows = cursor.fetchall()

        foods = []

        for row in rows:
            foods.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "price": float(row[3]),
                "category": row[4],
                "available": row[5]
            })

        return foods

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load foods: {str(e)}"
        )

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# ADMIN - GET ALL FOODS
# =========================================================

@app.get("/api/foods/all")
def get_all_foods():

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                name,
                description,
                price,
                category,
                available
            FROM food_items
            ORDER BY id ASC;
        """)

        rows = cursor.fetchall()

        foods = []

        for row in rows:
            foods.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "price": float(row[3]),
                "category": row[4],
                "available": row[5]
            })

        return foods

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load all foods: {str(e)}"
        )

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# ADMIN - ADD FOOD
# =========================================================

@app.post("/api/admin/foods")
def add_food(food: FoodRequest):

    if not food.name.strip():
        raise HTTPException(
            status_code=400,
            detail="Food name is required."
        )

    if food.price <= 0:
        raise HTTPException(
            status_code=400,
            detail="Food price must be greater than 0."
        )

    if not food.category.strip():
        raise HTTPException(
            status_code=400,
            detail="Food category is required."
        )

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO food_items
            (
                name,
                description,
                price,
                category,
                available
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """, (
            food.name.strip(),
            food.description.strip(),
            food.price,
            food.category.strip(),
            food.available
        ))

        food_id = cursor.fetchone()[0]

        conn.commit()

        return {
            "success": True,
            "message": "Food added successfully!",
            "id": food_id
        }

    except Exception as e:

        if conn:
            conn.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Unable to add food: {str(e)}"
        )

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# ADMIN - UPDATE FOOD
# =========================================================

@app.put("/api/admin/foods/{food_id}")
def update_food(food_id: int, food: FoodRequest):

    if not food.name.strip():
        raise HTTPException(
            status_code=400,
            detail="Food name is required."
        )

    if food.price <= 0:
        raise HTTPException(
            status_code=400,
            detail="Food price must be greater than 0."
        )

    if not food.category.strip():
        raise HTTPException(
            status_code=400,
            detail="Food category is required."
        )

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id
            FROM food_items
            WHERE id = %s;
        """, (food_id,))

        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="Food item not found."
            )

        cursor.execute("""
            UPDATE food_items
            SET
                name = %s,
                description = %s,
                price = %s,
                category = %s,
                available = %s
            WHERE id = %s;
        """, (
            food.name.strip(),
            food.description.strip(),
            food.price,
            food.category.strip(),
            food.available,
            food_id
        ))

        conn.commit()

        return {
            "success": True,
            "message": "Food updated successfully!"
        }

    except HTTPException:
        if conn:
            conn.rollback()
        raise

    except Exception as e:

        if conn:
            conn.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Unable to update food: {str(e)}"
        )

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# ADMIN - CHANGE FOOD AVAILABILITY
# =========================================================

@app.put("/api/admin/foods/{food_id}/availability")
def change_food_availability(
    food_id: int,
    data: AvailabilityRequest
):

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id
            FROM food_items
            WHERE id = %s;
        """, (food_id,))

        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="Food item not found."
            )

        cursor.execute("""
            UPDATE food_items
            SET available = %s
            WHERE id = %s;
        """, (
            data.available,
            food_id
        ))

        conn.commit()

        return {
            "success": True,
            "message": (
                "Food is now available."
                if data.available
                else "Food is now unavailable."
            )
        }

    except HTTPException:
        if conn:
            conn.rollback()
        raise

    except Exception as e:

        if conn:
            conn.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Unable to change availability: {str(e)}"
        )

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# ADMIN - DELETE FOOD
# =========================================================

@app.delete("/api/admin/foods/{food_id}")
def delete_food(food_id: int):

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id
            FROM food_items
            WHERE id = %s;
        """, (food_id,))

        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="Food item not found."
            )

        cursor.execute("""
            SELECT COUNT(*)
            FROM order_items
            WHERE food_id = %s;
        """, (food_id,))

        order_count = cursor.fetchone()[0]

        if order_count > 0:
            raise HTTPException(
                status_code=400,
                detail=(
                    "This food is already used in an order. "
                    "Please make it unavailable instead of deleting it."
                )
            )

        cursor.execute("""
            DELETE FROM food_items
            WHERE id = %s;
        """, (food_id,))

        conn.commit()

        return {
            "success": True,
            "message": "Food deleted successfully!"
        }

    except HTTPException:
        if conn:
            conn.rollback()
        raise

    except Exception as e:

        if conn:
            conn.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Unable to delete food: {str(e)}"
        )

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# CUSTOMER - CHECK REGULAR CUSTOMER DISCOUNT
# =========================================================

@app.get("/api/customer-discount/{phone}")
def check_customer_discount(phone: str):

    phone = phone.strip()

    if not phone:
        raise HTTPException(
            status_code=400,
            detail="Phone number is required."
        )

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id
            FROM customers
            WHERE phone = %s;
        """, (phone,))

        customer = cursor.fetchone()

        # New customer
        if not customer:
            return {
                "eligible": False,
                "discount_percent": 0,
                "discount_amount": 0,
                "order_days": 0,
                "required_order_days": REQUIRED_ORDER_DAYS,
                "checking_days": CHECKING_DAYS,
                "message": "New customer. No regular customer discount."
            }

        customer_id = customer[0]

        discount_info = calculate_customer_discount(
            cursor,
            customer_id,
            100
        )

        return {
            "eligible": discount_info["eligible"],
            "discount_percent": discount_info["discount_percent"],
            "discount_amount": discount_info["discount_amount"],
            "order_days": discount_info["order_days"],
            "required_order_days": REQUIRED_ORDER_DAYS,
            "checking_days": CHECKING_DAYS,
            "message": discount_info["message"]
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Unable to check customer discount: {str(e)}"
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# CUSTOMER - PLACE ORDER
# =========================================================

@app.post("/api/orders")
def place_order(order: OrderRequest):

    if not order.name.strip():
        raise HTTPException(
            status_code=400,
            detail="Customer name is required."
        )

    if not order.phone.strip():
        raise HTTPException(
            status_code=400,
            detail="Phone number is required."
        )

    if not order.address.strip():
        raise HTTPException(
            status_code=400,
            detail="Delivery address is required."
        )

    if order.payment_method not in [
        "Cash",
        "QR",
        "cash",
        "qr"
    ]:
        raise HTTPException(
            status_code=400,
            detail="Invalid payment method."
        )

    if not order.items:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty."
        )

    if order.total_amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Order amount must be greater than 0."
        )

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor()

        # -------------------------------------------------
        # FIND CUSTOMER
        # -------------------------------------------------

        cursor.execute("""
            SELECT id
            FROM customers
            WHERE phone = %s;
        """, (order.phone.strip(),))

        customer = cursor.fetchone()

        if customer:

            customer_id = customer[0]

            cursor.execute("""
                UPDATE customers
                SET
                    name = %s,
                    email = %s,
                    address = %s
                WHERE id = %s;
            """, (
                order.name.strip(),
                order.email.strip() if order.email else "",
                order.address.strip(),
                customer_id
            ))

        else:

            cursor.execute("""
                INSERT INTO customers
                (
                    name,
                    phone,
                    email,
                    address
                )
                VALUES (%s, %s, %s, %s)
                RETURNING id;
            """, (
                order.name.strip(),
                order.phone.strip(),
                order.email.strip() if order.email else "",
                order.address.strip()
            ))

            customer_id = cursor.fetchone()[0]

        # -------------------------------------------------
        # CALCULATE REGULAR CUSTOMER DISCOUNT
        # -------------------------------------------------

        discount_info = calculate_customer_discount(
            cursor,
            customer_id,
            order.total_amount
        )

        subtotal_amount = round(
            order.total_amount,
            2
        )

        discount_amount = round(
            discount_info["discount_amount"],
            2
        )

        final_amount = round(
            discount_info["final_amount"],
            2
        )

        # -------------------------------------------------
        # CREATE ORDER
        # -------------------------------------------------

        cursor.execute("""
            INSERT INTO orders
            (
                customer_id,
                total_amount,
                payment_method,
                order_status
            )
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """, (
            customer_id,
            final_amount,
            order.payment_method.lower(),
            "pending"
        ))

        order_id = cursor.fetchone()[0]

        # -------------------------------------------------
        # ORDER ITEMS
        # -------------------------------------------------

        for item in order.items:

            cursor.execute("""
                INSERT INTO order_items
                (
                    order_id,
                    food_id,
                    quantity,
                    price
                )
                VALUES (%s, %s, %s, %s);
            """, (
                order_id,
                item.food_id,
                item.quantity,
                item.price
            ))

        conn.commit()

        return {
            "success": True,
            "message": "Order placed successfully!",
            "order_id": order_id,
            "customer_id": customer_id,

            # Discount information
            "subtotal_amount": subtotal_amount,
            "discount_eligible": discount_info["eligible"],
            "discount_percent": discount_info["discount_percent"],
            "discount_amount": discount_amount,
            "final_amount": final_amount,
            "order_days": discount_info["order_days"],
            "required_order_days": REQUIRED_ORDER_DAYS,
            "checking_days": CHECKING_DAYS,

            "discount_message": discount_info["message"]
        }

    except Exception as e:

        if conn:
            conn.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Unable to place order: {str(e)}"
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# ADMIN - GET ALL ORDERS
# =========================================================

@app.get("/api/admin/orders")
def get_all_orders():

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                o.id,
                c.name,
                c.phone,
                c.address,
                o.total_amount,
                o.payment_method,
                o.order_status,
                o.created_at
            FROM orders o
            LEFT JOIN customers c
                ON o.customer_id = c.id
            ORDER BY o.id DESC;
        """)

        rows = cursor.fetchall()

        orders = []

        for row in rows:

            orders.append({
                "id": row[0],
                "customer_name": row[1],
                "customer_phone": row[2],
                "customer_address": row[3],
                "total_amount": float(row[4]),
                "payment_method": row[5],
                "order_status": row[6],
                "created_at": row[7].isoformat() if row[7] else None
            })

        return orders

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Unable to load orders: {str(e)}"
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# ADMIN - GET ORDER DETAILS / ITEMS
# =========================================================

@app.get("/api/admin/orders/{order_id}")
def get_order_details(order_id: int):

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                o.id,
                c.name,
                c.phone,
                c.email,
                c.address,
                o.total_amount,
                o.payment_method,
                o.order_status,
                o.created_at
            FROM orders o
            LEFT JOIN customers c
                ON o.customer_id = c.id
            WHERE o.id = %s;
        """, (order_id,))

        order = cursor.fetchone()

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found."
            )

        cursor.execute("""
            SELECT
                oi.food_id,
                f.name,
                oi.quantity,
                oi.price
            FROM order_items oi
            LEFT JOIN food_items f
                ON oi.food_id = f.id
            WHERE oi.order_id = %s
            ORDER BY oi.id ASC;
        """, (order_id,))

        item_rows = cursor.fetchall()

        items = []

        for row in item_rows:

            items.append({
                "food_id": row[0],
                "food_name": row[1],
                "quantity": row[2],
                "price": float(row[3])
            })

        return {
            "id": order[0],
            "customer_name": order[1],
            "customer_phone": order[2],
            "customer_email": order[3],
            "customer_address": order[4],
            "total_amount": float(order[5]),
            "payment_method": order[6],
            "order_status": order[7],
            "created_at": (
                order[8].isoformat()
                if order[8]
                else None
            ),
            "items": items
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Unable to load order details: {str(e)}"
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# ADMIN - UPDATE ORDER STATUS
# =========================================================

@app.put("/api/admin/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    data: OrderStatusRequest
):

    allowed_statuses = [
        "pending",
        "preparing",
        "ready",
        "delivered",
        "cancelled"
    ]

    new_status = data.order_status.strip().lower()

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid order status. Allowed values: "
                "pending, preparing, ready, delivered, cancelled."
            )
        )

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id
            FROM orders
            WHERE id = %s;
        """, (order_id,))

        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="Order not found."
            )

        cursor.execute("""
            UPDATE orders
            SET order_status = %s
            WHERE id = %s;
        """, (
            new_status,
            order_id
        ))

        conn.commit()

        return {
            "success": True,
            "message": "Order status updated successfully!",
            "order_id": order_id,
            "order_status": new_status
        }

    except HTTPException:

        if conn:
            conn.rollback()

        raise

    except Exception as e:

        if conn:
            conn.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Unable to update order status: {str(e)}"
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# CUSTOMER - TRACK ORDER
# =========================================================

@app.get("/api/orders/{order_id}/status")
def track_order(order_id: int):

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                o.id,
                o.total_amount,
                o.payment_method,
                o.order_status,
                o.created_at
            FROM orders o
            WHERE o.id = %s;
        """, (order_id,))

        order = cursor.fetchone()

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found."
            )

        return {
            "order_id": order[0],
            "total_amount": float(order[1]),
            "payment_method": order[2],
            "order_status": order[3],
            "created_at": (
                order[4].isoformat()
                if order[4]
                else None
            )
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Unable to track order: {str(e)}"
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# ADMIN - GET ALL CUSTOMERS
# =========================================================

@app.get("/api/admin/customers")
def get_all_customers():

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                c.id,
                c.name,
                c.phone,
                c.email,
                c.address,
                COUNT(o.id) AS total_orders,
                COALESCE(SUM(o.total_amount), 0) AS total_spending
            FROM customers c
            LEFT JOIN orders o
                ON c.id = o.customer_id
            GROUP BY
                c.id,
                c.name,
                c.phone,
                c.email,
                c.address
            ORDER BY c.id DESC;
        """)

        rows = cursor.fetchall()

        customers = []

        for row in rows:

            customers.append({
                "id": row[0],
                "name": row[1],
                "phone": row[2],
                "email": row[3],
                "address": row[4],
                "total_orders": row[5],
                "total_spending": float(row[6])
            })

        return customers

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Unable to load customers: {str(e)}"
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# SERVE WEBSITE
# =========================================================

app.mount(
    "/",
    StaticFiles(
        directory="static",
        html=True
    ),
    name="static"
)
