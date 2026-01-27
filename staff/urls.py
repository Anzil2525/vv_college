from django.urls import path
from . import views

urlpatterns = [
    path("staff_home/", views.staff_home, name="staff_home"),
    path("new_students/", views.new_students, name="new_students"),
    path(
        "varify_students/<int:id>/<int:boo>",
        views.varify_students,
        name="varify_students",
    ),
    path("reject_students/<int:id>/", views.reject_students, name="reject_students"),
    path(
        "view_students/<int:sem>/<str:course>",
        views.view_students,
        name="view_students",
    ),
    path("rejected_students/", views.rejected_students, name="rejected_students"),
    path("student_cat/", views.student_cat, name="student_cat"),
    path(
        "student_cat_course/<int:sem>",
        views.student_cat_course,
        name="student_cat_course",
    ),
    path(
        "take_attendance/<int:sem>/<str:course>",
        views.take_attendance,
        name="take_attendance",
    ),
    path(
        "view_student_all_attendance/<int:id>/",
        views.view_student_all_attendance,
        name="view_student_all_attendance",
    ),
    path(
        "student/<int:student_id>/attendance/pdf/<int:year>/<int:month>/",
        views.generate_student_attendance_pdf_view,
        name="generate_student_attendance_pdf",
    ),
    path(
        "droup_out/<int:id>/<int:year>/<str:course>", views.droup_out, name="droup_out"
    ),
    path(
        "temp_discontinue/<int:id>/<int:year>/<str:course>",
        views.temp_discontinue,
        name="temp_discontinue",
    ),
    path("leave_application/", views.leave_application, name="leave_application"),
    path(
        "leave_application_hod/",
        views.leave_application_hod,
        name="leave_application_hod",
    ),
    path(
        "verify_leave_application_hod/<int:id>/",
        views.verify_leave_application_hod,
        name="verify_leave_application_hod",
    ),
    path(
        "reject_leave_application_hod/<int:id>/",
        views.reject_leave_application_hod,
        name="reject_leave_application_hod",
    ),
    path(
        "my_leave_applications/",
        views.my_leave_applications,
        name="my_leave_applications",
    ),
    path("cancle_leave/<int:id>", views.cancle_leave, name="cancle_leave"),
    path("leave_history_hod/", views.leave_history_hod, name="leave_history_hod"),
    path("staff_profile/", views.staff_profile, name="staff_profile"),
    path(
        "staff_profile_edit/<int:id>/",
        views.staff_profile_edit,
        name="staff_profile_edit",
    ),
    path(
        "view_temp_Discontinue/",
        views.view_temp_Discontinue,
        name="view_temp_Discontinue",
    ),
    path("rejoin_student/<int:id>/", views.rejoin_student, name="rejoin_student"),
    path(
        "edit_student_details/<int:id>/<int:boo>/",
        views.edit_student_details,
        name="edit_student_details",
    ),
    path(
        "attendance_details_staff/details/<int:student_id>/<str:date>/",
        views.attendance_details_staff,
        name="attendance_details_staff",
    ),
    path(
        "view_gud_data/<int:id>/<str:course>/<int:sem>/",
        views.view_gud_data,
        name="view_gud_data",
    ),
    path("other_dep_att/", views.other_dep_att, name="other_dep_att"),
    path("view_other_deps/<int:sem>/", views.view_other_deps, name="view_other_deps"),
    path(
        "view_other_students/<int:sem>/<int:course>/",
        views.view_other_students,
        name="view_other_students",
    ),
    path(
        "view_all_att_by_staff/<str:course>/<int:sem>/",
        views.view_all_att_by_staff,
        name="view_all_att_by_staff",
    ),
    path(
        "view_monthly_report/<str:course>/<int:sem>/",
        views.view_monthly_report,
        name="view_monthly_report",
    ),
    path(
        "class_monthly_report/<str:course>/<int:sem>/",
        views.generate_class_monthly_pdf,
        name="class_monthly_report",
    ),
    path(
        "reset_password/<int:reg_id>/<int:boo>/",
        views.reset_password,
        name="reset_password",
    ),
    path(
        "change_password_staff/<int:id>/",
        views.change_password_staff,
        name="change_password_staff",
    ),
    path(
        "setting_time_table_hod_7d",
        views.setting_time_table_hod_7d,
        name="setting_time_table_hod_7d",
    ),
    path("time_table/<int:sem>/", views.time_table, name="time_table"),
    path(
        "select_sem_for_timetable",
        views.select_sem_for_timetable,
        name="select_sem_for_timetable",
    ),
    path(
        "reg_examination/<str:course>/<int:sem>/",
        views.reg_examination,
        name="reg_examination",
    ),
    path(
        "individual_report_card/<int:id>",
        views.individual_report_card,
        name="individual_report_card",
    ),
    path(
        "edit_individual_report_card/<int:id>",
        views.edit_individual_report_card,
        name="edit_individual_report_card",
    ),
]
