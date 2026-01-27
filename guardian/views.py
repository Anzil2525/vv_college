from django.shortcuts import render, get_object_or_404, redirect
from index.models import GuadinReg, StudentReg, Attendance, LoginTable, MarkList
from datetime import date
import calendar

# Create your views here.
def guardian_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.session.get('type') != 'guardian':
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper_func


@guardian_required
def guardian_home(request):
    login_email = request.session.get('guardian_login_email')
    gud_reg_ins = get_object_or_404(GuadinReg, Guadin_email = login_email)

    reg_ins = get_object_or_404(StudentReg, parent_1 = gud_reg_ins)
    
    # calculating the curent sem attendance
    sem = reg_ins.sem
    all_attendance = Attendance.objects.filter(student = reg_ins, sem = sem)
    total_working_days = all_attendance.count()
    present_days = 0

    for i in all_attendance:
        present_days += i.today

    if total_working_days > 0:
        sem_attendance_persentage = (present_days / total_working_days) * 100
    else:
        sem_attendance_persentage = 0

    # calculating the month attendace
    current_date = date.today()
    current_month = current_date.month
    monthly_attendance_of_this_sem = Attendance.objects.filter(student = reg_ins, date__month = current_month)
    total_working_days_in_this_month = monthly_attendance_of_this_sem.count()
    present_days_in_this_month = 0

    for i in monthly_attendance_of_this_sem:
        present_days_in_this_month += i.today

    if total_working_days_in_this_month > 0:
        monthly_attendance_persentage = (present_days_in_this_month / total_working_days_in_this_month) * 100
    else:
        monthly_attendance_persentage = 0

    progress1 = int(sem_attendance_persentage)
    progress2 = int(monthly_attendance_persentage)

    total_length = 2 * 3.1416 * 100  # r = 100
    stroke_offset1 = total_length - (progress1 / 100) * total_length
    stroke_offset2 = total_length - (progress2 / 100) * total_length
    return render(request, 'guardian/guardian_home.html', {
        'progress1': progress1,
        'progress2': progress2,
        'stroke_offset1': stroke_offset1,
        'stroke_offset2': stroke_offset2,
        'reg_ins':reg_ins
    })
    # return render(request, 'guardian/guardian_home.html')


@guardian_required
def view_all_student_att_guardian(request):
    login_email = request.session.get('guardian_login_email')
    gud_reg_ins = get_object_or_404(GuadinReg, Guadin_email = login_email)

    student = get_object_or_404(StudentReg, parent_1 = gud_reg_ins)

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
    return render(request, 'student/view_all_student_att.html', context)
    # return render(request, 'guardian/view_all_student_att_guardian.html')



# @guardian_required
# def attendance_details_guad(request, student_id, date):
#     attendance = Attendance.objects.filter(student_id=student_id, date=date).first()
#     student = StudentReg.objects.get(id=student_id)
#     return render(request, 'guardian/attendance_details_guad.html', {
#         'attendance': attendance,
#         'student': student
#     })


@guardian_required
def view_report_card_guardian(request, reg_ins_id):
    student = StudentReg.objects.get(id=reg_ins_id)
    mark_list_ins = MarkList.objects.filter(student=student)
    return render(
        request, "guardian/view_report_card_guardian.html", {"mark_list": mark_list_ins}
    )