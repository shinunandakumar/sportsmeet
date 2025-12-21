import csv

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q

from .models import User, Department, UserRole
from .forms import StudentBulkUploadForm, ManualStudentAddForm
from meet.models import Event, Registration
from django.contrib.auth import logout


# -----------------------------
# HOME
# -----------------------------

def home(request):
    return render(request, "accounts/home.html")


# -----------------------------
# SINGLE LOGIN VIEW (ALL ROLES)
# -----------------------------

def login_view(request):
    # -------------------------
    # GET REQUEST → SHOW LOGIN
    # -------------------------
    if request.method == "GET":
        return render(request, "accounts/login.html")

    # -------------------------
    # POST REQUEST → LOGIN
    # -------------------------
    identifier = request.POST.get("username")
    password = request.POST.get("password")
    selected_role = request.POST.get("role")

    user = None

    # Student login via register number
    if selected_role == UserRole.STUDENT:
        try:
            u = User.objects.get(register_number=identifier)
            user = authenticate(
                request,
                email=u.email,
                password=password
            )
        except User.DoesNotExist:
            user = None

    # Others login via email
    else:
        user = authenticate(
            request,
            email=identifier,
            password=password
        )

    if user is None:
        messages.error(request, "Invalid credentials")
        return render(request, "accounts/login.html")

    if user.role != selected_role:
        messages.error(request, "Role mismatch")
        return render(request, "accounts/login.html")

    login(request, user)

    # -------------------------
    # ROLE-BASED REDIRECT
    # -------------------------
    if user.role == UserRole.STUDENT:
        return redirect("accounts:student_dashboard")

    elif user.role == UserRole.STUDENT_COORDINATOR:
        return redirect("accounts:student_coordinator_dashboard")

    elif user.role == UserRole.FACULTY:
        return redirect("accounts:faculty_dashboard")

    elif user.role == UserRole.FACULTY_COORDINATOR:
        return redirect("accounts:faculty_coordinator_dashboard")

    # Safety fallback
    logout(request)
    messages.error(request, "Invalid role")
    return redirect("accounts:login")

# -----------------------------
# DASHBOARDS
@login_required
def student_dashboard(request):
    if request.user.role != UserRole.STUDENT:
        return HttpResponseForbidden("Access denied")

    # Already registered events
    registrations = (
        Registration.objects
        .filter(participant=request.user)
        .select_related("event", "event__meet")
    )

    registered_event_ids = registrations.values_list("event_id", flat=True)

    # Gender-based event filter
    if request.user.gender == "MALE":
        allowed_gender = "BOYS"
    else:
        allowed_gender = "GIRLS"

    available_events = (
        Event.objects
        .filter(
            meet__status="ACTIVE",
            status="ACTIVE",
            gender=allowed_gender
        )
        .exclude(id__in=registered_event_ids)
        .select_related("meet")
    )

    return render(
        request,
        "accounts/dashboards/student_dashboard.html",
        {
            "student": request.user,
            "registrations": registrations,
            "available_events": available_events,
        },
    )

@login_required
def student_coordinator_dashboard(request):
    if request.user.role != UserRole.STUDENT_COORDINATOR:
        return HttpResponseForbidden("Access denied")

    registrations = (
        Registration.objects
        .select_related("participant", "event", "event__meet")
    )

    return render(
        request,
        "accounts/dashboards/student_coordinator_dashboard.html",
        {"registrations": registrations},
    )


@login_required
def faculty_dashboard(request):
    if request.user.role != UserRole.FACULTY:
        return HttpResponseForbidden("Access denied")

    events = Event.objects.filter(
        meet__status="ACTIVE"
    ).select_related("meet")

    return render(
        request,
        "accounts/dashboards/faculty_dashboard.html",
        {"events": events},
    )


@login_required
def faculty_coordinator_dashboard(request):
    if request.user.role != UserRole.FACULTY_COORDINATOR:
        return HttpResponseForbidden("Access denied")

    events = (
        Event.objects
        .all()
        .select_related("meet")
        .prefetch_related("registrations")
    )

    return render(
        request,
        "accounts/dashboards/faculty_coordinator_dashboard.html",
        {"events": events},
    )



# -----------------------------
# PERMISSION CHECK
# -----------------------------
def is_admin_or_coordinator(user):
    return user.role in [
        UserRole.ADMIN,
        UserRole.FACULTY_COORDINATOR,
        UserRole.STUDENT_COORDINATOR,
    ]


# -----------------------------
# STUDENT BULK UPLOAD
# -----------------------------
@login_required
def student_bulk_upload(request):
    if not is_admin_or_coordinator(request.user):
        return HttpResponseForbidden("Not allowed")

    if request.method == "POST":
        form = StudentBulkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES["csv_file"]
            decoded = csv_file.read().decode("utf-8").splitlines()
            reader = csv.DictReader(decoded)

            for row in reader:
                department, _ = Department.objects.get_or_create(
                    name=row["department"]
                )

                User.objects.get_or_create(
                    register_number=row["register_number"],
                    defaults={
                        "full_name": row["full_name"],
                        "email": row["email"],
                        "department": department,
                        "role": UserRole.STUDENT,
                    },
                )

            return redirect("accounts:student_list")
    else:
        form = StudentBulkUploadForm()

    return render(
        request,
        "accounts/student_bulk_upload.html",
        {"form": form},
    )


@login_required
def logout_view(request):
    logout(request)
    return redirect("accounts:login")

# -----------------------------
# STUDENT SEARCH
# -----------------------------
@login_required
def student_search(request):
    if not is_admin_or_coordinator(request.user):
        return HttpResponseForbidden("Not allowed")

    query = request.GET.get("q", "")

    students = User.objects.filter(
        role=UserRole.STUDENT
    ).filter(
        Q(full_name__icontains=query)
        | Q(register_number__icontains=query)
    )

    return render(
        request,
        "accounts/student_search.html",
        {"students": students, "query": query},
    )


# -----------------------------
# STUDENT LIST
# -----------------------------
@login_required
def student_list(request):
    if not is_admin_or_coordinator(request.user):
        return HttpResponseForbidden("Not allowed")

    students = User.objects.filter(role=UserRole.STUDENT)

    return render(
        request,
        "accounts/student_list.html",
        {"students": students},
    )


# -----------------------------
# EVENT REGISTRATION
# -----------------------------
@login_required
def add_student_to_event(request, event_id):
    if not is_admin_or_coordinator(request.user):
        return HttpResponseForbidden("Not allowed")

    event = get_object_or_404(Event, id=event_id)
    query = request.GET.get("q", "")
    students = []

    if query:
        students = User.objects.filter(
            role=UserRole.STUDENT
        ).filter(
            Q(full_name__icontains=query)
            | Q(register_number__icontains=query)
        )

    manual_form = ManualStudentAddForm()

    return render(
        request,
        "accounts/add_student_to_event.html",
        {
            "event": event,
            "students": students,
            "query": query,
            "manual_form": manual_form,
        },
    )


@login_required
def register_existing_student(request, event_id, student_id):
    if not is_admin_or_coordinator(request.user):
        return HttpResponseForbidden("Not allowed")

    event = get_object_or_404(Event, id=event_id)

    if event.status != "ACTIVE":
        return HttpResponseForbidden("Event is not active")

    student = get_object_or_404(
        User, id=student_id, role=UserRole.STUDENT
    )

    Registration.objects.get_or_create(
        event=event,
        participant=student,
        defaults={"registered_by": request.user},
    )

    return redirect(
        "accounts:add_student_to_event",
        event_id=event.id,
    )


@login_required
def add_new_student_and_register(request, event_id):
    if not is_admin_or_coordinator(request.user):
        return HttpResponseForbidden("Not allowed")

    if request.method != "POST":
        return HttpResponseForbidden("Invalid request")

    event = get_object_or_404(Event, id=event_id)

    if event.status != "ACTIVE":
        return HttpResponseForbidden("Event is not active")

    form = ManualStudentAddForm(request.POST)
    if form.is_valid():
        student = form.save()
        Registration.objects.get_or_create(
            event=event,
            participant=student,
            defaults={"registered_by": request.user},
        )

    return redirect(
        "accounts:add_student_to_event",
        event_id=event.id,
    )


# -----------------------------
# COORDINATOR EVENTS
# -----------------------------
@login_required
def coordinator_events(request):
    if not is_admin_or_coordinator(request.user):
        return HttpResponseForbidden("Not allowed")

    events = Event.objects.filter(status="ACTIVE")

    return render(
        request,
        "accounts/coordinator_events.html",
        {"events": events},
    )


# -----------------------------
# EVENT REPORT
# -----------------------------
@login_required
def event_student_report(request):
    if not is_admin_or_coordinator(request.user):
        return HttpResponseForbidden("Not allowed")

    query = request.GET.get("q", "").lower()

    events = Event.objects.filter(
        status="ACTIVE"
    ).prefetch_related("registrations__participant")

    result = []

    for event in events:
        regs = event.registrations.all()

        if query:
            regs = [
                r for r in regs
                if query in r.participant.full_name.lower()
                or query in r.participant.register_number.lower()
            ]

        if regs:
            result.append(
                {"event": event, "registrations": regs}
            )

    return render(
        request,
        "accounts/event_student_report.html",
        {"events": result, "query": query},
    )

@login_required
def student_register_event(request, event_id):
    if request.user.role != UserRole.STUDENT:
        return HttpResponseForbidden("Access denied")

    event = get_object_or_404(Event, id=event_id)

    # Gender check
    if request.user.gender == "MALE" and event.gender != "BOYS":
        return HttpResponseForbidden("Not allowed")

    if request.user.gender == "FEMALE" and event.gender != "GIRLS":
        return HttpResponseForbidden("Not allowed")

    Registration.objects.get_or_create(
        event=event,
        participant=request.user,
        defaults={"registered_by": request.user},
    )

    return redirect("accounts:student_dashboard")
