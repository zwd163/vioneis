from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger('django')

def send_password_reset_email(user_email, username, reset_link):
    """
    Send a password reset email to the user

    Args:
        user_email (str): The user's email address
        username (str): The user's username
        reset_link (str): The password reset link

    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    try:
        subject = 'GreaterWMS Password Reset'

        # Create HTML message
        html_message = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Password Reset</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #4285f4;
                    color: white;
                    padding: 10px 20px;
                    text-align: center;
                }}
                .content {{
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-top: none;
                }}
                .button {{
                    display: inline-block;
                    background-color: #4285f4;
                    color: white;
                    text-decoration: none;
                    padding: 10px 20px;
                    border-radius: 4px;
                    margin: 20px 0;
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 12px;
                    color: #777;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>GreaterWMS Password Reset</h1>
            </div>
            <div class="content">
                <p>Hello {username},</p>
                <p>We received a request to reset your password for your GreaterWMS account. If you didn't make this request, you can ignore this email.</p>
                <p>To reset your password, please click the button below:</p>
                <p style="text-align: center;">
                    <a href="{reset_link}" class="button">Reset Password</a>
                </p>
                <p>Or copy and paste the following link into your browser:</p>
                <p>{reset_link}</p>
                <p>This link will expire in 24 hours.</p>
                <p>Thank you,<br>The GreaterWMS Team</p>
            </div>
            <div class="footer">
                <p>This is an automated email, please do not reply.</p>
            </div>
        </body>
        </html>
        '''

        # Create plain text message
        plain_message = f'''
        Hello {username},

        We received a request to reset your password for your GreaterWMS account. If you didn't make this request, you can ignore this email.

        To reset your password, please visit the following link:
        {reset_link}

        This link will expire in 24 hours.

        Thank you,
        The GreaterWMS Team
        '''

        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False
        )

        logger.info(f"Password reset email sent to {user_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send password reset email to {user_email}: {str(e)}")
        return False
