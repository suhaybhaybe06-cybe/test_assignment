from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST


from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


from .models import (
    Patient,
    Doctor,
    Department,
    Appointment,
    MedicalRecord,
    Prescription,
    Bill,
    HospitalSettings,
    Notification,
)

from .forms import (
    PatientForm,
    DoctorForm,
    DepartmentForm,
    AppointmentForm,
    MedicalRecordForm,
    PrescriptionForm,
    BillForm,
    HospitalSettingsForm,
    ProfileForm,
    ChangePasswordForm
)


# =====================================================
# PATIENTS
# =====================================================

@login_required
def patient_list(request):

    search = request.GET.get(
        'search',
        ''
    )

    patients = Patient.objects.all()

    if search:

        patients = patients.filter(
            first_name__icontains=search
        ) | patients.filter(
            last_name__icontains=search
        ) | patients.filter(
            phone__icontains=search
        )

    return render(
        request,
        'hospital/patient_list.html',
        {
            'patients': patients,
            'search': search
        }
    )



@login_required
def add_patient(request):

    if request.method == 'POST':

        form = PatientForm(request.POST)

        if form.is_valid():

            patient = form.save()

            # Abuur ogeysiis cusub
            Notification.objects.create(
                title='New Patient Registered',
                message=(
                    f'A new patient, {patient}, '
                    f'has been registered.'
                ),
                notification_type='Patient'
            )

            return redirect('patient_list')

    else:
        form = PatientForm()

    return render(
        request,
        'hospital/add_patient.html',
        {
            'form': form
        }
    )



@login_required
def patient_detail(request, patient_id):

    patient = get_object_or_404(
    Patient,
    id=patient_id
)

    medical_records = MedicalRecord.objects.filter(
        patient=patient
    ).order_by(
        '-record_date'
    )

    return render(
        request,
        'hospital/patient_detail.html',
        {
            'patient': patient,
            'medical_records': medical_records,
        }
    )


@login_required
def edit_patient(request, patient_id):

    patient = Patient.objects.get(
        id=patient_id
    )

    if request.method == 'POST':

        form = PatientForm(
            request.POST,
            instance=patient
        )

        if form.is_valid():

            form.save()

            return redirect(
                'patient_detail',
                patient_id=patient.id
            )

    else:

        form = PatientForm(
            instance=patient
        )

    return render(
        request,
        'hospital/edit_patient.html',
        {
            'form': form,
            'patient': patient
        }
    )


@login_required
def delete_patient(request, patient_id):

    patient = Patient.objects.get(
        id=patient_id
    )

    if request.method == 'POST':

        patient.delete()

        return redirect(
            'patient_list'
        )

    return render(
        request,
        'hospital/delete_patient.html',
        {
            'patient': patient
        }
    )


# =====================================================
# DASHBOARD
# =====================================================


@login_required
def dashboard(request):
    from datetime import timedelta
    from django.utils import timezone
    from django.db.models import Sum

    # =====================================
    # DASHBOARD STATISTICS
    # =====================================

    total_patients = Patient.objects.count()
    total_doctors = Doctor.objects.count()
    total_departments = Department.objects.count()
    total_appointments = Appointment.objects.count()
    total_medical_records = MedicalRecord.objects.count()
    total_prescriptions = Prescription.objects.count()
    total_bills = Bill.objects.count()

    # Wadarta lacagta la bixiyey
    total_revenue = (
        Bill.objects.filter(
            payment_status='Paid'
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0
    )

    # =====================================
    # RECENT DATA
    # =====================================

    recent_patients = Patient.objects.all().order_by(
        '-id'
    )[:5]

    recent_appointments = Appointment.objects.select_related(
        'patient',
        'doctor'
    ).order_by(
        '-appointment_date',
        '-appointment_time'
    )[:5]

    recent_bills = Bill.objects.select_related(
        'patient'
    ).order_by(
        '-bill_date'
    )[:5]

    # =====================================
    # NOTIFICATIONS SYSTEM
    # =====================================

    today = timezone.localdate()
    tomorrow = today + timedelta(days=1)

    # Ballamaha maanta
    today_appointments = Appointment.objects.select_related(
        'patient',
        'doctor'
    ).filter(
        appointment_date=today
    ).order_by(
        'appointment_time'
    )

    # Ballamaha berri
    tomorrow_appointments = Appointment.objects.select_related(
        'patient',
        'doctor'
    ).filter(
        appointment_date=tomorrow
    ).order_by(
        'appointment_time'
    )

    # Biilasha sugaya lacag-bixinta
    pending_bills = Bill.objects.select_related(
        'patient'
    ).filter(
        payment_status='Pending'
    ).order_by(
        '-bill_date'
    )

   
    pending_bills_count = pending_bills.count()

    # Ogeysiisyada aan weli la akhrin
    unread_notifications_count = Notification.objects.filter(
        is_read=False
    ).count()

    today_appointments_count = today_appointments.count()
    tomorrow_appointments_count = tomorrow_appointments.count()

    pending_amount = (
    pending_bills.aggregate(
        total=Sum('amount')
    )['total'] or 0
)

    # Wadarta ogeysiisyada
    notification_count = (
        today_appointments_count
        + tomorrow_appointments_count
        + pending_bills_count
    )

    # =====================================
    # DASHBOARD CONTEXT
    # =====================================

    context = {
        # Statistics
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_departments': total_departments,
        'total_appointments': total_appointments,
        'total_medical_records': total_medical_records,
        'total_prescriptions': total_prescriptions,
        'total_bills': total_bills,
        'total_revenue': total_revenue,

        # Recent data
        'recent_patients': recent_patients,
        'recent_appointments': recent_appointments,
        'recent_bills': recent_bills,

        # Notifications
       'today': today,
        'tomorrow': tomorrow,
        'today_appointments': today_appointments,
        'tomorrow_appointments': tomorrow_appointments,
        'today_appointments_count': today_appointments_count,
        'tomorrow_appointments_count': tomorrow_appointments_count,
        'pending_bills': pending_bills,
        'pending_bills_count': pending_bills_count,
        'pending_amount': pending_amount,
        'notification_count': notification_count,
        'unread_notifications_count': unread_notifications_count,
    }

    return render(
        request,
        'hospital/dashboard.html',
        context
    )
    
    
    
@login_required
@require_POST
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(
        Notification,
        id=notification_id
    )

    notification.is_read = True
    notification.save(update_fields=['is_read'])

    return redirect('notification_list')


@login_required
@require_POST
def mark_all_notifications_read(request):
    Notification.objects.filter(
        is_read=False
    ).update(is_read=True)

    return redirect('notification_list')

    
    # =====================================================
# NOTIFICATIONS
# =====================================================

@login_required
def notification_list(request):
    notifications = Notification.objects.all()

    unread_notifications_count = notifications.filter(
        is_read=False
    ).count()

    return render(
        request,
        'hospital/notification_list.html',
        {
            'notifications': notifications,
            'unread_notifications_count': unread_notifications_count,
        }
    )


# =====================================================
# DOCTORS
# =====================================================

@login_required
def doctor_list(request):

    search = request.GET.get(
        'search',
        ''
    )

    doctors = Doctor.objects.all()

    if search:

        doctors = doctors.filter(
            first_name__icontains=search
        ) | doctors.filter(
            last_name__icontains=search
        ) | doctors.filter(
            specialization__icontains=search
        ) | doctors.filter(
            phone__icontains=search
        )

    return render(
        request,
        'hospital/doctor_list.html',
        {
            'doctors': doctors,
            'search': search
        }
    )


@login_required
def add_doctor(request):

    if request.method == 'POST':

        form = DoctorForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            return redirect(
                'doctor_list'
            )

    else:

        form = DoctorForm()

    return render(
        request,
        'hospital/add_doctor.html',
        {
            'form': form
        }
    )


@login_required
def doctor_detail(request, doctor_id):

    doctor = get_object_or_404(Doctor, id=doctor_id)

    return render(
        request,
        'hospital/doctor_detail.html',
        {
            'doctor': doctor
        }
    )


@login_required
def edit_doctor(request, doctor_id):

    doctor = Doctor.objects.get(
        id=doctor_id
    )

    if request.method == 'POST':

        form = DoctorForm(
            request.POST,
            instance=doctor
        )

        if form.is_valid():

            form.save()

            return redirect(
                'doctor_detail',
                doctor_id=doctor.id
            )

    else:

        form = DoctorForm(
            instance=doctor
        )

    return render(
        request,
        'hospital/edit_doctor.html',
        {
            'form': form,
            'doctor': doctor
        }
    )


@login_required
def delete_doctor(request, doctor_id):

    doctor = Doctor.objects.get(
        id=doctor_id
    )

    if request.method == 'POST':

        doctor.delete()

        return redirect(
            'doctor_list'
        )

    return render(
        request,
        'hospital/delete_doctor.html',
        {
            'doctor': doctor
        }
    )


# =====================================================
# DEPARTMENTS
# =====================================================

@login_required
def add_department(request):

    if request.method == 'POST':

        form = DepartmentForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            return redirect(
                'department_list'
            )

    else:

        form = DepartmentForm()

    return render(
        request,
        'hospital/add_department.html',
        {
            'form': form
        }
    )


@login_required
def department_list(request):

    departments = Department.objects.all()

    return render(
        request,
        'hospital/department_list.html',
        {
            'departments': departments
        }
    )


@login_required
def department_detail(request, department_id):

    department = get_object_or_404(
    Department,
    id=department_id
)

    return render(
        request,
        'hospital/department_detail.html',
        {
            'department': department
        }
    )


@login_required
def edit_department(request, department_id):

    department = Department.objects.get(
        id=department_id
    )

    if request.method == 'POST':

        form = DepartmentForm(
            request.POST,
            instance=department
        )

        if form.is_valid():

            form.save()

            return redirect(
                'department_detail',
                department_id=department.id
            )

    else:

        form = DepartmentForm(
            instance=department
        )

    return render(
        request,
        'hospital/edit_department.html',
        {
            'form': form,
            'department': department
        }
    )


@login_required
def delete_department(request, department_id):

    department = Department.objects.get(
        id=department_id
    )

    if request.method == 'POST':

        department.delete()

        return redirect(
            'department_list'
        )

    return render(
        request,
        'hospital/delete_department.html',
        {
            'department': department
        }
    )


# =====================================================
# APPOINTMENTS
# =====================================================

@login_required
def appointment_list(request):

    search = request.GET.get(
        'search',
        ''
    )

    appointments = Appointment.objects.select_related(
        'patient',
        'doctor'
    ).all().order_by(
        'appointment_date',
        'appointment_time'
    )

    if search:

        appointments = appointments.filter(
            patient__first_name__icontains=search
        ) | appointments.filter(
            patient__last_name__icontains=search
        ) | appointments.filter(
            doctor__first_name__icontains=search
        ) | appointments.filter(
            doctor__last_name__icontains=search
        )

    return render(
        request,
        'hospital/appointment_list.html',
        {
            'appointments': appointments,
            'search': search
        }
    )



@login_required
def add_appointment(request):

    if request.method == 'POST':

        form = AppointmentForm(request.POST)

        if form.is_valid():

            appointment = form.save()

            # Abuur ogeysiis cusub
            Notification.objects.create(
                title='New Appointment',
                message=(
                    f'A new appointment has been created '
                    f'for {appointment.patient}.'
                ),
                notification_type='Appointment'
            )

            return redirect('appointment_list')

    else:
        form = AppointmentForm()

    return render(
        request,
        'hospital/add_appointment.html',
        {
            'form': form
        }
    )


@login_required
def appointment_detail(request, appointment_id):

    appointment = get_object_or_404(
    Appointment,
    id=appointment_id
)

    return render(
        request,
        'hospital/appointment_detail.html',
        {
            'appointment': appointment
        }
    )


@login_required
def edit_appointment(request, appointment_id):

    appointment = Appointment.objects.get(
        id=appointment_id
    )

    if request.method == 'POST':

        form = AppointmentForm(
            request.POST,
            instance=appointment
        )

        if form.is_valid():

            form.save()

            return redirect(
                'appointment_detail',
                appointment_id=appointment.id
            )

    else:

        form = AppointmentForm(
            instance=appointment
        )

    return render(
        request,
        'hospital/edit_appointment.html',
        {
            'form': form,
            'appointment': appointment
        }
    )


@login_required
def delete_appointment(request, appointment_id):

    appointment = Appointment.objects.get(
        id=appointment_id
    )

    if request.method == 'POST':

        appointment.delete()

        return redirect(
            'appointment_list'
        )

    return render(
        request,
        'hospital/delete_appointment.html',
        {
            'appointment': appointment
        }
    )


# =====================================================
# MEDICAL RECORDS
# =====================================================

@login_required
def medical_record_list(request):

    records = MedicalRecord.objects.select_related(
        'patient',
        'doctor'
    ).all().order_by(
        '-record_date'
    )

    return render(
        request,
        'hospital/medical_record_list.html',
        {
            'records': records
        }
    )



@login_required
def add_medical_record(request):

    if request.method == 'POST':

        form = MedicalRecordForm(
            request.POST
        )

        if form.is_valid():

            medical_record = form.save()

            Notification.objects.create(
                title='New Medical Record Created',
                message=(
                    f'A new medical record has been created '
                    f'for patient {medical_record.patient}.'
                ),
                notification_type='General'
            )

            return redirect(
                'medical_record_list'
            )

    else:

        form = MedicalRecordForm()

    return render(
        request,
        'hospital/add_medical_record.html',
        {
            'form': form
        }
    )



@login_required
def medical_record_detail(request, record_id):

    record = get_object_or_404(
    MedicalRecord,
    id=record_id
)
    

    return render(
        request,
        'hospital/medical_record_detail.html',
        {
            'record': record
        }
    )


@login_required
def edit_medical_record(request, record_id):

    record = MedicalRecord.objects.get(
        id=record_id
    )

    if request.method == 'POST':

        form = MedicalRecordForm(
            request.POST,
            instance=record
        )

        if form.is_valid():

            form.save()

            return redirect(
                'medical_record_detail',
                record_id=record.id
            )

    else:

        form = MedicalRecordForm(
            instance=record
        )

    return render(
        request,
        'hospital/edit_medical_record.html',
        {
            'form': form,
            'record': record
        }
    )


@login_required
def delete_medical_record(request, record_id):

    record = MedicalRecord.objects.get(
        id=record_id
    )

    if request.method == 'POST':

        record.delete()

        return redirect(
            'medical_record_list'
        )

    return render(
        request,
        'hospital/delete_medical_record.html',
        {
            'record': record
        }
    )


# =====================================================
# LOGIN
# =====================================================

def user_login(request):

    if request.method == 'POST':

        username = request.POST.get(
            'username'
        )

        password = request.POST.get(
            'password'
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            return redirect(
                'dashboard'
            )

        else:

            return render(
                request,
                'hospital/login.html',
                {
                    'error':
                    'Invalid username or password.'
                }
            )

    return render(
        request,
        'hospital/login.html'
    )


# =====================================================
# LOGOUT
# =====================================================

@login_required
@require_POST
def user_logout(request):
    logout(request)
    return redirect('login')


# =====================================================
# PRESCRIPTIONS
# =====================================================

@login_required
def prescription_list(request):

    prescriptions = Prescription.objects.select_related(
        'patient',
        'doctor'
    ).all().order_by(
        '-prescription_date'
    )

    return render(
        request,
        'hospital/prescription_list.html',
        {
            'prescriptions': prescriptions
        }
    )



@login_required
def add_prescription(request):

    if request.method == 'POST':

        form = PrescriptionForm(
            request.POST
        )

        if form.is_valid():

            prescription = form.save()

            Notification.objects.create(
                title='New Prescription Created',
                message=(
                    f'A new prescription has been created '
                    f'for patient {prescription.patient}.'
                ),
                notification_type='Prescription'
            )

            return redirect(
                'prescription_list'
            )

    else:

        form = PrescriptionForm()

    return render(
        request,
        'hospital/add_prescription.html',
        {
            'form': form
        }
    )


@login_required
def prescription_detail(
    request,
    prescription_id
):

    prescription = get_object_or_404(
    Prescription,
    id=prescription_id
)

    return render(
        request,
        'hospital/prescription_detail.html',
        {
            'prescription': prescription
        }
    )


@login_required
def edit_prescription(
    request,
    prescription_id
):

    prescription = Prescription.objects.get(
        id=prescription_id
    )

    if request.method == 'POST':

        form = PrescriptionForm(
            request.POST,
            instance=prescription
        )

        if form.is_valid():

            form.save()

            return redirect(
                'prescription_detail',
                prescription_id=prescription.id
            )

    else:

        form = PrescriptionForm(
            instance=prescription
        )

    return render(
        request,
        'hospital/edit_prescription.html',
        {
            'form': form,
            'prescription': prescription
        }
    )


@login_required
def delete_prescription(
    request,
    prescription_id
):

    prescription = Prescription.objects.get(
        id=prescription_id
    )

    if request.method == 'POST':

        prescription.delete()

        return redirect(
            'prescription_list'
        )

    return render(
        request,
        'hospital/delete_prescription.html',
        {
            'prescription': prescription
        }
    )


# =====================================================
# BILLING
# =====================================================

@login_required
def bill_list(request):

    search = request.GET.get(
        'search',
        ''
    )

    bills = Bill.objects.select_related(
        'patient'
    ).all().order_by(
        '-bill_date'
    )

    if search:

        bills = bills.filter(
            patient__first_name__icontains=search
        ) | bills.filter(
            patient__last_name__icontains=search
        ) | bills.filter(
            invoice_number__icontains=search
        )

    return render(
        request,
        'hospital/bill_list.html',
        {
            'bills': bills,
            'search': search
        }
    )



@login_required
def add_bill(request):

    if request.method == 'POST':

        form = BillForm(
            request.POST
        )

        if form.is_valid():

            bill = form.save()

            Notification.objects.create(
                title='New Bill Created',
                message=(
                    f'A new bill has been created '
                    f'for patient {bill.patient}.'
                ),
                notification_type='Billing'
            )

            return redirect(
                'bill_list'
            )

    else:

        form = BillForm()

    return render(
        request,
        'hospital/add_bill.html',
        {
            'form': form
        }
    )


@login_required
def bill_detail(request, bill_id):

    bill = Bill.objects.select_related(
        'patient'
    ).get(
        id=bill_id
    )

    return render(
        request,
        'hospital/bill_detail.html',
        {
            'bill': bill
        }
    )


@login_required
def edit_bill(request, bill_id):

    bill = get_object_or_404(
    Bill,
    id=bill_id
)

    if request.method == 'POST':

        form = BillForm(
            request.POST,
            instance=bill
        )

        if form.is_valid():

            form.save()

            return redirect(
                'bill_detail',
                bill_id=bill.id
            )

    else:

        form = BillForm(
            instance=bill
        )

    return render(
        request,
        'hospital/edit_bill.html',
        {
            'form': form,
            'bill': bill
        }
    )


@login_required
def delete_bill(request, bill_id):

    bill = Bill.objects.get(
        id=bill_id
    )

    if request.method == 'POST':

        bill.delete()

        return redirect(
            'bill_list'
        )

    return render(
        request,
        'hospital/delete_bill.html',
        {
            'bill': bill
        }
    )


# =====================================================
# REPORTS
# =====================================================

@login_required
def reports(request):

    # ==============================
    # DATE FILTER
    # ==============================

    start_date = request.GET.get(
        'start_date'
    )

    end_date = request.GET.get(
        'end_date'
    )

    # ==============================
    # BASE DATA
    # ==============================

    patients = Patient.objects.all()

    doctors = Doctor.objects.all()

    departments = Department.objects.all()

    appointments = Appointment.objects.select_related(
        'patient',
        'doctor'
    ).all()

    medical_records = MedicalRecord.objects.select_related(
        'patient',
        'doctor'
    ).all()

    prescriptions = Prescription.objects.select_related(
        'patient',
        'doctor'
    ).all()

    bills = Bill.objects.select_related(
        'patient'
    ).all()

    # ==============================
    # DATE FILTERING
    # ==============================

    if start_date:

        appointments = appointments.filter(
            appointment_date__gte=start_date
        )

        medical_records = medical_records.filter(
            record_date__gte=start_date
        )

        prescriptions = prescriptions.filter(
            prescription_date__gte=start_date
        )

        bills = bills.filter(
            bill_date__gte=start_date
        )

    if end_date:

        appointments = appointments.filter(
            appointment_date__lte=end_date
        )

        medical_records = medical_records.filter(
            record_date__lte=end_date
        )

        prescriptions = prescriptions.filter(
            prescription_date__lte=end_date
        )

        bills = bills.filter(
            bill_date__lte=end_date
        )

    # ==============================
    # BILLING STATISTICS
    # ==============================

    total_bills = bills.count()

    paid_bills = bills.filter(
        payment_status='Paid'
    ).count()

    pending_bills = bills.filter(
        payment_status='Pending'
    ).count()

    cancelled_bills = bills.filter(
        payment_status='Cancelled'
    ).count()

    total_revenue = sum(
        bill.amount
        for bill in bills.filter(
            payment_status='Paid'
        )
    )

    pending_amount = sum(
        bill.amount
        for bill in bills.filter(
            payment_status='Pending'
        )
    )

    # ==============================
    # COUNTS
    # ==============================

    total_patients = patients.count()

    total_doctors = doctors.count()

    total_departments = departments.count()

    total_appointments = appointments.count()

    total_medical_records = medical_records.count()

    total_prescriptions = prescriptions.count()

    # ==============================
    # RECENT REPORT DATA
    # ==============================

    recent_appointments = appointments.order_by(
        '-appointment_date',
        '-appointment_time'
    )[:10]

    recent_medical_records = medical_records.order_by(
        '-record_date'
    )[:10]

    recent_prescriptions = prescriptions.order_by(
        '-prescription_date'
    )[:10]

    recent_bills = bills.order_by(
        '-bill_date'
    )[:10]

    # ==============================
    # CONTEXT
    # ==============================

    context = {

        'total_patients':
        total_patients,

        'total_doctors':
        total_doctors,

        'total_departments':
        total_departments,

        'total_appointments':
        total_appointments,

        'total_medical_records':
        total_medical_records,

        'total_prescriptions':
        total_prescriptions,

        'total_bills':
        total_bills,

        'paid_bills':
        paid_bills,

        'pending_bills':
        pending_bills,

        'cancelled_bills':
        cancelled_bills,

        'total_revenue':
        total_revenue,

        'pending_amount':
        pending_amount,

        'recent_appointments':
        recent_appointments,

        'recent_medical_records':
        recent_medical_records,

        'recent_prescriptions':
        recent_prescriptions,

        'recent_bills':
        recent_bills,

        'start_date':
        start_date,

        'end_date':
        end_date,
    }

    return render(
        request,
        'hospital/reports.html',
        context
    )


# =====================================================
# SETTINGS
# =====================================================

@login_required
def settings_view(request):

    # ==============================
    # HOSPITAL SETTINGS
    # ==============================

    hospital_settings, created = (
        HospitalSettings.objects.get_or_create(
            id=1
        )
    )

    # ==============================
    # DEFAULT FORMS
    # ==============================

    hospital_form = HospitalSettingsForm(
        instance=hospital_settings
    )

    profile_form = ProfileForm(
        instance=request.user
    )

    password_form = ChangePasswordForm(
        request.user
    )

    # ==============================
    # POST REQUEST
    # ==============================

    if request.method == 'POST':

        form_type = request.POST.get(
            'form_type'
        )

        # ==============================
        # HOSPITAL INFORMATION
        # ==============================

        if form_type == 'hospital':

            hospital_form = HospitalSettingsForm(
                request.POST,
                instance=hospital_settings
            )

            if hospital_form.is_valid():

                hospital_form.save()

                return redirect(
                    'settings'
                )

        # ==============================
        # USER PROFILE
        # ==============================

        elif form_type == 'profile':

            profile_form = ProfileForm(
                request.POST,
                instance=request.user
            )

            if profile_form.is_valid():

                profile_form.save()

                return redirect(
                    'settings'
                )

        # ==============================
        # CHANGE PASSWORD
        # ==============================

        elif form_type == 'password':

            password_form = ChangePasswordForm(
                request.user,
                request.POST
            )

            if password_form.is_valid():

                new_password = (
                    password_form.cleaned_data[
                        'new_password'
                    ]
                )

                request.user.set_password(
                    new_password
                )

                request.user.save()

                return redirect(
                    'login'
                )

    # ==============================
    # RENDER SETTINGS
    # ==============================

    return render(
        request,
        'hospital/settings.html',
        {
            'hospital_form':
            hospital_form,

            'profile_form':
            profile_form,

            'password_form':
            password_form,

            'hospital_settings':
            hospital_settings,
        }
    )
