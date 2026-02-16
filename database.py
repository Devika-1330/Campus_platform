"""Database connection and initialization."""
from flask import g
import mysql.connector


class _DictConnection:
    """Wrapper so .cursor() returns dict-like rows (like Flask-MySQLdb DictCursor)."""
    def __init__(self, conn):
        self._conn = conn

    def cursor(self):
        return self._conn.cursor(dictionary=True)

    def commit(self):
        return self._conn.commit()

    def close(self):
        return self._conn.close()


class _MySQLStore:
    @property
    def connection(self):
        return g.mysql_conn


mysql_store = _MySQLStore()


def init_db(app):
    """Initialize MySQL with app and create tables if they don't exist."""
    app.config["MYSQL_HOST"] = app.config.get("MYSQL_HOST", "localhost")
    app.config["MYSQL_USER"] = app.config.get("MYSQL_USER", "root")
    app.config["MYSQL_PASSWORD"] = app.config.get("MYSQL_PASSWORD", "")
    app.config["MYSQL_DB"] = app.config.get("MYSQL_DB", "campus_platform")
    create_tables(app)

    @app.before_request
    def _before_request():
        g.mysql_conn = _DictConnection(mysql.connector.connect(
            host=app.config["MYSQL_HOST"],
            user=app.config["MYSQL_USER"],
            password=app.config["MYSQL_PASSWORD"],
            database=app.config["MYSQL_DB"],
        ))

    @app.teardown_appcontext
    def _teardown(exception=None):
        if "mysql_conn" in g:
            g.mysql_conn.close()

    return mysql_store


def get_connection(app):
    """Get raw MySQL connection for DDL (CREATE DATABASE / TABLE)."""
    return mysql.connector.connect(
        host=app.config.get("MYSQL_HOST", "localhost"),
        user=app.config.get("MYSQL_USER", "root"),
        password=app.config.get("MYSQL_PASSWORD", ""),
    )


def create_tables(app):
    """Create database and tables if they don't exist."""
    conn = get_connection(app)
    cur = conn.cursor()
    db_name = app.config.get("MYSQL_DB", "campus_platform")
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
    cur.execute(f"USE `{db_name}`")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS lost_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            item_name VARCHAR(255) NOT NULL,
            description TEXT,
            location VARCHAR(255),
            date_lost DATE,
            contact VARCHAR(255),
            status VARCHAR(50) DEFAULT 'open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS found_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            item_name VARCHAR(255) NOT NULL,
            description TEXT,
            location VARCHAR(255),
            date_found DATE,
            contact VARCHAR(255),
            status VARCHAR(50) DEFAULT 'open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            category VARCHAR(100) NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            location VARCHAR(255),
            status VARCHAR(50) DEFAULT 'Pending',
            admin_remark TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    # Predefined admin (password hashed with Werkzeug for demo)
    cur.execute("SELECT id FROM users WHERE email = 'admin@campus.edu'")
    if cur.fetchone() is None:
        from werkzeug.security import generate_password_hash
        admin_hash = generate_password_hash("admin123")
        cur.execute(
            "INSERT INTO users (email, password, name) VALUES (%s, %s, %s)",
            ("admin@campus.edu", admin_hash, "Campus Admin")
        )
    conn.commit()
    cur.close()
    conn.close()
