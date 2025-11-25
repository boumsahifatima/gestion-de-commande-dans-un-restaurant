from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from models import get_db_connection, init_db

app = Flask(__name__)

# Route pour la page d'accueil / menu
@app.route('/')
def menu():
    """Affiche la page du menu avec tous les articles disponibles"""
    conn = get_db_connection()
    
    # Récupère tous les articles du menu
    menu_items = conn.execute('SELECT * FROM menu_items').fetchall()
    
    conn.close()
    
    # Rend le template menu.html en passant les articles
    return render_template('menu.html', menu_items=menu_items)

# Route pour passer commande
@app.route('/order', methods=['GET', 'POST'])
def order():
    """Gère l'affichage et le traitement du formulaire de commande"""
    
    if request.method == 'POST':
        # Récupération des données du formulaire
        customer_name = request.form['customer_name']
        selected_items = request.form.getlist('menu_items')
        quantities = request.form.getlist('quantities')
        
        conn = get_db_connection()
        
        # Calcul du total de la commande
        total = 0
        for i, item_id in enumerate(selected_items):
            # Récupère le prix de l'article
            menu_item = conn.execute(
                'SELECT price FROM menu_items WHERE id = ?', (item_id,)
            ).fetchone()
            
            quantity = int(quantities[i])
            total += menu_item['price'] * quantity
        
        # Création de la commande
        cursor = conn.execute(
            'INSERT INTO orders (customer_name, total) VALUES (?, ?)',
            (customer_name, total)
        )
        order_id = cursor.lastrowid
        
        # Ajout des articles à la commande
        for i, item_id in enumerate(selected_items):
            quantity = int(quantities[i])
            conn.execute(
                'INSERT INTO order_items (order_id, menu_item_id, quantity) VALUES (?, ?, ?)',
                (order_id, item_id, quantity)
            )
        
        conn.commit()
        conn.close()
        
        # Redirection vers la page d'administration après commande
        return redirect(url_for('admin'))
    
    # GET request : affiche le formulaire de commande
    conn = get_db_connection()
    menu_items = conn.execute('SELECT * FROM menu_items').fetchall()
    conn.close()
    
    return render_template('order.html', menu_items=menu_items)

# Route pour l'interface d'administration
@app.route('/admin')
def admin():
    """Affiche l'interface admin avec toutes les commandes"""
    conn = get_db_connection()
    
    # Récupère toutes les commandes avec leurs articles
    orders = conn.execute('''
        SELECT o.*, 
               GROUP_CONCAT(m.name || ' (x' || oi.quantity || ')') as items
        FROM orders o
        LEFT JOIN order_items oi ON o.id = oi.order_id
        LEFT JOIN menu_items m ON oi.menu_item_id = m.id
        GROUP BY o.id
        ORDER BY o.created_at DESC
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin.html', orders=orders)

# Route pour mettre à jour le statut d'une commande
@app.route('/update_status/<int:order_id>/<new_status>')
def update_status(order_id, new_status):
    """Met à jour le statut d'une commande"""
    conn = get_db_connection()
    
    conn.execute(
        'UPDATE orders SET status = ? WHERE id = ?',
        (new_status, order_id)
    )
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin'))

# Supprimer une commande
@app.route('/delete_order/<int:order_id>')
def delete_order(order_id):
    """Supprime une commande et ses articles associés"""
    conn = get_db_connection()
    
    # Supprime d'abord les articles de la commande (clé étrangère)
    conn.execute('DELETE FROM order_items WHERE order_id = ?', (order_id,))
    
    # Puis supprime la commande elle-même
    conn.execute('DELETE FROM orders WHERE id = ?', (order_id,))
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin'))

if __name__ == '__main__':
    # Initialise la base de données au démarrage
    init_db()
    # Lance l'application en mode debug
    app.run(debug=True)