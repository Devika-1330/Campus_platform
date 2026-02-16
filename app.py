"""
Campus Platform - Lost & Found + Complaints Management
Flask backend with MySQL.
"""
import os
# Use PyMySQL on Windows if MySQLdb is not available
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import init_db, mysql_store

app = Flask(__name__)
app.config.from_object("config.Config")
init_db(app)

# Admin email for role check
ADMIN_EMAIL = "admin@campus.edu"


def login_required(f):
    from functools import wraps
    @wraps(f)
    def inner(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return inner


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def inner(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        if session.get("email") != ADMIN_EMAIL:
            flash("Admin access required.", "danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return inner


@app.route("/")
def index():
    if "user_id" in session:
        if session.get("email") == ADMIN_EMAIL:
            return redirect(url_for("admin_dashboard"))
        return redirect(url_for("user_dashboard"))
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        name = request.form.get("name", "").strip()
        if not email or not password or not name:
            flash("All fields are required.", "danger")
            return render_template("register.html")
        cur = mysql_store.connection.cursor()
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            flash("Email already registered.", "danger")
            cur.close()
            return render_template("register.html")
        hashed = generate_password_hash(password)
        cur.execute(
            "INSERT INTO users (email, password, name) VALUES (%s, %s, %s)",
            (email, hashed, name)
        )
        mysql_store.connection.commit()
        cur.close()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        if not email or not password:
            flash("Email and password are required.", "danger")
            return render_template("login.html")
        cur = mysql_store.connection.cursor()
        cur.execute("SELECT id, email, password, name FROM users WHERE email = %s", (email,))
        row = cur.fetchone()
        cur.close()
        if row and check_password_hash(row["password"], password):
            session["user_id"] = row["id"]
            session["email"] = row["email"]
            session["name"] = row["name"]
            flash(f"Welcome, {row['name']}!", "success")
            if row["email"] == ADMIN_EMAIL:
                return redirect(url_for("admin_dashboard"))
            return redirect(url_for("user_dashboard"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


# ---------- User: Lost & Found ----------
@app.route("/lost-found")
@login_required
def lost_found():
    cur = mysql_store.connection.cursor()
    cur.execute(
        "SELECT * FROM lost_items ORDER BY created_at DESC"
    )
    lost = cur.fetchall()
    cur.execute(
        "SELECT * FROM found_items ORDER BY created_at DESC"
    )
    found = cur.fetchall()
    cur.close()
    return render_template("lost_found.html", lost_items=lost, found_items=found)


@app.route("/report-lost", methods=["GET", "POST"])
@login_required
def report_lost():
    if request.method == "POST":
        item_name = request.form.get("item_name", "").strip()
        description = request.form.get("description", "").strip()
        location = request.form.get("location", "").strip()
        date_lost = request.form.get("date_lost", "").strip() or None
        contact = request.form.get("contact", "").strip()
        if not item_name:
            flash("Item name is required.", "danger")
            return render_template("report_lost.html")
        cur = mysql_store.connection.cursor()
        cur.execute(
            """INSERT INTO lost_items (user_id, item_name, description, location, date_lost, contact)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (session["user_id"], item_name, description, location, date_lost, contact)
        )
        mysql_store.connection.commit()
        cur.close()
        flash("Lost item reported successfully.", "success")
        return redirect(url_for("lost_found"))
    return render_template("report_lost.html")


@app.route("/report-found", methods=["GET", "POST"])
@login_required
def report_found():
    if request.method == "POST":
        item_name = request.form.get("item_name", "").strip()
        description = request.form.get("description", "").strip()
        location = request.form.get("location", "").strip()
        date_found = request.form.get("date_found", "").strip() or None
        contact = request.form.get("contact", "").strip()
        if not item_name:
            flash("Item name is required.", "danger")
            return render_template("report_found.html")
        cur = mysql_store.connection.cursor()
        cur.execute(
            """INSERT INTO found_items (user_id, item_name, description, location, date_found, contact)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (session["user_id"], item_name, description, location, date_found, contact)
        )
        mysql_store.connection.commit()
        cur.close()
        flash("Found item reported successfully.", "success")
        return redirect(url_for("lost_found"))
    return render_template("report_found.html")


# ---------- User: Complaints ----------
@app.route("/complaints")
@login_required
def complaints_list():
    cur = mysql_store.connection.cursor()
    cur.execute(
        "SELECT * FROM complaints WHERE user_id = %s ORDER BY created_at DESC",
        (session["user_id"],)
    )
    complaints = cur.fetchall()
    cur.close()
    return render_template("complaints_list.html", complaints=complaints)


@app.route("/complaints/raise", methods=["GET", "POST"])
@login_required
def raise_complaint():
    categories = ["Hostel", "Classroom", "Canteen", "Infrastructure", "Library", "Other"]
    if request.method == "POST":
        category = request.form.get("category", "").strip()
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        location = request.form.get("location", "").strip()
        if not category or not title or not description:
            flash("Category, title and description are required.", "danger")
            return render_template("raise_complaint.html", categories=categories)
        cur = mysql_store.connection.cursor()
        cur.execute(
            """INSERT INTO complaints (user_id, category, title, description, location, status)
               VALUES (%s, %s, %s, %s, %s, 'Pending')""",
            (session["user_id"], category, title, description, location)
        )
        mysql_store.connection.commit()
        cur.close()
        flash("Complaint submitted successfully. You can track its status from your dashboard.", "success")
        return redirect(url_for("complaints_list"))
    return render_template("raise_complaint.html", categories=categories)


# ---------- User Dashboard ----------
@app.route("/dashboard")
@login_required
def user_dashboard():
    cur = mysql_store.connection.cursor()
    cur.execute(
        "SELECT * FROM complaints WHERE user_id = %s ORDER BY created_at DESC LIMIT 5",
        (session["user_id"],)
    )
    recent_complaints = cur.fetchall()
    cur.execute(
        "SELECT COUNT(*) AS c FROM lost_items WHERE user_id = %s", (session["user_id"],)
    )
    lost_count = cur.fetchone()["c"]
    cur.execute(
        "SELECT COUNT(*) AS c FROM found_items WHERE user_id = %s", (session["user_id"],)
    )
    found_count = cur.fetchone()["c"]
    cur.execute(
        "SELECT COUNT(*) AS c FROM complaints WHERE user_id = %s", (session["user_id"],)
    )
    complaint_count = cur.fetchone()["c"]
    cur.close()
    return render_template(
        "user_dashboard.html",
        recent_complaints=recent_complaints,
        lost_count=lost_count,
        found_count=found_count,
        complaint_count=complaint_count,
    )


# ---------- Admin ----------
@app.route("/admin")
@admin_required
def admin_dashboard():
    cur = mysql_store.connection.cursor()
    cur.execute("SELECT COUNT(*) AS c FROM complaints WHERE status = 'Pending'")
    pending = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) AS c FROM complaints WHERE status = 'In Progress'")
    in_progress = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) AS c FROM complaints WHERE status = 'Resolved'")
    resolved = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) AS c FROM lost_items WHERE status = 'open'")
    lost_open = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) AS c FROM found_items WHERE status = 'open'")
    found_open = cur.fetchone()["c"]
    cur.execute(
        "SELECT * FROM complaints ORDER BY created_at DESC LIMIT 10"
    )
    recent_complaints = cur.fetchall()
    cur.execute("SELECT * FROM lost_items ORDER BY created_at DESC LIMIT 5")
    recent_lost = cur.fetchall()
    cur.execute("SELECT * FROM found_items ORDER BY created_at DESC LIMIT 5")
    recent_found = cur.fetchall()
    cur.close()
    return render_template(
        "admin_dashboard.html",
        pending=pending,
        in_progress=in_progress,
        resolved=resolved,
        lost_open=lost_open,
        found_open=found_open,
        recent_complaints=recent_complaints,
        recent_lost=recent_lost,
        recent_found=recent_found,
    )


@app.route("/admin/complaints")
@admin_required
def admin_complaints():
    cur = mysql_store.connection.cursor()
    cur.execute(
        """SELECT c.*, u.name AS user_name, u.email AS user_email
           FROM complaints c JOIN users u ON c.user_id = u.id
           ORDER BY c.created_at DESC"""
    )
    complaints = cur.fetchall()
    cur.close()
    return render_template("admin_complaints.html", complaints=complaints)


@app.route("/admin/complaints/<int:cid>/status", methods=["POST"])
@admin_required
def update_complaint_status(cid):
    status = request.form.get("status", "").strip()
    remark = request.form.get("admin_remark", "").strip()
    if status not in ("Pending", "In Progress", "Resolved"):
        flash("Invalid status.", "danger")
        return redirect(url_for("admin_complaints"))
    cur = mysql_store.connection.cursor()
    cur.execute(
        "UPDATE complaints SET status = %s, admin_remark = %s WHERE id = %s",
        (status, remark, cid)
    )
    mysql_store.connection.commit()
    cur.close()
    flash("Complaint status updated.", "success")
    return redirect(url_for("admin_complaints"))


@app.route("/admin/lost-found")
@admin_required
def admin_lost_found():
    cur = mysql_store.connection.cursor()
    cur.execute(
        "SELECT l.*, u.name AS user_name FROM lost_items l JOIN users u ON l.user_id = u.id ORDER BY l.created_at DESC"
    )
    lost = cur.fetchall()
    cur.execute(
        "SELECT f.*, u.name AS user_name FROM found_items f JOIN users u ON f.user_id = u.id ORDER BY f.created_at DESC"
    )
    found = cur.fetchall()
    cur.close()
    return render_template("admin_lost_found.html", lost_items=lost, found_items=found)


@app.route("/admin/lost-found/remove-lost/<int:lid>", methods=["POST"])
@admin_required
def admin_remove_lost(lid):
    cur = mysql_store.connection.cursor()
    cur.execute("DELETE FROM lost_items WHERE id = %s", (lid,))
    mysql_store.connection.commit()
    cur.close()
    flash("Lost item entry removed.", "success")
    return redirect(url_for("admin_lost_found"))


@app.route("/admin/lost-found/remove-found/<int:fid>", methods=["POST"])
@admin_required
def admin_remove_found(fid):
    cur = mysql_store.connection.cursor()
    cur.execute("DELETE FROM found_items WHERE id = %s", (fid,))
    mysql_store.connection.commit()
    cur.close()
    flash("Found item entry removed.", "success")
    return redirect(url_for("admin_lost_found"))


@app.route("/admin/lost-found/verify-lost/<int:lid>", methods=["POST"])
@admin_required
def admin_verify_lost(lid):
    cur = mysql_store.connection.cursor()
    cur.execute("UPDATE lost_items SET status = 'verified' WHERE id = %s", (lid,))
    mysql_store.connection.commit()
    cur.close()
    flash("Lost item marked as verified.", "success")
    return redirect(url_for("admin_lost_found"))


@app.route("/admin/lost-found/verify-found/<int:fid>", methods=["POST"])
@admin_required
def admin_verify_found(fid):
    cur = mysql_store.connection.cursor()
    cur.execute("UPDATE found_items SET status = 'verified' WHERE id = %s", (fid,))
    mysql_store.connection.commit()
    cur.close()
    flash("Found item marked as verified.", "success")
    return redirect(url_for("admin_lost_found"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
