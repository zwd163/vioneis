# IP 监控服务

## 功能概述

IP 监控服务是一个随 Web 服务器自动启动和停止的后台任务，用于定期检查服务器的公网 IP 地址是否发生变化。如果检测到 IP 变化，系统会自动向所有活跃的员工发送通知邮件，确保他们能够继续访问系统。

## 工作原理

1. 当 Web 服务器启动时，IP 监控服务会自动启动
2. 服务会定期检查服务器的公网 IP 地址（默认每小时检查一次）
3. 如果检测到 IP 地址变化，系统会：
   - 生成包含新 IP 地址的访问链接二维码
   - 向所有未删除且未锁定的员工（`is_delete=False, is_lock=False`）发送邮件通知
   - 邮件中包含访问按钮和嵌入的二维码图片
4. 当 Web 服务器停止时，IP 监控服务也会自动停止

## 配置说明

### 检查间隔设置

默认情况下，系统每小时（3600 秒）检查一次 IP 变化。您可以通过在 `settings.py` 中添加以下配置来修改检查间隔：

```python
# 设置 IP 检查间隔为 30 分钟（1800 秒）
IP_CHECK_INTERVAL = 1800
```

### 邮件设置

确保在 `settings.py` 中正确配置了邮件发送设置：

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'your-smtp-server.com'
EMAIL_PORT = 587  # 或其他端口
EMAIL_USE_TLS = True  # 或 False
EMAIL_USE_SSL = False  # 或 True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-password'
DEFAULT_FROM_EMAIL = 'your-email@example.com'
```

## 手动管理服务

虽然 IP 监控服务会随 Web 服务器自动启动和停止，但您也可以使用以下命令手动管理服务：

### 查看服务状态

```bash
python manage.py ip_monitor status
```

这个命令会显示服务的当前状态，包括：
- 是否正在运行
- 运行服务的进程 ID (PID)
- 最后更新时间
- 如果服务停止，显示停止原因

### 手动启动服务

```bash
python manage.py ip_monitor start
```

这个命令会启动 IP 监控服务。如果服务已经在运行（在当前进程或其他进程中），它会先尝试停止现有服务，然后启动新的服务实例。

### 手动停止服务

```bash
python manage.py ip_monitor stop
```

这个命令会停止 IP 监控服务。如果服务在当前进程中运行，它会停止当前进程中的服务。如果服务在其他进程中运行，它会尝试终止该进程。

## 日志记录

IP 监控服务的所有活动都会记录在系统日志中。您可以在 `logs/server.log` 文件中查看服务的运行状态和错误信息。

## 故障排除

### 服务未自动启动

- 确保 `utils` 应用已添加到 `settings.py` 的 `INSTALLED_APPS` 中
- 检查日志文件中是否有错误信息
- 尝试手动启动服务：`python manage.py ip_monitor start`

### 邮件发送失败

- 检查邮件服务器配置是否正确
- 确认邮箱账号和密码是否有效
- 查看日志文件获取详细错误信息

### IP 检测问题

- 系统使用多种方法尝试获取公网 IP，如果一种方法失败会自动尝试其他方法
- 如果所有方法都失败，请确保服务器能够访问互联网
- 检查防火墙设置，确保允许对外连接
