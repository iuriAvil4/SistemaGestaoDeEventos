from django.urls import path
from .views import (ticket_sales_report,
                    ticket_status_report,
                    event_attendance,
                    ticket_type_list_for_published_events,
                    ticket_sales_detail,
                    events_with_ticket_types)

urlpatterns = [
    #Relatorio Gerais
    path('ticket_sales/<int:event_id>', ticket_sales_report),
    path('ticket_status/<int:event_id>', ticket_status_report),
    path('event_attendance/<int:event_id>', event_attendance),
    path('ticket_type_list_for_published_events/', ticket_type_list_for_published_events),
    path('ticket_sales_detail/', ticket_sales_detail),
    path('events_with_ticket_types/', events_with_ticket_types)
]
