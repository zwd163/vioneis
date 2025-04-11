import urllib.request
import socket
import qrcode
import logging
import os
import time
from io import BytesIO
from django.conf import settings
from staff.models import ListModel as StaffModel
from utils.models import SystemSettings

logger = logging.getLogger('django')

# 配置
SERVER_PORT = "8008"  # 服务器端口
IP_CHECK_KEY = "last_public_ip"  # 存储上次 IP 的键名
QR_CODE_DIR = os.path.join(settings.MEDIA_ROOT, 'qrcodes')

# 确保二维码目录存在
if not os.path.exists(QR_CODE_DIR):
    os.makedirs(QR_CODE_DIR)

def get_public_ip():
    """
    获取公网 IP 地址，尝试多种方法
    """
    # 方法 1: 使用外部 API
    try:
        with urllib.request.urlopen('https://api.ipify.org', timeout=5) as response:
            ip_address = response.read().decode('utf-8')
            logger.info(f"IP 地址通过 ipify.org 获取: {ip_address}")
            return ip_address
    except Exception as e:
        logger.warning(f"通过 ipify.org 获取 IP 失败: {e}")

    # 方法 2: 备用 API
    try:
        with urllib.request.urlopen('https://ifconfig.me/ip', timeout=5) as response:
            ip_address = response.read().decode('utf-8')
            logger.info(f"IP 地址通过 ifconfig.me 获取: {ip_address}")
            return ip_address
    except Exception as e:
        logger.warning(f"通过 ifconfig.me 获取 IP 失败: {e}")

    # 方法 3: 使用 socket 连接（不太可靠，但作为备用）
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        logger.info(f"IP 地址通过 socket 获取: {ip_address}")
        return ip_address
    except Exception as e:
        logger.error(f"通过 socket 获取 IP 失败: {e}")
        return None

def generate_qrcode(ip_address):
    """
    为给定的 IP 地址生成二维码并返回文件路径
    """
    url = f"http://{ip_address}:{SERVER_PORT}/"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # 保存到文件
    filename = f"qrcode_{ip_address.replace('.', '_')}.png"
    filepath = os.path.join(QR_CODE_DIR, filename)
    with open(filepath, 'wb') as f:
        img.save(f)

    # 同时返回内存中的图像用于邮件附件
    img_buffer = BytesIO()
    img.save(img_buffer)
    img_buffer.seek(0)

    logger.info(f"为 URL {url} 生成二维码，保存到 {filepath}")
    return filepath, img_buffer, url

def send_ip_change_email(ip_address, qrcode_buffer, url):
    """
    向所有活跃的 staff 用户发送 IP 变更邮件
    """
    # 获取所有活跃的 staff 用户
    active_staff = StaffModel.objects.filter(is_delete=False, is_lock=False, email__isnull=False).exclude(email='')

    if not active_staff.exists():
        logger.warning("没有找到活跃的 staff 用户，无法发送邮件")
        return False

    # 邮件计数
    sent_count = 0
    failed_count = 0

    for staff in active_staff:
        try:
            # 确保邮箱不为 None
            if staff.email is None or staff.email == '':
                logger.warning(f"Staff {staff.staff_name} 的邮箱为空，跳过")
                continue

            # 准备邮件内容
            subject = "服务器 IP 地址变更通知"

            # 准备 HTML 内容
            html_message = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>服务器 IP 地址变更通知</title>
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
                    <h1>服务器 IP 地址变更通知</h1>
                </div>
                <div class="content">
                    <p>尊敬的 {staff.real_name or staff.staff_name}：</p>
                    <p>系统检测到服务器地址已变更。请使用以下方式访问系统：</p>
                    <p style="text-align: center;">
                        <a href="{url}" class="button">访问系统</a>
                    </p>
                    <p>您也可以扫描下方的二维码直接访问系统：</p>
                    <div id="qrcode-placeholder" style="text-align: center;"></div>
                    <p>感谢您的使用，<br>GreaterWMS 团队</p>
                </div>
                <div class="footer">
                    <p>此邮件由系统自动发送，请勿回复。</p>
                </div>
            </body>
            </html>
            '''

            # 纯文本内容
            plain_message = f'''
            服务器 IP 地址变更通知

            尊敬的 {staff.real_name or staff.staff_name}：

            系统检测到服务器 IP 地址已变更。

            您可以点击邮件中的“访问系统”按钮访问系统。

            您也可以扫描邮件中的二维码直接访问系统。

            感谢您的使用，
            GreaterWMS 团队
            '''

            # 尝试使用 Django 的 send_mail 发送邮件
            try:
                # 打印调试信息
                logger.info(f"尝试发送 IP 变更邮件到 {staff.email}")
                logger.info(f"Email settings: HOST={settings.EMAIL_HOST}, PORT={settings.EMAIL_PORT}, USER={settings.EMAIL_HOST_USER}")

                # 准备二维码嵌入到邮件正文中
                qrcode_buffer.seek(0)  # 确保从头开始读取
                qrcode_data = qrcode_buffer.read()

                from django.core.mail import EmailMultiAlternatives
                import base64

                # 将二维码图片转换为base64格式直接嵌入HTML
                qrcode_base64 = base64.b64encode(qrcode_data).decode('utf-8')

                # 修改HTML内容，直接嵌入base64编码的图片
                html_with_img = html_message.replace('<div id="qrcode-placeholder" style="text-align: center;"></div>',
                    f'<div style="text-align: center;">\n                        <img src="data:image/png;base64,{qrcode_base64}" alt="访问二维码" style="width: 200px; height: 200px;">\n                    </div>')

                # 创建邮件消息
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[staff.email]
                )

                # 添加HTML内容（已包含嵌入的二维码图片）
                email.attach_alternative(html_with_img, "text/html")

                # 发送邮件
                email.send()

                logger.info(f"Email sent successfully using EmailMultiAlternatives")
            except Exception as e:
                logger.error(f"Error using EmailMultiAlternatives: {str(e)}")

                # 如果失败，尝试使用更低级别的方式
                import smtplib
                from email.mime.text import MIMEText
                from email.mime.multipart import MIMEMultipart

                try:
                    # 创建multipart消息
                    msg = MIMEMultipart('alternative')
                    msg['Subject'] = subject
                    msg['From'] = settings.DEFAULT_FROM_EMAIL
                    msg['To'] = staff.email

                    # 将二维码图片转换为base64格式直接嵌入HTML
                    qrcode_buffer.seek(0)  # 确保从头开始读取
                    img_data = qrcode_buffer.read()

                    import base64
                    qrcode_base64 = base64.b64encode(img_data).decode('utf-8')

                    # 修改HTML内容，直接嵌入base64编码的图片
                    html_with_img = html_message.replace('<div id="qrcode-placeholder" style="text-align: center;"></div>',
                        f'<div style="text-align: center;">\n                            <img src="data:image/png;base64,{qrcode_base64}" alt="访问二维码" style="width: 200px; height: 200px;">\n                        </div>')

                    # 添加纯文本和HTML部分
                    part1 = MIMEText(plain_message, 'plain')
                    part2 = MIMEText(html_with_img, 'html')
                    msg.attach(part1)
                    msg.attach(part2)

                    # 打印邮件设置
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
                    server.sendmail(settings.DEFAULT_FROM_EMAIL, [staff.email], msg.as_string())
                    server.quit()

                    logger.info(f"Email sent successfully using smtplib")
                except Exception as inner_e:
                    logger.error(f"Error using smtplib: {str(inner_e)}")
                    raise inner_e

            sent_count += 1
            logger.info(f"成功发送 IP 变更邮件到 {staff.email}")

            # 添加延迟，避免触发邮件服务器的速率限制
            time.sleep(3)

        except Exception as e:
            failed_count += 1
            logger.error(f"发送邮件到 {staff.email} 失败: {e}")

    logger.info(f"IP 变更邮件发送完成: 成功 {sent_count}, 失败 {failed_count}")
    return sent_count > 0

def check_ip_change():
    """
    检查 IP 是否变化，如果变化则发送邮件
    """
    logger.info("开始检查 IP 地址变化...")
    current_ip = get_public_ip()

    if current_ip is None:
        logger.error("无法获取当前 IP 地址")
        return False

    # 获取上次记录的 IP
    try:
        ip_setting, created = SystemSettings.objects.get_or_create(
            key=IP_CHECK_KEY,
            defaults={'value': current_ip, 'description': '上次检测到的公网 IP 地址'}
        )
        last_ip = ip_setting.value
    except Exception as e:
        logger.error(f"获取上次 IP 记录失败: {e}")
        return False

    # 如果是首次运行或 IP 已变化
    if created:
        logger.info(f"首次运行，记录当前 IP: {current_ip}")
        return True

    if current_ip != last_ip:
        logger.info(f"IP 地址已变化: {last_ip} -> {current_ip}")

        # 生成二维码
        try:
            _, qrcode_buffer, url = generate_qrcode(current_ip)

            # 发送邮件
            if send_ip_change_email(current_ip, qrcode_buffer, url):
                # 更新 IP 记录
                ip_setting.value = current_ip
                ip_setting.save()
                logger.info(f"IP 记录已更新为: {current_ip}")
                return True
            else:
                logger.warning("邮件发送失败，不更新 IP 记录")
                return False
        except Exception as e:
            logger.error(f"处理 IP 变化时出错: {e}")
            return False
    else:
        logger.info(f"IP 地址未变化: {current_ip}")
        return True
