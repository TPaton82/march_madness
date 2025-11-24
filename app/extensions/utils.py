from google.cloud import secretmanager
import os
import hashlib
from functools import wraps
from flask import redirect, url_for, session, current_app

def get_cloud_secret(secret_name):
    client = secretmanager.SecretManagerServiceClient()
    response = client.access_secret_version(name=f"projects/168510284961/secrets/{secret_name}/versions/latest")
    return response.payload.data.decode("UTF-8")


def create_secure_password(password, secret_key, hash_algo="sha256", iterations=100000):
    salt = os.urandom(16)

    hash_value = hashlib.pbkdf2_hmac(
        hash_algo,
        password.encode('utf-8') + secret_key.encode('utf-8'),
        salt,
        iterations
    )

    password_hash = salt + hash_value

    return password_hash[:16], password_hash[16:], hash_algo, iterations

def logged_in(func):
    @wraps(func)
    def check_logged_in():
        # Only show the page if user is logged in
        if 'loggedin' in session:
            return func()

        # User is not loggedin so redirect to login page
        return redirect('/login')

    return check_logged_in


def get_team_logo(team_name):
    """Return the static URL for team logo, preferring SVG, falling back to PNG."""
    svg_path = os.path.join(current_app.static_folder, "images/team_logos", f"{team_name}.svg")
    png_path = os.path.join(current_app.static_folder, "images/team_logos", f"{team_name}.png")

    if os.path.exists(svg_path):
        return url_for("static", filename=f"images/team_logos/{team_name}.svg")

    elif os.path.exists(png_path):
        return url_for("static", filename=f"images/team_logos/{team_name}.png")

    else:
        return url_for("static", filename="images/team_logos/placeholder.png")