from django.urls import path
from .views import home, student_bulk_upload, student_search, student_list,add_student_to_event, register_existing_student,  add_new_student_and_register, coordinator_events, event_student_report, faculty_dashboard, student_coordinator_dashboard

app_name = "accounts"

urlpatterns = [
    path("", home, name="home"),
    path("students/", student_list, name="student_list"),
    path("students/upload/", student_bulk_upload, name="student_bulk_upload"),
    path("students/search/", student_search, name="student_search"),
]
urlpatterns += [
    path(
        "events/<int:event_id>/add-students/",
        add_student_to_event,
        name="add_student_to_event",
    ),
    path(
        "events/<int:event_id>/add-existing/<int:student_id>/",
        register_existing_student,
        name="register_existing_student",
    ),
    path(
        "events/<int:event_id>/add-new/",
        add_new_student_and_register,
        name="add_new_student_and_register",
    ),
    path("coordinator/events/", coordinator_events, name="coordinator_events"),
    path(
        "reports/event-students/",
        event_student_report,
        name="event_student_report",
    ),
    path(
        "faculty/dashboard/",
        faculty_dashboard,
        name="faculty_dashboard",
    ),
    path(
        "student-coordinator/dashboard/",
        student_coordinator_dashboard,
        name="student_coordinator_dashboard",
    ),
]
