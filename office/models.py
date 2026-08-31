from django.db import models
from index.models import OfficeFacultyRegistration

class OfficeAttendance(models.Model):
    STATUS_CHOICES = [
        ('P', 'Present'),
        ('A', 'Absent'),
        ('L', 'Leave'),
    ]

    office_staff = models.ForeignKey(OfficeFacultyRegistration, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='P')
    marked_at = models.DateTimeField(null=True, blank=True)
    checked_out_at = models.DateTimeField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ('office_staff', 'date')

    def __str__(self):
        return f"{self.office_staff.name} - {self.date} ({self.get_status_display()})"


class OfficeLeaveApplication(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('ML', 'Medical Leave'),
        ('CL', 'Casual Leave'), 
        ('DL', 'Duty Leave'),
        ('VL', 'Vacation Leave'),
        ('OL', 'Other Leave'),
    ]

    LEAVE_STATUS_CHOICES = [
        ('P', 'Pending'),
        ('A', 'Approved'),
        ('R', 'Rejected'),
    ]

    DAY_TYPE_CHOICES = [
        ('full', 'Full Day'),
        ('half', 'Half Day'),
    ]

    office_staff = models.ForeignKey(OfficeFacultyRegistration, on_delete=models.CASCADE, related_name='leave_applications')
    reason = models.TextField()
    leave_type = models.CharField(max_length=3, choices=LEAVE_TYPE_CHOICES, default='CL')
    day_type = models.CharField(max_length=10, choices=DAY_TYPE_CHOICES, default='full')
    start_date = models.DateField()
    end_date = models.DateField()
    submitted_on = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=2, choices=LEAVE_STATUS_CHOICES, default='P')
    num_of_days = models.FloatField(default=1.0)

    def __str__(self):
        return f"Office Leave from {self.office_staff.name} ({self.start_date} to {self.end_date})"

