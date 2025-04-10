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
