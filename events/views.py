from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import login
from datetime import datetime

from .models import customuser, Club, Event, Registration
from .serializers import CustomUserSerializer, UserLoginSerializer, ClubSerializer, EventSerializer, RegistrationSerializer

class UserCreateView(generics.CreateAPIView):
    queryset = customuser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        password = self.request.data.get('password')  
        serializer.save(password=password)

class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            user_data = {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone_number': user.phone_number,
                'roll_number': user.roll_number,
                'is_active': user.is_active,
                'isClubAdmin': user.isClubAdmin, 
            }

            return Response({'token': token.key, 'user': user_data})
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = customuser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()

        if user.isClubAdmin:
            clubs = Club.objects.filter(club_admin=user)
            club_serializer = ClubSerializer(clubs, many=True)
            
            user_serializer = self.get_serializer(user)
            data = user_serializer.data
            data['clubs'] = club_serializer.data

            return Response(data)
        else:
            
            return super().retrieve(request, *args, **kwargs)


class ClubListCreateView(generics.ListCreateAPIView):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        roll_number = self.request.data.get('club_admin')  
        serializer.save(club_admin=roll_number)  


class ClubDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class EventListCreateView(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    def perform_create(self, serializer):
        club_id = self.request.data.get('event_club')
        serializer.save(event_club=club_id)

class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class RegistrationListCreateView(generics.ListCreateAPIView):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        student_roll_number = self.request.data.get('student_id')
        event_id = self.request.data.get('event_id')
        
        serializer.save(student_id=student_roll_number, event_id=event_id)

class RegistrationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class RegisteredEventsView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user  
        registrations = Registration.objects.filter(student_id=user)
        registered_event_ids = [registration.event_id.event_id for registration in registrations]
        return Event.objects.filter(event_id__in=registered_event_ids)

class UpcomingEventsList(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        current_datetime = datetime.now()
        return Event.objects.filter(event_date__gte=current_datetime.date()).exclude(
            event_date=current_datetime.date(),
            event_time__lt=current_datetime.time()
        ).order_by('event_date', 'event_time')