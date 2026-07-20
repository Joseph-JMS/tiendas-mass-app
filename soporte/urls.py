from django.urls import path

from soporte import views

app_name = 'soporte'

urlpatterns = [
    path('nuevo/', views.crear_ticket, name='crear_ticket'),
    path('mis-tickets/', views.mis_tickets, name='mis_tickets'),
    path('panel/', views.lista_tickets, name='lista_tickets'),
    path('panel/<int:ticket_id>/atender/', views.atender_ticket, name='atender_ticket'),
    path('mantenimiento/', views.panel_mantenimiento, name='panel_mantenimiento'),
    path('mantenimiento/prueba/', views.registrar_log_prueba, name='registrar_log_prueba'),
    path('chatbot/responder/', views.chatbot_responder, name='chatbot_responder'),
]