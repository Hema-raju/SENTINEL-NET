from flask import Flask, render_template

from api import api
from database import initialize_database
from console_config import HOST, PORT, DEBUG


app = Flask(__name__)

# Register the API routes
app.register_blueprint(api)


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/")
def dashboard():

    return render_template(
        "dashboard.html"
    )


# ============================================================
# HISTORY
# ============================================================

@app.route("/history")
def history():

    return render_template(
        "history.html"
    )

# ============================================================
# PROCESSES
# ============================================================

@app.route("/processes")
def processes():

    return render_template(
        "processes.html"
    )

# ============================================================
# NETWORK
# ============================================================

@app.route("/network")
def network():

    return render_template(
        "network.html"
    )

# ============================================================
# REPORTS
# ============================================================

@app.route("/reports")
def reports():

    return render_template(
        "reports.html"
    )

# ============================================================
# START SECURITY CONSOLE
# ============================================================

if __name__ == "__main__":

    initialize_database()

    print("=" * 70)
    print("SENTINELNET SECURITY CONSOLE")
    print("=" * 70)

    print(
        f"Server: http://{HOST}:{PORT}"
    )

    print()

    print("Available endpoints:")

    print(
        f"  http://{HOST}:{PORT}/"
    )

    print(
        f"  http://{HOST}:{PORT}/history"
    )

    print(
        f"  http://{HOST}:{PORT}/api/status"
    )

    print(
        f"  http://{HOST}:{PORT}/api/agent/data"
    )

    print()

    print(
        "Press CTRL+C to stop the Security Console."
    )

    print("=" * 70)

    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG
    )