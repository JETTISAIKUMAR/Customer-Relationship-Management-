from django.contrib import admin
from .models import UserProfile, Customer, Lead, Task, ActivityLog

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone')
    list_filter = ('role',)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'company', 'assigned_to', 'created_at')
    search_fields = ('name', 'email', 'company')
    list_filter = ('created_at',)

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'status', 'source', 'value', 'assigned_to', 'created_at')
    search_fields = ('name', 'email', 'company')
    list_filter = ('status', 'source')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_to', 'priority', 'status', 'due_date', 'created_at')
    list_filter = ('status', 'priority')
    search_fields = ('title', 'description')

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'user', 'timestamp')
    list_filter = ('timestamp',)
