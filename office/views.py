import datetime
import json
import math
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.db import transaction
from django.db.models import DecimalField, ExpressionWrapper, F, Prefetch, Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from index.models import Course, DepTable, FeePayment, FeeStructure, OfficeFacultyRegistration, StudentFee, StudentReg
from .models import OfficeAttendance, OfficeLeaveApplication
from .forms import FeePaymentForm, FeeStructureForm, OfficeLeaveApplicationForm, StudentFeeForm, StudentPaymentSearchForm, StudentSeatTypeForm
from web_admin.attendance_utils import (
    compute_office_staff_attendance,
    get_holidays_dict,
)

# kvvs location
# OFFICE_LAT = 9.073323
# OFFICE_LNG = 76.775516

# test location
OFFICE_LAT = 9.073180
OFFICE_LNG = 76.775355

MAX_DISTANCE_METERS = 500.0

def calculate_distance(lat1, lon1, lat2=OFFICE_LAT, lon2=OFFICE_LNG):
    R = 6371000  # Radius of the Earth in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def office_home(request):
    office_login_id = request.session.get("office_login_id")
    session_type = request.session.get("type")
    
    if not office_login_id or session_type != 'office':
        return redirect('login')

    office_staff = get_object_or_404(OfficeFacultyRegistration, login_info__id=office_login_id)
    
    today = datetime.date.today()
    today_attendance = OfficeAttendance.objects.filter(office_staff=office_staff, date=today).first()
    
    summary = compute_office_staff_attendance(office_staff)
    holidays_dict = get_holidays_dict()

    registered_on_str = summary['registered_on'].strftime("%Y-%m-%d")

    context = {
        'office_staff': office_staff,
        'today': today,
        'today_attendance': today_attendance,
        'attendance_dict_json': json.dumps(summary['attendance_dict']),
        'holidays_dict_json': json.dumps(holidays_dict),
        'total_days': summary['total_days'],
        'present_days': summary['present_days'],
        'absent_days': summary['absent_days'],
        'leave_days': summary['leave_days'],
        'attendance_percentage': summary['att_percentage'],
        'office_lat': OFFICE_LAT,
        'office_lng': OFFICE_LNG,
        'max_distance_meters': MAX_DISTANCE_METERS,
        'registered_on_str': registered_on_str,
    }
    return render(request, "office/office_home.html", context)


def student_fee_management(request):
    office_login_id = request.session.get("office_login_id")
    session_type = request.session.get("type")

    if not office_login_id or session_type != 'office':
        return redirect('login')

    office_staff = get_object_or_404(OfficeFacultyRegistration, login_info__id=office_login_id)
    if office_staff.position != 'BS':
        return HttpResponseForbidden('Only Billing Staff can access student fee management.')

    return render(request, "office/student_fee_management.html", {
        "office_staff": office_staff,
    })


def _billing_staff_page(request, page_title):
    office_login_id = request.session.get("office_login_id")
    session_type = request.session.get("type")

    if not office_login_id or session_type != 'office':
        return redirect('login')

    office_staff = get_object_or_404(OfficeFacultyRegistration, login_info__id=office_login_id)
    if office_staff.position != 'BS':
        return HttpResponseForbidden('Only Billing Staff can access student fee management.')

    return render(request, "office/student_fee_management_placeholder.html", {
        "office_staff": office_staff,
        "page_title": page_title,
    })


def fee_structure_management(request):
    office_login_id = request.session.get("office_login_id")
    session_type = request.session.get("type")

    if not office_login_id or session_type != 'office':
        return redirect('login')

    office_staff = get_object_or_404(OfficeFacultyRegistration, login_info__id=office_login_id)
    if office_staff.position != 'BS':
        return HttpResponseForbidden('Only Billing Staff can access student fee management.')

    fee_structures = FeeStructure.objects.order_by('semester', 'id')
    departments = DepTable.objects.prefetch_related(
        Prefetch(
            'course_set',
            queryset=Course.objects.prefetch_related(
                Prefetch('feestructure_set', queryset=fee_structures)
            ).order_by('course'),
            to_attr='fee_courses',
        )
    ).order_by('dep')

    return render(request, "office/fee_structure_management.html", {
        "office_staff": office_staff,
        "departments": departments,
    })


def course_fee_details(request, course_id):
    office_login_id = request.session.get("office_login_id")
    session_type = request.session.get("type")

    if not office_login_id or session_type != 'office':
        return redirect('login')

    office_staff = get_object_or_404(OfficeFacultyRegistration, login_info__id=office_login_id)
    if office_staff.position != 'BS':
        return HttpResponseForbidden('Only Billing Staff can access student fee management.')

    course = get_object_or_404(Course, id=course_id)
    fees = course.feestructure_set.order_by('semester', 'id')
    return render(request, "office/course_fee_details.html", {
        "office_staff": office_staff,
        "course": course,
        "fees": fees,
        "fee_form": FeeStructureForm(),
    })


def save_fee_structure(request, course_id):
    office_login_id = request.session.get("office_login_id")
    session_type = request.session.get("type")

    if not office_login_id or session_type != 'office':
        return redirect('login')

    office_staff = get_object_or_404(OfficeFacultyRegistration, login_info__id=office_login_id)
    if office_staff.position != 'BS':
        return HttpResponseForbidden('Only Billing Staff can access student fee management.')

    if request.method != 'POST':
        return redirect('fee_structure_management')

    course = get_object_or_404(Course, id=course_id)
    fee_id = request.POST.get('fee_id')
    form = FeeStructureForm(request.POST)
    if form.is_valid():
        if fee_id:
            fee_structure = get_object_or_404(FeeStructure, id=fee_id, course=course)
            fee_structure.semester = form.cleaned_data['semester']
            fee_structure.merit_amount = form.cleaned_data['merit_amount']
            fee_structure.management_amount = form.cleaned_data['management_amount']
            fee_structure.due_date = form.cleaned_data['due_date']
            fee_structure.save()
            created = False
        else:
            fee_structure, created = FeeStructure.objects.get_or_create(
                course=course,
                semester=form.cleaned_data['semester'],
                defaults={
                    'merit_amount': form.cleaned_data['merit_amount'],
                    'management_amount': form.cleaned_data['management_amount'],
                    'due_date': form.cleaned_data['due_date'],
                },
            )
            if not created:
                fee_structure.merit_amount = form.cleaned_data['merit_amount']
                fee_structure.management_amount = form.cleaned_data['management_amount']
                fee_structure.due_date = form.cleaned_data['due_date']
                fee_structure.save()
        action = 'added' if created else 'updated'
        messages.success(request, f'Fee structure {action} for {course}.')
    else:
        messages.error(request, 'Please enter a valid semester, amount, and due date.')

    return redirect('course_fee_details', course_id=course.id)


def delete_fee_structure(request, course_id, fee_id):
    office_login_id = request.session.get("office_login_id")
    session_type = request.session.get("type")

    if not office_login_id or session_type != 'office':
        return redirect('login')

    office_staff = get_object_or_404(OfficeFacultyRegistration, login_info__id=office_login_id)
    if office_staff.position != 'BS':
        return HttpResponseForbidden('Only Billing Staff can access student fee management.')

    course = get_object_or_404(Course, id=course_id)
    fee_structure = get_object_or_404(FeeStructure, id=fee_id, course=course)
    if request.method == 'POST':
        fee_structure.delete()
        messages.success(request, f'Semester {fee_structure.semester} fee structure deleted for {course}.')

    return redirect('course_fee_details', course_id=course.id)


def fee_payment_management(request):
    office_staff = _get_billing_staff(request)
    if not isinstance(office_staff, OfficeFacultyRegistration):
        return office_staff

    department_id = request.GET.get('department') or None
    selected_course_id = request.GET.get('course') or None
    if selected_course_id and not department_id:
        department_id = Course.objects.filter(
            id=selected_course_id
        ).values_list('dep_id', flat=True).first()
    search_form = StudentPaymentSearchForm(
        request.GET or None,
        department_id=department_id,
    )
    students = StudentReg.objects.filter(login_info__status='V').select_related(
        'course', 'dep'
    ).order_by('reg_no')

    if search_form.is_valid():
        cleaned = search_form.cleaned_data
        if cleaned['name']:
            students = students.filter(name__icontains=cleaned['name'])
        if cleaned['semester'] is not None:
            students = students.filter(sem=cleaned['semester'])
        if cleaned['year_of_admision'] is not None:
            students = students.filter(year_of_admision=cleaned['year_of_admision'])
        if cleaned['course']:
            students = students.filter(course=cleaned['course'])
        if cleaned['department']:
            students = students.filter(dep=cleaned['department'])
        if cleaned['reg_no'] is not None:
            students = students.filter(reg_no=cleaned['reg_no'])
        if cleaned['phone']:
            students = students.filter(pho__icontains=cleaned['phone'])

    return render(request, 'office/fee_payment_management.html', {
        'office_staff': office_staff,
        'form': search_form,
        'students': students,
        'course_options': Course.objects.order_by('course').values('id', 'course', 'dep_id'),
        'has_search': any(value not in (None, '') for value in search_form.data.values()),
    })


def student_payment_details(request, student_id):
    office_staff = _get_billing_staff(request)
    if not isinstance(office_staff, OfficeFacultyRegistration):
        return office_staff

    student = get_object_or_404(
        StudentReg.objects.select_related('course', 'dep'),
        id=student_id,
        login_info__status='V',
    )
    assigned_fees = StudentFee.objects.filter(
        student=student,
    ).select_related('fee_structure__course').annotate(
        paid_amount=Coalesce(
            Sum('feepayment__amount'),
            Value(Decimal('0.00')),
            output_field=DecimalField(max_digits=10, decimal_places=2),
        ),
    ).annotate(
        remaining_amount=ExpressionWrapper(
            F('total_amount') - F('paid_amount'),
            output_field=DecimalField(max_digits=10, decimal_places=2),
        )
    ).order_by('semester', 'id')
    for fee in assigned_fees:
        if fee.paid_amount <= 0:
            fee.payment_status = 'No Payment'
        elif fee.paid_amount >= fee.total_amount:
            fee.payment_status = 'Paid'
        else:
            fee.payment_status = 'Partially Paid'
    return render(request, 'office/student_payment_details.html', {
        'office_staff': office_staff,
        'student': student,
        'assigned_fees': assigned_fees,
    })


def student_fee_payment_details(request, student_fee_id):
    office_staff = _get_billing_staff(request)
    if not isinstance(office_staff, OfficeFacultyRegistration):
        return office_staff

    student_fee = get_object_or_404(
        StudentFee.objects.select_related('student', 'fee_structure__course'),
        id=student_fee_id,
        student__login_info__status='V',
    )
    payments = FeePayment.objects.filter(student_fee=student_fee).order_by('-payment_date', '-entered_at', '-id')
    total_paid = payments.aggregate(total=Sum('amount'))['total'] or 0
    remaining_amount = student_fee.total_amount - total_paid
    form = FeePaymentForm(request.POST or None, remaining_amount=remaining_amount)

    if request.method == 'POST' and form.is_valid():
        payment = form.save(commit=False)
        payment.student_fee = student_fee
        payment.entered_by = office_staff
        payment.save()
        messages.success(request, 'Payment added successfully.')
        return redirect('student_fee_payment_details', student_fee_id=student_fee.id)

    return render(request, 'office/student_fee_payment_details.html', {
        'office_staff': office_staff,
        'student_fee': student_fee,
        'student': student_fee.student,
        'payments': payments,
        'total_payable': student_fee.total_amount,
        'total_paid': total_paid,
        'remaining_amount': remaining_amount,
        'form': form,
    })


def individual_student_fee_management(request):
    office_staff = _get_billing_staff(request)
    if not isinstance(office_staff, OfficeFacultyRegistration):
        return office_staff

    semesters = StudentReg.objects.filter(
        login_info__status='V'
    ).values_list('sem', flat=True).distinct().order_by('sem')
    return render(request, 'office/individual_student_fee_management.html', {
        'office_staff': office_staff,
        'semesters': semesters,
    })


def individual_student_fee_departments(request, semester):
    office_staff = _get_billing_staff(request)
    if not isinstance(office_staff, OfficeFacultyRegistration):
        return office_staff

    departments = DepTable.objects.filter(
        studentreg__sem=semester,
        studentreg__login_info__status='V',
    ).distinct().order_by('dep')
    return render(request, 'office/individual_student_fee_departments.html', {
        'office_staff': office_staff,
        'semester': semester,
        'departments': departments,
    })


def individual_student_fee_courses(request, semester, department_id):
    office_staff = _get_billing_staff(request)
    if not isinstance(office_staff, OfficeFacultyRegistration):
        return office_staff

    department = get_object_or_404(DepTable, id=department_id)
    courses = Course.objects.filter(
        dep=department,
        studentreg__sem=semester,
        studentreg__login_info__status='V',
    ).distinct().order_by('course')
    return render(request, 'office/individual_student_fee_courses.html', {
        'office_staff': office_staff,
        'semester': semester,
        'department': department,
        'courses': courses,
    })


def individual_student_fee_students(request, semester, course_id):
    office_staff = _get_billing_staff(request)
    if not isinstance(office_staff, OfficeFacultyRegistration):
        return office_staff

    course = get_object_or_404(Course, id=course_id)
    students = StudentReg.objects.filter(
        sem=semester,
        course=course,
        login_info__status='V',
    ).prefetch_related(
        Prefetch(
            'studentfee_set',
            queryset=StudentFee.objects.filter(
                semester=semester,
                fee_structure__course=course,
            ).order_by('-updated_at', '-id'),
            to_attr='assigned_fees',
        )
    ).order_by('reg_no')
    return render(request, 'office/individual_student_fee_students.html', {
        'office_staff': office_staff,
        'semester': semester,
        'course': course,
        'students': students,
    })


def assign_student_fees(request, semester, course_id):
    office_staff = _get_billing_staff(request)
    if not isinstance(office_staff, OfficeFacultyRegistration):
        return office_staff

    if request.method != 'POST':
        return redirect('individual_student_fee_students', semester=semester, course_id=course_id)

    course = get_object_or_404(Course, id=course_id)
    fee_structure = FeeStructure.objects.filter(
        course=course,
        semester=semester,
    ).order_by('-updated_at', '-id').first()
    if not fee_structure:
        messages.error(request, 'No fee structure is configured for this course and semester.')
        return redirect('individual_student_fee_students', semester=semester, course_id=course_id)

    students = StudentReg.objects.filter(
        sem=semester,
        course=course,
        login_info__status='V',
    )
    assigned_count = 0
    skipped_count = 0
    with transaction.atomic():
        for student in students:
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
                    'semester': semester,
                    'total_amount': amount,
                    'due_date': fee_structure.due_date,
                    'updated_by': office_staff,
                },
                create_defaults={
                    'semester': semester,
                    'total_amount': amount,
                    'due_date': fee_structure.due_date,
                    'created_by': office_staff,
                    'updated_by': office_staff,
                },
            )
            assigned_count += 1

    messages.success(request, f'Fee structure assigned to {assigned_count} student(s).')
    if skipped_count:
        messages.warning(
            request,
            f'{skipped_count} student(s) were skipped because their seat type or matching fee amount is not set.',
        )
    return redirect('individual_student_fee_students', semester=semester, course_id=course_id)


def edit_individual_student_fee(request, semester, course_id, student_id):
    office_staff = _get_billing_staff(request)
    if not isinstance(office_staff, OfficeFacultyRegistration):
        return office_staff

    course = get_object_or_404(Course, id=course_id)
    student = get_object_or_404(
        StudentReg,
        id=student_id,
        sem=semester,
        course=course,
        login_info__status='V',
    )
    fee_structure = FeeStructure.objects.filter(
        course=course,
        semester=semester,
    ).order_by('-updated_at', '-id').first()
    if not fee_structure:
        messages.error(request, 'No fee structure is configured for this course and semester.')
        return redirect('individual_student_fee_students', semester=semester, course_id=course_id)

    student_fee = StudentFee.objects.filter(
        student=student,
        fee_structure=fee_structure,
    ).first()
    form = StudentFeeForm(request.POST or None, instance=student_fee)
    if request.method == 'POST' and form.is_valid():
        student_fee = form.save(commit=False)
        student_fee.student = student
        student_fee.fee_structure = fee_structure
        student_fee.semester = semester
        if not student_fee.pk:
            student_fee.created_by = office_staff
        student_fee.updated_by = office_staff
        student_fee.save()
        messages.success(request, f'Individual fee saved for {student}.')
        return redirect('individual_student_fee_students', semester=semester, course_id=course_id)

    return render(request, 'office/edit_individual_student_fee.html', {
        'office_staff': office_staff,
        'student': student,
        'course': course,
        'semester': semester,
        'fee_structure': fee_structure,
        'form': form,
    })


def edit_student_seat_type(request, semester, course_id, student_id):
    office_staff = _get_billing_staff(request)
    if not isinstance(office_staff, OfficeFacultyRegistration):
        return office_staff

    course = get_object_or_404(Course, id=course_id)
    student = get_object_or_404(
        StudentReg,
        id=student_id,
        sem=semester,
        course=course,
        login_info__status='V',
    )
    form = StudentSeatTypeForm(request.POST or None, instance=student)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Seat type saved for {student}.')
        return redirect('individual_student_fee_students', semester=semester, course_id=course_id)

    return render(request, 'office/edit_student_seat_type.html', {
        'office_staff': office_staff,
        'student': student,
        'course': course,
        'semester': semester,
        'form': form,
    })


def _get_billing_staff(request):
    office_login_id = request.session.get("office_login_id")
    session_type = request.session.get("type")
    if not office_login_id or session_type != 'office':
        return redirect('login')

    office_staff = get_object_or_404(OfficeFacultyRegistration, login_info__id=office_login_id)
    if office_staff.position != 'BS':
        return HttpResponseForbidden('Only Billing Staff can access student fee management.')
    return office_staff


def mark_office_attendance(request):
    if request.method == "POST":
        office_login_id = request.session.get("office_login_id")
        session_type = request.session.get("type")
        
        if not office_login_id or session_type != 'office':
            return JsonResponse({'success': False, 'message': 'Unauthorized session'}, status=401)

        office_staff = get_object_or_404(OfficeFacultyRegistration, login_info__id=office_login_id)
        today = datetime.date.today()
        
        try:
            lat = float(request.POST.get('latitude', 0))
            lng = float(request.POST.get('longitude', 0))
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'message': 'Invalid latitude/longitude coordinates provided.'}, status=400)

        dist = calculate_distance(lat, lng)
        
        if dist > MAX_DISTANCE_METERS:
            return JsonResponse({
                'success': False,
                'message': f'You are {round(dist, 1)}m away from office. Must be within {int(MAX_DISTANCE_METERS)}m of office premises.'
            }, status=400)

        existing = OfficeAttendance.objects.filter(office_staff=office_staff, date=today).first()
        
        # Scenario 1: No attendance record today -> Perform Check In
        if not existing:
            attendance = OfficeAttendance.objects.create(
                office_staff=office_staff,
                date=today,
                status='P',
                marked_at=timezone.now(),
                latitude=lat,
                longitude=lng
            )
            return JsonResponse({
                'success': True,
                'action': 'checkin',
                'message': 'Check-in recorded successfully!',
                'time_formatted': attendance.marked_at.strftime("%I:%M %p"),
                'date': today.strftime("%Y-%m-%d")
            })
        
        # Scenario 2: Check-in done, but not checked out -> Perform Check Out
        elif existing and not existing.checked_out_at:
            existing.checked_out_at = timezone.now()
            existing.save()
            return JsonResponse({
                'success': True,
                'action': 'checkout',
                'message': 'Check-out recorded successfully!',
                'time_formatted': existing.checked_out_at.strftime("%I:%M %p"),
                'date': today.strftime("%Y-%m-%d")
            })
        
        # Scenario 3: Both Check-in and Check-out completed for today
        else:
            return JsonResponse({
                'success': False,
                'message': 'Attendance and Check-out for today are already completed.'
            }, status=400)

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)


def change_password_office(request):
    office_login_id = request.session.get("office_login_id")
    session_type = request.session.get("type")
    
    if not office_login_id or session_type != 'office':
        return redirect('login')

    office_staff = get_object_or_404(OfficeFacultyRegistration, login_info__id=office_login_id)

    if request.method == "POST":
        old_password = request.POST.get("oldPassword")
        new_password = request.POST.get("newPassword")
        confirm_password = request.POST.get("confirmPassword")

        if old_password and old_password != office_staff.login_info.password:
            messages.error(request, "Incorrect current password.")
            return redirect("change_password_office")

        if new_password == confirm_password:
            office_staff.login_info.password = new_password
            office_staff.login_info.save()
            messages.success(request, "Password changed successfully!")
            return redirect("office_home")
        else:
            messages.error(request, "New password and confirmation do not match.")
            return redirect("change_password_office")

    return render(request, "office/change_password_office.html", {"office_staff": office_staff})


def apply_office_leave(request):
    office_login_id = request.session.get("office_login_id")
    session_type = request.session.get("type")
    
    if not office_login_id or session_type != 'office':
        return redirect('login')

    office_staff = get_object_or_404(OfficeFacultyRegistration, login_info__id=office_login_id)

    if request.method == "POST":
        form = OfficeLeaveApplicationForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.office_staff = office_staff
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            day_type = request.POST.get('day_type', 'full')
            
            if start_date == end_date and day_type == 'half':
                leave.day_type = 'half'
                leave.num_of_days = 0.5
            else:
                leave.day_type = 'full'
                num_days = (end_date - start_date).days + 1
                leave.num_of_days = float(num_days)

            leave.status = 'P'
            leave.save()
            messages.success(request, "Your leave application has been submitted successfully. Awaiting Admin verification.")
            return redirect("my_office_leave_applications")
    else:
        form = OfficeLeaveApplicationForm()

    return render(request, "office/apply_office_leave.html", {
        "office_staff": office_staff,
        "form": form
    })


def my_office_leave_applications(request):
    office_login_id = request.session.get("office_login_id")
    session_type = request.session.get("type")
    
    if not office_login_id or session_type != 'office':
        return redirect('login')

    office_staff = get_object_or_404(OfficeFacultyRegistration, login_info__id=office_login_id)
    leaves = OfficeLeaveApplication.objects.filter(office_staff=office_staff).order_by('-submitted_on', '-id')

    return render(request, "office/my_office_leave_applications.html", {
        "office_staff": office_staff,
        "leaves": leaves
    })


def cancel_office_leave(request, id):
    office_login_id = request.session.get("office_login_id")
    session_type = request.session.get("type")
    
    if not office_login_id or session_type != 'office':
        return redirect('login')

    office_staff = get_object_or_404(OfficeFacultyRegistration, login_info__id=office_login_id)
    leave = get_object_or_404(OfficeLeaveApplication, id=id, office_staff=office_staff)
    
    if leave.status == 'P':
        leave.delete()
        messages.success(request, "Leave application cancelled successfully.")
    else:
        messages.error(request, "Only pending leave applications can be cancelled.")
        
    return redirect("my_office_leave_applications")