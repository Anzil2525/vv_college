from django.contrib import admin
from .models import (
	LoginTable,
	DepTable,
	Course,
	MinorCourse,
	Positions,
	StaffReg,
	GuadinReg,
	StudentReg,
	TimeTableSet,
	TimeTable,
	Attendance,
	LeaveApplication,
	ExamRegistration,
	MarkList,
	OfficeFacultyRegistration,
	FeeStructure,
	StudentFee,
	FeePayment,
	UpiPaymentSettings,
)

# Register your models here.
admin.site.register(LoginTable)
admin.site.register(DepTable)
admin.site.register(Course)
admin.site.register(MinorCourse)
admin.site.register(Positions)
admin.site.register(StaffReg)
admin.site.register(GuadinReg)
admin.site.register(StudentReg)
admin.site.register(Attendance)
admin.site.register(LeaveApplication)
admin.site.register(TimeTableSet)
admin.site.register(TimeTable)
admin.site.register(ExamRegistration)
admin.site.register(MarkList)
admin.site.register(OfficeFacultyRegistration)
admin.site.register(FeeStructure)
admin.site.register(StudentFee)
admin.site.register(FeePayment)
admin.site.register(UpiPaymentSettings)
