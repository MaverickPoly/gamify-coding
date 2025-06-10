from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Lower
from django.db.models import Q
from django.db.models import Count
from django.core.paginator import Paginator

from .models import *
import random

# ====== Auth Views

def register(request: HttpRequest):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        bio = request.POST.get("bio")

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("register")
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken!")
            return redirect("register")
        
        user = User(
            username=username, email=email
        )
        user.set_password(password)
        user.save()
        userProfile = UserProfile.objects.create(
            user=user, bio=bio
        )

        messages.success(request, "Registration successful!")
        return redirect("login")
    else:
        context = {
            "fields": ['username','email','password','confirm_password','bio'],
            "pw_fields": ["password", "confirm_password"]
        }
        return render(request, "auth/register.html", context)
    

def login_view(request: HttpRequest):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("profile", user_id=user.id)
        else:
            messages.error(request, "Invalid credentials!")
            return redirect("login")
    else:
        context = {
            "fields": ["username", "password"],
        }
        return render(request, "auth/login.html", context)

@login_required(login_url="/auth/login/")
def logout_view(request: HttpRequest):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("login")


# Get User's Profile
@login_required(login_url="/auth/login/")
def user_profile(request: HttpRequest, user_id: int):
    user = get_object_or_404(User, id=user_id)
    completed_projects = user.completed_projects.select_related('project').all()
    context = {
        "user": user,
        "completed_projects": completed_projects,
    }
    return render(request, "profile.html", context)


# ====== Project Views
# View All programming Languages
@login_required(login_url="/auth/login/")
def all_languages(request):
    languages = Project.objects.values('programming_language') \
        .annotate(count=Count('id')) \
        .order_by('programming_language')

    language_dict = {lang['programming_language']: lang['count'] for lang in languages}

    return render(request, 'all_languages.html', {'languages': language_dict})


# View projects inside programming langauges
@login_required(login_url="/auth/login/")
def all_projects(request: HttpRequest, language: str):
    projects = Project.objects.filter(programming_language=language)
    completed_ids = CompletedProject.objects.filter(user=request.user).values_list('project_id', flat=True)

    context = {
        "projects": projects,
        "completed_ids": set(completed_ids),
    }
    return render(request, "all_projects.html", context)

@login_required(login_url="/auth/login/")
def project_detail(request: HttpRequest, project_id: int):
    project = get_object_or_404(Project, id=project_id)
    is_completed = CompletedProject.objects.filter(user=request.user, project=project).exists()
    context = {
        "project": project,
        "is_completed": is_completed
    }
    return render(request, "project_detail.html", context)


# Search Results
@login_required(login_url="/auth/login/")
def search_results(request):
    query = request.GET.get("query", "")
    language = request.GET.get("lang", "")
    difficulty: str = request.GET.get("difficulty", "")
    category = request.GET.get("category", "")
    page_number = request.GET.get("page")

    projects = Project.objects.all()

    if query:
        projects = projects.filter(title__icontains=query)

    if language:
        projects = projects.filter(programming_language=language)

    if difficulty:
        projects = projects.filter(difficulty=difficulty.title())

    if category:
        projects = projects.filter(field=category)

    paginator = Paginator(projects, 52)  # Show 52 projects per page
    page_obj = paginator.get_page(page_number)

    completed_ids = CompletedProject.objects.filter(user=request.user).values_list('project_id', flat=True)

    context = {
        "page_obj": page_obj,
        "query": query,
        "language": language,
        "difficulty": difficulty,
        "category": category,
        "languages": Project.objects.values_list('programming_language', flat=True).distinct(),
        "completed_ids": set(completed_ids),
        "project": Project,  # for DIFFICULTY_CHOICES etc.
    }
    return render(request, "search_results.html", context)


# ====== Completed Project Views
# Complete Project
@login_required(login_url="/auth/login/")
def complete_project(request: HttpRequest, project_id: int):
    project = get_object_or_404(Project, id=project_id)

    if CompletedProject.objects.filter(user=request.user, project=project).exists():
        messages.error(request, "You already completed this project!")
        return redirect("project_detail", project_id=project_id)

    if request.method == "POST":
        github_link = request.POST.get("github_link")

        completed_project = CompletedProject.objects.create(
            user=request.user,
            project=project,
            github_link=github_link
        )

        messages.success(request, "Project completed successfully!")
        return redirect("all_languages")
    else:
        context = {
            "project": project
        }
        return render(request, "complete_project.html", context)


# Leaderboard view
@login_required(login_url="/auth/login/")
def leaderboard_view(request: HttpRequest):
    users = UserProfile.objects.all().order_by("-xp")
    context = {
        "users": users
    }
    return render(request, "leaderboard.html", context)


# ====== Random Wheel Views
@login_required(login_url="/auth/login/")
def random_language(request: HttpRequest):
    languages = Project.objects.values_list('programming_language', flat=True).distinct()
    if not languages:
        return render(request, "random_page.html", {"title": "Random Language", "result": "No languages available."})
    lang = random.choice([lang for lang in languages if lang])
    context = {
        "title": "Random Language", 
        "result": lang
    }
    return render(request, "random_page.html", context)

@login_required(login_url="/auth/login/")
def random_field(request: HttpRequest):
    fields = dict(Project.FIELD_CHOICES).values()
    field = random.choice(list(fields))
    context = {
        "title": "Random Field", 
        "result": field
    }
    return render(request, "random_page.html", context)

@login_required(login_url="/auth/login/")
def random_project(request: HttpRequest):
    project = Project.objects.order_by("?").first()
    if not project:
        context = {
            "title": "Random Project", 
            "result": "No project available."
        }
        return render(request, "random_page.html", context)
    return redirect("project_detail", project_id=project.id)



