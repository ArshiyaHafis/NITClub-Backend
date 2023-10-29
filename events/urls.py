from django.urls import path, include
from .views import UserCreateView, UserLoginView, UserDetailView, ClubListCreateView, ClubDetailView

urlpatterns = [
    path('register/', UserCreateView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('profile/', UserDetailView.as_view(), name='user-profile'),
    path('clubs/', ClubListCreateView.as_view(), name='club-list-create'),
    path('clubs/<str:pk>/', ClubDetailView.as_view(), name='club-detail'),
]
