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
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="gharzaika_db",
        user="postgres",
        password="Vidisha@123"
    )


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


# =========================================================
# CUSTOMER WEBSITE - AVAILABLE FOODS
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
# ADMIN - ADD NEW FOOD
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

        existing = cursor.fetchone()

        if not existing:
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
# ADMIN - CHANGE AVAILABILITY
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

        existing = cursor.fetchone()

        if not existing:
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

        existing = cursor.fetchone()

        if not existing:
            raise HTTPException(
                status_code=404,
                detail="Food item not found."
            )

        # Check whether this food was already used in an order
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
                    "You cannot delete it. Please make it unavailable instead."
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
# PLACE ORDER
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

    if order.payment_method not in ["Cash", "QR", "cash", "qr"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid payment method."
        )

    if not order.items:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty."
        )

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor()

        # -------------------------------------------------
        # FIND EXISTING CUSTOMER
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
            order.total_amount,
            order.payment_method.lower(),
            "pending"
        ))

        order_id = cursor.fetchone()[0]

        # -------------------------------------------------
        # INSERT ORDER ITEMS
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
            "customer_id": customer_id
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
# SERVE WEBSITE
# =========================================================

app.mount(
    "/",
    StaticFiles(directory="static", html=True),
    name="static"
)