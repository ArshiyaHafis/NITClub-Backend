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
        password = make_password(password)  # Hash the password
        user = self.model(first_name=first_name, last_name=last_name, email=email, phone_number=phone_number, roll_number=roll_number, **extra_fields)
        user.password = password
        user.save(using=self._db)
        return user

    def create_club_admin(self, first_name, last_name, email, phone_number, roll_number, password, **extra_fields):
        extra_fields.setdefault('isClubAdmin', True)  
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
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    roll_number = models.CharField(max_length=15, primary_key=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    date_joined = models.DateTimeField(default=datetime.today)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    isClubAdmin = models.BooleanField(default=False)  # Add isClubAdmin field
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number', 'roll_number']

    def __str__(self):
        return self.email
    
    def update_admin(self):
        self.isClubAdmin=True
        self.save()

    
class Club(models.Model):
    club_id = models.CharField(max_length=200, primary_key=True)
    club_name = models.CharField(max_length=200)
    club_fa = models.CharField(max_length=200)
    club_admin = models.ForeignKey(customuser, on_delete=models.CASCADE, default="B210021CS")
    club_opening_balance = models.FloatField()
    club_balance = models.FloatField()
    club_logo = models.ImageField(upload_to='images/club_logo/', blank=True)

    def update_balance(self):
        total_event_budget = Event.objects.filter(event_club=self).aggregate(total_budget=models.Sum('event_budget'))['total_budget'] or 0
        total_event_profit = Event.objects.filter(event_club=self).aggregate(total_profit=models.Sum('event_profit'))['total_profit'] or 0
        self.club_balance = self.club_opening_balance - total_event_budget + total_event_profit
        self.save()
        
    def save(self, *args, **kwargs):
        super(Club, self).save(*args, **kwargs)
        self.club_admin.update_admin()



class Event(models.Model):
    event_id = CustomAutoField(primary_key=True)
    event_name = models.CharField(max_length=200)
    event_date = models.DateField(default=datetime.today)
    event_time = models.TimeField()
    event_venue = models.CharField(max_length=300)
    event_budget = models.FloatField(null=True)
    event_cost = models.FloatField(null=True)
    event_regfee = models.FloatField()
    event_profit = models.FloatField(null=True)
    event_club = models.ForeignKey(Club, on_delete=models.CASCADE)
    event_image = models.ImageField(upload_to='images/event_images/', blank=True)
    event_students = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.event_id:
            last_id = Event.objects.all().order_by('-event_id').first()
            if last_id:
                last_id_value = int(last_id.event_id[1:])
                new_id_value = last_id_value + 1
                self.event_id = f'E{new_id_value:06}'
            else:
                self.event_id = 'E000001'
        
        self.event_profit = self.event_budget - self.event_cost
        super(Event, self).save(*args, **kwargs)
        self.event_club.update_balance()


class Registration(models.Model):
    reg_id = CustomAutoField(primary_key = True)
    student_id = models.ForeignKey(customuser, on_delete=models.CASCADE, default=1)
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE)


    def save(self, *args, **kwargs):
        if not self.reg_id:
            last_id = Registration.objects.all().order_by('-reg_id').first()
            if last_id:
                last_id_value = int(last_id.reg_id[1:])
                new_id_value = last_id_value + 1
                self.reg_id = f'R{new_id_value:06}'
            else:
                self.reg_id = 'R000001'

        super(Registration, self).save(*args, **kwargs)

        if self.event_id:
            event = self.event_id
            event.event_students = Registration.objects.filter(event_id=event).count()
            event.save()
