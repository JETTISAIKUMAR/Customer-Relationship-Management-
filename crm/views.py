import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from .models import Customer, Lead, Task, UserProfile, ActivityLog
from .forms import UserRegisterForm, CustomerForm, LeadForm, TaskForm

def log_activity(user, action, details=''):
    ActivityLog.objects.create(user=user if user.is_authenticated else None, action=action, details=details)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        u_name = request.POST.get('username')
        p_word = request.POST.get('password')
        user = authenticate(request, username=u_name, password=p_word)
        if user is not None:
            login(request, user)
            log_activity(user, "User Login", f"User '{user.username}' logged in successfully.")
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            role = form.cleaned_data['role']
            phone = form.cleaned_data['phone']
            UserProfile.objects.create(user=user, role=role, phone=phone)
            
            log_activity(user, "User Registration", f"New user '{user.username}' registered as {role}.")
            messages.success(request, "Account created successfully! Please log in.")
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = UserRegisterForm()

    return render(request, 'register.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        log_activity(request.user, "User Logout", f"User '{request.user.username}' logged out.")
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('login')


@login_required
def dashboard(request):
    user = request.user
    is_admin = hasattr(user, 'profile') and user.profile.role == 'ADMIN'

    # Metrics
    if is_admin:
        total_customers = Customer.objects.count()
        total_leads = Lead.objects.count()
        pending_tasks = Task.objects.filter(status='Pending').count()
        total_deal_val = Lead.objects.aggregate(total=Sum('value'))['total'] or 0
    else:
        total_customers = Customer.objects.filter(assigned_to=user).count()
        total_leads = Lead.objects.filter(assigned_to=user).count()
        pending_tasks = Task.objects.filter(assigned_to=user, status='Pending').count()
        total_deal_val = Lead.objects.filter(assigned_to=user).aggregate(total=Sum('value'))['total'] or 0

    converted_leads_count = Lead.objects.filter(status='Converted').count()
    all_leads_count = Lead.objects.count()
    conversion_rate = round((converted_leads_count / all_leads_count * 100), 1) if all_leads_count > 0 else 0

    # Status distribution data for Chart.js
    lead_status_counts = list(Lead.objects.values('status').annotate(count=Count('id')))
    status_labels = [item['status'] for item in lead_status_counts]
    status_data = [item['count'] for item in lead_status_counts]

    # Source distribution data for Chart.js
    lead_source_counts = list(Lead.objects.values('source').annotate(count=Count('id')))
    source_labels = [item['source'] for item in lead_source_counts]
    source_data = [item['count'] for item in lead_source_counts]

    # Recent activities
    recent_activities = ActivityLog.objects.all()[:8]

    # Recent tasks
    recent_tasks = Task.objects.filter(assigned_to=user) if not is_admin else Task.objects.all()
    recent_tasks = recent_tasks.order_by('-created_at')[:5]

    context = {
        'total_customers': total_customers,
        'total_leads': total_leads,
        'pending_tasks': pending_tasks,
        'conversion_rate': conversion_rate,
        'total_deal_val': total_deal_val,
        'recent_activities': recent_activities,
        'recent_tasks': recent_tasks,
        'status_labels_json': json.dumps(status_labels),
        'status_data_json': json.dumps(status_data),
        'source_labels_json': json.dumps(source_labels),
        'source_data_json': json.dumps(source_data),
        'is_admin': is_admin,
    }
    return render(request, 'dashboard.html', context)


@login_required
def customers(request):
    query = request.GET.get('q', '')
    if query:
        customer_list = Customer.objects.filter(name__icontains=query) | Customer.objects.filter(company__icontains=query)
    else:
        customer_list = Customer.objects.all().order_by('-created_at')

    return render(request, 'customers.html', {'customers': customer_list, 'query': query})


@login_required
def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            cust = form.save()
            log_activity(request.user, "Added Customer", f"Customer '{cust.name}' added.")
            messages.success(request, f"Customer '{cust.name}' created successfully!")
            return redirect('customers')
    else:
        form = CustomerForm()
    return render(request, 'customer_form.html', {'form': form, 'title': 'Add New Customer'})


@login_required
def edit_customer(request, pk):
    cust = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=cust)
        if form.is_valid():
            form.save()
            log_activity(request.user, "Updated Customer", f"Customer '{cust.name}' updated.")
            messages.success(request, f"Customer '{cust.name}' updated!")
            return redirect('customers')
    else:
        form = CustomerForm(instance=cust)
    return render(request, 'customer_form.html', {'form': form, 'title': 'Edit Customer', 'customer': cust})


@login_required
def delete_customer(request, pk):
    cust = get_object_or_404(Customer, pk=pk)
    name = cust.name
    cust.delete()
    log_activity(request.user, "Deleted Customer", f"Customer '{name}' was deleted.")
    messages.success(request, f"Customer '{name}' deleted.")
    return redirect('customers')


@login_required
def detail_customer(request, pk):
    cust = get_object_or_404(Customer, pk=pk)
    return render(request, 'customer_detail.html', {'customer': cust})


@login_required
def leads(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    
    lead_list = Lead.objects.all()
    if query:
        lead_list = lead_list.filter(name__icontains=query) | lead_list.filter(company__icontains=query)
    if status_filter:
        lead_list = lead_list.filter(status=status_filter)
        
    lead_list = lead_list.order_by('-created_at')
    
    return render(request, 'leads.html', {
        'leads': lead_list,
        'query': query,
        'selected_status': status_filter
    })


@login_required
def add_lead(request):
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save()
            log_activity(request.user, "Added Lead", f"Lead '{lead.name}' created.")
            messages.success(request, f"Lead '{lead.name}' created successfully!")
            return redirect('leads')
    else:
        form = LeadForm()
    return render(request, 'lead_form.html', {'form': form, 'title': 'Add New Lead'})


@login_required
def edit_lead(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            log_activity(request.user, "Updated Lead", f"Lead '{lead.name}' updated.")
            messages.success(request, f"Lead '{lead.name}' updated!")
            return redirect('leads')
    else:
        form = LeadForm(instance=lead)
    return render(request, 'lead_form.html', {'form': form, 'title': 'Edit Lead', 'lead': lead})


@login_required
def delete_lead(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    name = lead.name
    lead.delete()
    log_activity(request.user, "Deleted Lead", f"Lead '{name}' deleted.")
    messages.success(request, f"Lead '{name}' deleted.")
    return redirect('leads')


@login_required
def convert_lead(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    if lead.status == 'Converted':
        messages.info(request, f"Lead '{lead.name}' is already converted!")
        return redirect('leads')

    # Convert lead into Customer
    customer = Customer.objects.create(
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        company=lead.company,
        notes=f"Converted from Lead. Source: {lead.source}, Est Value: ${lead.value}",
        assigned_to=lead.assigned_to
    )
    lead.status = 'Converted'
    lead.save()

    log_activity(request.user, "Converted Lead", f"Lead '{lead.name}' converted into Customer '{customer.name}'.")
    messages.success(request, f"🚀 Lead '{lead.name}' has been successfully converted into a Customer!")
    return redirect('customers')


@login_required
def tasks(request):
    user = request.user
    status_filter = request.GET.get('status', '')

    if hasattr(user, 'profile') and user.profile.role == 'ADMIN':
        task_list = Task.objects.all()
    else:
        task_list = Task.objects.filter(assigned_to=user)

    if status_filter:
        task_list = task_list.filter(status=status_filter)

    task_list = task_list.order_by('-created_at')
    return render(request, 'tasks.html', {'tasks': task_list, 'selected_status': status_filter})


@login_required
def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            log_activity(request.user, "Added Task", f"Task '{task.title}' assigned to {task.assigned_to.username}.")
            messages.success(request, f"Task '{task.title}' created successfully!")
            return redirect('tasks')
    else:
        form = TaskForm()
    return render(request, 'task_form.html', {'form': form, 'title': 'Create New Task'})


@login_required
def edit_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            log_activity(request.user, "Updated Task", f"Task '{task.title}' updated.")
            messages.success(request, f"Task '{task.title}' updated!")
            return redirect('tasks')
    else:
        form = TaskForm(instance=task)
    return render(request, 'task_form.html', {'form': form, 'title': 'Edit Task', 'task': task})


@login_required
def toggle_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if task.status == 'Pending':
        task.status = 'In Progress'
    elif task.status == 'In Progress':
        task.status = 'Done'
    else:
        task.status = 'Pending'
    task.save()
    log_activity(request.user, "Task Status Toggle", f"Task '{task.title}' status changed to {task.status}.")
    messages.success(request, f"Task status updated to '{task.status}'!")
    return redirect('tasks')


@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    title = task.title
    task.delete()
    log_activity(request.user, "Deleted Task", f"Task '{title}' deleted.")
    messages.success(request, f"Task '{title}' deleted.")
    return redirect('tasks')


@login_required
def reports(request):
    total_customers = Customer.objects.count()
    total_leads = Lead.objects.count()
    converted_leads = Lead.objects.filter(status='Converted').count()
    conversion_rate = round((converted_leads / total_leads * 100), 1) if total_leads > 0 else 0
    total_pipeline_val = Lead.objects.aggregate(Sum('value'))['value__sum'] or 0

    # Performance per employee
    employee_stats = User.objects.annotate(
        assigned_leads=Count('leads'),
        assigned_tasks=Count('tasks'),
        assigned_customers=Count('customers')
    )

    context = {
        'total_customers': total_customers,
        'total_leads': total_leads,
        'converted_leads': converted_leads,
        'conversion_rate': conversion_rate,
        'total_pipeline_val': total_pipeline_val,
        'employee_stats': employee_stats,
    }
    return render(request, 'reports.html', context)
