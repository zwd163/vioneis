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
        # 打印调试信息
        logger.info(f"Attempting to send password reset email to {user_email}")
        logger.info(f"Email settings: HOST={settings.EMAIL_HOST}, PORT={settings.EMAIL_PORT}, USER={settings.EMAIL_HOST_USER}")

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

        # 尝试使用更简单的方式发送邮件
        try:
            # 先尝试使用原始方式
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user_email],
                html_message=html_message,
                fail_silently=False
            )
            logger.info(f"Email sent successfully using send_mail")
        except Exception as e:
            logger.error(f"Error using send_mail: {str(e)}")

            # 如果失败，尝试使用更低级别的方式
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            try:
                # 创建multipart消息
                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = settings.DEFAULT_FROM_EMAIL
                msg['To'] = user_email

                # 添加纯文本和HTML部分
                part1 = MIMEText(plain_message, 'plain')
                part2 = MIMEText(html_message, 'html')
                msg.attach(part1)
                msg.attach(part2)

                # Print email settings
                logger.info(f'Email settings:')
                logger.info(f'  EMAIL_BACKEND: {settings.EMAIL_BACKEND}')
                logger.info(f'  EMAIL_HOST: {settings.EMAIL_HOST}')
                logger.info(f'  EMAIL_PORT: {settings.EMAIL_PORT}')
                logger.info(f'  EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}')
                logger.info(f'  EMAIL_USE_SSL: {getattr(settings, "EMAIL_USE_SSL", False)}')
                logger.info(f'  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
                logger.info(f'  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}')



                # 连接到SMTP服务器
                if settings.EMAIL_USE_SSL:
                    server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
                else:
                    server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
                server.ehlo()
                if settings.EMAIL_USE_TLS:
                    server.starttls()
                server.ehlo()
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

                # 发送邮件
                server.sendmail(settings.DEFAULT_FROM_EMAIL, [user_email], msg.as_string())
                server.quit()

                logger.info(f"Email sent successfully using smtplib")
            except Exception as inner_e:
                logger.error(f"Error using smtplib: {str(inner_e)}")
                raise inner_e

        logger.info(f"Password reset email sent to {user_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send password reset email to {user_email}: {str(e)}")
        return False
