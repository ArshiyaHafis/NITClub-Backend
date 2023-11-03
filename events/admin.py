from django.contrib import admin
from .models import Event, Club, customuser, Registration

# Register your models here.
admin.site.register(Event)
admin.site.register(Club)
admin.site.register(customuser)
admin.site.register(Registration)

# new_club = Club(club_id="C123", club_name="Club1", club_fa="FA1", club_opening_balance=1000.0, club_balance=1000.0)
# new_event = Event(event_name="Sample Event", event_date="2023-10-30",event_time="15:00:00", event_venue="Sample Venue", event_budget=1000.00, event_cost=500.00, event_regfee=20.00, event_club=new_club)
# new_reg=Registration(student_id=user, event_id=new_event)
# new_user.set_password(password)
# new_user = customuser(first_name="Aritro", last_name="Ghosh", email="aritro_b210466cs@nitc.ac.in", phone_number="9007213007", roll_number="B210466CS", password = "aritro")
# new_user = customuser(first_name="Chandrakant", last_name="V Bellary", email="chandrakant_b210462cs@nitc.ac.in", phone_number="8137005243", roll_number="B210462CS", password = "chandu")
# new_user = customuser(first_name="Allamaneni", last_name="Srikar", email="allamaneni_b210492cs@nitc.ac.in", phone_number="8328489716", roll_number="B210492CS", password = "Srikar")
# new_club = Club(club_id="C456", club_name="Club2", club_fa="FA2", club_opening_balance=1500.0, club_balance=600.0, club_admin_id=new_user)
# {
#   "event_id": "E000001",
#   "event_club": "C123",
#   "event_name": "Sample Event",
#   "event_date": "2023-10-30",
#   "event_time": "15:00:00",
#   "event_venue": "Sample Venue",
#   "event_budget": null,
#   "event_cost": null,
#   "event_regfee": 20.0,
#   "event_image": null,
#   "event_students": 1,
#   "event_profit": 0.0
# }