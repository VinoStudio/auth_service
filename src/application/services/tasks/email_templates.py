from datetime import datetime


def generate_registration_html(user_data):
    """Generate HTML content for registration email"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #4a86e8; color: white; padding: 10px; text-align: center; }}
            .content {{ padding: 20px; border: 1px solid #ddd; }}
            .button {{ background-color: #4a86e8; color: white; padding: 10px 15px; 
                      text-decoration: none; border-radius: 4px; display: inline-block; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome, {user_data['username']}!</h1>
            </div>
            <div class="content">
                <p>Thank you for joining our platform. Your account has been created successfully.</p>
                <p>If you have any questions, feel free to contact our support team.</p>
            </div>
        </div>
    </body>
    </html>
    """


def generate_notification_html(
    email: str,
    verification_url: str | None,
    username: str | None,
    title: str,
    heading: str,
    message: str,
    button_text: str | None,
    expiration_note: str,
    security_note: str,
) -> str:
    """Generate stylish HTML for any notification email"""

    button_html = ""
    if verification_url and button_text:
        button_html = (
            f'<a href="{verification_url}" class="reset-button">{button_text}</a>'
        )

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background-color: #f9f9f9;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #ffffff;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                text-align: center;
                padding: 20px 0;
                border-bottom: 1px solid #eee;
            }}
            .header h1 {{
                color: #2c3e50;
                margin: 0;
                font-size: 24px;
            }}
            .content {{
                padding: 30px 20px;
                text-align: center;
            }}
            .reset-button {{
                display: inline-block;
                background-color: #3498db;
                color: white;
                text-decoration: none;
                padding: 12px 30px;
                border-radius: 4px;
                font-weight: bold;
                margin: 20px 0;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }}
            .reset-button:hover {{
                background-color: #2980b9;
            }}
            .security-note {{
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 4px;
                font-size: 14px;
                margin: 20px 0;
                border-left: 4px solid #ffc107;
                text-align: left;
            }}
            .footer {{
                margin-top: 30px;
                text-align: center;
                color: #7f8c8d;
                font-size: 12px;
                border-top: 1px solid #eee;
                padding-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{heading}</h1>
            </div>
            <div class="content">
                <p>Hello, {username}</p>
                <p>{message}</p>
                {button_html}
                {f'<p>{expiration_note}</p>' if expiration_note else ''}

                <div class="security-note">
                    <p><strong>Security Note:</strong> {security_note}</p>
                </div>
            </div>
            <div class="footer">
                <p>This is an automated message, please do not reply to this email.</p>
                <p>&copy; 2025 Your Company. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """


# Example for password reset
def generate_reset_password_html(
    email: str, reset_url: str, username: str | None
) -> str:
    return generate_notification_html(
        email=email,
        verification_url=reset_url,
        username=username,
        title="Reset Your Password",
        heading="Password Reset Request",
        message=f"We received a request to reset the password for your account: <strong>{email}</strong>",
        button_text="Reset Password",
        expiration_note="This link will expire in 15 minutes.",
        security_note="If you didn't request a password reset, please ignore this email or contact support if you have concerns about your account security.",
    )


# Example for email change
def generate_email_change_html(
    email: str, verification_url: str, username: str | None
) -> str:
    return generate_notification_html(
        email=email,
        verification_url=verification_url,
        username=username,
        title="Verify Your New Email Address",
        heading="Email Change Verification",
        message=f"We received a request to change your email address to: <strong>{email}</strong>",
        button_text="Verify Email Address",
        expiration_note="This link will expire in 24 hours.",
        security_note="If you didn't request this email change, please contact support immediately as someone may be attempting to access your account.",
    )


def generate_password_changed_html(
    email: str,
    username: str | None = None,
    timestamp: str | None = None,
) -> str:
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return generate_notification_html(
        email=email,
        verification_url=None,
        username=username,
        title="Password Changed",
        heading="Your Password Has Been Changed",
        message=f"The password for your account (<strong>{email}</strong>) was changed on {timestamp}.",
        button_text=None,
        expiration_note="",
        security_note="If you did not change your password, please contact our support team immediately or reset your password as your account may have been compromised.",
    )


def generate_email_changed_html(
    email: str,
    username: str | None = None,
    timestamp: str | None = None,
) -> str:
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return generate_notification_html(
        email=email,
        verification_url=None,
        username=username,
        title="Email Changed",
        heading="Your Email Has Been Changed",
        message=f"The email address of your account (<strong>{email}</strong>) was changed on {timestamp}.",
        button_text=None,
        expiration_note="",
        security_note="If you did not change your email address, please contact our support team immediately or reset your password as your account may have been compromised.",
    )
