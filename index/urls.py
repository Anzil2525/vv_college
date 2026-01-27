from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dep_reg/', views.dep_reg, name='dep_reg'),
    path('staff_reg/', views.staff_reg, name='staff_reg'),
    # path('parent_reg/', views.parent_reg, name='parent_reg'),
    path('student_reg/', views.student_reg, name='student_reg'),
    path('resent/<int:login_ins>', views.resent, name = 'resent'),
    path('login/', views.login, name='login'),
    path('guardian_reg/', views.guardian_reg, name='guardian_reg'),
    path('log_out_function/', views.log_out_function, name='log_out_function'),
]