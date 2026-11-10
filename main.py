import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# 1. ΣΥΝΔΕΣΗ ΜΕ ΤΗ ΒΑΣΗ
# Δημιουργεί ένα αρχείο 'shop.db' στον φάκελό σου. Αν υπάρχει ήδη, απλά το ανοίγει.
conn = sqlite3.connect("shop.db", check_same_thread=False)
cursor = conn.cursor()

# 2. ΔΗΜΙΟΥΡΓΙΑ ΠΙΝΑΚΑ
# Λέμε στη βάση: "Φτιάξε έναν πίνακα 'products' με στήλες id, name και price"
cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL
    )
""")
conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL
)
""")
conn.commit()

# Το BaseModel παραμένει ίδιο ("Ο Πορτιέρης")
class NewProduct(BaseModel):
    name: str
    price: float

class NewUser(BaseModel):
    username: str
    email: str

# 3. ΕΓΓΡΑΦΗ ΣΤΗ ΒΑΣΗ (POST)
@app.post("/products")
def create_product(product: NewProduct):
    # Βάζουμε τα δεδομένα του χρήστη μέσα στον πίνακα της βάσης
    cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", (product.name, product.price))
    conn.commit() # Αποθήκευση αλλαγών!
    
    return {"status": "success", "message": f"Το προϊόν {product.name} αποθηκεύτηκε ΜΟΝΙΜΑ!"}

# 4. ΑΝΑΓΝΩΣΗ ΑΠΟ ΤΗ ΒΑΣΗ (GET)
@app.get("/products")
def get_products():
    # Ζητάμε από τη βάση όλα τα προϊόντα
    cursor.execute("SELECT name, price FROM products")
    rows = cursor.fetchall()
    
    # Πακετάρουμε τα αποτελέσματα σε μορφή JSON/Λεξικού για να τα διαβάσει το front-end
    db_products = [{"name": row[0], "price": row[1]} for row in rows]

    return {"status": "success", "products": db_products}

# 5. ΔΙΑΓΡΑΦΗ ΠΡΟΪΟΝΤΟΣ ΜΕ ΕΛΕΓΧΟ ΣΦΑΛΜΑΤΟΣ (DELETE)
@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    # Βήμα 1: Ψάχνουμε να βρούμε αν υπάρχει αυτό το ID στη βάση
    cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
    existing_product = cursor.fetchone() # Φέρνει το αποτέλεσμα ή None (τίποτα)
    
    # Βήμα 2: Αν δεν υπάρχει, πετάμε σφάλμα 404 και σταματάμε τον κώδικα
    if existing_product is None:
        raise HTTPException(status_code=404, detail="Το προϊόν δεν βρέθηκε!")
        
    # Βήμα 3: Αν υπάρχει, προχωράμε κανονικά στη διαγραφή
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit() 
    
    return {"status": "success", "message": f"Το προϊόν με ID {product_id} διαγράφηκε επιτυχώς!"}

# 6. ΕΝΗΜΕΡΩΣΗ ΠΡΟΪΟΝΤΟΣ ΜΕ ΕΛΕΓΧΟ ΣΦΑΛΜΑΤΟΣ (PUT)
@app.put("/products/{product_id}")
def update_product(product_id: int, product: NewProduct):
    # Έλεγχος αν υπάρχει
    cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
    if cursor.fetchone() is None:
        raise HTTPException(status_code=404, detail="Το προϊόν δεν βρέθηκε, η ενημέρωση ακυρώθηκε!")
        
    # Ενημέρωση αν βρεθεί
    cursor.execute("""
        UPDATE products 
        SET name = ?, price = ? 
        WHERE id = ?
    """, (product.name, product.price, product_id))
    
    conn.commit() 
    return {"status": "success", "message": f"Το προϊόν με ID {product_id} ενημερώθηκε επιτυχώς!"}


# --- USERS ENDPOINTS ---

@app.post("/users")
def create_user(user: NewUser):
    cursor.execute("INSERT INTO users (username, email) VALUES (?, ?)", (user.username, user.email))
    conn.commit()
    return {"status": "success", "message": f"Ο χρήστης {user.username} δημιουργήθηκε!"}

@app.get("/users")
def get_users():
    cursor.execute("SELECT id, username, email FROM users")
    rows = cursor.fetchall()
    db_users = [{"id": row[0], "username": row[1], "email": row[2]} for row in rows]
    return {"status": "success", "users": db_users}
    