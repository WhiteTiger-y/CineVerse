import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

# --- Brevo API Configuration ---
# This part sets up the connection to your Brevo account
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = os.getenv('BREVO_API_KEY')
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
# --------------------------------

def send_welcome_email(to_email: str, first_name: str, username: str):
    """Sends a welcome email to a new user using Brevo."""
    sender_email = os.getenv("SENDER_EMAIL")
    if not sender_email:
        print("Error: SENDER_EMAIL not set in .env")
        return

    subject = "Welcome to CineVerse AI!"
    html_content = f"""
    <div style="font-family: sans-serif; padding: 20px; color: #333;">
        <h2>Welcome to CineVerse AI, {first_name}!</h2>
        <p>Your account has been created successfully. Your username is: <strong>{username}</strong></p>
        <p>You can now log in and start discovering your next favorite movie.</p>
        <p><em>The CineVerse AI Team</em></p>
    </div>
    """
    
    sender = {"name": "CineVerse AI", "email": sender_email}
    to = [{"email": to_email, "name": first_name}]
    
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to, 
        sender=sender, 
        subject=subject, 
        html_content=html_content
    )

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(f"Welcome email sent to {to_email} via Brevo. Response: {api_response}")
    except ApiException as e:
        print(f"Error sending welcome email to {to_email} via Brevo: {e}")

def send_password_reset_email(to_email: str, token: str):
    """Sends a password reset email to a user using Brevo."""
    sender_email = os.getenv("SENDER_EMAIL")
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    reset_url = f"{frontend_url}/reset-password?token={token}"

    subject = "Your CineVerse AI Password Reset Request"
    html_content = f"""
    <div style="font-family: sans-serif; padding: 20px; color: #333;">
        <h2>Password Reset Request</h2>
        <p>We received a request to reset your password. Click the link below to set a new password:</p>
        <a href="{reset_url}" style="display: inline-block; padding: 10px 20px; background-color: #7c3aed; color: #ffffff; text-decoration: none; border-radius: 5px;">
            Reset Your Password
        </a>
        <p>This link will expire in 1 hour.</p>
        <p>If you did not request a password reset, please ignore this email.</p>
        <p><em>The CineVerse AI Team</em></p>
    </div>
    """

    sender = {"name": "CineVerse AI", "email": sender_email}
    to = [{"email": to_email}]
    
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to, 
        sender=sender, 
        subject=subject, 
        html_content=html_content
    )

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(f"Password reset email sent to {to_email} via Brevo. Response: {api_response}")
    except ApiException as e:
        print(f"Error sending password reset email to {to_email} via Brevo: {e}")