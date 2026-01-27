from django.urls import path
from . import views

urlpatterns = [
    path('student_home/', views.student_home, name='student_home'),
    path('view_all_student_att/', views.view_all_student_att, name='view_all_student_att'),
    path('attendance_details_guad_stu/details/<int:student_id>/<str:date>/', views.attendance_details_guad_stu, name='attendance_details_guad_stu'),
    path('change_password_student/<int:student_id>/', views.change_password_student, name='change_password_student'),
    path('view_report_card_student/<int:reg_id>/', views.view_report_card_student, name='view_report_card_student'),
    path('time_table_student/', views.time_table_student, name='time_table_student')
]
