import sqlite3
from datetime import datetime

# Connexion à la base SQLite
def get_db_connection():
    """Établit une connexion à la base de données SQLite"""
    conn = sqlite3.connect('restaurant.db')
    conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par nom
    return conn

def init_db():
    """Initialise la base de données avec les tables nécessaires"""
    conn = get_db_connection()
    
    # Table des articles du menu
    conn.execute('''
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT
        )
    ''')
    
    # Table des commandes
    conn.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            total REAL DEFAULT 0,
            status TEXT DEFAULT 'en attente',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table des éléments de commande (relation many-to-many)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            menu_item_id INTEGER,
            quantity INTEGER DEFAULT 1,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (menu_item_id) REFERENCES menu_items (id)
        )
    ''')
    
    # Insertion de données de démonstration pour le menu
    menu_items = [
        ('Pizza Margherita', 12.50, 'Tomate, mozzarella, basilic'),
        ('Pasta Carbonara', 14.00, 'Pâtes, œuf, pancetta, parmesan'),
        ('Salade César', 9.50, 'Laitue, croûtons, parmesan, sauce césar'),
        ('Tiramisu', 6.00, 'Dessert italien au café')
    ]
    
    # Vérifie si le menu est vide avant d'insérer
    existing_items = conn.execute('SELECT COUNT(*) as count FROM menu_items').fetchone()['count']
    if existing_items == 0:
        conn.executemany(
            'INSERT INTO menu_items (name, price, description) VALUES (?, ?, ?)',
            menu_items
        )
    
    conn.commit()
    conn.close()