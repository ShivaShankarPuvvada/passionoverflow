from rest_framework import serializers

from django.contrib.auth import get_user_model

User = get_user_model()


class ObtainTokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields =   "__all__"

        # fields = ('id', 'username', 'email', 'first_name', 'last_name')  # Customize fields as needed
        """
        # Choose fields from below user dictionary
        "user": {
        "id": 1,
        "password": "pbkdf2_sha256$600000$JieXiSGYHGVRy8VYno0Zh1$gt8ijkJFulzbXj+WlHlGWmuhewIk3jcrnJBvMvI5jcs=",
        "last_login": "2023-09-09T14:34:11.199796Z",
        "is_superuser": true,
        "username": "pndiode",
        "first_name": "",
        "last_name": "",
        "email": "pndiode@gmail.com",
        "is_staff": true,
        "is_active": true,
        "date_joined": "2023-09-09T14:11:57.752288Z",
        "phone_number": null,
        "gender": null,
        "country": null,
        "groups": [],
        "user_permissions": []
    }
        """


class UserCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email", "phone_number", "gender", "country")


