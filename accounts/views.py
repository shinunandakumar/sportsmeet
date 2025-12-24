import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Q

from .models import User, Department, UserRole
from .forms import StudentBulkUploadForm, ManualStudentAddForm
from meet.models import Event, Registration




@login_required
def home(request):
    return render(request, "accounts/home.html")




def is_admin_or_coordinator(user):
    return user.role in [
        UserRole.ADMIN,
        UserRole.FACULTY_COORDINATOR,
        UserRole.STUDENT_COORDINATOR,
    ]


def get_user_department(user):
    if user.role in (
        UserRole.FACULTY_COORDINATOR,
        UserRole.STUDENT_COORDINATOR,
    ):
        return user.department
    return None


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
                    }
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
def student_search(request):
    if not is_admin_or_coordinator(request.user):
        return HttpResponseForbidden("Not allowed")

    query = request.GET.get("q", "")
    
    dept = get_user_department(request.user)
    students = User.objects.filter(role=UserRole.STUDENT)
    
    if dept:
        students = students.filter(department=dept)

    students = students.filter(
        Q(full_name__icontains=query) |
        Q(register_number__icontains=query)
    )

    return render(
        request,
        "accounts/student_search.html",
        {
            "students": students,
            "query": query,
        }
    )

    

    
    
@login_required
def student_list(request):
    if not is_admin_or_coordinator(request.user):
        return HttpResponseForbidden("Not allowed")
    
    dept = get_user_department(request.user)
    students = User.objects.filter(role=UserRole.STUDENT)
    
    if dept:
        students = students.filter(department=dept)

    return render(
        request,
        "accounts/student_list.html",
        {"students": students},
    )



@login_required
def add_student_to_event(request, event_id):
    if not is_admin_or_coordinator(request.user):
        return HttpResponseForbidden("Not allowed")

    event = get_object_or_404(Event, id=event_id)
    query = request.GET.get("q", "")
    students = []
    
    dept = get_user_department(request.user)

    if query:
        students = User.objects.filter(role=UserRole.STUDENT)
        
        if dept:
            students = students.filter(department=dept)
            
        students = students.filter(
            Q(full_name__icontains=query) |
            Q(register_number__icontains=query)
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
        }
    )

@login_required
def register_existing_student(request, event_id, student_id):
    if not is_admin_or_coordinator(request.user):
        return HttpResponseForbidden("Not allowed")
    

    event = get_object_or_404(Event, id=event_id)

    if event.status != "ACTIVE":
        return HttpResponseForbidden("Event is not active")

    student = get_object_or_404(User, id=student_id, role=UserRole.STUDENT)
    
    if request.user.role in (
        UserRole.FACULTY_COORDINATOR,
        UserRole.STUDENT_COORDINATOR,
    ):
        if student.department != request.user.department:
            return HttpResponseForbidden("Not Allowed")
        

    Registration.objects.get_or_create(
        event=event,
        participant=student,
        defaults={"registered_by": request.user},
    )

    return redirect("accounts:add_student_to_event", event_id=event.id)




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
        student = form.save(commit=False)
        
        if request.user.role in (
            UserRole.FACULTY_COORDINATOR,
            UserRole.STUDENT_COORDINATOR,
        ):
            student.department = request.user.department
            
        student.save()
        
        Registration.objects.get_or_create(
            event=event,
            participant=student,
            defaults={"registered_by": request.user},
        )

    return redirect("accounts:add_student_to_event", event_id=event.id)




@login_required
def coordinator_events(request):
    if not is_admin_or_coordinator(request.user):
        return HttpResponseForbidden("Not Allowed")
    
    events = Event.objects.filter(status="ACTIVE")
    
    return render(request, "accounts/coordinator_events.html", {"events": events})



@login_required
def event_student_report(request):
    if not is_admin_or_coordinator(request.user):
        return HttpResponseForbidden("Not allowed")

    query = request.GET.get("q", "").lower()

    events = Event.objects.filter(
        status="ACTIVE"
    ).prefetch_related(
        "registrations__participant"
    )

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
            result.append({
                "event": event,
                "registrations": regs,
            })

    return render(
        request,
        "accounts/event_student_report.html",
        {
            "events": result,
            "query": query,
        }
    )


@login_required
def faculty_dashboard(request):
    if request.user.role != UserRole.FACULTY_COORDINATOR:
        return HttpResponseForbidden("Not allowed")
    
    department = request.user.department
    
    return render(request, "accounts/faculty_dashboard.html", {'department': department})


@login_required
def student_coordinator_dashboard(request):
    if request.user.role != UserRole.STUDENT_COORDINATOR:
        return HttpResponseForbidden("Not Allowed")
    
    department = request.user.department
    
    return render(request, "accounts/student_coordinator_dashboard.html", {"department": department})