from django.urls import path
from tickets.views import (
    TicketListCreateView,
    TicketDetailView,
    BuyerTicketsListView,
    TicketTypeListCreateView,
    TicketTypeDetailView,
    PayTicketView,
    UseTicketView
)

urlpatterns = [
    # Tickets URLs
    path('tickets/', TicketListCreateView.as_view(), name='ticket-list-create'),
    path('tickets/<int:pk>/', TicketDetailView.as_view(), name='ticket-detail'),
    path('tickets/buyer/', BuyerTicketsListView.as_view(), name='buyer-ticket-list'),

    # Ticket Types URLs
    path('ticket-types/', TicketTypeListCreateView.as_view(), name='ticket-type-list-create'),
    path('ticket-types/<int:pk>/', TicketTypeDetailView.as_view(), name='ticket-type-detail'),

    # Ticket Usage
    path('tickets/<int:ticket_id>/pay/', PayTicketView.as_view(), name='pay_ticket'),
    path('tickets/<int:ticket_id>/use/', UseTicketView.as_view(), name='use_ticket'),
]

