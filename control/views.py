from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
import websocket
import threading
import time

def connect_continuous(uri, stop_signal):
    ws = websocket.create_connection(uri)
    try:
        while not stop_signal.is_set():
            ws.send("ping")
            received_message = ws.recv()
            print(f"Received Message: {received_message}")
            time.sleep(5)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ws.close()

running_task = None
stop_signal = threading.Event()

class StartView(APIView):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        global running_task, stop_signal
        if running_task is None or not running_task.is_alive():
            stop_signal.clear()
            running_task = threading.Thread(target=connect_continuous, args=("wss://stream.bybit.com/v5/public/linear", stop_signal))
            running_task.start()
        return Response({"status": "started"}, status=status.HTTP_200_OK)

class EndView(APIView):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        global stop_signal
        stop_signal.set()
        return Response({"status": "stopped"}, status=status.HTTP_200_OK)
