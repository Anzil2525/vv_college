from django.contrib import admin
from .models import LoginTable, DepTable, Course, Positions, StaffReg, GuadinReg, StudentReg, Attendance, LeaveApplication, TimeTable

# Register your models here.
admin.site.register(LoginTable)
admin.site.register(DepTable)
admin.site.register(Course)
admin.site.register(Positions)
admin.site.register(StaffReg)
admin.site.register(GuadinReg)
admin.site.register(StudentReg)
admin.site.register(Attendance)
admin.site.register(LeaveApplication)
admin.site.register(TimeTable)
