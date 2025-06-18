from django.shortcuts import render, redirect
from django.utils.timezone import localtime, now
from django.utils import timezone
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum

from django.shortcuts import get_object_or_404, redirect
from django.db.models import Count
from django.contrib.auth import authenticate, login as auth_login ,logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Patient, LabTest,Doctor, Appointment,LabTestRequest,MedicalRecord,Receptionist,User,LabTestResult,Laboratorist,Invoice, InvoiceItem

# Create your views here.



def home(request):
    return render(request, 'home.html')


#admin views
def login_admin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        try:
        
            user = User.objects.get(username=username)
            if user.check_password(password):
                request.session['user_id'] = user.id
                return redirect('admiin_dashboard') 
            else:
                messages.error(request, 'Invalid password.')
        except User.DoesNotExist:
            messages.error(request, 'User does not exist.')

    return render(request, 'login_admiin.html')

@staff_member_required
def admin_dashboard(request):
    return render(request, 'admiin_dashboard.html',)
@staff_member_required
def admin_invoice_summary(request):
    invoices = Invoice.objects.select_related('patient').prefetch_related('items')
    total_collected = Invoice.objects.aggregate(total= Sum('total_amount'))['total'] or 0

    return render(request, 'admiin_invoice_summary.html', {
        'invoices': invoices,
        'total_collected': total_collected})
@staff_member_required
def approve_users(request):
    doctors_list = Doctor.objects.filter(approved=False)
    doctor_paginator = Paginator(doctors_list, 5)
    doctor_page = request.GET.get('doctor_page', 1)
    doctors = doctor_paginator.get_page(doctor_page)

    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')

        if user_type == 'doctor':
            try:
                doctor = Doctor.objects.get(id=user_id)
                if action == 'approve':
                    doctor.approved = True
                    doctor.save()
                    messages.success(request, f'Doctor {doctor.name} approved successfully.')
                elif action == 'delete':
                    doctor.delete()
                    messages.success(request, f'Doctor {doctor.name} deleted successfully.')
            except Doctor.DoesNotExist:
                messages.error(request, 'Doctor not found.')

        return redirect('approve_users')

    return render(request, 'approve_users.html', {
        'doctors': doctors
    })
@staff_member_required
def register_receptionist(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        reception_id = request.POST.get('id')  
        password = request.POST.get('password')
        phone = request.POST.get('phone')

      
        if Receptionist.objects.filter(reception_id=reception_id).exists():
            messages.error(request, "Reception ID already taken.")
            return render(request, 'register_receptionist.html')
        user = User.objects.create_user(username=username, password=password)
        Receptionist.objects.create(
            reception_id=reception_id,
            user=user,
            phone=phone,
            username=username
        )

        return redirect('register_receptionist')

    return render(request, 'register_receptionist.html')
@staff_member_required
def laboratorist_register(request):
    if request.method == 'POST':
        lab_id = request.POST.get('lab_id')
        name = request.POST.get('name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        phone = request.POST.get('phone')
        if password != password2:
            return HttpResponse("Passwords do not match")

        if Laboratorist.objects.filter(lab_id=lab_id).exists():
            return HttpResponse("Laboratorist ID already exists")

        user = User.objects.create_user(username=username, password=password)
        Laboratorist.objects.create(
            user=user,
            lab_id=lab_id,
            name=name,
            phone=phone,
        )
        return render(request , 'admiin_dashboard.html')

    return render(request, 'laboratorist_register.html')

@staff_member_required
def lab_test_list(request):
    tests = LabTest.objects.all()
    return render(request, 'lab_test_list.html', {'tests': tests})

@staff_member_required
def lab_test_create(request):
    error = ''
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        price = request.POST.get('price', '').strip()
        if not name:
            error = 'Name is required.'
        elif not price:
            error = 'Price is required.'
        else:
            try:
                price_val = float(price)
                if price_val < 0:
                    error = 'Price cannot be negative.'
            except ValueError:
                error = 'Invalid price value.'

        if not error:
            LabTest.objects.create(name=name, price=price_val)
            return redirect('lab_test_list')

    return render(request, 'lab_test_price.html', {'error': error, 'action': 'Add', 'labtest': None})

@staff_member_required
def lab_test_edit(request, test_id):
    test = get_object_or_404(LabTest, id=test_id)
    error = ''

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        price = request.POST.get('price', '').strip()
        if not name:
            error = 'Name is required.'
        elif not price:
            error = 'Price is required.'
        else:
            try:
                price_val = float(price)
                if price_val < 0:
                    error = 'Price cannot be negative.'
            except ValueError:
                error = 'Invalid price value.'

        if not error:
            test.name = name
            test.price = price_val
            test.save()
            return redirect('lab_test_list')

    return render(request, 'lab_test_form.html', {'error': error, 'action': 'Edit', 'labtest': test})


@staff_member_required
def all_users(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        user_id = request.POST.get('user_id')

        if user_type == 'doctor':
            obj = get_object_or_404(Doctor, id=user_id)
            obj.delete()
        elif user_type == 'patient':
            obj = get_object_or_404(Patient, id=user_id)
            obj.delete()
        elif user_type == 'receptionist':
            obj = get_object_or_404(Receptionist, id=user_id)
            obj.delete()
        elif user_type == 'laboratorist':
            obj = get_object_or_404(Laboratorist, id=user_id)
            obj.delete()

        return redirect('all_users')

    context = {
        'doctors': Doctor.objects.all(),
        'patients': Patient.objects.all(),
        'receptionists': Receptionist.objects.all(),
        'laboratorists': Laboratorist.objects.all(),
    }
    return render(request, 'all_users.html', context)




# Doctor Views
def register_doctor(request):
    if request.method == 'POST':
        did = request.POST['doctor_id']
        name = request.POST['name']
        personal_file = request.FILES.get('personal_file')
        specialization = request.POST['specialization']
        password = request.POST['password']

   
        if User.objects.filter(username=name).exists():
            messages.error(request, "A user with this name already exists.")
            return redirect('doctor_register') 

     
        user = User.objects.create_user(username=name, password=password)

     
        Doctor.objects.create(
            user=user,
            name=name,
            doctor_id=did,
            personal_info=personal_file,
            specialization=specialization,
            approved=False 
        )

        messages.success(request, "Doctor registered successfully. Please wait for approval.")
        return redirect('home')  

    return render(request, 'register_doctor.html')

def login_doctor(request):
    if request.method == 'POST':
        name = request.POST['name']
        password = request.POST['password']
        user = authenticate(request, username=name, password=password)

        if user is not None:
            try:
                doctor = user.doctor
                if not doctor.approved:
                    messages.warning(request, 'Your account is not approved yet.')
                    return render(request, 'login_doctor.html')
                auth_login(request, user)
                request.session['doctor_id'] = doctor.id 
                return redirect('doctor_dashboard')
            except Doctor.DoesNotExist:
                messages.error(request, 'You are not registered as a doctor.')
        else:
            messages.error(request, 'Invalid login credentials.')

    return render(request, 'login_doctor.html')


def receptionist_dashboard(request):
    total_doctors = Doctor.objects.count()
    total_patients = Patient.objects.count()
    patients = Patient.objects.all()
    appointment_status_counts = Appointment.objects.values('status').annotate(count=Count('id'))
    status_counts = {item['status']: item['count'] for item in appointment_status_counts}


    current_datetime = localtime(now())
    current_date = current_datetime.date()
    current_time = current_datetime.time()

    busy_doctor_ids = Appointment.objects.filter(
        date=current_date,
        time=current_time,
        status='scheduled'
    ).values_list('doctor_id', flat=True)

    available_now_doctors = Doctor.objects.exclude(id__in=busy_doctor_ids).filter(approved=True)

    return render(request, 'receptionist_dashboard.html', {
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'status_counts': status_counts,
        'available_now_doctors': available_now_doctors,
        'current_date': current_date,
        'current_time': current_time,
        'patients':patients,
    })
 

def register_patient(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        name = request.POST.get('name')
        password= request.POST.get('password')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        contact_number = request.POST.get('contact_number')
        address = request.POST.get('address')
        medical_history = request.POST.get('medical_history', '')
        emergency_contact_name = request.POST.get('emergency_contact_name')
        emergency_contact_number = request.POST.get('emergency_contact_number')
        if Patient.objects.filter(patient_id=id).exists():

            messages.error(request, 'Patient ID already exists.')
            return render(request, 'register_patient.html')

        if not all([name, age, gender, contact_number, address, emergency_contact_name, emergency_contact_number,password]):
            messages.error(request, "All fields are required.")
            return render(request, 'register_patient.html')

        patient = Patient(
            patient_id=id,
            name=name,
            age=age,
            gender=gender,
            contact_number=contact_number,
            address=address,
            medical_history=medical_history,
            emergency_contact_name=emergency_contact_name,
            emergency_contact_number=emergency_contact_number,
            approved=False, 
        )
        patient.set_password(password)
        patient.save()

        messages.success(request, "Patient registered successfully.")
        return redirect('patients') 
    return render(request, 'register_patient.html')



def login_patient(request):
    if request.method == 'POST':
        name = request.POST.get('username')
        password = request.POST.get('password')

        try:
            patient = Patient.objects.get(name=name)
            
            if patient.check_password(password): 
                request.session['patient_id'] = patient.id
                return redirect('patient_dashboard')
            else:
                messages.error(request, 'Invalid password')
        except Patient.DoesNotExist:
            messages.error(request, 'User does not exist')

    return render(request, 'login_patient.html')



def patient_list(request):

    patients = Patient.objects.all()
    appt = Appointment.objects.all()

    search_query = request.GET.get('search', '')
    if search_query:
        patients = patients.filter(name__icontains=search_query)
    return render(request, 'patients.html', {'patients': patients, 'search_query': search_query, 'appt':appt})






def schedule_appointment(request):
    doctors = Doctor.objects.all()
    patients = Patient.objects.all()
    selected_doctor = None
    selected_patient = None
    doctor_appointments = []

    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        doctor_id = request.POST.get('doctor_id')
        date = request.POST.get('date')
        time = request.POST.get('time')

        conflicting_appointment = Appointment.objects.filter(doctor_id=doctor_id, date=date, time=time).first()

        if conflicting_appointment:
            doctor = Doctor.objects.get(id=doctor_id)
            messages.error(request, f"Dr. {doctor.name} is already booked at {time} on {date}.")
            return redirect('schedule_appointment')

        try:
            patient = Patient.objects.get(id=patient_id)
            doctor = Doctor.objects.get(id=doctor_id)

            Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                date=date,
                time=time,
                status='scheduled'
            )

            messages.success(request, f"Appointment scheduled with Dr. {doctor.name} on {date} at {time}.")
            return redirect('receptionist_dashboard')

        except (Patient.DoesNotExist, Doctor.DoesNotExist):
            messages.error(request, "Invalid patient or doctor selected.")
            return redirect('schedule_appointment')

    else:
        doctor_id = request.GET.get('doctor_id')
        patient_id = request.GET.get('patient_id')

        if doctor_id:
            try:
                selected_doctor = Doctor.objects.get(id=doctor_id)
                doctor_appointments = Appointment.objects.filter(doctor=selected_doctor).order_by('date', 'time')
            except Doctor.DoesNotExist:
                messages.error(request, "Doctor not found.")

        if patient_id:
            try:
                selected_patient = Patient.objects.get(id=patient_id)
            except Patient.DoesNotExist:
                selected_patient = None  

    return render(request, 'schedule_appointment.html', {
        'doctors': doctors,
        'patients': patients,
        'selected_doctor': selected_doctor,
        'selected_patient': selected_patient,
        'doctor_appointments': doctor_appointments
    })



@login_required
def doctor_schedule_view(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, "You are not authorized to view this page.")
        return redirect('login_doctor') 

    appointments = Appointment.objects.filter(doctor=doctor).order_by('date', 'time')
    return render(request, 'doctor_schedule.html', {'appointments': appointments, 'doctor': doctor})




def update_appointment_status(request, appointment_id, action):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to update appointment status.")
        return redirect('login_doctor')

    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, "Only doctors are allowed to perform this action.")
        return redirect('login_doctor')

    appointment = Appointment.objects.filter(id=appointment_id).first()
    if not appointment:
        messages.error(request, "Appointment not found.")
        return redirect('doctor_schedule')

    if appointment.doctor != doctor:
        messages.error(request, "You are not authorized to update this appointment.")
        return redirect('doctor_schedule')

    valid_actions = ['accepted', 'rejected', 'completed']
    if action in valid_actions:
        appointment.status = action
        appointment.save()
        
    else:
        messages.error(request, "Invalid action.")

    return redirect('doctor_schedule')



def upload_medical_record(request):
    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        return redirect('login_doctor')

    doctor = get_object_or_404(Doctor, id=doctor_id)
    medical = Appointment.objects.filter(doctor=doctor, status='accepted').select_related('patient')

    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        diagnosis = request.POST.get('diagnosis')
        treatment = request.POST.get('treatment')

        if not patient_id or not diagnosis or not treatment:
            messages.error(request, "All fields are required.")
        else:
            try:
                patient = Patient.objects.get(id=patient_id)
                MedicalRecord.objects.create(
                    patient=patient,
                    doctor=doctor,
                    diagnosis=diagnosis,
                    treatment=treatment,
                )
                messages.success(request, "Medical record saved successfully.")
                return redirect('doctor_dashboard')
            except Patient.DoesNotExist:
                messages.error(request, "Selected patient does not exist.")

    return render(request, 'upload_medical_record.html', {
        'doctor': doctor,
        'medical': medical,
    })




def patient_medical_records(request):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('login_patient')

    patient = get_object_or_404(Patient, id=patient_id)
    records = MedicalRecord.objects.filter(patient=patient).order_by('-date')

    return render(request, 'patient_medical_records.html', {
        'patient': patient,
        'records': records,
    })




def patient_dashboard(request):
    if 'patient_id' not in request.session:
        return redirect('login_patient')

    patient = Patient.objects.get(id=request.session['patient_id'])
    appointments = Appointment.objects.filter(patient=patient).order_by('-date', '-time')
    medical_records = MedicalRecord.objects.filter(patient=patient).order_by('-date')
    invoices = Invoice.objects.filter(patient_id=patient)

    return render(request, 'patient_dashboard.html', {
        'patient': patient,
        'appointments': appointments,
        'invoices':invoices,
        'medical_records': medical_records,
    })

def doctor_dashboard(request):
   
    doctor = Doctor.objects.get(id=request.session['doctor_id'])
    appointments = Appointment.objects.filter(doctor=doctor).exclude(status='completed')
    return render(request, 'doctor_dashboard.html', {'doctor': doctor, 'appointments': appointments})


def completed_appointments(request):
    doctor = Doctor.objects.get(id=request.session['doctor_id'])
    completed = Appointment.objects.filter(doctor=doctor, status='completed')
    return render(request, 'completed_appointments.html', {'doctor': doctor, 'completed': completed})


def delete_appointment(request, pk):
    doctor = Doctor.objects.get(id=request.session['doctor_id'])
    appointment = get_object_or_404(Appointment, id=pk, doctor=doctor)

   
    appointment.delete()
    
    return redirect('completed_appointments')





def view_appointments(request):
    doctor = Doctor.objects.get(id=request.session['doctor_id'])
    appointments = Appointment.objects.filter(doctor=doctor)
    return render(request, 'view_appointments.html', {'appointments': appointments})


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)  

        if user is not None:
            try:
                user.laboratorist
                auth_login(request, user)
                return redirect('pending_lab_requests')
            except Laboratorist.DoesNotExist:
                pass
            try:
                user.receptionist
                auth_login(request, user)
                return redirect('receptionist_dashboard')
            except Receptionist.DoesNotExist:
                return HttpResponse("You are not registered.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'lab_login.html')



def logout(request):
    auth_logout(request)
    return redirect('/')





@login_required
def request_lab_test(request):
    doctor = get_object_or_404(Doctor, user=request.user)

    patients = Patient.objects.filter(
        appointments__doctor=doctor,
        appointments__status='accepted'
    ).distinct()

    tests = LabTest.objects.all()

    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        test_id = request.POST.get('test_id')
        description = request.POST.get('description')

        
        patient = get_object_or_404(
            Patient,
            id=patient_id,
            appointments__doctor=doctor,
            appointments__status='accepted'
        )

        test = get_object_or_404(LabTest, id=test_id)

        LabTestRequest.objects.create(
            doctor=doctor,
            patient=patient,
            test=test,
            description=description
        )
        return redirect('doctor_dashboard')

    return render(request, 'request_lab_test.html', {
        'patients': patients,
        'tests': tests
    })





@login_required
def pending_lab_requests(request):
    laboratorist = get_object_or_404(Laboratorist, user=request.user)
    pending_requests = LabTestRequest.objects.filter(is_completed=False)
    return render(request, 'pending_requests.html', {'pending_requests': pending_requests})






@login_required
def submit_lab_result(request, request_id):
    laboratorist = get_object_or_404(Laboratorist, user=request.user)
    test_request = get_object_or_404(LabTestRequest, id=request_id)

    if request.method == 'POST':
        result_text = request.POST.get('result_text')
        result_file = request.FILES.get('result_file')

        lab_result, created = LabTestResult.objects.get_or_create(
            request=test_request,
            defaults={
                'laboratorist': laboratorist,
                'result_text': result_text,
                'result_file': result_file if isinstance(result_file, UploadedFile) else None
            }
        )

        if not created:
        
            lab_result.result_text = result_text
            if isinstance(result_file, UploadedFile):
                lab_result.result_file = result_file
            lab_result.laboratorist = laboratorist
            lab_result.save()


        test_request.is_completed = True
        test_request.save()


        invoice_exists = InvoiceItem.objects.filter(
            invoice__patient=test_request.patient,
            description__icontains=test_request.test.name
        ).exists()

        if not invoice_exists:
            test_fee = test_request.test.price
            invoice = Invoice.objects.create(
                patient=test_request.patient,
                created_by=request.user,
                total_amount=test_fee
            )
            InvoiceItem.objects.create(
                invoice=invoice,
                description=f"Lab Test: {test_request.test.name}",
                amount=test_fee
            )

        return render(request, 'pending_requests.html')

    return render(request, 'submit_lab_result.html', {'test_request': test_request})




@login_required
def doctor_view_results(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    results = LabTestResult.objects.filter(request__doctor=doctor)

    return render(request, 'doctor_view_results.html', {'results': results})




def complete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'completed'
    appointment.save()

    invoice_exists = Invoice.objects.filter(
        patient=appointment.patient,
        date_issued__date=timezone.now().date(),
        items__description__icontains='Doctor Consultation Fee'
    ).exists()

    if not invoice_exists:
        invoice = Invoice.objects.create(
            patient=appointment.patient,
            created_by=request.user if request.user.is_authenticated else None,
            total_amount=500  )
        InvoiceItem.objects.create(
            invoice=invoice,
            description="Doctor Consultation Fee",
            amount=500
        )
    
    return redirect('appointment_success')






