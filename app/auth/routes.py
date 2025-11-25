import hashlib
import re
from flask import Blueprint, render_template, request, redirect, session, current_app
from app.extensions.models import User
from app.extensions.db import db
from app.extensions.utils import create_secure_password, logged_in

auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/')
@logged_in
def landing_page():
    return redirect("/bracket")


def get_user(name):
    """Fetch a user by name. Returns None if user does not exist."""
    user = User.query.filter_by(name=name).first()
    return user


def create_user(name, password_hash, salt, hash_algo, iterations):
    """Create a new user."""
    new_user = User(
        name=name,
        password_hash=password_hash,
        salt=salt,
        hash_algo=hash_algo,
        iterations=iterations
    )

    db.session.add(new_user)
    db.session.commit()


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    msg = ""

    if request.method == "POST" and "name" in request.form and "password" in request.form:
        # Get the name and password
        name = request.form['name']
        password = request.form['password']

        # If account already exists or not a valid name, show error message
        user = get_user(name)

        if user is not None:
            msg = f"Account with that name already exists!"

        elif not re.match(r'[A-Za-z]+', name):
            msg = 'Name must contain only characters, no numbers or special characters!'

        else:
            # Create hash of password for storage
            salt, password_hash, hash_algo, iterations = create_secure_password(password, current_app.secret_key)

            # User doesn't exist and the form data is valid, so create the new user
            create_user(name, password_hash, salt, hash_algo, iterations)
            return render_template('login.html', msg='You have successfully registered!')

    elif request.method == 'POST':
        msg = 'Please input Name and Password!'

    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    msg = ""

    if request.method == "POST" and "name" in request.form and "password" in request.form:
        # Get the name and password
        name = request.form['name']
        password = request.form['password']

        # Check if user exists
        user = get_user(name)

        if user is None:
            # Account doesn't exist
            msg = 'Incorrect Name / Password!'
        else:
            # Recompute hash from user entered password
            password_hash = hashlib.pbkdf2_hmac(
                user.hash_algo,
                password.encode('utf-8') + current_app.secret_key.encode('utf-8'),
                user.salt,
                user.iterations
            )

            # Compare hashes
            if password_hash == user.password_hash:
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['user_id'] = user.user_id

                # Redirect to leaderboard
                return redirect("/bracket")
            else:
                msg = 'Incorrect Name / Password!'

    return render_template("login.html", msg=msg)


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
