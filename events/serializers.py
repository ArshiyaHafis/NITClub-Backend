from rest_framework import serializers
from django.contrib.auth import authenticate

from .models import customuser, Club

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = customuser
        fields = ('roll_number', 'first_name', 'last_name', 'email', 'phone_number', 'isClubAdmin', 'date_joined', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')  
        user = customuser(**validated_data) 
        user.set_password(password)
        user.save()
        return user
    
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("User is not active.")

        data['user'] = user
        return data
    
class ClubSerializer(serializers.ModelSerializer):
    club_admin = serializers.CharField(write_only=True, required=True)  

    class Meta:
        model = Club
        fields = '__all__'

    def create(self, validated_data):
        club_admin = validated_data.pop('club_admin')
        user = customuser.objects.get(roll_number=club_admin)
        club = Club.objects.create(club_admin=user, **validated_data)
        return club