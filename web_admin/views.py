from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from index.models import *
from .models import Holiday
from .attendance_utils import (
    compute_office_staff_attendance,
    get_holidays_dict,
    is_second_saturday,
    is_sunday,
)
from office.models import OfficeAttendance, OfficeLeaveApplication
from .forms import *
from django.db import transaction
from django.db.models import Min, ProtectedError
from datetime import datetime, date, time, timedelta
from django.utils import timezone
from django.utils.dateparse import parse_date
import calendar
import json

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
def upi_payment_settings(request):
    settings = UpiPaymentSettings.objects.first()
    form = UpiPaymentSettingsForm(request.POST or None, request.FILES or None, instance=settings)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'UPI payment settings saved successfully.')
        return redirect('upi_payment_settings')

    return render(request, 'web_admin/upi_payment_settings.html', {'form': form, 'settings': settings})


@admin_required
def new_staff(request):
    staffs = StaffReg.objects.filter(login_info__status = "P")
    office = OfficeFacultyRegistration.objects.filter(login_info__status = "P")
    return render(request, 'web_admin/new_staff.html', {'staffs': staffs, 'office': office})


@admin_required
def view_rejected_staff(request):
    staffs = StaffReg.objects.filter(login_info__status = "R")
    office = OfficeFacultyRegistration.objects.filter(login_info__status = "R")
    return render(request, 'web_admin/view_rejected_staff.html', {'staffs': staffs, 'office': office})


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
def verify_office(request, id, boo):
    office = get_object_or_404(OfficeFacultyRegistration, id = id)
    office.login_info.status = "V"
    office.login_info.save()
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
def reject_office(request, id):
    reason = request.GET.get('reason', 'No reason provided.')
    office = get_object_or_404(OfficeFacultyRegistration, id = id)
    office.login_info.status = "R"
    office.login_info.rejection_reason = reason
    office.login_info.save()
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
def view_office_staff(request):
    staffs = OfficeFacultyRegistration.objects.filter(login_info__status="V")
    return render(request, 'web_admin/view_office_staff.html', {'staffs': staffs})


@admin_required
def view_office_staff_attendance(request, id):
    staff = get_object_or_404(OfficeFacultyRegistration, id=id)
    summary = compute_office_staff_attendance(staff)
    holidays_dict = get_holidays_dict()
    holidays_list = Holiday.objects.all().order_by('date')
    
    return render(request, 'web_admin/view_office_staff_attendance.html', {
        'staff': staff,
        'records': summary['records'],
        'attendance_dict_json': json.dumps(summary['attendance_dict']),
        'holidays_dict_json': json.dumps(holidays_dict),
        'holidays_list': holidays_list,
        'registered_on_str': summary['registered_on'].strftime("%Y-%m-%d"),
        'total_days': summary['total_days'],
        'present_days': summary['present_days'],
        'absent_days': summary['absent_days'],
        'leave_days': summary['leave_days'],
        'att_percentage': summary['att_percentage'],
    })


@admin_required
def update_office_staff_attendance(request, id):
    staff = get_object_or_404(OfficeFacultyRegistration, id=id)
    if request.method == 'POST':
        date_str = request.POST.get('date')
        status = request.POST.get('status', 'P')
        check_in_str = request.POST.get('check_in_time')
        check_out_str = request.POST.get('check_out_time')
        
        if not date_str:
            messages.error(request, "Date is required.")
            return redirect('view_office_staff_attendance', id=id)
            
        try:
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect('view_office_staff_attendance', id=id)
            
        tz = timezone.get_current_timezone()
        
        marked_at = None
        checked_out_at = None

        if status == 'P':
            if check_in_str:
                try:
                    t_in = datetime.strptime(check_in_str, "%H:%M").time()
                    marked_at = timezone.make_aware(datetime.combine(parsed_date, t_in), tz)
                except ValueError:
                    pass
            else:
                t_in = time(9, 0)
                marked_at = timezone.make_aware(datetime.combine(parsed_date, t_in), tz)
                    
            if check_out_str:
                try:
                    t_out = datetime.strptime(check_out_str, "%H:%M").time()
                    checked_out_at = timezone.make_aware(datetime.combine(parsed_date, t_out), tz)
                except ValueError:
                    pass
            else:
                t_out = time(17, 0)
                checked_out_at = timezone.make_aware(datetime.combine(parsed_date, t_out), tz)
                
        attendance, created = OfficeAttendance.objects.get_or_create(
            office_staff=staff,
            date=parsed_date,
            defaults={'status': status, 'marked_at': marked_at, 'checked_out_at': checked_out_at}
        )
        
        if not created:
            attendance.status = status
            attendance.marked_at = marked_at
            attendance.checked_out_at = checked_out_at
            attendance.save()
            
        action_word = "added" if created else "updated"
        messages.success(request, f"Attendance for {parsed_date.strftime('%d %b %Y')} successfully {action_word}.")
        
    return redirect('view_office_staff_attendance', id=id)


@admin_required
def delete_office_staff_attendance(request, id, att_id=None):
    staff = get_object_or_404(OfficeFacultyRegistration, id=id)
    date_str = request.GET.get('date') or request.POST.get('date')
    
    if att_id:
        att = get_object_or_404(OfficeAttendance, id=att_id, office_staff=staff)
        date_display = att.date.strftime('%d %b %Y')
        att.delete()
        messages.success(request, f"Attendance record for {date_display} deleted successfully.")
    elif date_str:
        try:
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            OfficeAttendance.objects.filter(office_staff=staff, date=parsed_date).delete()
            messages.success(request, f"Attendance record for {parsed_date.strftime('%d %b %Y')} reset successfully.")
        except ValueError:
            messages.error(request, "Invalid date.")
            
    return redirect('view_office_staff_attendance', id=id)


@admin_required
def add_holiday(request):
    if request.method == 'POST':
        date_str = request.POST.get('date')
        name = (request.POST.get('name') or '').strip()
        description = (request.POST.get('description') or '').strip()
        staff_id = request.POST.get('staff_id')
        redirect_to = request.POST.get('next')
        
        if not date_str or not name:
            messages.error(request, "Date and Holiday Name are required.")
        else:
            try:
                parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                holiday, created = Holiday.objects.update_or_create(
                    date=parsed_date,
                    defaults={'name': name, 'description': description}
                )
                action = "added" if created else "updated"
                messages.success(request, f"College Holiday '{name}' on {parsed_date.strftime('%d %b %Y')} {action} successfully.")
            except Exception as e:
                messages.error(request, f"Error saving holiday: {str(e)}")
                
        if staff_id:
            return redirect('view_office_staff_attendance', id=staff_id)
        if redirect_to:
            return redirect(redirect_to)
        return redirect('admin_home')
    return redirect('admin_home')


@admin_required
def delete_holiday(request, id):
    holiday = get_object_or_404(Holiday, id=id)
    name = holiday.name
    date_display = holiday.date.strftime('%d %b %Y')
    staff_id = request.GET.get('staff_id') or request.POST.get('staff_id')
    redirect_to = request.GET.get('next') or request.POST.get('next')
    
    holiday.delete()
    messages.success(request, f"College Holiday '{name}' on {date_display} removed successfully.")
    
    if staff_id:
        return redirect('view_office_staff_attendance', id=staff_id)
    if redirect_to:
        return redirect(redirect_to)
    return redirect('admin_home')


@admin_required
def reset_password_of_office_staff(request, id):
    staff = get_object_or_404(OfficeFacultyRegistration, id=id)
    staff.login_info.password = staff.phone
    staff.login_info.save()
    messages.success(request, f"Successfully reset password for {staff.name}.")
    return redirect('view_office_staff')


@admin_required
def delete_office_staff(request, id):
    try:
        staff = get_object_or_404(OfficeFacultyRegistration, id=id)
        login_info = staff.login_info
        login_info.delete()
        messages.success(request, 'Successfully Deleted Office Staff Member.')
    except Exception as e:
        messages.error(request, 'Error deleting staff member.')
    return redirect('view_office_staff')


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
    office_leaves = OfficeLeaveApplication.objects.filter(status='P')

    return render(request, 'web_admin/view_leave_application_admin.html', {
        'leaves': leaves,
        'office_leaves': office_leaves
    })


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
def admin_verify_office_leave(request, id):
    leave = get_object_or_404(OfficeLeaveApplication, id=id)
    leave.status = "A"
    leave.save()

    # Automatically mark attendance as Leave ('L') for the date range
    curr = leave.start_date
    while curr <= leave.end_date:
        att, created = OfficeAttendance.objects.update_or_create(
            office_staff=leave.office_staff,
            date=curr,
            defaults={'status': 'L', 'marked_at': None, 'checked_out_at': None}
        )
        if not created:
            att.status = 'L'
            att.marked_at = None
            att.checked_out_at = None
            att.save()
        curr += timedelta(days=1)

    messages.success(request, f'Office Leave Request for {leave.office_staff.name} Verified & Attendance updated.')
    return redirect('view_leave_application_admin')


@admin_required
def admin_reject_office_leave(request, id):
    leave = get_object_or_404(OfficeLeaveApplication, id=id)
    leave.status = "R"
    leave.save()
    messages.error(request, f'Office Leave Request for {leave.office_staff.name} Rejected.')
    return redirect('view_leave_application_admin')


@admin_required
def view_leave_admin(request, id):
    staff = StaffReg.objects.get(id = id)
    leave_requests = LeaveApplication.objects.filter(from_staff = staff)
    
    return render(request, 'web_admin/view_leave_admin.html', {'leave_requests':leave_requests})

# currently we are editing this function...
@admin_required
def change_sem(request, sem, course):
    course_instance = get_object_or_404(Course, id=course)
    students = StudentReg.objects.filter(
        sem=sem,
        course=course_instance,
        login_info__status="V",
    )
    next_semester = sem + 1
    fee_structure = FeeStructure.objects.filter(
        course=course_instance,
        semester=next_semester,
    ).order_by('-updated_at', '-id').first()

    assigned_count = 0
    skipped_count = 0
    with transaction.atomic():
        for student in students:
            student.sem = next_semester
            student.save(update_fields=['sem'])

            if fee_structure:
                if student.seat_type == 'MG':
                    amount = fee_structure.management_amount
                elif student.seat_type == 'MS':
                    amount = fee_structure.merit_amount
                else:
                    skipped_count += 1
                    continue

                if amount is None:
                    skipped_count += 1
                    continue

                StudentFee.objects.update_or_create(
                    student=student,
                    fee_structure=fee_structure,
                    defaults={
                        'semester': next_semester,
                        'total_amount': amount,
                        'due_date': fee_structure.due_date,
                    },
                )
                assigned_count += 1

    if fee_structure:
        messages.success(request, f'Semester changed and fees assigned to {assigned_count} student(s).')
        if skipped_count:
            messages.warning(
                request,
                f'{skipped_count} student(s) were skipped because their seat type or matching fee amount is not set.',
            )
    else:
        messages.warning(request, 'Semester changed, but no fee structure is configured for the new semester.')
    return redirect('student_cat_admin')


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
