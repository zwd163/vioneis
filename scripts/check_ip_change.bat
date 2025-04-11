@echo off
REM 设置工作目录为项目根目录
cd /d %~dp0\..

REM 激活虚拟环境并运行 IP 检查命令
call venv\Scripts\activate && python manage.py check_ip_change

REM 输出完成信息
echo IP 检查完成于 %date% %time%
