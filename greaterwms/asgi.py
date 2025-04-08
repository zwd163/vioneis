import os

from django.core.asgi import get_asgi_application
from utils.websocket import websocket_application
#from asgihandler.core import ASGIHandler
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greaterwms.settings')

http_application = get_asgi_application()


import logging

async def application(scope, receive, send):
    logger = logging.getLogger('asgi')
    logger.info(f"ASGI请求处理开始, scope类型: {scope['type']}, 路径: {scope.get('path', '')}, 方法: {scope.get('method', '')}, 查询参数: {scope.get('query_string', b'').decode()}")
    if scope['type'] in ['http', 'https']:
        # 这里有风险，向外部链接发送数据
        #ASGIHandler.asgi_get_handler(scope)

        await http_application(scope, receive, send)
    elif scope['type'] in ['websocket']:
        await websocket_application(scope, receive, send)
    else:
        raise Exception('Unknown Type' + scope['type'])

