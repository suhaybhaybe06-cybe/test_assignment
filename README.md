g# test_assignment
this the test_assignment


from django.urls import path
from . import views


urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path(
        'login/',
        views.user_login,
        name='login'
    ),
    
    path(
    'settings/',
    views.settings_view,
    name='settings'
),
    
    path(
    'reports/',
    views.reports,
    name='reports'
),
    
    path(
    'logout/',
    views.user_logout,
    name='logout'
),

    path(
        'patients/',
        views.patient_list,
        name='patient_list'
    ),

    path(
        'patients/add/',
        views.add_patient,
        name='add_patient'
    ),

    path(
        'patients/<int:patient_id>/',
        views.patient_detail,
        name='patient_detail'
    ),

    path(
        'patients/<int:patient_id>/edit/',
        views.edit_patient,
        name='edit_patient'
    ),

    path(
        'patients/<int:patient_id>/delete/',
        views.delete_patient,
        name='delete_patient'
    ),

    path(
        'doctors/',
        views.doctor_list,
        name='doctor_list'
    ),

    path(
        'doctors/add/',
        views.add_doctor,
        name='add_doctor'
    ),

    path(
        'doctors/<int:doctor_id>/',
        views.doctor_detail,
        name='doctor_detail'
    ),

    path(
        'doctors/<int:doctor_id>/edit/',
        views.edit_doctor,
        name='edit_doctor'
    ),

    path(
        'doctors/<int:doctor_id>/delete/',
        views.delete_doctor,
        name='delete_doctor'
    ),

    path(
        'departments/',
        views.department_list,
        name='department_list'
    ),

    path(
        'departments/add/',
        views.add_department,
        name='add_department'
    ),

    path(
        'departments/<int:department_id>/',
        views.department_detail,
        name='department_detail'
    ),

    path(
        'departments/<int:department_id>/edit/',
        views.edit_department,
        name='edit_department'
    ),

    path(
        'departments/<int:department_id>/delete/',
        views.delete_department,
        name='delete_department'
    ),

    path(
        'appointments/',
        views.appointment_list,
        name='appointment_list'
    ),

    path(
        'appointments/add/',
        views.add_appointment,
        name='add_appointment'
    ),

    path(
        'appointments/<int:appointment_id>/',
        views.appointment_detail,
        name='appointment_detail'
    ),

    path(
        'appointments/<int:appointment_id>/edit/',
        views.edit_appointment,
        name='edit_appointment'
    ),

    path(
        'appointments/<int:appointment_id>/delete/',
        views.delete_appointment,
        name='delete_appointment'
    ),

    path(
        'medical-records/',
        views.medical_record_list,
        name='medical_record_list'
    ),

    path(
        'medical-records/add/',
        views.add_medical_record,
        name='add_medical_record'
    ),

    path(
        'medical-records/<int:record_id>/',
        views.medical_record_detail,
        name='medical_record_detail'
    ),

    path(
        'medical-records/<int:record_id>/edit/',
        views.edit_medical_record,
        name='edit_medical_record'
    ),

    path(
        'medical-records/<int:record_id>/delete/',
        views.delete_medical_record,
        name='delete_medical_record'
    ),
    
    
        path(
        'prescriptions/',
        views.prescription_list,
        name='prescription_list'
    ),

    path(
        'prescriptions/add/',
        views.add_prescription,
        name='add_prescription'
    ),

    path(
        'prescriptions/<int:prescription_id>/',
        views.prescription_detail,
        name='prescription_detail'
    ),

    path(
        'prescriptions/<int:prescription_id>/edit/',
        views.edit_prescription,
        name='edit_prescription'
    ),

    path(
        'prescriptions/<int:prescription_id>/delete/',
        views.delete_prescription,
        name='delete_prescription'
    ),
    
    
    path(
    'bills/',
    views.bill_list,
    name='bill_list'
),

path(
    'bills/add/',
    views.add_bill,
    name='add_bill'
),

path(
    'bills/<int:bill_id>/',
    views.bill_detail,
    name='bill_detail'
),

path(
    'bills/<int:bill_id>/edit/',
    views.edit_bill,
    name='edit_bill'
),

path(
    'bills/<int:bill_id>/delete/',
    views.delete_bill,
    name='delete_bill'
),
    
]



kan ku xigaana waa models.py






from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Doctor(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name}"


class Patient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    age = models.IntegerField()
    phone = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Appointment(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE
    )
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField()

    def __str__(self):
        return f"{self.patient} - Dr. {self.doctor.last_name}"
    
    
    
class MedicalRecord(models.Model):

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE
    )

    diagnosis = models.CharField(
        max_length=255
    )

    symptoms = models.TextField(
        blank=True
    )

    treatment = models.TextField(
        blank=True
    )

    notes = models.TextField(
        blank=True
    )

    record_date = models.DateField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.patient} - {self.diagnosis}"
    
    
    
class Prescription(models.Model):

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE
    )

    medicine = models.CharField(
        max_length=255
    )

    dosage = models.CharField(
        max_length=100
    )

    frequency = models.CharField(
        max_length=100
    )

    duration = models.CharField(
        max_length=100
    )

    instructions = models.TextField(
        blank=True
    )

    prescription_date = models.DateField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.patient} - {self.medicine}"
    
    
class Bill(models.Model):

    PAYMENT_STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
        ('Cancelled', 'Cancelled'),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE
    )

    invoice_number = models.CharField(
        max_length=50,
        unique=True
    )

    service = models.CharField(
        max_length=255
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='Pending'
    )

    bill_date = models.DateField(
        auto_now_add=True
    )

    notes = models.TextField(
        blank=True
    )

    def __str__(self):
        return f"{self.invoice_number} - {self.patient}"
    
    
    
class HospitalSettings(models.Model):

    hospital_name = models.CharField(
        max_length=200,
        default='Hospital Management System'
    )

    phone = models.CharField(
        max_length=30,
        blank=True
    )

    email = models.EmailField(
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    website = models.CharField(
        max_length=200,
        blank=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.hospital_name
