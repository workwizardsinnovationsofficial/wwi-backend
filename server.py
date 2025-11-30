from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

@app.route("/send-email", methods=["POST"])
def send_email():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    if not all([name, email, message]):
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    subject = f"New Contact Message from {name}"
    body = f"""
    You have received a new contact form submission:

    Name: {name}
    Email: {email}

    Message:
    {message}
    """

    try:
        msg = MIMEMultipart()
        msg["From"] = f"{name} via Contact Form <{EMAIL_USER}>"
        msg["To"] = RECEIVER_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        print("🔐 Logging in as:", EMAIL_USER)
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)

        print("✅ Email sent successfully")
        return jsonify({"status": "success", "message": "Email sent successfully"}), 200

    except smtplib.SMTPAuthenticationError as e:
        print("❌ SMTP Authentication failed:", e)
        return jsonify({
            "status": "error",
            "message": "Invalid Gmail App Password or email. Please check .env."
        }), 500
    except Exception as e:
        print("❌ General error:", e)
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
