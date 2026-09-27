from .models import ActivityLog

def activity_context(request):
    """
    Context processor to make recent system activities available globally across all navbar templates.
    """
    if request.user.is_authenticated:
        activities = ActivityLog.objects.select_related('user').all()[:10]
        return {
            'navbar_activities': activities,
            'navbar_activities_count': activities.count(),
        }
    return {
        'navbar_activities': [],
        'navbar_activities_count': 0,
    }
