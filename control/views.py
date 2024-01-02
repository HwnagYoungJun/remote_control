from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class StartView(APIView):
    # /start GET
    def get(self, request):
        result = {
            "start": "OK"
        }
        return Response(data=result, status=status.HTTP_200_OK)