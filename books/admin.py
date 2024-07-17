from django.contrib import admin

from books.models import Ticket, TicketPassenger

# Register your models here.
admin.site.register(Ticket)
admin.site.register(TicketPassenger)
