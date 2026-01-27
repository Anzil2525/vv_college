from django.shortcuts import render, get_object_or_404, redirect
from index.models import *
from .forms import AttendanceForm, LeaveApplicationForm
from datetime import date, timedelta
import calendar
from django.forms import modelform_factory, inlineformset_factory
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from django.db.models import Min, Sum
import datetime
from django.utils.dateparse import parse_date
from index.forms import *

# Create your views here.


def staff_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.session.get("type") != "staff":
            return redirect("login")
        return view_func(request, *args, **kwargs)

    return wrapper_func


@staff_required
def staff_home(request):
    id = request.session.get("staff_login_id")
    log_ins = get_object_or_404(LoginTable, id=id)
    staff_ins = get_object_or_404(StaffReg, login_info=log_ins)

    pos = staff_ins.pos.pos

    return render(request, "staff/staff_home.html", {"pos": pos})


@staff_required
def new_students(request):
    id = request.session.get("staff_login_id")
    log_ins = get_object_or_404(LoginTable, id=id)
    staff_ins = get_object_or_404(StaffReg, login_info=log_ins)
    department = staff_ins.dep
    students = StudentReg.objects.filter(dep=department, login_info__status="P")
    return render(request, "staff/new_students.html", {"students": students})


@staff_required
def varify_students(request, id, boo):
    student = StudentReg.objects.get(id=id)
    student.login_info.status = "V"
    student.login_info.save()
    messages.success(request, "Successfully Verified.")
    id = request.session.get("staff_login_id")
    log_ins = get_object_or_404(LoginTable, id=id)
    staff_ins = get_object_or_404(StaffReg, login_info=log_ins)
    department = staff_ins.dep
    if boo == 1:
        students = StudentReg.objects.filter(dep=department, login_info__status="P")
        return redirect("new_students")
    else:
        return redirect("rejected_students")


@staff_required
def reject_students(request, id):
    student = StudentReg.objects.get(id=id)
    student.login_info.status = "R"
    student.login_info.save()
    messages.error(request, "Successfully Registered.")
    id = request.session.get("staff_login_id")
    log_ins = get_object_or_404(LoginTable, id=id)
    staff_ins = get_object_or_404(StaffReg, login_info=log_ins)
    department = staff_ins.dep
    students = StudentReg.objects.filter(dep=department, login_info__status="P")
    return render(request, "staff/new_students.html", {"students": students})


@staff_required
def view_students(request, sem, course):
    id = request.session.get("staff_login_id")
    log_ins = get_object_or_404(LoginTable, id=id)
    staff_ins = get_object_or_404(StaffReg, login_info=log_ins)
    department = staff_ins.dep
    course = Course.objects.get(course=course)
    students = StudentReg.objects.filter(
        dep=department, course=course, sem=sem, login_info__status="V"
    ).order_by("reg_no")
    return render(
        request,
        "staff/view_students.html",
        {"students": students, "year": sem, "course": course},
    )


@staff_required
def rejected_students(request):
    id = request.session.get("staff_login_id")
    log_ins = get_object_or_404(LoginTable, id=id)
    staff_ins = get_object_or_404(StaffReg, login_info=log_ins)
    department = staff_ins.dep
    students = StudentReg.objects.filter(dep=department, login_info__status="R")
    return render(request, "staff/rej_students.html", {"students": students})


@staff_required
def student_cat(request):
    id = request.session.get("staff_login_id")
    log_ins = get_object_or_404(LoginTable, id=id)
    staff_ins = get_object_or_404(StaffReg, login_info=log_ins)
    department = staff_ins.dep
    sem = (
        StudentReg.objects.filter(login_info__status="V", dep=department)
        .values("sem")
        .annotate(min_sem=Min("sem"))
        .order_by("sem")
    )

    return render(request, "staff/student_cat.html", {"sem": sem})


@staff_required
def student_cat_course(request, sem):
    id = request.session.get("staff_login_id")
    log_ins = get_object_or_404(LoginTable, id=id)
    staff_ins = get_object_or_404(StaffReg, login_info=log_ins)
    department = staff_ins.dep
    courses = Course.objects.filter(dep=department, studentreg__sem=sem).distinct()
    return render(
        request, "staff/student_cat_course.html", {"courses": courses, "sem": sem}
    )


@staff_required
def take_attendance(request, sem, course):
    today = date.today()
    day = datetime.datetime.now().strftime("%A")[:2].upper()

    id = request.session.get("staff_login_id")
    log_ins = get_object_or_404(LoginTable, id=id)
    staff_ins = get_object_or_404(StaffReg, login_info=log_ins)
    department = staff_ins.dep

    course_obj = Course.objects.get(course=course)
    students = StudentReg.objects.filter(
        dep=department, course=course_obj, sem=sem, login_info__status="V"
    ).order_by("reg_no")

    if request.method == "POST":
        time_table = (
            TimeTable.objects.filter(course=course_obj, sem=sem, day=day)
            .order_by("-created_at")
            .first()
        )

        for student in students:
            instance, _ = Attendance.objects.get_or_create(student=student, date=today)
            form = AttendanceForm(
                request.POST, prefix=str(student.id), instance=instance
            )
            if form.is_valid():
                ins = form.save(commit=False)
                total = 0

                # Save attendance taken time and taken by for each period
                now_time = datetime.datetime.now().strftime("%H:%M:%S")
                staff_name = (
                    staff_ins.__str__()
                    if hasattr(staff_ins, "__str__")
                    else staff_ins.login_info.email
                )

                # Morning session (3 periods)
                morning_attendance = (
                    ins.first_hour.upper() == "P"
                    and ins.second_hour.upper() == "P"
                    and ins.third_hour.upper() == "P"
                )
                if morning_attendance:
                    total += 0.5

                # Afternoon session (2 periods)
                afternoon_attendance = (
                    ins.fourth_hour.upper() == "P" and ins.fifth_hour.upper() == "P"
                )
                if afternoon_attendance:
                    total += 0.5

                # Save attendance time and taken by for each period if marked
                if ins.first_hour != "PE" and not ins.first_attendance_time:
                    ins.first_attendance_time = now_time
                    ins.first_attendance_taken_by = staff_name
                if ins.second_hour != "PE" and not ins.second_attendance_time:
                    ins.second_attendance_time = now_time
                    ins.second_attendance_taken_by = staff_name
                if ins.third_hour != "PE" and not ins.third_attendance_time:
                    ins.third_attendance_time = now_time
                    ins.third_attendance_taken_by = staff_name
                if ins.fourth_hour != "PE" and not ins.fourth_attendance_time:
                    ins.fourth_attendance_time = now_time
                    ins.fourth_attendance_taken_by = staff_name
                if ins.fifth_hour != "PE" and not ins.fifth_attendance_time:
                    ins.fifth_attendance_time = now_time
                    ins.fifth_attendance_taken_by = staff_name

                ins.today = total
                ins.sem = student.sem

                if ins.todays_time_table == None:
                    ins.todays_time_table = time_table

                ins.save()

        messages.success(request, "Attendance Registered.")
        return redirect("take_attendance", sem=sem, course=course)

    attendance_data = []
    for student in students:
        try:
            instance = Attendance.objects.get(student=student, date=today)
        except Attendance.DoesNotExist:
            instance = None
        form = AttendanceForm(prefix=str(student.id), instance=instance)
        attendance_data.append((student, form))

    return render(
        request,
        "staff/take_attendance.html",
        {"attendance_data": attendance_data, "today": today},
    )


@staff_required
def view_student_all_attendance(request, id):
    student = get_object_or_404(StudentReg, id=id)
    all_student_attendance = Attendance.objects.filter(student=student).order_by("date")

    # Prepare attendance data for easy lookup: {date_obj: attendance_obj}
    attendance_map = {att.date: att for att in all_student_attendance}

    # Get year and month from query parameters, default to current month/year
    today_date = date.today()
    year = int(request.GET.get("year", today_date.year))
    month = int(request.GET.get("month", today_date.month))

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
            day_data = {"day_num": day_num, "attendance": None, "date_obj": None}
            if day_num != 0:
                current_day_date_obj = date(year, month, day_num)
                day_data["date_obj"] = current_day_date_obj
                if current_day_date_obj in attendance_map:
                    day_data["attendance"] = attendance_map[current_day_date_obj]
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
        "student": student,
        "year": year,
        "month": month,
        "month_name": month_name,
        "weeks_data": weeks_data,
        "days_of_week": [
            day for day in calendar.day_abbr
        ],  # ['Mon', 'Tue', ..., 'Sun']
        "prev_nav_year": prev_nav_year,
        "prev_nav_month": prev_nav_month,
        "next_nav_year": next_nav_year,
        "next_nav_month": next_nav_month,
        "all_attendance_records": all_student_attendance,  # For optional detailed list
    }
    return render(request, "staff/view_student_all_attendance.html", context)


# can't use @staff_required because this is a common function for both admin and staff
# Helper function to convert HTML to PDF
def html_to_pdf_helper(html_string):
    result = BytesIO()
    # Ensure html_string is encoded to UTF-8 bytes
    pdf = pisa.CreatePDF(BytesIO(html_string.encode("UTF-8")), dest=result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type="application/pdf")
    return None


# can't use @staff_required because this is a common function for both admin and staff
def generate_student_attendance_pdf_view(request, student_id, year, month):
    student = get_object_or_404(StudentReg, id=student_id)

    # 1. Fetch attendance for the given month and year
    monthly_attendance_records = Attendance.objects.filter(
        student=student, date__year=year, date__month=month
    ).order_by("date")

    # 2. Calculate monthly attendance percentage
    monthly_percentage = 0.0
    if monthly_attendance_records.exists():
        total_present_equivalent_days_month = sum(
            att.today for att in monthly_attendance_records
        )
        num_lecture_days_month = monthly_attendance_records.count()
        if num_lecture_days_month > 0:
            monthly_percentage = (
                total_present_equivalent_days_month / num_lecture_days_month
            ) * 100

    # 3. Calculate semester attendance percentage
    current_semester = student.sem
    semester_percentage = 0.0

    # Fetch all attendance records for the student in the current semester
    # The 'sem' field in Attendance model should be populated correctly when attendance is taken.
    semester_attendance_records = Attendance.objects.filter(
        student=student, sem=current_semester
    )

    if semester_attendance_records.exists():
        total_present_equivalent_days_semester = sum(
            att.today for att in semester_attendance_records
        )
        num_lecture_days_semester = semester_attendance_records.count()
        if num_lecture_days_semester > 0:
            semester_percentage = (
                total_present_equivalent_days_semester / num_lecture_days_semester
            ) * 100

    # Prepare context for the PDF template
    context = {
        "student": student,
        "year": year,
        "month_name": calendar.month_name[month],
        "monthly_attendance_records": monthly_attendance_records,
        "monthly_percentage": f"{monthly_percentage:.2f}",
        "semester_percentage": f"{semester_percentage:.2f}",
        "current_semester": current_semester,
        "today_date": date.today(),
    }

    # Render an HTML template to a string
    # Ensure you have 'staff/attendance_pdf_template.html'
    html_string = render_to_string("staff/attendance_pdf_template.html", context)

    # Generate PDF
    pdf_response = html_to_pdf_helper(html_string)
    if pdf_response:
        # Make filename safe
        reg_no_cleaned = "".join(c if c.isalnum() else "_" for c in str(student.reg_no))
        pdf_response["Content-Disposition"] = (
            f'attachment; filename="attendance_{reg_no_cleaned}_{year}_{month}.pdf"'
        )
        return pdf_response

    return HttpResponse("Error generating PDF. Please check server logs.", status=500)


@staff_required
def droup_out(request, id, year, course):
    student = get_object_or_404(StudentReg, id=id)
    student.login_info.status = "DO"
    student.login_info.save()

    messages.error(request, "Droup Out!")
    return redirect("view_students", year, course)


@staff_required
def temp_discontinue(request, id, year, course):
    student = get_object_or_404(StudentReg, id=id)
    student.login_info.status = "TD"
    student.login_info.save()

    messages.error(request, "Temp Discontinued!")
    return redirect("view_students", year, course)


@staff_required
def leave_application(request):
    staff_login_id = request.session.get("staff_login_id")
    current_staff = get_object_or_404(StaffReg, login_info__id=staff_login_id)

    current_year = datetime.date.today().year
    leave_applications_of__this_year = LeaveApplication.objects.filter(
        start_date__year=current_year,
        from_staff=current_staff,
        status="A",
        leave_type__in=["ML", "CL"],
    )
    total_leave_agg = leave_applications_of__this_year.aggregate(
        total_days=Sum("num_of_days")
    )
    num_of_total_leave_days = total_leave_agg["total_days"] or 0.0
    # You can now use num_of_total_leave_days to enforce leave policies, e.g. check if it exceeds a limit.

    remining_days_of_paid_leave = (
        20 - num_of_total_leave_days
    )  # At this point of time the total num of leave with pay is 20

    if not staff_login_id:
        messages.error(request, "You must be logged in to apply for leave.")
        return redirect("login")

    # Determine the recipient of the leave application
    to_staff = None
    staff_position = current_staff.pos.pos

    if staff_position == "HOD":
        try:
            # HOD applies to the Principal
            to_staff = StaffReg.objects.get(pos__pos="Principal")
            status = "FH"
        except StaffReg.DoesNotExist:
            messages.error(
                request, "Cannot find the Principal. Please contact an administrator."
            )
            return redirect("staff_home")
        except StaffReg.MultipleObjectsReturned:
            # Handle case where multiple Principals exist (e.g., pick the first one)
            to_staff = StaffReg.objects.filter(pos__pos="Principal").first()
    else:  # Any other staff applies to their HOD
        try:
            to_staff = StaffReg.objects.get(
                dep=current_staff.dep, pos__pos="HOD", login_info__status="V"
            )
            status = "P"
        except StaffReg.DoesNotExist:
            messages.error(
                request,
                f"Cannot find the HOD for the {current_staff.dep.dep} department. Please contact an administrator.",
            )
            return redirect("staff_home")
        except StaffReg.MultipleObjectsReturned:
            # Handle case where multiple HODs exist for a department (e.g., pick the first one)
            to_staff = StaffReg.objects.filter(
                dep=current_staff.dep, pos__pos="HOD"
            ).first()

    if request.method == "POST":
        leave_days = request.POST.get("leave_days")
        print(leave_days)
        # Pass the current_staff to the form's __init__ if you want to filter 'to_staff' choices
        # (as was done in a previous suggestion for staff/forms.py)
        form = LeaveApplicationForm(request.POST, user=current_staff)
        if form.is_valid():
            leave_request = form.save(commit=False)  # Get the instance from the form
            leave_request.from_staff = (
                current_staff  # Set the 'from_staff' on the instance
            )
            leave_request.to_staff = to_staff  # Set the 'to_staff' on the instance
            leave_request.status = status
            leave_request.num_of_days = leave_days
            leave_request.save()  # Save the instance to the database
            messages.success(
                request, "Your leave application has been submitted successfully."
            )
            return redirect("staff_home")
    else:
        # Pass the current_staff to the form's __init__ for initial display
        form = LeaveApplicationForm(user=current_staff)

    return render(
        request,
        "staff/leave_application.html",
        {"form": form, "remining_days_of_paid_leave": remining_days_of_paid_leave},
    )


@staff_required
# this function is only visible to hod
def leave_application_hod(request):
    id = request.session.get("staff_login_id")
    log_ins = get_object_or_404(LoginTable, id=id)
    staff_ins = get_object_or_404(StaffReg, login_info=log_ins)

    leave_requests = LeaveApplication.objects.filter(to_staff=staff_ins, status="P")

    return render(
        request, "staff/leave_application_hod.html", {"leave_requests": leave_requests}
    )


@staff_required
def verify_leave_application_hod(request, id):
    leave = get_object_or_404(LeaveApplication, id=id)
    leave.status = "H"
    leave.save()
    messages.success(request, "Successfully Verified")
    return redirect("leave_application_hod")


@staff_required
def reject_leave_application_hod(request, id):
    leave = get_object_or_404(LeaveApplication, id=id)
    leave.status = "HR"
    messages.success(request, "Successfully Registered.")
    leave.save()

    return redirect("leave_application_hod")


@staff_required
def my_leave_applications(request):
    id = request.session.get("staff_login_id")
    log_ins = get_object_or_404(LoginTable, id=id)
    staff_ins = get_object_or_404(StaffReg, login_info=log_ins)

    leaves = LeaveApplication.objects.filter(from_staff=staff_ins)
    return render(request, "staff/my_leave_applications.html", {"leaves": leaves})


@staff_required
def cancle_leave(request, id):
    leave = get_object_or_404(LeaveApplication, id=id)
    leave.delete()
    messages.error(request, "Leave Application Cancled")
    return redirect("my_leave_applications")


@staff_required
def leave_history_hod(request):
    id = request.session.get("staff_login_id")
    log_ins = get_object_or_404(LoginTable, id=id)
    staff_ins = get_object_or_404(StaffReg, login_info=log_ins)
    department = staff_ins.dep

    leave_requests = LeaveApplication.objects.filter(
        from_staff__dep=department
    ).order_by("-submitted_on")

    return render(
        request, "staff/leave_history_hod.html", {"leave_requests": leave_requests}
    )


@staff_required
def staff_profile(request):
    id = request.session.get("staff_login_id")
    log_ins = get_object_or_404(LoginTable, id=id)
    staff_ins = get_object_or_404(StaffReg, login_info=log_ins)

    return render(request, "staff/staff_profile.html", {"staff_ins": staff_ins})


@staff_required
def staff_profile_edit(request, id):
    staff = get_object_or_404(StaffReg, id=id)
    login = get_object_or_404(LoginTable, email=staff.login_info.email)

    if request.method == "POST":
        form = StaffEditReg(request.POST, request.FILES, instance=staff)
        login = LoginEditForm(request.POST, instance=login)
        if form.is_valid() and login.is_valid():
            form.save()
            login.save()
            messages.success(request, "Successfully Edited.")
            return redirect("staff_profile")

    else:
        form = StaffEditReg(instance=staff)
        login = LoginEditForm(instance=login)

    return render(
        request, "staff/staff_profile_edit.html", {"form": form, "login": login}
    )


@staff_required
def view_temp_Discontinue(request):
    students = StudentReg.objects.filter(login_info__status="TD")

    return render(request, "staff/view_temp_Discontinue.html", {"students": students})


@staff_required
def rejoin_student(request, id):
    student = StudentReg.objects.get(id=id)
    student.login_info.status = "V"
    student.login_info.save()
    messages.success(request, "Successfully Rejoined.")

    return redirect("view_temp_Discontinue")


@staff_required
def edit_student_details(request, id, boo):
    student = get_object_or_404(StudentReg, id=id)
    guardian = get_object_or_404(GuadinReg, id=student.parent_1.id)

    if request.method == "POST":
        form = StudentRegForm(request.POST, instance=student)
        gud = GuadinRegForm(request.POST, instance=guardian)

        if form.is_valid() and gud.is_valid():
            dep = form.cleaned_data["dep"]
            course = form.cleaned_data["course"]

            dep_ins = DepTable.objects.get(dep=dep)

            try:
                course_ins = Course.objects.get(course=course, dep=dep_ins)
                form.save()
                gud.save()
                messages.success(request, "Successfully Edited.")

                if boo == 1:
                    return redirect("new_students")
                else:
                    return redirect("student_cat")
            except Course.DoesNotExist:
                messages.error(request, "Please Select Valid Course")
    else:
        form = StudentRegForm(instance=student)
        gud = GuadinRegForm(instance=guardian)

    return render(
        request,
        "staff/edit_student_details.html",
        {"form": form, "gud": gud, "reg_id": id, "boo": boo},
    )


@staff_required
def attendance_details_staff(request, student_id, date):
    attendance = Attendance.objects.filter(student_id=student_id, date=date).first()
    student = StudentReg.objects.get(id=student_id)
    return render(
        request,
        "staff/attendance_details_staff.html",
        {"attendance": attendance, "student": student},
    )


@staff_required
def view_gud_data(request, id, course, sem):
    try:
        student = StudentReg.objects.get(id=id)
        parent_reg = student.parent_1
        parent_log = LoginTable.objects.get(email=parent_reg.Guadin_email)

    except StudentReg.DoesNotExist:
        messages.error(request, "Invalid Student")
        return redirect("view_students", sem, course)  # Or another safe fallback

    except LoginTable.DoesNotExist:
        messages.error(request, "Guardian hasn't registered yet.")
        return redirect("view_students", sem, course)  # Or another fallback

    return render(
        request,
        "staff/view_gud_data.html",
        {"student": student, "parent_log": parent_log},
    )


@staff_required
def other_dep_att(request):
    sem = StudentReg.objects.values_list("sem", flat=True).distinct()

    return render(request, "staff/other_dep_att.html", {"sem": sem})


@staff_required
def view_other_deps(request, sem):
    courses = Course.objects.all()

    return render(
        request, "staff/view_other_deps.html", {"sem": sem, "courses": courses}
    )


@staff_required
def view_other_students(request, sem, course):
    today = date.today()

    id = request.session.get("staff_login_id")
    log_ins = get_object_or_404(LoginTable, id=id)
    staff_ins = get_object_or_404(StaffReg, login_info=log_ins)
    department = staff_ins.dep

    course_obj = get_object_or_404(Course, pk=course)

    students = StudentReg.objects.filter(
        course=course_obj, sem=sem, login_info__status="V"
    ).order_by("reg_no")

    if request.method == "POST":
        for student in students:
            instance, _ = Attendance.objects.get_or_create(student=student, date=today)
            form = AttendanceForm(
                request.POST, prefix=str(student.id), instance=instance
            )
            if form.is_valid():
                ins = form.save(commit=False)
                total = 0

                # Save attendance taken time and taken by for each period
                now_time = datetime.datetime.now().strftime("%H:%M:%S")
                staff_name = (
                    staff_ins.__str__()
                    if hasattr(staff_ins, "__str__")
                    else staff_ins.login_info.email
                )

                # Morning session (3 periods)
                morning_attendance = (
                    ins.first_hour.upper() == "P"
                    and ins.second_hour.upper() == "P"
                    and ins.third_hour.upper() == "P"
                )
                if morning_attendance:
                    total += 0.5

                # Afternoon session (2 periods)
                afternoon_attendance = (
                    ins.fourth_hour.upper() == "P" and ins.fifth_hour.upper() == "P"
                )
                if afternoon_attendance:
                    total += 0.5

                # Save attendance time and taken by for each period if marked
                if ins.first_hour != "PE" and not ins.first_attendance_time:
                    ins.first_attendance_time = now_time
                    ins.first_attendance_taken_by = staff_name
                if ins.second_hour != "PE" and not ins.second_attendance_time:
                    ins.second_attendance_time = now_time
                    ins.second_attendance_taken_by = staff_name
                if ins.third_hour != "PE" and not ins.third_attendance_time:
                    ins.third_attendance_time = now_time
                    ins.third_attendance_taken_by = staff_name
                if ins.fourth_hour != "PE" and not ins.fourth_attendance_time:
                    ins.fourth_attendance_time = now_time
                    ins.fourth_attendance_taken_by = staff_name
                if ins.fifth_hour != "PE" and not ins.fifth_attendance_time:
                    ins.fifth_attendance_time = now_time
                    ins.fifth_attendance_taken_by = staff_name

                ins.today = total
                ins.sem = student.sem

                ins.save()

        messages.success(request, "Attendance Registered.")
        return redirect("view_other_students", sem=sem, course=course)

    attendance_data = []
    for student in students:
        try:
            instance = Attendance.objects.get(student=student, date=today)
        except Attendance.DoesNotExist:
            instance = None
        form = AttendanceForm(prefix=str(student.id), instance=instance)
        attendance_data.append((student, form))

    return render(
        request,
        "staff/view_other_students.html",
        {"attendance_data": attendance_data, "today": today},
    )


def view_all_att_by_staff(request, course, sem):
    # Safely handle posted date input. If missing or invalid, fall back to today's date
    if request.method == "POST":
        d_raw = (request.POST.get("date") or "").strip()
        if not d_raw:
            d = date.today()
        else:
            # parse_date returns a date object for YYYY-MM-DD format, else None
            parsed = parse_date(d_raw)
            if parsed is None:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
                d = date.today()
            else:
                d = parsed
    else:
        d = date.today()

    course = Course.objects.get(course=course)
    att = Attendance.objects.filter(
        student__course=course, student__sem=sem, date=d
    ).order_by("student__reg_no")
    return render(
        request,
        "staff/view_all_att_by_staff.html",
        {"attendance": att, "sem": sem, "course": course, "date": d},
    )


def view_monthly_report(request, course, sem):
    """
    Render an HTML monthly report for all students in the given course and sem.
    Query params: year, month (optional) - defaults to current.
    The template will receive:
      - days: list of date objects for the month
      - students_stats: list of dicts {student, reg_no, name, sem, course, daily: [{date, status, value}], total, num_days, percent}
    """
    # parse year and month
    try:
        year = (
            int(request.GET.get("year"))
            if request.GET.get("year")
            else date.today().year
        )
    except (TypeError, ValueError):
        year = date.today().year
    try:
        month = (
            int(request.GET.get("month"))
            if request.GET.get("month")
            else date.today().month
        )
    except (TypeError, ValueError):
        month = date.today().month

    if month < 1 or month > 12:
        month = date.today().month

    # resolve course
    try:
        course_obj = Course.objects.get(course=course)
    except Course.DoesNotExist:
        messages.error(request, "Invalid course specified.")
        return redirect("student_cat")

    # build list of days for the month
    import calendar as _cal

    _, ndays = _cal.monthrange(year, month)
    days = [date(year, month, d) for d in range(1, ndays + 1)]

    students = StudentReg.objects.filter(
        course=course_obj, sem=sem, login_info__status="V"
    ).order_by("reg_no")

    students_stats = []
    for student in students:
        records_qs = Attendance.objects.filter(
            student=student, date__year=year, date__month=month
        )
        records_map = {rec.date: rec for rec in records_qs}

        daily = []
        total_present_equivalent = 0.0
        recorded_days = 0
        for d in days:
            rec = records_map.get(d)
            if rec is None:
                status = "Absent"
                val = 0.0
            else:
                val = float(rec.today or 0.0)
                if val >= 1.0:
                    status = "Full"
                elif val >= 0.5:
                    status = "Half"
                else:
                    status = "Absent"
                recorded_days += 1
                total_present_equivalent += val

            daily.append({"date": d, "status": status, "value": val})

        percent = 0.0
        if recorded_days > 0:
            percent = (total_present_equivalent / recorded_days) * 100

        students_stats.append(
            {
                "student": student,
                "reg_no": getattr(student, "reg_no", ""),
                "name": getattr(student, "name", str(student)),
                "sem": student.sem,
                "course": course_obj.course,
                "daily": daily,
                "total": total_present_equivalent,
                "num_days": recorded_days,
                "percent": percent,
            }
        )

    context = {
        "course": course_obj,
        "sem": sem,
        "year": year,
        "month": month,
        "month_name": calendar.month_name[month],
        "days": days,
        "students_stats": students_stats,
        "generated_on": date.today(),
    }

    return render(request, "staff/view_monthly_report.html", context)


# PDF generator for whole class monthly report
def generate_class_monthly_pdf(request, course, sem):
    """Generate PDF for class monthly report. Accepts query params year and month."""
    try:
        year = (
            int(request.GET.get("year"))
            if request.GET.get("year")
            else date.today().year
        )
    except (TypeError, ValueError):
        year = date.today().year
    try:
        month = (
            int(request.GET.get("month"))
            if request.GET.get("month")
            else date.today().month
        )
    except (TypeError, ValueError):
        month = date.today().month

    if month < 1 or month > 12:
        month = date.today().month

    try:
        course_obj = Course.objects.get(course=course)
    except Course.DoesNotExist:
        return HttpResponse("Invalid course", status=404)

    # Build same context as view_monthly_report
    import calendar as _cal

    _, ndays = _cal.monthrange(year, month)
    days = [date(year, month, d) for d in range(1, ndays + 1)]

    students = StudentReg.objects.filter(
        course=course_obj, sem=sem, login_info__status="V"
    ).order_by("reg_no")
    students_stats = []
    for student in students:
        records_qs = Attendance.objects.filter(
            student=student, date__year=year, date__month=month
        )
        records_map = {rec.date: rec for rec in records_qs}

        daily = []
        total_present_equivalent = 0.0
        recorded_days = 0
        for d in days:
            rec = records_map.get(d)
            if rec is None:
                status = "Absent"
                val = 0.0
            else:
                val = float(rec.today or 0.0)
                if val >= 1.0:
                    status = "Full"
                elif val >= 0.5:
                    status = "Half"
                else:
                    status = "Absent"
                recorded_days += 1
                total_present_equivalent += val

            daily.append({"date": d, "status": status, "value": val})

        percent = 0.0
        if recorded_days > 0:
            percent = (total_present_equivalent / recorded_days) * 100

        students_stats.append(
            {
                "student": student,
                "reg_no": getattr(student, "reg_no", ""),
                "name": getattr(student, "name", str(student)),
                "sem": student.sem,
                "course": course_obj.course,
                "daily": daily,
                "total": total_present_equivalent,
                "num_days": recorded_days,
                "percent": percent,
            }
        )

    context = {
        "course": course_obj,
        "sem": sem,
        "year": year,
        "month": month,
        "month_name": calendar.month_name[month],
        "days": days,
        "students_stats": students_stats,
        "generated_on": date.today(),
    }

    # Use a simplified PDF-friendly template that avoids wide tables
    html_string = render_to_string("staff/class_monthly_report_pdf.html", context)
    pdf_response = html_to_pdf_helper(html_string)
    if pdf_response:
        safe_course = "".join(c if c.isalnum() else "_" for c in str(course_obj.course))
        pdf_response["Content-Disposition"] = (
            f'attachment; filename="attendance_{safe_course}_sem{sem}_{year}_{month}.pdf"'
        )
        return pdf_response

    return HttpResponse("Error generating PDF", status=500)


@staff_required
def reset_password(request, reg_id, boo):
    student_data = StudentReg.objects.get(id=reg_id)
    student_data.login_info.password = student_data.reg_no
    student_data.login_info.save()
    messages.success(request, "Password reset successfully")

    return redirect("edit_student_details", id=reg_id, boo=boo)


@staff_required
def change_password_staff(request, id):
    staff_data = StaffReg.objects.get(id=id)
    if request.method == "POST":
        newPassword = request.POST.get("newPassword")
        confirmPassword = request.POST.get("confirmPassword")

        if newPassword == confirmPassword:
            staff_data.login_info.password = newPassword
            staff_data.login_info.save()
            messages.success(request, "Password changed successfully")
            return redirect("staff_home")
        else:
            messages.error(request, "Passwords do not match")
            return redirect("change_password_staff", id=id)

    return render(request, "staff/change_password_staff.html")


def setting_time_table_hod_7d(request):
    id = request.session.get("staff_login_id")
    if not id:
        return redirect("login")

    log_ins = get_object_or_404(LoginTable, id=id)
    staff_ins = get_object_or_404(StaffReg, login_info=log_ins)

    dep = staff_ins.dep
    courses = Course.objects.filter(dep=dep)

    if request.method == "POST":
        form = TimeTableForm(request.POST)
        if form.is_valid():
            form_ins = form.save(commit=False)
            course = request.POST.get("Course")

            course_ins = Course.objects.get(id=course)
            form_ins.course = course_ins
            form_ins.save()

            messages.success(request, "Time Table saved successfully ✅")
            return redirect("staff_home")  # redirect to same page or another
        else:
            messages.error(request, "Please correct the errors below ❌")

    form = TimeTableForm()

    return render(
        request,
        "staff/setting_time_table_hod_7d.html",
        {"timeTableForm": form, "courses": courses},
    )


@staff_required
def select_sem_for_timetable(request):
    id = request.session.get("staff_login_id")
    if not id:
        return redirect("login")

    log_ins = get_object_or_404(LoginTable, id=id)
    staff_ins = get_object_or_404(StaffReg, login_info=log_ins)

    pos = staff_ins.pos.pos

    all_time_table_sem = (
        TimeTable.objects.filter(course__dep=staff_ins.dep)
        .values_list("sem", flat=True)
        .distinct()
    )

    return render(
        request,
        "staff/select_sem_for_timetable.html",
        {"pos": pos, "sems": all_time_table_sem},
    )


@staff_required
def time_table(request, sem):

    id = request.session.get("staff_login_id")
    if not id:
        return redirect("login")

    log_ins = get_object_or_404(LoginTable, id=id)
    staff_ins = get_object_or_404(StaffReg, login_info=log_ins)

    pos = staff_ins.pos.pos

    # Fetch all, ordered by creation time (oldest to newest)
    all_time_tables = TimeTable.objects.filter(
        course__dep=staff_ins.dep, sem=sem
    ).order_by("created_at")

    # Keep only the latest for each (course, sem)
    latest_map = {}
    for tt in all_time_tables:
        if tt.course_id and tt.sem and tt.day:
            latest_map[(tt.course_id, tt.sem, tt.day)] = tt

    days_order = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
    time_tables = sorted(
        latest_map.values(),
        key=lambda x: days_order.index(x.day) if x.day in days_order else 999,
    )

    return render(
        request, "staff/time_table.html", {"pos": pos, "time_tables": time_tables}
    )


@staff_required
def reg_examination(request, course, sem):
    students = StudentReg.objects.filter(
        course__course=course, sem=sem, login_info__status="V"
    ).order_by("reg_no")
    course_obj = get_object_or_404(Course, course=course)

    MarkListFormSet = inlineformset_factory(
        ExamRegistration,
        MarkList,
        fields=("student", "marks"),
        extra=students.count(),
        can_delete=False,
    )

    if request.method == "POST":
        exam_reg_form = ExamRegistrationForm(request.POST)
        if exam_reg_form.is_valid():
            exam = exam_reg_form.save(commit=False)
            exam.course = course_obj
            exam.sem = sem
            exam.save()

            formset = MarkListFormSet(request.POST, instance=exam)
            # Re-inject initial data for disabled fields to pass validation
            for form, student in zip(formset.forms, students):
                form.initial["student"] = student
                form.fields["student"].disabled = True

            if formset.is_valid():
                formset.save()
                messages.success(request, "Exam & marks saved successfully")
                return redirect("student_cat_course", sem=sem)
        else:
            # If exam form is invalid, we still need to initialize the formset for the template
            formset = MarkListFormSet(request.POST)
    else:
        exam_reg_form = ExamRegistrationForm()
        formset = MarkListFormSet(instance=ExamRegistration())
        for form, student in zip(formset.forms, students):
            form.initial["student"] = student
            form.fields["student"].disabled = True

    return render(
        request,
        "staff/reg_examination.html",
        {"exam_reg_form": exam_reg_form, "formset": formset},
    )


@staff_required
def individual_report_card(request, id):
    student = StudentReg.objects.get(id=id)
    mark_list_ins = MarkList.objects.filter(student=student)
    return render(
        request, "staff/individual_report_card.html", {"mark_list": mark_list_ins}
    )


@staff_required
def edit_individual_report_card(request, id):
    student = get_object_or_404(StudentReg, id=id)

    # Create formset to edit existing marks
    MarkListFormSet = inlineformset_factory(
        StudentReg, MarkList, fields=("exam", "marks"), extra=0, can_delete=True
    )

    if request.method == "POST":
        formset = MarkListFormSet(request.POST, instance=student)

        # We must disable the fields in POST as well so Django knows to
        # use the initial/instance value and not expect it in request.POST
        for form in formset.forms:
            if form.instance.pk:
                form.fields["exam"].disabled = True

        if formset.is_valid():
            formset.save()
            messages.success(request, "Report card updated successfully.")
            return redirect("individual_report_card", id=id)
    else:
        formset = MarkListFormSet(instance=student)
        # Disable the exam dropdown so users don't accidentally swap exams
        for form in formset.forms:
            if form.instance.pk:
                form.fields["exam"].disabled = True

    return render(
        request,
        "staff/edit_individual_report_card.html",
        {"formset": formset, "student": student},
    )
