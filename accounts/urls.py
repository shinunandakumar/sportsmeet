from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # -------------------------
    # Auth
    # -------------------------
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # -------------------------
    # Student management
    # -------------------------
    path("students/", views.student_list, name="student_list"),
    path("students/upload/", views.student_bulk_upload, name="student_bulk_upload"),
    path("students/search/", views.student_search, name="student_search"),

    # -------------------------
    # Event & registration
    # -------------------------
    path(
        "events/<int:event_id>/add-students/",
        views.add_student_to_event,
        name="add_student_to_event",
    ),
    path(
        "events/<int:event_id>/add-existing/<int:student_id>/",
        views.register_existing_student,
        name="register_existing_student",
    ),
    path(
        "events/<int:event_id>/add-new/",
        views.add_new_student_and_register,
        name="add_new_student_and_register",
    ),

    # -------------------------
    # Student self-registration
    # -------------------------
    path(
        "student/register-event/<int:event_id>/",
        views.student_register_event,
        name="student_register_event",
    ),

    # -------------------------
    # Coordinator
    # -------------------------
    path(
        "coordinator/events/",
        views.coordinator_events,
        name="coordinator_events",
    ),

    # -------------------------
    # Reports
    # -------------------------
    path(
        "reports/event-students/",
        views.event_student_report,
        name="event_student_report",
    ),

    # -------------------------
    # Dashboards
    # -------------------------
    path(
        "student/dashboard/",
        views.student_dashboard,
        name="student_dashboard",
    ),
    path(
        "student-coordinator/dashboard/",
        views.student_coordinator_dashboard,
        name="student_coordinator_dashboard",
    ),
    path(
        "faculty/dashboard/",
        views.faculty_dashboard,
        name="faculty_dashboard",
    ),
    path(
        "faculty-coordinator/dashboard/",
        views.faculty_coordinator_dashboard,
        name="faculty_coordinator_dashboard",
    ),
]
