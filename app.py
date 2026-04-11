from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# ✅ STRICT environment-based configuration (NO hardcoding)
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
}

# ✅ Safe DB connection
def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print("DB CONNECTION ERROR:", e)
        return None

# ✅ Helper
def task_to_dict(row):
    return {
        'id': row[0],
        'title': row[1],
        'description': row[2] or '',
        'status': row[3],
        'priority': row[4],
        'created_at': row[5].strftime('%Y-%m-%d %H:%M') if row[5] else '',
        'updated_at': row[6].strftime('%Y-%m-%d %H:%M') if row[6] else '',
    }

# ── Routes ─────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

# 🔹 GET all tasks
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'DB connection failed'}), 500

    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, description, status, priority, created_at, updated_at
        FROM tasks
        ORDER BY created_at DESC
    """)
    tasks = [task_to_dict(row) for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return jsonify({'tasks': tasks, 'count': len(tasks)})

# 🔹 GET single task
@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'DB connection failed'}), 500

    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, description, status, priority, created_at, updated_at
        FROM tasks WHERE id = %s
    """, (task_id,))
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if not row:
        return jsonify({'error': 'Task not found'}), 404

    return jsonify(task_to_dict(row))

# 🔹 CREATE
@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()

    title = (data.get('title') or '').strip()
    if not title:
        return jsonify({'error': 'Title is required'}), 400

    description = (data.get('description') or '').strip()
    status = data.get('status', 'todo')
    priority = data.get('priority', 'medium')

    conn = get_connection()
    if not conn:
        return jsonify({'error': 'DB connection failed'}), 500

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (title, description, status, priority)
        VALUES (%s, %s, %s, %s)
    """, (title, description, status, priority))

    conn.commit()
    task_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({'message': 'Task created', 'id': task_id}), 201

# 🔹 UPDATE
@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()

    conn = get_connection()
    if not conn:
        return jsonify({'error': 'DB connection failed'}), 500

    cursor = conn.cursor()

    cursor.execute("SELECT id FROM tasks WHERE id = %s", (task_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Task not found'}), 404

    fields = []
    values = []

    for key in ['title', 'description', 'status', 'priority']:
        if key in data:
            fields.append(f"{key} = %s")
            values.append(data[key])

    if not fields:
        cursor.close()
        conn.close()
        return jsonify({'error': 'No fields to update'}), 400

    values.append(task_id)

    query = f"UPDATE tasks SET {', '.join(fields)} WHERE id = %s"
    cursor.execute(query, values)

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({'message': 'Task updated'})

# 🔹 DELETE
@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'DB connection failed'}), 500

    cursor = conn.cursor()

    cursor.execute("SELECT id FROM tasks WHERE id = %s", (task_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Task not found'}), 404

    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({'message': 'Task deleted'})

# 🔹 STATS
@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'DB connection failed'}), 500

    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            COUNT(*) AS total,
            SUM(status = 'todo'),
            SUM(status = 'in_progress'),
            SUM(status = 'done')
        FROM tasks
    """)

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    return jsonify({
        'total': row[0] or 0,
        'todo': row[1] or 0,
        'in_progress': row[2] or 0,
        'done': row[3] or 0
    })

# ── ENTRY POINT ────────────────────────────────────

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)