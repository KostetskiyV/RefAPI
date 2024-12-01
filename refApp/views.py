from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from time import sleep

from .serializers import AuthSerializer, ProfileSerializer
from .renderers import UserJSONRenderer
from . import phones

class AuthAPIView(APIView):

    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = AuthSerializer

    def post(self, request):

        phoneNumber = request.data.get('phone')

        if phoneNumber is None:
            raise serializers.ValidationError('Users must have a phone number.')

        phoneNumber = str(phoneNumber)
        if 11 > len(phoneNumber) or len(phoneNumber) > 13 or not phoneNumber.isdigit():
            raise serializers.ValidationError('Phone number must be 11-13 symbols in len and contain only digits.')


        if phoneNumber in phones.wait_for_authorize:

            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            phones.rem(phoneNumber)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            phones.add(phoneNumber)
            sleep(1.5)
            return Response({"phone": phoneNumber, "Message": "Введите четырёхзначный код"}, status=status.HTTP_200_OK)

class ProfileAPIView(APIView):

    permission_classes = (AllowAny,)
    #renderer_classes = (UserJSONRenderer,)
    serializer_class = ProfileSerializer

    def get(self, request, phoneNumber):
        serializer = self.serializer_class(data={}, context={"phoneNumber": phoneNumber, "method": "GET"})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request, phoneNumber):

        serializer = self.serializer_class(data={}, context={"phoneNumber": phoneNumber, "ref_code": request.data.get("ref_code"), "method": "POST"})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)