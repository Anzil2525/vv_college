from django.urls import path
from . import views

urlpatterns = [
    path('admin_home/', views.admin_home, name='admin_home'),
    path('view_staff/<int:id>', views.view_staff, name='view_staff'),
    path('new_staff/', views.new_staff, name='new_staff'),
    path('verify_staff/<int:id>/ <int:boo>/', views.verify_staff, name='verify_staff'),
    path('reject_staff/<int:id>/', views.reject_staff, name='reject_staff'),
    path('view_rejected_staff/', views.view_rejected_staff, name='view_rejected_staff'),
    path('delete_staff/<int:id>/', views.delete_staff, name='delete_staff'),
    path('view_dep/', views.view_dep, name='view_dep'),
    path('del_dep/<int:id>/', views.del_dep, name='del_dep'),
    path('add_course/<int:id>', views.add_course, name='add_course'),
    path('view_course/<int:id>', views.view_course, name='view_course'),
    path('del_course/<int:id>', views.del_course, name='del_course'),
    # path('reg_positions/', views.reg_positions, name='reg_positions'),
    # path('view_positions/', views.view_positions, name='view_positions'),
    # path('remove_position/<int:id>', views.remove_position, name='remove_position'),
    path('view_staff_based_on_dep', views.view_staff_based_on_dep, name='view_staff_based_on_dep'),
    path('student_cat_admin/', views.student_cat_admin, name='student_cat_admin'),
    path('student_cat_dep_admin/<int:sem>/', views.student_cat_dep_admin, name='student_cat_dep_admin'),
    path('student_cat_course_admin/<int:dep>/<int:sem>', views.student_cat_course_admin, name='student_cat_course_admin'),
    path('view_students_admin/<int:course>/<int:sem>/', views.view_students_admin, name='view_students_admin'),
    path('view_student_all_attendance_admin/<int:id>/', views.view_student_all_attendance_admin, name='view_student_all_attendance_admin'),
    path('pass_out_admin/<int:sem>/', views.pass_out_admin, name='pass_out_admin'),
    path('view_leave_application_admin/', views.view_leave_application_admin, name='view_leave_application_admin'),
    path('admin_leave_varification/<int:id>/', views.admin_leave_varification, name='admin_leave_varification'),
    path('admin_leave_rejected/<int:id>/', views.admin_leave_rejected, name='admin_leave_rejected'),
    path('view_leave_admin/<int:id>/', views.view_leave_admin, name='view_leave_admin'),
    path('promotion/<int:id>/', views.promotion, name="promotion"),
    path('change_sem/<int:sem>/<int:course>/', views.change_sem, name='change_sem'),
    path('view_course_attendance/<str:course>/<int:sem>/', views.view_course_attendance, name='view_course_attendance'),
    path('attendance/details/<int:student_id>/<str:date>/', views.attendance_details_admin, name='attendance_details_admin'),
    path('edit_course_admin/<int:id>/', views.edit_course_admin, name='edit_course_admin'),
    # path('search_attendance_admin/<str:course>/<int:sem>/', views.search_attendance_admin, name='search_attendance_admin')
    path('reset_password_of_staff/<int:id>/', views.reset_password_of_staff, name='reset_password_of_staff'),
    path('view_report_card_admin/<int:id>/', views.view_report_card_admin, name='view_report_card_admin')
]