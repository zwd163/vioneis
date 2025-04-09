from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.mail import send_mail
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger('django')

class Command(BaseCommand):
    help = 'Test email sending functionality'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email address to send test email to')
        parser.add_argument('--method', type=str, default='both', choices=['django', 'smtp', 'both'], 
                            help='Method to use for sending email (django, smtp, or both)')

    def handle(self, *args, **options):
        email = options['email']
        method = options['method']
        
        self.stdout.write(self.style.SUCCESS(f'Testing email sending to {email} using method: {method}'))
        
        # Print email settings
        self.stdout.write(f'Email settings:')
        self.stdout.write(f'  EMAIL_BACKEND: {settings.EMAIL_BACKEND}')
        self.stdout.write(f'  EMAIL_HOST: {settings.EMAIL_HOST}')
        self.stdout.write(f'  EMAIL_PORT: {settings.EMAIL_PORT}')
        self.stdout.write(f'  EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}')
        self.stdout.write(f'  EMAIL_USE_SSL: {getattr(settings, "EMAIL_USE_SSL", False)}')
        self.stdout.write(f'  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
        self.stdout.write(f'  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}')
        
        subject = 'vioneip Test Email'
        plain_message = 'This is a test email from GreaterWMS. If you received this, email sending is working correctly!'
        html_message = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Test Email</title>
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
                <h1>GreaterWMS Test Email</h1>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>This is a test email from GreaterWMS. If you received this, email sending is working correctly!</p>
                <p>Email settings:</p>
                <ul>
                    <li>EMAIL_BACKEND: {settings.EMAIL_BACKEND}</li>
                    <li>EMAIL_HOST: {settings.EMAIL_HOST}</li>
                    <li>EMAIL_PORT: {settings.EMAIL_PORT}</li>
                    <li>EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}</li>
                    <li>EMAIL_USE_SSL: {getattr(settings, "EMAIL_USE_SSL", False)}</li>
                    <li>EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}</li>
                    <li>DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}</li>
                </ul>
                <p>Thank you,<br>The GreaterWMS Team</p>
            </div>
            <div class="footer">
                <p>This is an automated email, please do not reply.</p>
            </div>
        </body>
        </html>
        '''
        
        success = False
        
        # Try Django's send_mail
        if method in ['django', 'both']:
            self.stdout.write('Trying to send email using Django\'s send_mail...')
            try:
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    html_message=html_message,
                    fail_silently=False
                )
                self.stdout.write(self.style.SUCCESS('Email sent successfully using Django\'s send_mail!'))
                success = True
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error using Django\'s send_mail: {str(e)}'))
                if method == 'django':
                    raise CommandError(f'Failed to send email using Django\'s send_mail: {str(e)}')
        
        # Try direct SMTP
        if method in ['smtp', 'both'] and (method == 'smtp' or not success):
            self.stdout.write('Trying to send email using direct SMTP...')
            try:
                # Create multipart message
                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = settings.DEFAULT_FROM_EMAIL
                msg['To'] = email
                
                # Add plain text and HTML parts
                part1 = MIMEText(plain_message, 'plain')
                part2 = MIMEText(html_message, 'html')
                msg.attach(part1)
                msg.attach(part2)
                
                # Connect to SMTP server
                self.stdout.write(f'Connecting to SMTP server[ {settings.EMAIL_HOST}:{settings.EMAIL_PORT}]...')
                server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
                server.set_debuglevel(1)  # Enable debug output
                server.ehlo()                

                if settings.EMAIL_USE_TLS:
                    self.stdout.write('Starting TLS...')
                    server.starttls()
                    server.ehlo()
                
                self.stdout.write(f'Logging in as [{settings.EMAIL_HOST_USER}]...')
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                
                self.stdout.write(f'Sending email from {settings.DEFAULT_FROM_EMAIL} to {email}...')
                server.sendmail(settings.DEFAULT_FROM_EMAIL, [email], msg.as_string())
                server.quit()
                
                self.stdout.write(self.style.SUCCESS('Email sent successfully using direct SMTP!'))
                success = True
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error using direct SMTP: {str(e)}'))
                if method == 'smtp' or not success:
                    raise CommandError(f'Failed to send email using direct SMTP: {str(e)}')
        
        if success:
            self.stdout.write(self.style.SUCCESS(f'Test email sent successfully to {email}!'))
        else:
            raise CommandError('Failed to send test email using any method.')
