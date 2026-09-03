from django.db import models
import uuid
import datetime

# Create your models here.

class LoginTable(models.Model):
    CHOICE = [
        ("V", "Verified"),
        ("P", "Pending"),
        ("R", "Rejected"),
        ("PA", "PassOut"),
        ("DO", "DroupOut"),
        ("TR", "Transfer"),
        ("RE", "Resign"),
        ("TD", "Temp Discontinue")
    ]

    email = models.EmailField(unique=True)
    password = models.CharField(max_length=20)
    auto_login_id = models.UUIDField(
        default=uuid.uuid4,  # Automatically sets a unique UUID when created
        unique=True,         # Ensures no two records have the same ID
        null=True, 
        blank=True
    )
    user = models.CharField(max_length=10)
    status = models.CharField(max_length=2, choices=CHOICE, default="P")
    rejection_reason = models.TextField(null=True, blank=True)
    registered_on = models.DateField(default=datetime.date.today, null=True, blank=True)

    def __str__(self):
        return self.email
    

class DepTable(models.Model):
    dep = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.dep
    

class Course(models.Model):
    course = models.CharField(max_length=50, unique=True)
    dep = models.ForeignKey(DepTable, on_delete=models.CASCADE)

    def __str__(self):
        return self.course
    

class Positions(models.Model):
    pos = models.CharField(max_length=50)

    def __str__(self):
        return self.pos
    

class StaffReg(models.Model):
    name = models.CharField(max_length=50)
    pho = models.CharField(max_length=15)
    dep = models.ForeignKey(DepTable, on_delete=models.SET_NULL, null=True, blank=True)
    pos = models.ForeignKey(Positions, on_delete=models.SET_NULL, null=True)
    profile_photo = models.ImageField(upload_to='staff_profiles/', null=True, blank=True)
    login_info = models.ForeignKey(LoginTable, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class GuadinReg(models.Model):
    Guadin_Name = models.CharField(max_length=50)
    Guadin_phone_Number = models.CharField(max_length=15)
    Guadin_email = models.EmailField(unique=True)

    def __str__(self):
        return self.Guadin_Name
    

class StudentReg(models.Model):
    SEAT_TYPE_CHOICES = [
        ('MG', 'Management Seat'),
        ('MS', 'Merit Seat'),
    ]

    name = models.CharField(max_length=50)
    reg_no = models.IntegerField()
    sem = models.IntegerField()
    year_of_admision = models.IntegerField()
    pho = models.CharField(max_length=15)
    address = models.TextField(null=True)
    blood_type = models.CharField(max_length=10, null=True)
    seat_type = models.CharField(max_length=2, choices=SEAT_TYPE_CHOICES, null=True, blank=True)
    parent_1 = models.ForeignKey(GuadinReg, on_delete=models.SET_NULL, null=True, blank=True, related_name="parent_1")
    dep = models.ForeignKey(DepTable, on_delete=models.SET_NULL, null=True)
    course = models.ForeignKey(Course, on_delete=models.PROTECT, null=True)
    login_info = models.ForeignKey(LoginTable, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class TimeTableSet(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    sem = models.IntegerField()
    name = models.CharField(max_length=100)
    is_selected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course} - {self.sem} - {self.name}"

class TimeTable(models.Model):
    CHOICE = [
        ("MO", "Monday"),
        ("TU", "Tuesday"),
        ("WE", "Wednesday"),
        ("TH", "Thursday"),
        ("FR", "Friday"),
        ("SA", "Saturday"),
        ("SU", "Sunday")
    ]

    timetable_set = models.ForeignKey(
        TimeTableSet,
        on_delete=models.CASCADE,
        related_name='timetables',
        null=True,
        blank=True,
    )

    first_hour_subject = models.CharField(max_length=50)
    first_houre_staff = models.CharField(max_length=50)

    second_hour_subject = models.CharField(max_length=50)
    second_hour_staff = models.CharField(max_length=50)

    third_hour_subject = models.CharField(max_length=50)
    third_hour_staff = models.CharField(max_length=50)

    fourth_hour_subject = models.CharField(max_length=50)
    fourth_hour_staff = models.CharField(max_length=50)

    fifth_hour_subject = models.CharField(max_length=50)
    fifth_hour_staff = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)
    day = models.CharField(max_length=2, choices=CHOICE, default='MO')

    def __str__(self):
        return f"{self.timetable_set} - {self.get_day_display()}"
    
class Attendance(models.Model):
    CHOICE = [
        ('P', 'Present'),
        ('A', 'Absent'),
        ('PE', 'Pending')
    ]

    first_hour = models.CharField(max_length=2, choices=CHOICE, default='PE')
    first_attendance_time = models.CharField(max_length=10, null=True, blank=True)
    first_attendance_taken_by = models.CharField(max_length=30, null=True, blank=True)

    second_hour = models.CharField(max_length=2, choices=CHOICE, default='PE')
    second_attendance_time = models.CharField(max_length=10, null=True, blank=True)
    second_attendance_taken_by = models.CharField(max_length=30, null=True, blank=True)

    third_hour = models.CharField(max_length=2, choices=CHOICE, default='PE')
    third_attendance_time = models.CharField(max_length=10, null=True, blank=True)
    third_attendance_taken_by = models.CharField(max_length=30, null=True, blank=True)

    fourth_hour = models.CharField(max_length=2, choices=CHOICE, default='PE')
    fourth_attendance_time = models.CharField(max_length=10, null=True, blank=True)
    fourth_attendance_taken_by = models.CharField(max_length=30, null=True, blank=True)

    fifth_hour = models.CharField(max_length=2, choices=CHOICE, default='PE')
    fifth_attendance_time = models.CharField(max_length=10, null=True, blank=True)
    fifth_attendance_taken_by = models.CharField(max_length=30, null=True, blank=True)

    today = models.FloatField(default=0)
    sem = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)
    student = models.ForeignKey(StudentReg, on_delete=models.CASCADE)
    todays_time_table = models.ForeignKey(TimeTable, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('student', 'date')

    def __str__(self):
        return f"{self.student} - {self.date}"
    

class LeaveApplication(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('ML', 'Medical Leave'),
        ('CL', 'Casual Leave'), 
        ('DL', 'Duty Leave'),
        ('VL', 'Vacation Leave')
    ]

    LEAVE_STATUS_CHOICES = [
        ('P', 'Pending'),
        ('H', 'HOD Approved'),
        ('HR', 'HOD Rejected'),
        ('FH', 'From HOD'),
        ('A', 'principal Approved'),
        ('R', 'principal Rejected'),
    ]

    from_staff = models.ForeignKey(StaffReg, on_delete=models.CASCADE, related_name='leave_applications_sent')
    to_staff = models.ForeignKey(StaffReg, on_delete=models.SET_NULL, null=True, blank=True, related_name='leave_applications_received')
    reason = models.TextField()
    leave_type = models.CharField(max_length=3, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    submitted_on = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=2, choices=LEAVE_STATUS_CHOICES, default='P')
    num_of_days = models.FloatField()

    def __str__(self):
        return f"Leave from {self.from_staff.name} ({self.start_date} to {self.end_date})"


class ExamRegistration(models.Model):
    CHOICE = [
        ('CT', 'Class Test'),
        ('ME', 'Model Exam'),
        ('SE', 'Sem Exam')
    ]
    sem = models.IntegerField(null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True)
    
    exam_type = models.CharField(max_length=2, choices=CHOICE)
    exam_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    subject = models.CharField(max_length=50)
    total_mark = models.IntegerField()
    
    def __str__(self):
        return f"{self.subject} - {self.exam_date} - {self.exam_type}"
    
    
class MarkList(models.Model):
    exam = models.ForeignKey(ExamRegistration, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentReg, on_delete=models.CASCADE)
    marks = models.IntegerField()
    
    def __str__(self):
        return f"{self.student} - {self.exam}"
    

class OfficeFacultyRegistration(models.Model):
    POSITIONS = [
        ('OH', 'Office Head'),
        ('BS', 'Billing Staff'),
        ('OS', 'Other Staff')
    ]

    name = models.CharField(max_length=50)
    position = models.CharField(max_length=20, choices=POSITIONS)
    phone = models.CharField(max_length=15)
    login_info = models.ForeignKey(LoginTable, on_delete=models.CASCADE)

    def __str__ (self):
        return(self.name)


class FeeStructure(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.IntegerField()
    merit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    management_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course} - Semester {self.semester}"


class StudentFee(models.Model):
    student = models.ForeignKey(StudentReg, on_delete=models.CASCADE)
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)
    semester = models.IntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        OfficeFacultyRegistration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='student_fees_created',
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        OfficeFacultyRegistration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='student_fees_updated',
    )


class FeePayment(models.Model):
    student_fee = models.ForeignKey(StudentFee, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    entered_at = models.DateTimeField(auto_now_add=True)
    entered_by = models.ForeignKey(
        OfficeFacultyRegistration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fee_payments_entered',
    )
    payment_method = models.CharField(max_length=20)
    reference_number = models.CharField(max_length=100, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)