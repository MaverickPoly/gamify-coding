from django.urls import path
from . import views


urlpatterns = [
    # Auth
    path("auth/register/", views.register, name="register"),
    path("auth/login/", views.login_view, name="login"),
    path("auth/logout/", views.logout_view, name="logout"),
    path("u/<int:user_id>/", views.user_profile, name="profile"),

    # Project
    path("", views.all_languages, name="all_languages"),
    path("lang/<str:language>/", views.all_projects, name="all_projects"),
    path("project/<int:project_id>/", views.project_detail, name="project_detail"),
    path("search/", views.search_results, name="search_results"),

    # Completed Projects
    path("project/<int:project_id>/complete/", views.complete_project, name="complete_project"),
    path("leaderboard/", views.leaderboard_view, name="leaderboard"),

    # Random Pages
    path("random-language/", views.random_language, name="random_language"),
    path("random-field/", views.random_field, name="random_field"),
    path("random-project/", views.random_project, name="random_project"),
]