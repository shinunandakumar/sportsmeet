from django.db import models

from accounts.models import User


class MeetStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    ACTIVE = "ACTIVE", "Active"
    COMPLETED = "COMPLETED", "Completed"


class EventStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    INACTIVE = "INACTIVE", "Inactive"


class EventType(models.TextChoices):
    TRACK = "TRACK", "Track"
    FIELD = "FIELD", "Field"
    OTHER = "OTHER", "Other"


class Meet(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=16, choices=MeetStatus.choices, default=MeetStatus.DRAFT)

    def __str__(self):
        return self.name



class EventGender(models.TextChoices):
    BOYS = "BOYS", "Boys"
    GIRLS = "GIRLS", "Girls"



class Event(models.Model):
    meet = models.ForeignKey(
        Meet,
        on_delete=models.CASCADE,
        related_name="events"
    )
    name = models.CharField(max_length=255)
    event_type = models.CharField(max_length=16, choices=EventType.choices, default=EventType.OTHER)
    gender = models.CharField(
        max_length=10,
        choices=EventGender.choices,
        default=EventGender.BOYS
    )
    status = models.CharField(max_length=16, choices=EventStatus.choices, default=EventStatus.ACTIVE)

    class Meta:
        unique_together = ("meet", "name")

    def __str__(self):
        return f"{self.meet.name} - {self.name}"


class Registration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    participant = models.ForeignKey(User, on_delete=models.CASCADE)
    registered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="registrations_done"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("event", "participant")

    def clean(self):
        if self.event.meet.status != MeetStatus.ACTIVE:
            raise ValueError("Registrations allowed only for active meets")

    def __str__(self):
        return f"{self.participant.email} → {self.event.name}"
