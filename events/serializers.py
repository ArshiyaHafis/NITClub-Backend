from rest_framework import serializers
from django.contrib.auth import authenticate
from django.db.models import Sum

from .models import customuser, Club, Event, Registration

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = customuser
        fields = '__all__'
        # fields = ('roll_number', 'first_name', 'last_name', 'email', 'phone_number', 'isClubAdmin', 'date_joined', 'password')
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
    club_admin = serializers.CharField(required=True)

    class Meta:
        model = Club
        fields = '__all__'

    def create(self, validated_data):
        club_admin = validated_data.pop('club_admin')
        user = customuser.objects.get(roll_number=club_admin)
        user.isClubAdmin=True
        # admin_position = validated_data.get('admin_position', '')
        # print(admin_position)
        # user.admin_position = admin_position
        user.save()
        validated_data['club_balance'] = validated_data['club_opening_balance']
        club = Club.objects.create(club_admin=user, **validated_data)
        club.save()
        return club



class EventSerializer(serializers.ModelSerializer):
    event_club = serializers.PrimaryKeyRelatedField(queryset=Club.objects.all())
    event_id = serializers.CharField(read_only=True)  

    class Meta:
        model = Event
        fields = '__all__'

    def create(self, validated_data):
        
        validated_data.pop('event_cost', None)
        validated_data.pop('event_profit', None)
        validated_data.pop('event_budget', None)

        event_club = validated_data.pop('event_club')
        club = Club.objects.get(club_id=event_club)


        if 'event_id' not in validated_data:
            last_id = Event.objects.all().order_by('-event_id').first()
            if last_id:
                last_id_value = int(last_id.event_id[1:])
                new_id_value = last_id_value + 1
                validated_data['event_id'] = f'E{new_id_value:06}'
            else:
                validated_data['event_id'] = 'E000001'
                
        event_budget = validated_data.get('event_budget', 0)
        event_cost = validated_data.get('event_cost', 0)
        validated_data['event_profit'] = event_budget - event_cost

        event = Event.objects.create(event_club=club, **validated_data)
        self.update_club_balance(club)

        return event

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)


        event_budget = validated_data.get('event_budget', instance.event_budget)
        event_cost = validated_data.get('event_cost', instance.event_cost)
        instance.event_profit = event_budget - event_cost

        instance.save()
        self.update_club_balance(instance.event_club)

        return instance

    def update_club_balance(self, club):
        total_event_budget = Event.objects.filter(event_club=club).aggregate(total_budget=Sum('event_budget'))['total_budget'] or 0
        total_event_cost = Event.objects.filter(event_club=club).aggregate(total_profit=Sum('event_cost'))['total_profit'] or 0
        print(total_event_budget, total_event_cost)
        club.club_balance = club.club_opening_balance - total_event_budget + total_event_cost
        print(club.club_balance)
        club.save()

class RegistrationSerializer(serializers.ModelSerializer):
    student_id = serializers.CharField(write_only=True, required=True)
    event_id = serializers.CharField(write_only=True, required=True)
    reg_id = serializers.CharField(read_only=True)

    class Meta:
        model = Registration
        fields = '__all__'

    def create(self, validated_data):
        student_id = validated_data.pop('student_id')
        event_id = validated_data.pop('event_id')
        student = customuser.objects.get(roll_number=student_id)
        event = Event.objects.get(event_id=event_id)

        last_registration = Registration.objects.all().order_by('-reg_id').first()
        if last_registration and last_registration.reg_id:
            last_id_value = int(last_registration.reg_id[1:])
            new_id_value = last_id_value + 1
            validated_data['reg_id'] = f'R{new_id_value:06}'
        else:
            validated_data['reg_id'] = 'R000001'

        registration = Registration(student_id=student, event_id=event, reg_id=validated_data['reg_id'])
        registration.save()
        student.event_registration_count += 1
        student.save()
        event.event_students = Registration.objects.filter(event_id=event).count()
        event.save()

        return registration