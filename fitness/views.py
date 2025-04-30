from django.shortcuts import render, redirect
from .models import FitnessActivity, DietaryLog, WeightEntry, UserProfile
from .forms import UserRegisterForm, ActivityForm, DietaryLogForm, WeightEntryForm
from django.contrib.auth import logout
from collections import defaultdict
from django.db.models import Sum
from django.utils.timezone import localtime
from django.db.models.functions import TruncDate

def activity_list(request):
    activities = FitnessActivity.objects.filter(user=request.user)

    # Aggregate calories burned per date
    daily_data = defaultdict(int)
    for activity in activities:
        date_str = localtime(activity.date_time).strftime('%Y-%m-%d')
        daily_data[date_str] += activity.calories_burned

    chart_data = dict(sorted(daily_data.items()))

    return render(request, 'fitness/activity_list.html', {
        'activities': activities,
        'chart_data': chart_data
    })


    # Format for Chart.js
    chart_data = {entry['date'].strftime('%Y-%m-%d'): entry['total_calories'] for entry in calories_per_day}

    return render(request, 'fitness/activity_list.html', {
        'activities': activities,
        'chart_data': chart_data
    })
def custom_logout(request):
    logout(request)
    return redirect('login')

def diet_log(request):
    diet_logs = DietaryLog.objects.filter(user=request.user)

    # Get total calories per day
    calories_per_day = (
        diet_logs
        .annotate(date=TruncDate('date_time'))
        .values('date')
        .annotate(total_calories=Sum('calories'))
        .order_by('date')
    )

    chart_labels = [entry['date'].strftime('%Y-%m-%d') for entry in calories_per_day]
    chart_values = [entry['total_calories'] for entry in calories_per_day]

    return render(request, 'fitness/diet_log.html', {
        'diet_logs': diet_logs,
        'chart_labels': chart_labels,
        'chart_values': chart_values,
        'form': DietaryLogForm()
    })

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirect to the login page after successful registration
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'fitness/register.html', {'form': form})


def home(request):
    return render(request, 'fitness/home.html')


def add_activity(request):
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.user = request.user
            activity.save()
            return redirect('activity_list')
    else:
        form = ActivityForm()  # Make sure this line is correct

    return render(request, 'fitness/add_activity.html', {'form': form})

def add_diet_log(request):
    if request.method == 'POST':
        form = DietaryLogForm(request.POST)
        if form.is_valid():
            dietary_log = form.save(commit=False)
            dietary_log.user = request.user  # Set the user to the current user
            dietary_log.save()
            return redirect('diet_log')
    else:
        form = DietaryLogForm()
    return render(request, 'fitness/add_diet_log.html', {'form': form})



def weight_tracker(request):
    if request.method == 'POST':
        form = WeightEntryForm(request.POST)
        if form.is_valid():
            weight_entry = form.save(commit=False)
            weight_entry.user = request.user
            weight_entry.save()
            return redirect('weight_tracker')
    else:
        form = WeightEntryForm()

    # Fetch weight entries for the graph
    weight_entries = WeightEntry.objects.filter(user=request.user).order_by('date')
    dates = [entry.date.strftime("%Y-%m-%d") for entry in weight_entries]
    weights = [entry.weight for entry in weight_entries]

    return render(request, 'fitness/weight_tracker.html', {
        'form': form, 
        'dates': dates, 
        'weights': weights
    })


def profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    context = {
        'user': request.user,
        'user_profile': user_profile
    }
    return render(request, 'fitness/profile.html', context)
