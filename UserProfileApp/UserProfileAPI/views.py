import datetime

from django.contrib.auth.hashers import make_password, check_password
from django.http.response import JsonResponse
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
import jwt
from UserProfileApp.settings import SECRET_KEY

from .models import User
from .serializers import UserSerializer


class UserAPIView(APIView):

    def __init__(self):
        super().__init__()
        self.serializer_class = UserSerializer


class UserDetailsAPIView(UserAPIView):

    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            user_serializer = self.serializer_class(user)
            data = user_serializer.data
            data["IP Address"] = request.ip_address
            data["ID"] = user.id
            return JsonResponse(data)
        except User.DoesNotExist:
            return JsonResponse({'message': 'This user does not exist!'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            user_data = JSONParser().parse(request)
            user_serializer = self.serializer_class(user, data=user_data)
            if user_serializer.is_valid():
                user_serializer.password = make_password(user_serializer.password)
                user_serializer.save()
                return JsonResponse(user_serializer.data)
            return JsonResponse(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return JsonResponse({'message': 'This user does not exist!'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            user.delete()
            return JsonResponse({'message': 'This user was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return JsonResponse({'message': 'This user does not exist!'}, status=status.HTTP_404_NOT_FOUND)


class UserCreateAPIView(UserAPIView):

    def post(self, request):
        user_data = JSONParser().parse(request)
        user_data['password'] = make_password(user_data['password'])
        print(user_data['password'])
        user_serializer = self.serializer_class(data=user_data)
        if user_serializer.is_valid():
            user_serializer.save()
            return JsonResponse(user_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginAPIView(UserAPIView):

    def post(self, request):
        user_data = JSONParser().parse(request)
        users = User.objects.filter(email=user_data['email'])
        if not len(users):
            return JsonResponse({'message': 'This user does not exist!'}, status=status.HTTP_404_NOT_FOUND)
        if check_password(user_data['password'], users[0].password):
            token = jwt.encode(
                payload={
                    "email": user_data['email'],
                    "password": make_password(user_data['password']),
                    "time": datetime.datetime.utcnow().strftime("%m/%d/%Y, %H:%M:%S")
                },
                key=SECRET_KEY
            )
            return JsonResponse({'message': 'Login successful!', 'token': token.decode("utf-8")})
        else:
            return JsonResponse({'message': 'Incorrect email or password!'})



user_details_api = UserDetailsAPIView.as_view()
user_create_api = UserCreateAPIView.as_view()
user_login_api = UserLoginAPIView.as_view()