from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from crm.models import UserProfile, Customer, Lead, Task, ActivityLog
import datetime

class Command(BaseCommand):
    help = 'Seeds initial sample data for the CRM System'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Seeding CRM Database...'))

        # Create Admin User
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@crmtlc.com',
                'first_name': 'Sarah',
                'last_name': 'Connor',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            UserProfile.objects.create(user=admin_user, role='ADMIN', phone='+1 (555) 019-2831')
            self.stdout.write(self.style.SUCCESS('Admin user created: admin / admin123'))
        else:
            admin_user.profile.role = 'ADMIN'
            admin_user.profile.save()

        # Create Employee 1
        emp1, created = User.objects.get_or_create(
            username='employee1',
            defaults={
                'email': 'alex.m@crmtlc.com',
                'first_name': 'Alex',
                'last_name': 'Morgan'
            }
        )
        if created:
            emp1.set_password('emp123')
            emp1.save()
            UserProfile.objects.create(user=emp1, role='EMPLOYEE', phone='+1 (555) 014-9922')
            self.stdout.write(self.style.SUCCESS('Employee user created: employee1 / emp123'))

        # Create Employee 2
        emp2, created = User.objects.get_or_create(
            username='employee2',
            defaults={
                'email': 'david.k@crmtlc.com',
                'first_name': 'David',
                'last_name': 'Kumar'
            }
        )
        if created:
            emp2.set_password('emp123')
            emp2.save()
            UserProfile.objects.create(user=emp2, role='EMPLOYEE', phone='+1 (555) 018-3482')
            self.stdout.write(self.style.SUCCESS('Employee user created: employee2 / emp123'))

        # Seed Customers
        customers_data = [
            {'name': 'Acme Corporation', 'email': 'contact@acme.com', 'phone': '+1 555-1234', 'company': 'Acme Corp', 'notes': 'Key enterprise account looking for quarterly maintenance.', 'assigned_to': emp1},
            {'name': 'Stark Industries', 'email': 'tony@stark.io', 'phone': '+1 555-9876', 'company': 'Stark Ind', 'notes': 'Interested in high-end automation software licenses.', 'assigned_to': emp2},
            {'name': 'Wayne Enterprises', 'email': 'bruce@wayne.org', 'phone': '+1 555-4321', 'company': 'Wayne Ent', 'notes': 'Long-term cloud services partner.', 'assigned_to': admin_user},
            {'name': 'Cyberdyne Systems', 'email': 'info@cyberdyne.net', 'phone': '+1 555-8765', 'company': 'Cyberdyne', 'notes': 'AI and robotics integration hardware.', 'assigned_to': emp1},
        ]

        for c_data in customers_data:
            Customer.objects.get_or_create(email=c_data['email'], defaults=c_data)

        # Seed Leads
        leads_data = [
            {'name': 'NexusTech Solutions', 'email': 'sales@nexustech.com', 'phone': '+1 555-0011', 'company': 'NexusTech', 'source': 'Website', 'status': 'New', 'value': 12500.00, 'assigned_to': emp1},
            {'name': 'Global Dynamics', 'email': 'inquiries@gdynamics.com', 'phone': '+1 555-0022', 'company': 'Global Dynamics', 'source': 'Referral', 'status': 'In Progress', 'value': 35000.00, 'assigned_to': emp2},
            {'name': 'Apex Logistics', 'email': 'hello@apexlog.com', 'phone': '+1 555-0033', 'company': 'Apex Logistics', 'source': 'Cold Call', 'status': 'Contacted', 'value': 8200.00, 'assigned_to': emp1},
            {'name': 'Vanguard Media', 'email': 'media@vanguard.io', 'phone': '+1 555-0044', 'company': 'Vanguard', 'source': 'Social Media', 'status': 'Converted', 'value': 45000.00, 'assigned_to': admin_user},
            {'name': 'Omni Consumer Products', 'email': 'leads@ocp.corp', 'phone': '+1 555-0055', 'company': 'OCP', 'source': 'Event', 'status': 'Lost', 'value': 18000.00, 'assigned_to': emp2},
        ]

        for l_data in leads_data:
            Lead.objects.get_or_create(email=l_data['email'], defaults=l_data)

        # Seed Tasks
        tasks_data = [
            {'title': 'Follow up with NexusTech proposal', 'description': 'Send updated pricing sheet and contract draft.', 'assigned_to': emp1, 'priority': 'High', 'status': 'Pending', 'due_date': datetime.date.today() + datetime.timedelta(days=2)},
            {'title': 'Schedule demo for Global Dynamics', 'description': 'Prepare CRM analytics presentation slides.', 'assigned_to': emp2, 'priority': 'High', 'status': 'In Progress', 'due_date': datetime.date.today() + datetime.timedelta(days=1)},
            {'title': 'Review monthly sales metrics', 'description': 'Generate performance audit report for Q3.', 'assigned_to': admin_user, 'priority': 'Medium', 'status': 'Done', 'due_date': datetime.date.today() - datetime.timedelta(days=1)},
            {'title': 'Update Stark Industries contact info', 'description': 'Verify new procurement manager details.', 'assigned_to': emp2, 'priority': 'Low', 'status': 'Pending', 'due_date': datetime.date.today() + datetime.timedelta(days=5)},
        ]

        for t_data in tasks_data:
            Task.objects.get_or_create(title=t_data['title'], defaults=t_data)

        # Seed Activity Logs
        ActivityLog.objects.get_or_create(action='Database Seeded', user=admin_user, defaults={'details': 'Initial sample dataset populated successfully.'})

        self.stdout.write(self.style.SUCCESS('CRM Database successfully seeded with sample users, customers, leads, and tasks!'))
