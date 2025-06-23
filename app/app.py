from flask import Flask, render_template, request, redirect, url_for
import psycopg2, os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS')
    )

# 🔸 Landing page
@app.route('/')
def welcome():
    return render_template('landing.html')

# 🔹 Daftar wishlist (dipindah ke /wishlist)
@app.route('/wishlist')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM wishlist")
    items = cur.fetchall()
    conn.close()
    return render_template('index.html', items=items)

# 🔹 Tambah item
@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    brand = request.form['brand']
    image = request.form['image'] or 'default.jpg'
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO wishlist (name, brand, image) VALUES (%s, %s, %s)", (name, brand, image))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# 🔹 Edit item
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        name  = request.form['name']
        brand = request.form['brand']
        image = request.form['image'] or 'default.jpg'

        cur.execute("""
            UPDATE wishlist
            SET name = %s,
                brand = %s,
                image = %s
            WHERE id = %s
        """, (name, brand, image, id))

        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    # GET → tampilkan form
    cur.execute("SELECT * FROM wishlist WHERE id=%s", (id,))
    item = cur.fetchone()
    conn.close()
    return render_template('edit.html', item=item)


# 🔹 Hapus item
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM wishlist WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# 🔹 Dashboard statistik
@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    cur = conn.cursor()

    # Total item
    cur.execute("SELECT COUNT(*) FROM wishlist")
    total_items = cur.fetchone()[0]

    # Statistik per brand
    cur.execute("""
        SELECT brand, COUNT(*)
        FROM wishlist
        GROUP BY brand
        ORDER BY COUNT(*) DESC
    """)
    brand_stats = cur.fetchall()

    conn.close()
    return render_template('dashboard.html', total_items=total_items, brand_stats=brand_stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
