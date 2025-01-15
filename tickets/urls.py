from django.urls import path
from .views import (create_ticket_type, 
                    list_ticket_types, 
                    update_ticket_type, 
                    delete_ticket_type, 
                    create_ticket, 
                    list_tickets, 
                    list_user_tickets, 
                    list_tickets_by_buyer, 
                    update_ticket,
                    delete_ticket)

urlpatterns = [
    path('create_ticket_type/', create_ticket_type),
    path('list_ticket_types/', list_ticket_types),
    path('update_ticket_type/<int:id>', update_ticket_type),
    path('delete_ticket_type/<int:id>', delete_ticket_type),

    path('create_ticket/', create_ticket),
    path('list_tickets/', list_tickets),
    path('list_user_tickets/', list_user_tickets),
    path('list_tickets_by_buyer/<int:id>', list_tickets_by_buyer),
    path('update_ticket/<int:id>', update_ticket),
    path('delete_ticket/<int:id>', delete_ticket)
]
