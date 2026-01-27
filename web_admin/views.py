from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from index.models import *
from .forms import *
from django.db.models import Min, ProtectedError
from datetime import date, timedelta
from django.utils.dateparse import parse_date
import calendar

# Create your views here.

def admin_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.session.get('type') != 'admin':
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper_func


@admin_required
def admin_home(request):
    return render(request, 'web_admin/admin_home.html')


@admin_required
def new_staff(request):
    staffs = StaffReg.objects.filter(login_info__status = "P")
    return render(request, 'web_admin/new_staff.html', {'staffs':staffs})


@admin_required
def view_rejected_staff(request):
    staffs = StaffReg.objects.filter(login_info__status = "R")
    return render(request, 'web_admin/view_rejected_staff.html', {'staffs':staffs})


@admin_required
def verify_staff(request, id, boo):
    staff = get_object_or_404(StaffReg, id = id)
    staff.login_info.status = "V"
    staff.login_info.save()
    messages.success(request, 'Successfully Verified.')
    if boo == 1:
        return redirect('new_staff')
    else:
        return redirect('view_rejected_staff')


@admin_required
def reject_staff(request, id):
    reason = request.GET.get('reason', 'No reason provided.')
    staff = get_object_or_404(StaffReg, id = id)
    staff.login_info.status = "R"
    staff.login_info.rejection_reason = reason
    staff.login_info.save()
    messages.error(request, 'Successfully Rejected.')
    return redirect('new_staff')


@admin_required
def view_staff(request, id):
    dep = DepTable.objects.get(id = id)
    staffs = StaffReg.objects.filter(dep = dep, login_info__status = "V")
    return render(request, 'web_admin/view_staff.html', {'staffs':staffs})


@admin_required
def delete_staff(request, id):
    try:
        log_ins = LoginTable.objects.get(id = id)
        # log_ins.status="R"
        log_ins.delete()
        messages.success(request, 'Successfully Deleted.')
        return redirect("view_staff_based_on_dep")
    except LoginTable.DoesNotExist:
        messages.error(request,"Staff Doesn't exist")
        staffs = StaffReg.objects.filter(login_info__status = "V")
    return render(request, 'web_admin/view_staff.html', {'staffs':staffs})


@admin_required
def view_dep(request):
    deps = DepTable.objects.all()
    return render(request, 'web_admin/view_dep.html', {'deps':deps})


@admin_required
def del_dep(request, id):
    try:
        dep = DepTable.objects.get(id=id)

        # Check if any staff are assigned to this department
        if StaffReg.objects.filter(dep=dep).exists():
            messages.error(
                request,
                "This action cannot be completed at the moment, as there are faculty members currently assigned to this department. Please remove them first to proceed."
            )
            return redirect('view_dep')

        # If no staff found, delete department
        dep.delete()
        messages.success(request, 'Successfully Deleted.')
        return redirect('view_dep')

    except DepTable.DoesNotExist:
        messages.error(request, "Department doesn't exist")
        return redirect('view_dep')


@admin_required
def add_course(request, id):
    if request.method == 'POST':
        cou = request.POST.get('course')

        try:
            ins = Course.objects.get(course = cou)
            messages.error(request, 'Course already exist')
        except Course.DoesNotExist:
            pass

        form  = Course_form(request.POST)
        if form.is_valid():
            dep = DepTable.objects.get(id = id)
            ins = form.save(commit=False)
            ins.dep = dep
            ins.save()
            messages.success(request, 'Successfully Created.')
            return redirect('view_dep')
    else:
        form  = Course_form()
    return render(request, 'web_admin/add_course.html', {'form':form})


@admin_required
def view_course(request, id):
    dep = DepTable.objects.get(id = id)
    course = Course.objects.filter(dep = dep)
    return render(request, 'web_admin/view_course.html', {'course':course})


@admin_required
def del_course(request, id):
    try:
        course = Course.objects.get(id = id)
        course.delete()
        messages.success(request, 'Successfully Deleted.')
        
        return redirect('view_dep')
    
    # prevent the admin from deleting the course if any students are registered in it.
    except ProtectedError:
        messages.error(request, "Can't delete the course because some students are registered in it.")

        return redirect('view_dep')


# def view_positions(request):
#     datas = Positions.objects.all()
#     return render(request, 'web_admin/view_positions.html', {'datas':datas})

# def reg_positions(request):
#     if request.method == 'POST':
#         form = Positions_form(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('view_positions')
#     else:
#         form = Positions_form()
#     return render(request, 'web_admin/reg_positions.html', {'form':form})

# def remove_position(request, id):
#     pos = Positions.objects.get(id = id)
#     pos.delete()
#     return redirect('view_positions')


@admin_required
def view_staff_based_on_dep(request):
    dep = DepTable.objects.all()
    return render(request, 'web_admin/view_staff_based_on_dep.html', {'dep':dep})


@admin_required
def student_cat_admin(request):
    sem = StudentReg.objects.filter(login_info__status = "V").values(
        'sem'
    ).annotate(
        min_sem=Min('sem')
    ).order_by('sem')

    return render(request, 'web_admin/student_cat_admin.html', {'sem': sem})


@admin_required
def student_cat_dep_admin(request, sem):
    dep = DepTable.objects.filter(studentreg__sem=sem).distinct()

    return render(request, 'web_admin/student_cat_dep_admin.html', {'dep':dep, 'sem':sem})


# we need to edit this function also..
@admin_required
def student_cat_course_admin(request, dep, sem):
    dep = DepTable.objects.get(id = dep)
    courses = Course.objects.filter(dep = dep, studentreg__sem = sem).distinct()

    return render(request, 'web_admin/student_cat_course_admin.html', {'courses':courses, 'sem':sem})


@admin_required
def view_students_admin(request, course, sem):
    course = get_object_or_404(Course, id = course)
    students = StudentReg.objects.filter(sem = sem, course = course, login_info__status = "V").order_by('reg_no')

    return render(request, 'web_admin/view_students_admin.html', {'students':students})


@admin_required
def view_student_all_attendance_admin(request, id):
    student = get_object_or_404(StudentReg, id=id)
    all_student_attendance = Attendance.objects.filter(student=student).order_by('date')

    # Prepare attendance data for easy lookup: {date_obj: attendance_obj}
    attendance_map = {att.date: att for att in all_student_attendance}

    # Get year and month from query parameters, default to current month/year
    today_date = date.today()
    year = int(request.GET.get('year', today_date.year))
    month = int(request.GET.get('month', today_date.month))

    # Ensure month and year are valid after navigation
    try:
        current_month_display_date = date(year, month, 1)
    except ValueError:  # Invalid month/year from GET params
        year = today_date.year
        month = today_date.month
        current_month_display_date = date(year, month, 1)

    # Calendar object (Monday is the first day of the week by default)
    cal = calendar.Calendar()
    # monthdayscalendar returns a list of weeks, each week a list of day numbers (0 for days not in month)
    month_days_with_zeros = cal.monthdayscalendar(year, month)
    
    weeks_data = []
    for week in month_days_with_zeros:
        week_row = []
        for day_num in week:
            day_data = {'day_num': day_num, 'attendance': None, 'date_obj': None}
            if day_num != 0:
                current_day_date_obj = date(year, month, day_num)
                day_data['date_obj'] = current_day_date_obj
                if current_day_date_obj in attendance_map:
                    day_data['attendance'] = attendance_map[current_day_date_obj]
            week_row.append(day_data)
        weeks_data.append(week_row)

    # For navigation links
    if month == 1:
        prev_nav_month = 12
        prev_nav_year = year - 1
    else:
        prev_nav_month = month - 1
        prev_nav_year = year

    if month == 12:
        next_nav_month = 1
        next_nav_year = year + 1
    else:
        next_nav_month = month + 1
        next_nav_year = year
    
    month_name = current_month_display_date.strftime("%B")

    context = {
        'student': student,
        'year': year, 'month': month, 'month_name': month_name,
        'weeks_data': weeks_data,
        'days_of_week': [day for day in calendar.day_abbr], # ['Mon', 'Tue', ..., 'Sun']
        'prev_nav_year': prev_nav_year, 'prev_nav_month': prev_nav_month,
        'next_nav_year': next_nav_year, 'next_nav_month': next_nav_month,
        'all_attendance_records': all_student_attendance, # For optional detailed list
    }
    return render(request, 'web_admin/view_student_all_attendance_admin.html', context)


@admin_required
def pass_out_admin(request, sem):
    # Get all students from the specified year
    students = StudentReg.objects.filter(sem=sem)
    
    # Update the status in LoginTable for these students
    LoginTable.objects.filter(
        studentreg__in=students, status='V'
    ).update(status="PA")
    messages.success(request, 'Successfully Marked as Pass Out.')
    
    return redirect('student_cat_admin')


@admin_required
def view_leave_application_admin(request):
    leaves = LeaveApplication.objects.filter(status__in=['H','FH'])

    return render(request, 'web_admin/view_leave_application_admin.html', {'leaves':leaves})


@admin_required
def admin_leave_varification(request, id):
    leave = get_object_or_404(LeaveApplication, id = id)
    leave.status = "A"
    leave.save()
    messages.success(request, 'Leave Request Verified')
    return redirect('view_leave_application_admin')


@admin_required
def admin_leave_rejected(request, id):
    leave = get_object_or_404(LeaveApplication, id = id)
    leave.status = "R"
    leave.save()
    messages.error(request, 'Leave Request Rejected')
    return redirect('view_leave_application_admin')


@admin_required
def view_leave_admin(request, id):
    staff = StaffReg.objects.get(id = id)
    leave_requests = LeaveApplication.objects.filter(from_staff = staff)
    
    return render(request, 'web_admin/view_leave_admin.html', {'leave_requests':leave_requests})

# currently we are editing this function...
@admin_required
def change_sem(request, sem, course):
    students = StudentReg.objects.filter(sem = sem, course = course, login_info__status = "V")
    for student in students:
        student.sem += 1 
        student.save()

    messages.success(request, 'Successfully Changed sem.')
    return redirect(student_cat_admin)


@admin_required
def view_course_attendance(request, course, sem):
    # Safely handle posted date input. If missing or invalid, fall back to today's date
    if request.method == 'POST':
        d_raw = (request.POST.get('date') or '').strip()
        if not d_raw:
            d = date.today()
        else:
            # parse_date returns a date object for YYYY-MM-DD format, else None
            parsed = parse_date(d_raw)
            if parsed is None:
                messages.error(request, 'Invalid date format. Please use YYYY-MM-DD.')
                d = date.today()
            else:
                d = parsed
    else:
        d = date.today()

    course = Course.objects.get(course = course)
    att = Attendance.objects.filter(student__course = course, student__sem = sem, date = d).order_by('student__reg_no')

    time_table_ins = None
    
    for i in att:
        time_table_ins = i.todays_time_table
        if time_table_ins:
            break

    return render(request, 'web_admin/view_course_attendance.html', {
        'attendance':att, 
        'sem':sem, 
        'course':course, 
        'date':d, 
        'time_table':time_table_ins
    })



@admin_required
def promotion(request, id):
    staff = get_object_or_404(StaffReg, id=id)
    dep = staff.dep.id

    if request.method == 'POST':
        form = StaffPromotion(request.POST, instance=staff)  # bind to staff
        
        if form.is_valid():
            pos = form.cleaned_data['pos']

            if pos.pos == 'HOD':
                # ✅ check if another HOD already exists in this department
                hod_exists = StaffReg.objects.filter(dep=dep, pos__pos='HOD').exclude(id=staff.id).exists()
                
                if hod_exists:
                    messages.error(request, 'This department already has a designated Head of Department. Only one HOD is permitted per department.')
                    return redirect('promotion', id=id)

            # Save promotion
            form.save()
            messages.success(request, f"{staff.name} promoted to {pos} successfully.")
            return redirect('view_staff', id=dep)

        else:
            messages.error(request, "Something went wrong. Please try again.")
    else:
        form = StaffPromotion(instance=staff)  # pre-fill with current pos

    return render(request, 'web_admin/promotion.html', {
        'staff': staff,
        'form': form
    })


@admin_required
def attendance_details_admin(request, student_id, date):
    attendance = Attendance.objects.filter(student_id=student_id, date=date).first()
    student = StudentReg.objects.get(id=student_id)
    return render(request, 'web_admin/attendance_details_admin.html', {
        'attendance': attendance,
        'student': student
    })


@admin_required
def edit_course_admin(request, id):
    course = Course.objects.get(id = id)
    if request.method == 'POST':
        form = Course_form(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully Changed.')
            return redirect('view_dep')

    else:
        form = Course_form(instance=course)
    return render(request, 'web_admin/edit_course_admin.html', {'form':form})


# @admin_required
# def search_attendance_admin(request, course, sem):
#     date = request.POST.get("date")
#     print(date)
#     course = Course.objects.get(course = course)
#     att = Attendance.objects.filter(student__course = course, student__sem = sem, date = date).order_by('student__reg_no')
#     return render(request, 'web_admin/view_course_attendance.html', {'attendance':att, 'sem':sem, 'course':course})

@admin_required
def reset_password_of_staff(request, id):
    staff = StaffReg.objects.get(id = id)
    staff.login_info.password = staff.pho
    staff.login_info.save()
    messages.success(request, 'Successfully Reset.')

    return redirect('view_staff', id=staff.dep.id)

@admin_required
def view_report_card_admin(request, id):
    student = StudentReg.objects.get(id=id)
    mark_list_ins = MarkList.objects.filter(student=student)
    return render(
        request, "web_admin/view_report_card_admin.html", {"mark_list": mark_list_ins}
    )
