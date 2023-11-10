from django.db import models
from datetime import datetime
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import make_password

class CustomAutoField(models.Field):
    def db_type(self, connection):
        return 'char(10)'

    def get_internal_type(self):
        return 'CharField'

class CustomUserManager(BaseUserManager):
    def create_user(self, first_name, last_name, email, phone_number, roll_number, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)
        print("hehe")
        password = make_password(password)  
        user = self.model(first_name=first_name, last_name=last_name, email=email, phone_number=phone_number, roll_number=roll_number, **extra_fields)
        user.password = password
        user.save(using=self._db)
        return user

    def create_club_admin(self, first_name, last_name, email, phone_number, roll_number, password, club_position, **extra_fields):
        extra_fields.setdefault('isClubAdmin', True)  
        extra_fields.setdefault('club_position', club_position)
        return self.create_user(first_name, last_name, email, phone_number, roll_number, password, **extra_fields)

    def create_superuser(self, email, phone_number, roll_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('isClubAdmin', True)  

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email=email, phone_number=phone_number, roll_number=roll_number, password=password, **extra_fields)

class customuser(AbstractBaseUser, PermissionsMixin):
    HOSTEL_CHOICES = [(hostel, hostel) for hostel in ['MBH1', 'MBH2', 'MLH', 'LH1', 'LH2', 'LH3', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'PG']]
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    roll_number = models.CharField(max_length=15, primary_key=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    hostel_location = models.CharField(max_length=4, choices=HOSTEL_CHOICES)
    event_registration_count = models.IntegerField(default=0) 
    date_joined = models.DateTimeField(default=datetime.today)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    isClubAdmin = models.BooleanField(default=False)  
    admin_position = models.CharField(max_length=50, blank=True)


    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number', 'roll_number', 'hostel_location']

    def __str__(self):
        return self.roll_number
    
    def update_admin(self, admin_position=''):
        self.isClubAdmin = True
        self.admin_position = admin_position
        self.save()

    
class Club(models.Model):
    club_id = models.CharField(max_length=200, primary_key=True)
    club_name = models.CharField(max_length=200)
    club_fa = models.CharField(max_length=200)
    club_admin = models.ForeignKey(customuser, on_delete=models.CASCADE, default="B210021CS")
    club_opening_balance = models.FloatField()
    club_balance = models.FloatField(default=0)
    club_logo = models.ImageField(upload_to='images/club_logo/', blank=True)




class Event(models.Model):
    event_id = CustomAutoField(primary_key=True)
    event_name = models.CharField(max_length=200)
    event_date = models.DateField()
    event_time = models.TimeField()
    event_venue = models.CharField(max_length=300)
    event_budget = models.FloatField(null=True,default=0)
    event_cost = models.FloatField(null=True, default=0)
    event_regfee = models.FloatField()
    event_club = models.ForeignKey('Club', on_delete=models.CASCADE)
    event_image = models.ImageField(upload_to='images/event_images/', blank=True)
    event_students = models.IntegerField(default=0)
    event_profit = models.FloatField(default=0)

    def __str__(self):
        return self.event_name


class Registration(models.Model):
    reg_id = CustomAutoField(primary_key=True)
    student_id = models.ForeignKey(customuser, on_delete=models.CASCADE, default=1)
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['student_id', 'event_id']