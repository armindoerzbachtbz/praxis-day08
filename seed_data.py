"""
seed_data.py — Populate the TechStyle database with 20 fashion products.

Run directly:   python seed_data.py
Or from Flask:  import seed_data; seed_data.seed()
"""

import sqlite3
import os

DATABASE = "/tmp/techstyle.db"

PRODUCTS = [
    # ── Hoodies ──────────────────────────────────────────────────────────────
    {
        "name": "Commit & Chill Hoodie",
        "description": "Ultra-soft 340g fleece hoodie. Kangaroo pocket, ribbed cuffs. Perfect for late-night debugging sessions.",
        "price": 79.90,
        "category": "Hoodies",
        "image_url": "https://images.unsplash.com/photo-1556821840-3a63f15732ce?w=500&q=80",
        "stock": 45,
    },
    {
        "name": "Dark Mode Pullover",
        "description": "All-black minimalist hoodie with subtle Dark Mode embroidery on the chest. Your IDE-inspired wardrobe starts here.",
        "price": 84.90,
        "category": "Hoodies",
        "image_url": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=500&q=80",
        "stock": 30,
    },
    {
        "name": "Merge Conflict Zip-Up",
        "description": "Full-zip heavyweight hoodie in heather grey. Two front pockets, YKK zipper. Wear it when you push to main.",
        "price": 89.90,
        "category": "Hoodies",
        "image_url": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=500&q=80",
        "stock": 22,
    },
    # ── T-Shirts ──────────────────────────────────────────────────────────────
    {
        "name": "Hello World Tee",
        "description": "Classic cut 100% organic cotton t-shirt. Chest print: 'Hello, World!' in Monospace. The first step.",
        "price": 34.90,
        "category": "T-Shirts",
        "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500&q=80",
        "stock": 80,
    },
    {
        "name": "Stack Overflow Tee",
        "description": "Slim-fit tee with a subtle 'Google it' back print. Because we've all been there.",
        "price": 32.90,
        "category": "T-Shirts",
        "image_url": "https://images.unsplash.com/photo-1503341504253-dff4815485f1?w=500&q=80",
        "stock": 65,
    },
    {
        "name": "It Works On My Machine Tee",
        "description": "Certified 100% organic. Unisex fit. The sentence that launched a thousand post-mortems.",
        "price": 34.90,
        "category": "T-Shirts",
        "image_url": "https://images.unsplash.com/photo-1527719327859-c6ce80353573?w=500&q=80",
        "stock": 55,
    },
    {
        "name": "Root Access Tee",
        "description": "Oversized drop-shoulder tee. '#!' print on the back. For those who own their machines — and their style.",
        "price": 38.90,
        "category": "T-Shirts",
        "image_url": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=500&q=80",
        "stock": 40,
    },
    # ── Accessories ───────────────────────────────────────────────────────────
    {
        "name": "Rubber Duck Debug Kit",
        "description": "Genuine rubber duck + TechStyle tote bag. The OG debugging tool, now with fashion credentials.",
        "price": 19.90,
        "category": "Accessories",
        "image_url": "https://images.unsplash.com/photo-1515041219749-89347f83291a?w=500&q=80",
        "stock": 120,
    },
    {
        "name": "Mechanical Keyboard Wrist Rest",
        "description": "Memory foam wrist rest, 45cm. Keeps your wrists happy during 10-hour hackathons.",
        "price": 29.90,
        "category": "Accessories",
        "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500&q=80",
        "stock": 60,
    },
    {
        "name": "Git Blame Cap",
        "description": "Structured 6-panel cap, adjustable strap. Embroidered 'git blame' on the front. Wear your version history.",
        "price": 27.90,
        "category": "Accessories",
        "image_url": "https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=500&q=80",
        "stock": 35,
    },
    {
        "name": "TechStyle Laptop Sleeve 15\"",
        "description": "Neoprene laptop sleeve with soft inner lining. Fits 15\" MacBook Pro. Logo embossed on front.",
        "price": 44.90,
        "category": "Accessories",
        "image_url": "https://images.unsplash.com/photo-1547394765-185e1e68f34e?w=500&q=80",
        "stock": 28,
    },
    # ── Jackets ───────────────────────────────────────────────────────────────
    {
        "name": "DevOps Field Jacket",
        "description": "Water-resistant shell jacket with multiple pockets for all your devices. Ships code AND rain.",
        "price": 149.90,
        "category": "Jackets",
        "image_url": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500&q=80",
        "stock": 15,
    },
    {
        "name": "Cloud Native Bomber",
        "description": "Satin bomber jacket, embroidered infrastructure icons on the back. Enterprise grade, startup spirit.",
        "price": 129.90,
        "category": "Jackets",
        "image_url": "https://images.unsplash.com/photo-1520975954732-35dd22299614?w=500&q=80",
        "stock": 12,
    },
    {
        "name": "Kubernetes Puffer Vest",
        "description": "Lightweight puffer vest with hidden zip pockets. As scalable as your cluster. Available in navy and black.",
        "price": 99.90,
        "category": "Jackets",
        "image_url": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=500&q=80",
        "stock": 20,
    },
    # ── Pants ─────────────────────────────────────────────────────────────────
    {
        "name": "Agile Sprint Joggers",
        "description": "Premium tapered joggers with deep side pockets. Elastic waist, cuffed ankles. Built for two-week sprints.",
        "price": 69.90,
        "category": "Pants",
        "image_url": "https://images.unsplash.com/photo-1552902865-b72c031ac5ea?w=500&q=80",
        "stock": 38,
    },
    {
        "name": "Standby Sweatpants",
        "description": "Heavyweight lounge pants. Ribbed waistband and cuffs. For remote work days when pants are optional but style isn't.",
        "price": 59.90,
        "category": "Pants",
        "image_url": "https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=500&q=80",
        "stock": 42,
    },
    # ── Bags ──────────────────────────────────────────────────────────────────
    {
        "name": "Deploy Backpack 25L",
        "description": "25L daypack, dedicated 17\" laptop compartment, USB-A pass-through, reflective logo strip. Deploy yourself anywhere.",
        "price": 119.90,
        "category": "Bags",
        "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500&q=80",
        "stock": 18,
    },
    {
        "name": "Pipeline Tote",
        "description": "Heavy-duty canvas tote (10oz). Internal zip pocket. Screen-printed CI/CD pipeline graphic. For the conscious commuter.",
        "price": 24.90,
        "category": "Bags",
        "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?w=500&q=80",
        "stock": 75,
    },
    # ── Limited Edition ───────────────────────────────────────────────────────
    {
        "name": "404 Beanie",
        "description": "Ribbed knit beanie with woven '404' label. Limited run of 200 units. Style not found — until now.",
        "price": 24.90,
        "category": "Accessories",
        "image_url": "https://images.unsplash.com/photo-1576871337632-b9aef4c17ab9?w=500&q=80",
        "stock": 8,
    },
    {
        "name": "sudo make me a sandwich Longsleeve",
        "description": "Classic Unix humour on a premium cotton longsleeve. Back print. A conversation starter at every conference.",
        "price": 45.90,
        "category": "T-Shirts",
        "image_url": "https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=500&q=80",
        "stock": 50,
    },
]


def seed():
    db = sqlite3.connect(DATABASE)
    cur = db.cursor()

    # Ensure table exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT,
            image_url TEXT,
            stock INTEGER DEFAULT 100,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Clear existing products before re-seeding
    cur.execute("DELETE FROM products")

    for p in PRODUCTS:
        cur.execute(
            "INSERT INTO products (name, description, price, category, image_url, stock) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (p["name"], p["description"], p["price"], p["category"], p["image_url"], p["stock"]),
        )

    db.commit()
    db.close()
    print(f"Seeded {len(PRODUCTS)} products into {DATABASE}")


if __name__ == "__main__":
    seed()
