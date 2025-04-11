import threading
import time
import logging
import os
import sys
import atexit
import datetime
import json
from django.conf import settings

logger = logging.getLogger('django')

# 全局变量，用于控制后台线程
ip_monitor_thread = None
stop_event = threading.Event()

# 状态记录的键名
IP_MONITOR_STATUS_KEY = "ip_monitor_status"

# 注册退出函数，确保在程序退出时停止线程
@atexit.register
def cleanup():
    """Python 程序退出时自动调用此函数停止后台线程"""
    try:
        if ip_monitor_thread and ip_monitor_thread.is_alive():
            logger.info("\n\n程序退出，正在停止 IP 监控后台任务...")
            stop_event.set()
            ip_monitor_thread.join(5)  # 等待最多 5 秒
            logger.info("IP 监控后台任务已停止")

        # 更新服务状态
        try:
            update_service_status(False, None, "程序正常退出")
        except:
            pass  # 忽略退出时的数据库错误
    except:
        pass  # 忽略退出时的所有错误

def ip_monitor_worker():
    """
    IP 监控后台工作线程
    定期检查 IP 变化并发送通知邮件
    """
    from utils.ip_monitor import check_ip_change
    import traceback

    logger.info("\n\n===== IP 监控后台任务已启动 =====")

    # 检查间隔时间（秒）
    # 默认为 1 小时 = 3600 秒
    check_interval = getattr(settings, 'IP_CHECK_INTERVAL', 3600)
    logger.info(f"IP 检查间隔设置为 {check_interval} 秒")

    # 启动后立即执行一次检查，获取初始 IP
    try:
        logger.info("\n执行初始 IP 检查...")
        check_ip_change()
        logger.info("初始 IP 检查完成")
    except Exception as e:
        logger.error(f"\n初始 IP 检查出错: {e}")
        logger.error(traceback.format_exc())

    try:
        # 主循环
        while not stop_event.is_set():
            try:
                # 等待指定时间，或者直到收到停止信号
                logger.info(f"\n下次 IP 检查将在 {check_interval} 秒后执行")
                if stop_event.wait(check_interval):
                    # 如果收到停止信号，退出循环
                    logger.info("\n收到停止信号，结束 IP 监控任务")
                    break

                # 执行 IP 检查
                logger.info("\n执行定期 IP 检查...")
                check_ip_change()
                logger.info("定期 IP 检查完成")
            except Exception as e:
                logger.error(f"\nIP 监控任务执行出错: {e}")
                logger.error(traceback.format_exc())

                # 出错后等待一段时间再重试，避免频繁报错
                time.sleep(60)
    except Exception as e:
        logger.error(f"\nIP 监控后台线程异常退出: {e}")
        logger.error(traceback.format_exc())
    finally:
        logger.info("\n===== IP 监控后台任务已停止 =====")

def update_service_status(is_running, pid=None, error=None):
    """
    更新服务状态到数据库
    """
    try:
        from utils.models import SystemSettings
        import json
        import os
        import datetime

        # 准备状态数据
        status_data = {
            'is_running': is_running,
            'pid': pid or os.getpid(),
            'last_update': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': error
        }

        # 将状态数据存入数据库
        status_obj, created = SystemSettings.objects.update_or_create(
            key=IP_MONITOR_STATUS_KEY,
            defaults={
                'value': json.dumps(status_data),
                'description': 'IP 监控服务状态'
            }
        )

        return True
    except Exception as e:
        logger.error(f"\n更新服务状态时出错: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def get_service_status():
    """
    从数据库获取服务状态
    返回：(is_running, pid, last_update, error)
    """
    try:
        from utils.models import SystemSettings
        import json
        import psutil

        # 从数据库获取状态数据
        status_obj = SystemSettings.objects.filter(key=IP_MONITOR_STATUS_KEY).first()

        if not status_obj:
            return False, None, None, None

        status_data = json.loads(status_obj.value)
        is_running = status_data.get('is_running', False)
        pid = status_data.get('pid')
        last_update = status_data.get('last_update')
        error = status_data.get('error')

        # 如果标记为运行中，检查进程是否实际存在
        if is_running and pid:
            try:
                # 检查进程是否存在
                process = psutil.Process(pid)
                # 检查进程是否是 Python 进程
                if 'python' not in process.name().lower():
                    is_running = False
                    update_service_status(False, None, "进程存在但不是 Python 进程")
            except psutil.NoSuchProcess:
                is_running = False
                update_service_status(False, None, "进程不存在")

        return is_running, pid, last_update, error
    except Exception as e:
        logger.error(f"\n获取服务状态时出错: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False, None, None, str(e)

def start_ip_monitor():
    """
    启动 IP 监控后台任务
    返回：True - 启动成功，False - 启动失败
    """
    global ip_monitor_thread, stop_event

    try:
        # 检查服务是否已在运行
        is_running, pid, _, _ = get_service_status()

        # 如果服务已在运行，先停止它
        if is_running:
            logger.info(f"\n服务已在运行 (PID: {pid})，将尝试停止")
            stop_ip_monitor()

        # 如果已经有线程在运行，先停止它
        if ip_monitor_thread and ip_monitor_thread.is_alive():
            logger.info("\n已有 IP 监控后台任务在运行，将重新启动")
            stop_event.set()
            ip_monitor_thread.join(5)

        # 重置停止事件
        stop_event.clear()

        # 创建并启动新线程
        ip_monitor_thread = threading.Thread(target=ip_monitor_worker, daemon=True, name="IPMonitorThread")
        ip_monitor_thread.start()

        # 等待一小段时间，确保线程已启动
        time.sleep(0.5)

        if ip_monitor_thread.is_alive():
            # 更新服务状态
            update_service_status(True)
            logger.info("\nIP 监控后台任务启动成功")
            return True
        else:
            update_service_status(False, None, "Thread failed to start")
            logger.error("\nIP 监控后台任务启动失败")
            return False
    except Exception as e:
        update_service_status(False, None, str(e))
        logger.error(f"\n启动 IP 监控后台任务时出错: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def stop_ip_monitor():
    """
    停止 IP 监控后台任务
    返回：True - 停止成功或没有运行中的任务，False - 停止失败
    """
    global ip_monitor_thread, stop_event

    try:
        # 检查服务是否在运行
        is_running, pid, _, _ = get_service_status()

        # 如果服务在运行但不是当前进程，尝试终止该进程
        if is_running and pid and pid != os.getpid():
            try:
                import psutil
                logger.info(f"\n尝试终止其他进程中的服务 (PID: {pid})")
                process = psutil.Process(pid)
                process.terminate()
                # 等待进程终止
                gone, alive = psutil.wait_procs([process], timeout=5)
                if alive:
                    logger.warning(f"\n无法终止进程 (PID: {pid})")
            except psutil.NoSuchProcess:
                logger.info(f"\n进程 (PID: {pid}) 已不存在")
            except Exception as e:
                logger.error(f"\n终止进程时出错: {e}")

        # 如果当前进程中有线程在运行，停止它
        if ip_monitor_thread and ip_monitor_thread.is_alive():
            logger.info("\n正在停止当前进程中的 IP 监控后台任务...")

            # 发送停止信号
            stop_event.set()

            # 等待线程结束，最多等待 10 秒
            ip_monitor_thread.join(10)

            if ip_monitor_thread.is_alive():
                logger.warning("\nIP 监控后台任务未能在指定时间内停止")
                update_service_status(False, None, "任务无法在指定时间内停止")
                return False
            else:
                logger.info("\nIP 监控后台任务已成功停止")
                update_service_status(False)
                return True
        else:
            logger.info("\n当前进程中没有运行的 IP 监控后台任务")
            update_service_status(False)
            return True
    except Exception as e:
        logger.error(f"\n停止 IP 监控后台任务时出错: {e}")
        import traceback
        logger.error(traceback.format_exc())
        update_service_status(False, None, str(e))
        return False
