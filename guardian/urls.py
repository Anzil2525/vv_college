from django.urls import path
from . import views

urlpatterns = [
    path('guardian_home/', views.guardian_home, name='guardian_home'),
    path('view_all_student_att_guardian/', views.view_all_student_att_guardian, name='view_all_student_att_guardian'),
    path('view_report_card_guardian/<int:reg_ins_id>/', views.view_report_card_guardian, name='view_report_card_guardian'),
]