from django.core.management.base import BaseCommand
from utils.models import SystemSettings
from utils.ip_monitor import IP_CHECK_KEY, check_ip_change
import logging

logger = logging.getLogger('django')

class Command(BaseCommand):
    help = '测试 IP 变化检测和邮件发送功能'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='强制触发 IP 变化检测')
        parser.add_argument('--set-ip', type=str, help='手动设置上次 IP 地址以触发变化')

    def handle(self, *args, **options):
        force = options.get('force', False)
        set_ip = options.get('set_ip')
        
        if set_ip:
            try:
                ip_setting, created = SystemSettings.objects.get_or_create(
                    key=IP_CHECK_KEY,
                    defaults={'value': set_ip, 'description': '上次检测到的公网 IP 地址'}
                )
                if not created:
                    ip_setting.value = set_ip
                    ip_setting.save()
                self.stdout.write(self.style.SUCCESS(f'已将上次 IP 设置为: {set_ip}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'设置 IP 失败: {e}'))
                return
        
        if force:
            # 强制检测 IP 变化
            self.stdout.write(self.style.SUCCESS('强制检测 IP 变化...'))
            try:
                # 获取当前 IP 设置
                ip_setting = SystemSettings.objects.get(key=IP_CHECK_KEY)
                current_value = ip_setting.value
                
                # 临时修改为不同的值
                ip_setting.value = '0.0.0.0' if current_value != '0.0.0.0' else '1.1.1.1'
                ip_setting.save()
                
                self.stdout.write(self.style.SUCCESS(f'临时将 IP 从 {current_value} 修改为 {ip_setting.value}'))
                
                # 运行检测
                result = check_ip_change()
                
                # 恢复原值
                ip_setting.value = current_value
                ip_setting.save()
                self.stdout.write(self.style.SUCCESS(f'已恢复 IP 为: {current_value}'))
                
                if result:
                    self.stdout.write(self.style.SUCCESS('测试完成，邮件应已发送'))
                else:
                    self.stdout.write(self.style.WARNING('测试过程中出现问题，详情请查看日志'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'测试过程中出现异常: {e}'))
                logger.exception('IP 变化测试命令执行异常')
        else:
            # 正常检测 IP 变化
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
