from django.core.management.base import BaseCommand, CommandError
import logging
import os

logger = logging.getLogger('django')

class Command(BaseCommand):
    help = '管理 IP 监控后台任务'

    def add_arguments(self, parser):
        parser.add_argument('action', type=str, choices=['start', 'stop', 'status'],
                            help='要执行的操作: start - 启动任务, stop - 停止任务, status - 查看任务状态')

    def handle(self, *args, **options):
        action = options['action']

        try:
            from utils.ip_monitor_task import start_ip_monitor, stop_ip_monitor, get_service_status

            if action == 'start':
                self.stdout.write(self.style.SUCCESS('正在启动 IP 监控后台任务...'))
                result = start_ip_monitor()
                if result:
                    self.stdout.write(self.style.SUCCESS('IP 监控后台任务已成功启动'))
                else:
                    self.stdout.write(self.style.ERROR('启动 IP 监控后台任务失败'))

            elif action == 'stop':
                self.stdout.write(self.style.SUCCESS('正在停止 IP 监控后台任务...'))
                result = stop_ip_monitor()
                if result:
                    self.stdout.write(self.style.SUCCESS('IP 监控后台任务已成功停止'))
                else:
                    self.stdout.write(self.style.ERROR('停止 IP 监控后台任务失败'))

            elif action == 'status':
                is_running, pid, last_update, error = get_service_status()

                if is_running:
                    self.stdout.write(self.style.SUCCESS(f'IP 监控后台任务正在运行 (PID: {pid})'))
                    self.stdout.write(f'最后更新时间: {last_update}')

                    # 检查是否是当前进程
                    if pid == os.getpid():
                        self.stdout.write('服务运行在当前进程中')
                    else:
                        self.stdout.write(f'服务运行在其他进程中 (PID: {pid})')
                else:
                    self.stdout.write(self.style.WARNING('IP 监控后台任务未运行'))
                    if error:
                        self.stdout.write(f'错误信息: {error}')
                    if last_update:
                        self.stdout.write(f'最后更新时间: {last_update}')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'执行命令时出错: {e}'))
            logger.exception('IP 监控命令执行异常')
