from django.core.management.base import BaseCommand
from utils.ip_monitor import check_ip_change
import logging

logger = logging.getLogger('django')

class Command(BaseCommand):
    help = '检查服务器 IP 是否变化，如果变化则发送通知邮件'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('开始检查 IP 地址变化...'))
        
        try:
            result = check_ip_change()
            if result:
                self.stdout.write(self.style.SUCCESS('IP 检查完成'))
            else:
                self.stdout.write(self.style.WARNING('IP 检查过程中出现问题，详情请查看日志'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'IP 检查过程中出现异常: {e}'))
            logger.exception('IP 检查命令执行异常')
