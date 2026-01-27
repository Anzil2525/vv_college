from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import LoginTable, DepTable, Positions, Course, StaffReg, StudentReg, GuadinReg
from .forms import *
import datetime
from web_admin.views import admin_required
import uuid


# Create your views here.
def log_out_function(request):
    request.session.flush()
    
    return render(request, 'index/index.html')

def index(request):
    # request.session.flush()

    auto_login_id = request.session.get('auto_login_id')

    if auto_login_id:
        try:
            login_ins = LoginTable.objects.get(auto_login_id=uuid.UUID(auto_login_id))

            request.session.set_expiry(60 * 60 * 24 * 14)

            if login_ins.user == "admin" and login_ins.status == "V":
                request.session['admin_login_id'] = login_ins.id
                request.session['type'] = 'admin'
                return redirect('admin_home')
            
            elif login_ins.user == "student" and login_ins.status == "V":
                request.session['student_login_id'] = login_ins.id
                request.session['type'] = 'student'
                return redirect('student_home')
            
            elif login_ins.user == "staff" and login_ins.status == "V":
                request.session['staff_login_id'] = login_ins.id
                request.session['type'] = 'staff'
                return redirect('staff_home')
            
            elif login_ins.user == "staff" and login_ins.status == "R":
                reason_msg = f" Reason: {login_ins.rejection_reason}" if login_ins.rejection_reason else ""
                messages.error(
                    request, f'Your request was rejected by the admin.{reason_msg}'
                )
                return redirect('resent', login_ins = login_ins.id)
            
            elif login_ins.user == "guardian" and login_ins.status == "V":
                request.session['guardian_login_email'] = login_ins.email
                request.session['type'] = 'guardian'
                return redirect('guardian_home')
            else:
                messages.error(request, 'Admin verification pending')

        except LoginTable.DoesNotExist:
            return render(request, 'index/index.html')

    return render(request, 'index/index.html')


@admin_required
def dep_reg(request):
    if request.method == "POST":
        deprt = request.POST.get('dep')

        try:
            ins = DepTable.objects.get(dep = deprt)
            messages.error(request, 'Department already exist')
        except DepTable.DoesNotExist:
            pass

        form = DepTableForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully Registered.')
            return redirect("view_dep")
    else:
        form = DepTableForm()
    return render(request, 'index/dep_reg.html', {'data' : form})


def staff_reg(request):
    departments = DepTable.objects.all()
    position = Positions.objects.exclude(pos = 'Principal')

    if request.method == "POST":
        form = StaffRegForm(request.POST, request.FILES)
        login_form = LoginTableForm(request.POST)
        
        email = request.POST.get('email')
        if LoginTable.objects.filter(email=email).exists():
            messages.error(request, "It appears that an account with this email address already exists.")
        elif form.is_valid() and login_form.is_valid():
            pos = form.cleaned_data['pos']
            dep = form.cleaned_data['dep']

            if pos.pos == 'HOD':
                # ✅ check if another HOD already exists in this department
                hod_exists = StaffReg.objects.filter(dep=dep, pos__pos='HOD')
                
                if hod_exists:
                    messages.error(request, 'This department already has a designated Head of Department. Only one HOD is permitted per department.')
                    return redirect('staff_reg')

            ins = login_form.save(commit=False)
            ins.user = 'staff'
            ins.save()

            ins2 = form.save(commit=False)
            ins2.login_info = ins
            ins2.save()

            messages.success(request, 'Successfully Registered.')
            return redirect("login")

    else:
        form = StaffRegForm()
        login_form = LoginTableForm()
    return render(request, 'index/staff_reg.html', {'form':form, 'login':login_form,'departments':departments, 'position':position})


def student_reg(request):
    departments = DepTable.objects.all()
    course = Course.objects.all()
    current_year = datetime.date.today().year
    year_list = [i for i in range(current_year, 1999, -1)]

    if request.method == "POST":
        form = StudentRegForm(request.POST)
        guadin = GuadinRegForm(request.POST)
        login_form = LoginTableForm(request.POST)

        if form.is_valid() and guadin.is_valid() and login_form.is_valid():
            email = login_form.cleaned_data['email']

            # ✅ Check duplicate email
            if LoginTable.objects.filter(email=email).exists():
                messages.error(request, "This email is already registered. Please use another email or log in.")
                return render(request, 'index/student_reg.html', {
                    'form': form,
                    'login': login_form,
                    'guadin': guadin,
                    'departments': departments,
                    'year_list': year_list,
                    'course': course
                })
            
            dep = form.cleaned_data['dep']
            cou = form.cleaned_data['course']

            dep_ins = DepTable.objects.get(dep = dep)
            
            try:
                course_ins = Course.objects.get(course = cou, dep = dep_ins)
                # ✅ Save login first
                login_instance = login_form.save(commit=False)
                login_instance.user = 'student'
                login_instance.save()

                # ✅ Save guardian safely
                guardian_instance = guadin.save(commit=False)
                guardian_instance.save()

                # ✅ Save student and link both
                student_instance = form.save(commit=False)
                student_instance.login_info = login_instance
                student_instance.parent_1 = guardian_instance
                student_instance.save()

                messages.success(request, 'Successfully Registered.')
                return redirect("login")
                
            except Course.DoesNotExist:
                messages.error(request, 'Please Select Valid Course')

        else:
            messages.error(request, "Please correct the errors below and try again. This email's is already registered. Please use another email or log in.")

    else:
        form = StudentRegForm()
        guadin = GuadinRegForm()
        login_form = LoginTableForm()

    return render(request, 'index/student_reg.html', {
        'form': form,
        'login': login_form,
        'guadin': guadin,
        'departments': departments,
        'year_list': year_list,
        'course': course
    })


def resent(request, login_ins):
    login = LoginTable.objects.get(id = login_ins)
    reg = StaffReg.objects.get(login_info = login)
    departments = DepTable.objects.all()
    position = Positions.objects.all()

    if request.method == 'POST':
        form = StaffRegForm(request.POST, request.FILES, instance=reg)
        login_form = LoginTableForm(request.POST, instance=login)
        if form.is_valid() and login_form.is_valid():
            ins = login_form.save(commit=False)
            ins.status = "P"
            ins.save()
            form.save()
            messages.success(request, 'Successfully Resented.')
            
            return redirect("login")

    form = StaffRegForm(instance=reg)
    login_form = LoginTableForm(instance=login)

    return render(request, 'index/staff_reg_edit.html', {'form':form, 'login':login_form,'departments':departments, 'position':position})

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            remember_me = request.POST.get('remember_me')

            try:
                login_ins = LoginTable.objects.get(email = email)

                if password == login_ins.password:
                    if remember_me:
                        request.session.set_expiry(60 * 60 * 24 * 14)

                    else:
                        request.session.set_expiry(0)

                    if login_ins.user == "admin" and login_ins.status == "V":
                        request.session['admin_login_id'] = login_ins.id
                        request.session['auto_login_id'] = str(login_ins.auto_login_id)
                        request.session['type'] = 'admin'
                        return redirect('admin_home')
                    
                    elif login_ins.user == "student" and login_ins.status == "V":
                        request.session['student_login_id'] = login_ins.id
                        request.session['auto_login_id'] = str(login_ins.auto_login_id)
                        request.session['type'] = 'student'
                        return redirect('student_home')
                    
                    elif login_ins.user == "staff" and login_ins.status == "V":
                        request.session['staff_login_id'] = login_ins.id
                        request.session['auto_login_id'] = str(login_ins.auto_login_id)
                        request.session['type'] = 'staff'
                        return redirect('staff_home')
                    
                    elif login_ins.user == "staff" and login_ins.status == "R":
                        reason_msg = f" Reason: {login_ins.rejection_reason}" if login_ins.rejection_reason else ""
                        messages.error(
                            request, f'Your request was rejected by the admin.{reason_msg}'
                        )
                        return redirect('resent', login_ins = login_ins.id)
                    
                    elif login_ins.user == "guardian" and login_ins.status == "V":
                        request.session['guardian_login_email'] = login_ins.email
                        request.session['auto_login_id'] = str(login_ins.auto_login_id)
                        request.session['type'] = 'guardian'
                        return redirect('guardian_home')
                    else:
                        messages.error(request, 'Admin verification pending')
                else:
                    messages.error(request, 'Wrong Password')

            except LoginTable.DoesNotExist:
                messages.error(request, "User Doesn't exist")
    else:
        form = LoginForm()
    return render(request, 'index/login.html', {'form':form})


def guardian_reg(request):
    if request.method == 'POST':
        form = GuardianVerificationRegistration(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            email = data['email']
            phone = data['phone']

            # ✅ Step 1: Verify guardian exists
            try:
                parent_info = GuadinReg.objects.get(
                    Guadin_phone_Number=phone,
                    Guadin_email=email
                )
            except GuadinReg.DoesNotExist:
                messages.error(request,
                    "To ensure a smooth registration process, please note that parent registration is completed after the student's initial registration. "
                    "If the student is already registered, kindly use the same email address and phone number that were provided in the guardian information "
                    "section of the student's registration form. This will help us link your accounts efficiently."
                )
                return render(request, 'index/guardian_reg.html', {'form': form})

            # ✅ Step 2: Check duplicate email in LoginTable
            if LoginTable.objects.filter(email=email).exists():
                messages.error(request,
                    "This email is already registered. Please use a different email or login with existing credentials."
                )
                return render(request, 'index/guardian_reg.html', {'form': form})

            # ✅ Step 3: Create login entry
            login = LoginTable(
                email=email,
                password=data['password'],
                user="guardian",
                status="V"
            )
            login.save()

            messages.success(request, "Guardian account created successfully! You may now log in.")
            return redirect('login')

    else:
        form = GuardianVerificationRegistration()

    return render(request, 'index/guardian_reg.html', {'form': form})