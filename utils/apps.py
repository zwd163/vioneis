import os
import sys
from django.apps import AppConfig
import logging

logger = logging.getLogger('django')

class UtilsConfig(AppConfig):
    name = 'utils'
    verbose_name = 'Utilities'

    def ready(self):
        # 在应用启动时执行的代码

        # 避免在运行 manage.py migrate 等命令时启动后台任务
        if 'runserver' in sys.argv or 'daphne' in sys.argv or 'asgi' in ' '.join(sys.argv):
            # 仅在主进程中启动后台任务，避免在自动重载时启动多个任务
            if not os.environ.get('RUN_MAIN'):
                logger.info("\n\n正在启动 IP 监控后台任务...")
                try:
                    # 导入并启动 IP 监控任务
                    from utils.ip_monitor_task import start_ip_monitor
                    start_ip_monitor()
                except Exception as e:
                    logger.error(f"\n\n启动 IP 监控后台任务失败: {e}")
