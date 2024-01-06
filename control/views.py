from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
import websockets
import asyncio

# 비동기 함수
async def connect_continuous(uri, stop_signal):
    async with websockets.connect(uri) as websocket:
        while not stop_signal.is_set():
            try:
                await websocket.send("ping")
                received_message = await websocket.recv()
                print(f"Received Message: {received_message}")
            except Exception as e:
                print(f"Error: {e}")
            await asyncio.sleep(5)

# 글로벌 변수로 태스크 관리
running_task = None

class StartView(APIView):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    async def get(self, request):
        global running_task
        if running_task is None or running_task.done():
            stop_signal = asyncio.Event()
            running_task = asyncio.create_task(connect_continuous("wss://stream.bybit.com/v5/public/linear", stop_signal))
        return Response({"status": "started"}, status=status.HTTP_200_OK)

class EndView(APIView):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    async def get(self, request):
        global running_task
        if running_task and not running_task.done():
            running_task.cancel()
        return Response({"status": "stopped"}, status=status.HTTP_200_OK)
