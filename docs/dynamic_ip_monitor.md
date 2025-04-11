# 动态 IP 监控功能

## 功能概述

当服务器的 IP 地址发生变化时，系统会自动检测到这一变化，并向所有活跃的员工（staff）发送包含新 IP 地址和二维码的邮件通知。这样，即使服务器 IP 变化，用户也能够方便地访问系统。

## 工作原理

1. 系统定期检查服务器的公网 IP 地址
2. 如果检测到 IP 地址变化，系统会：
   - 生成包含新 IP 地址的访问链接二维码
   - 向所有未删除且未锁定的员工（`is_delete=False, is_lock=False`）发送邮件通知
   - 邮件中包含新的 IP 地址、访问链接和直接嵌入的二维码图片

## 配置说明

### 邮件设置

确保在 `settings.py` 中正确配置了邮件发送设置：

```python
# 邮件配置示例
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'your-smtp-server.com'
EMAIL_PORT = 587  # 或其他端口
EMAIL_USE_TLS = True  # 或 False
EMAIL_USE_SSL = False  # 或 True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-password'
DEFAULT_FROM_EMAIL = 'your-email@example.com'
```

### 端口设置

默认情况下，系统使用 8008 端口作为服务访问端口。如需修改，请编辑 `utils/ip_monitor.py` 文件中的 `SERVER_PORT` 变量。

## 使用方法

### 手动检查 IP 变化

您可以使用以下命令手动检查 IP 是否变化：

```bash
python manage.py check_ip_change
```

### 测试功能

要测试 IP 变化检测和邮件发送功能，可以使用以下命令：

```bash
# 正常检查 IP 变化
python manage.py test_ip_change

# 强制触发 IP 变化检测（不管 IP 是否真的变化）
python manage.py test_ip_change --force

# 手动设置上次记录的 IP 地址（用于测试）
python manage.py test_ip_change --set-ip 192.168.1.1
```

### 设置定时任务

为了自动检查 IP 变化，建议设置定时任务。以下是几种方法：

#### 使用 cron（Linux/Unix）

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每小时检查一次）
0 * * * * cd /path/to/your/project && /path/to/your/python manage.py check_ip_change
```

#### 使用计划任务（Windows）

1. 打开任务计划程序
2. 创建基本任务
3. 设置触发器（例如，每小时一次）
4. 设置操作：启动程序
   - 程序/脚本：`python`
   - 添加参数：`manage.py check_ip_change`
   - 起始于：`E:\Work\github\vioneis`（项目路径）

## 故障排除

### 邮件发送失败

- 检查邮件服务器配置是否正确
- 确认邮箱账号和密码是否有效
- 查看日志文件 `logs/server.log` 和 `logs/error.log` 获取详细错误信息

### IP 检测问题

- 系统使用多种方法尝试获取公网 IP，如果一种方法失败会自动尝试其他方法
- 如果所有方法都失败，请确保服务器能够访问互联网
- 检查防火墙设置，确保允许对外连接

## 注意事项

- 确保员工记录中的邮箱地址正确无误
- 邮件发送功能依赖于正确配置的 SMTP 服务器
- 二维码图片保存在 `media/qrcodes/` 目录下
