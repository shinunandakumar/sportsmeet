from django.db import models


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


class Category(models.Model):
    name = models.CharField(max_length=255)
    meet = models.ForeignKey(Meet, on_delete=models.CASCADE, related_name="categories")

    class Meta:
        unique_together = ("name", "meet")

    def __str__(self):
        return f"{self.meet} - {self.name}"


class Event(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=16, choices=EventType.choices, default=EventType.OTHER)
    status = models.CharField(max_length=16, choices=EventStatus.choices, default=EventStatus.ACTIVE)

    class Meta:
        unique_together = ("name", "category")

    def __str__(self):
        return f"{self.category} - {self.name}"
