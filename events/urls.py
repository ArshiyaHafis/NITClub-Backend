from django.urls import path, include
from .views import UserCreateView, UserLoginView, UserDetailView, ClubListCreateView, ClubDetailView, EventListCreateView, EventDetailView, RegistrationListCreateView, RegistrationDetailView, RegisteredEventsView,UpcomingEventsList


urlpatterns = [
    path('register/', UserCreateView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('profile/', UserDetailView.as_view(), name='user-profile'),
    path('clubs/', ClubListCreateView.as_view(), name='club-list-create'),
    path('clubs/<str:pk>/', ClubDetailView.as_view(), name='club-detail'),
    path('events/', EventListCreateView.as_view(), name='event-list-create'),
    path('events/<str:pk>/', EventDetailView.as_view(), name='event-detail'),
    path('registrations/', RegistrationListCreateView.as_view(), name='registration-list-create'),
    path('registrations/<str:pk>/', RegistrationDetailView.as_view(), name='registration-detail'),
    path('registered-events/', RegisteredEventsView.as_view(), name='registered-events'),
    path('upcoming-events/', UpcomingEventsList.as_view(), name='upcoming-events'),
]
