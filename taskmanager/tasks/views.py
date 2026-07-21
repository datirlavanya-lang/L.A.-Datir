
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db.models import Count, Q
from django.utils import timezone
from .models import Task
from .forms import TaskForm, RegisterForm

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'tasks/register.html', {'form': form})

@login_required
def dashboard(request):
    tasks = Task.objects.filter(user=request.user)
    
    # Statistics
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status='Completed').count()
    pending_tasks = tasks.filter(status='Pending').count()
    in_progress_tasks = tasks.filter(status='In Progress').count()
    overdue_tasks = tasks.filter(
        due_date__lt=timezone.now().date(),
        status__in=['Pending', 'In Progress']
    ).count()
    
    # Priority breakdown
    high_priority = tasks.filter(priority__in=['High', 'Urgent'], status__in=['Pending', 'In Progress']).count()
    
    # Recent tasks
    recent_tasks = tasks.order_by('-created_at')[:5]
    
    # Tasks due soon
    upcoming_tasks = tasks.filter(
        due_date__gte=timezone.now().date(),
        due_date__lte=timezone.now().date() + timezone.timedelta(days=7),
        status__in=['Pending', 'In Progress']
    ).order_by('due_date')[:5]
    
    # Priority counts for dashboard
    urgent_count = tasks.filter(priority='Urgent').count()
    high_count = tasks.filter(priority='High').count()
    medium_count = tasks.filter(priority='Medium').count()
    low_count = tasks.filter(priority='Low').count()
    
    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'overdue_tasks': overdue_tasks,
        'high_priority': high_priority,
        'recent_tasks': recent_tasks,
        'upcoming_tasks': upcoming_tasks,
        'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1),
        'urgent_count': urgent_count,
        'high_count': high_count,
        'medium_count': medium_count,
        'low_count': low_count,
    }
    
    return render(request, 'tasks/dashboard.html', context)


@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    # Filter by priority
    priority_filter = request.GET.get('priority', '')
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    
    # Sort by
    sort_by = request.GET.get('sort', 'created_at')
    if sort_by in ['title', 'status', 'priority', 'due_date', 'created_at']:
        tasks = tasks.order_by(sort_by)
    
    context = {
        'tasks': tasks,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'sort_by': sort_by,
    }
    return render(request, 'tasks/task_list.html', context)


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form})


@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form})


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')
    return render(request, 'tasks/task_delete.html', {'task': task})

@login_required
def reports(request):
    tasks = Task.objects.filter(user=request.user)
    
    # Statistics for reports
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status='Completed').count()
    pending_tasks = tasks.filter(status='Pending').count()
    in_progress_tasks = tasks.filter(status='In Progress').count()
    
    # Priority breakdown
    urgent_tasks = tasks.filter(priority='Urgent').count()
    high_tasks = tasks.filter(priority='High').count()
    medium_tasks = tasks.filter(priority='Medium').count()
    low_tasks = tasks.filter(priority='Low').count()
    
    # Recent activity
    recent_tasks = tasks.order_by('-created_at')[:10]
    
    # Calculate percentages
    urgent_percentage = round((urgent_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
    high_percentage = round((high_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
    medium_percentage = round((medium_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
    low_percentage = round((low_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
    
    completed_percentage = round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
    in_progress_percentage = round((in_progress_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
    pending_percentage = round((pending_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
    
    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'urgent_tasks': urgent_tasks,
        'high_tasks': high_tasks,
        'medium_tasks': medium_tasks,
        'low_tasks': low_tasks,
        'recent_tasks': recent_tasks,
        'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1),
        'urgent_percentage': urgent_percentage,
        'high_percentage': high_percentage,
        'medium_percentage': medium_percentage,
        'low_percentage': low_percentage,
        'completed_percentage': completed_percentage,
        'in_progress_percentage': in_progress_percentage,
        'pending_percentage': pending_percentage,
    }
    
    return render(request, 'tasks/reports.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        # Handle profile update
        user = request.user
        email = request.POST.get('email')
        if email:
            user.email = email
            user.save()
        return redirect('profile')
    
    # Get user statistics
    tasks = Task.objects.filter(user=request.user)
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status='Completed').count()
    
    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1),
    }
    
    return render(request, 'tasks/profile.html', context)
