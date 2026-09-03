from django.urls import path
from . import views

urlpatterns = [
    path('office_home/', views.office_home, name='office_home'),
    path('student_fee_management/', views.student_fee_management, name='student_fee_management'),
    path('fee-structure-management/', views.fee_structure_management, name='fee_structure_management'),
    path('fee-structure-management/course/<int:course_id>/', views.course_fee_details, name='course_fee_details'),
    path('fee-structure-management/course/<int:course_id>/save/', views.save_fee_structure, name='save_fee_structure'),
    path('fee-structure-management/course/<int:course_id>/delete/<int:fee_id>/', views.delete_fee_structure, name='delete_fee_structure'),
    path('fee-payment-management/', views.fee_payment_management, name='fee_payment_management'),
    path('fee-payment-management/student/<int:student_id>/', views.student_payment_details, name='student_payment_details'),
    path('fee-payment-management/student-fee/<int:student_fee_id>/', views.student_fee_payment_details, name='student_fee_payment_details'),
    path('individual-student-fee-management/', views.individual_student_fee_management, name='individual_student_fee_management'),
    path('individual-student-fee-management/semester/<int:semester>/', views.individual_student_fee_departments, name='individual_student_fee_departments'),
    path('individual-student-fee-management/semester/<int:semester>/department/<int:department_id>/', views.individual_student_fee_courses, name='individual_student_fee_courses'),
    path('individual-student-fee-management/semester/<int:semester>/course/<int:course_id>/', views.individual_student_fee_students, name='individual_student_fee_students'),
    path('individual-student-fee-management/semester/<int:semester>/course/<int:course_id>/assign/', views.assign_student_fees, name='assign_student_fees'),
    path('individual-student-fee-management/semester/<int:semester>/course/<int:course_id>/student/<int:student_id>/', views.edit_individual_student_fee, name='edit_individual_student_fee'),
    path('individual-student-fee-management/semester/<int:semester>/course/<int:course_id>/student/<int:student_id>/seat-type/', views.edit_student_seat_type, name='edit_student_seat_type'),
    path('mark_office_attendance/', views.mark_office_attendance, name='mark_office_attendance'),
    path('change_password_office/', views.change_password_office, name='change_password_office'),
    path('apply_office_leave/', views.apply_office_leave, name='apply_office_leave'),
    path('my_office_leave_applications/', views.my_office_leave_applications, name='my_office_leave_applications'),
    path('cancel_office_leave/<int:id>/', views.cancel_office_leave, name='cancel_office_leave'),
]