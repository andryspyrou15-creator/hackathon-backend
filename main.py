import sqlite3
from fastapi import FastAPI
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

# Το BaseModel παραμένει ίδιο ("Ο Πορτιέρης")
class NewProduct(BaseModel):
    name: str
    price: float

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

    # 5. ΔΙΑΓΡΑΦΗ ΠΡΟΪΟΝΤΟΣ (DELETE)
@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    # Λέμε στη βάση να σβήσει τη γραμμή που έχει αυτό το συγκεκριμένο ID
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit() # Αποθήκευση της διαγραφής!
    
    return {"status": "success", "message": f"Το προϊόν με ID {product_id} διαγράφηκε επιτυχώς!"}

# 6. ΕΝΗΜΕΡΩΣΗ ΠΡΟΪΟΝΤΟΣ (PUT)
@app.put("/products/{product_id}")
def update_product(product_id: int, product: NewProduct):
    # Λέμε στη βάση: "Άλλαξε το όνομα και την τιμή στο προϊόν με αυτό το συγκεκριμένο ID"
    cursor.execute("""
        UPDATE products 
        SET name = ?, price = ? 
        WHERE id = ?
    """, (product.name, product.price, product_id))
    
    conn.commit() # Αποθήκευση των αλλαγών
    
    return {"status": "success", "message": f"Το προϊόν με ID {product_id} ενημερώθηκε επιτυχώς!"}
    
    