from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Main Dashboard
    path('', views.dashboard, name='dashboard'),

    # Customers
    path('customers/', views.customers, name='customers'),
    path('add-customer/', views.add_customer, name='add_customer'),
    path('customers/edit/<int:pk>/', views.edit_customer, name='edit_customer'),
    path('customers/delete/<int:pk>/', views.delete_customer, name='delete_customer'),
    path('customers/detail/<int:pk>/', views.detail_customer, name='detail_customer'),

    # Leads
    path('leads/', views.leads, name='leads'),
    path('add-lead/', views.add_lead, name='add_lead'),
    path('leads/edit/<int:pk>/', views.edit_lead, name='edit_lead'),
    path('leads/delete/<int:pk>/', views.delete_lead, name='delete_lead'),
    path('leads/convert/<int:pk>/', views.convert_lead, name='convert_lead'),

    # Tasks
    path('tasks/', views.tasks, name='tasks'),
    path('add-task/', views.add_task, name='add_task'),
    path('tasks/edit/<int:pk>/', views.edit_task, name='edit_task'),
    path('tasks/toggle/<int:pk>/', views.toggle_task, name='toggle_task'),
    path('tasks/delete/<int:pk>/', views.delete_task, name='delete_task'),

    # Reports
    path('reports/', views.reports, name='reports'),
]
