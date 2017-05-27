from django.contrib import admin

from .models import Group, Ticket, User, Contest, Current, School, Contestant, Participate, Vote


admin.site.register((Group, Ticket, User, Contest, Current, School, Contestant, Participate, Vote))
