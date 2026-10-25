from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from backend.models.user import UserModel

auth_bp = Blueprint("auth", __name__, url_prefix="")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html", name=name, email=email)

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "warning")
            return render_template("register.html", name=name, email=email)

        try:
            user = UserModel.create_user(name, email, password)
            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]
            session["user_role"] = "student"

            flash(f"Welcome, {user['name']}! Student registration successful.", "success")
            return redirect(url_for("dashboard_view"))
        except ValueError as e:
            flash(str(e), "danger")
            return render_template("register.html", name=name, email=email)
        except Exception as e:
            flash(f"An unexpected error occurred: {str(e)}", "danger")
            return render_template("register.html", name=name, email=email)

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return render_template("login.html", email=email)

        email_clean = email.lower()

        # 1. Administrator dedicated authentication
        if UserModel.is_admin_email(email_clean):
            user = UserModel.find_by_email(email_clean)
            if not user or not UserModel.verify_password(user, password):
                flash("Invalid Administrator email or password.", "danger")
                return render_template("login.html", email=email)

            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user.get("name", "Course Instructor")
            session["user_email"] = "admin@gmail.com"
            session["user_role"] = "admin"

            flash(f"Welcome, Administrator! Logged into Instructor & Course Admin Portal.", "success")
            return redirect(url_for("admin_view"))

        # 2. Student authentication with own personal email and password
        user = UserModel.find_by_email(email_clean)
        if not user or not UserModel.verify_password(user, password):
            flash("Invalid email address or password. Please verify your credentials or register a new account.", "danger")
            return render_template("login.html", email=email)

        session.clear()
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        session["user_email"] = user["email"]
        session["user_role"] = "student"

        # Record student login activity in persistent database
        try:
            UserModel.record_login(user["id"])
        except Exception:
            pass

        flash(f"Welcome back, {user['name']}!", "success")
        return redirect(url_for("dashboard_view"))

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))

@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        code = request.form.get("code", "").strip()
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        # If user submitted the reset form
        if code and new_password:
            if new_password != confirm_password:
                flash("Passwords do not match.", "danger")
                return render_template("forgot_password.html", step=2, email=email, code=code)
            try:
                UserModel.reset_password(email, code, new_password)
                flash("Password reset successfully! Please sign in with your new password.", "success")
                return redirect(url_for("auth.login"))
            except ValueError as e:
                flash(str(e), "danger")
                return render_template("forgot_password.html", step=2, email=email, code=code)

        # If user submitted step 1 (request code)
        if not email:
            flash("Please enter your registered email address.", "danger")
            return render_template("forgot_password.html", step=1)

        res = UserModel.create_password_reset_code(email)
        if not res:
            flash("No registered account found with that email address. Please register or verify spelling.", "warning")
            return render_template("forgot_password.html", step=1, email=email)

        flash(f"A 6-digit recovery code has been generated for {email}. (Academic Demo Code: {res['code']})", "info")
        return render_template("forgot_password.html", step=2, email=email, demo_code=res['code'])

    return render_template("forgot_password.html", step=1)

@auth_bp.route("/api/auth/forgot-password/request", methods=["POST"])
def api_forgot_password_request():
    data = request.get_json(silent=True) or request.form
    email = data.get("email", "").strip().lower()
    if not email:
        return jsonify({"success": False, "message": "Email address is required."}), 400

    res = UserModel.create_password_reset_code(email)
    if not res:
        return jsonify({
            "success": False,
            "message": "No registered account found with this email address. Please check spelling or register."
        }), 404

    return jsonify({
        "success": True,
        "message": f"6-digit recovery code generated for {email}.",
        "email": email,
        "demo_code": res["code"],
        "expires_in_minutes": res["expires_in_minutes"]
    })

@auth_bp.route("/api/auth/forgot-password/verify-reset", methods=["POST"])
def api_forgot_password_verify_reset():
    data = request.get_json(silent=True) or request.form
    email = data.get("email", "").strip().lower()
    code = data.get("code", "").strip()
    new_password = data.get("new_password", "")
    confirm_password = data.get("confirm_password", "")

    if not email or not code or not new_password:
        return jsonify({"success": False, "message": "Email, verification code, and new password are required."}), 400

    if new_password != confirm_password:
        return jsonify({"success": False, "message": "New passwords do not match."}), 400

    if len(new_password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters long."}), 400

    try:
        UserModel.reset_password(email, code, new_password)
        return jsonify({
            "success": True,
            "message": "Password successfully reset! You can now sign in with your new credentials."
        })
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {str(e)}"}), 500

@auth_bp.route("/api/auth/me")
def current_user_api():
    if "user_id" in session:
        return jsonify({
            "authenticated": True,
            "user": {
                "id": session.get("user_id"),
                "name": session.get("user_name"),
                "email": session.get("user_email"),
                "role": session.get("user_role", "student")
            }
        })
    return jsonify({"authenticated": False, "user": None}), 401
