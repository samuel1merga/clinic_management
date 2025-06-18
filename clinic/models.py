from django.db import models
from django.contrib.auth.models import User

from django.contrib.auth.hashers import make_password, check_password


# Create your models here.

    
class Patient(models.Model):
    patient_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    password=models.CharField(max_length=20)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    contact_number = models.CharField(max_length=15)
    address = models.TextField()
    medical_history = models.TextField(blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    doctor_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    personal_info = models.FileField(upload_to='personal/', blank=True, null=True)

    specialization = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    approved = models.BooleanField(default=False)

class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, related_name='medical_record', on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, related_name='doctor_records', on_delete=models.CASCADE)
    diagnosis = models.TextField()
    treatment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Record for {self.patient.name} by Dr. {self.doctor.name} on {self.date.strftime('%Y-%m-%d')}"


class Appointment(models.Model):

    patient = models.ForeignKey(Patient, related_name='appointments', on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, related_name='appointments', on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(
        max_length=20,
        choices=[('scheduled', 'Scheduled'), ('accepted','accepted'), ('completed', 'Completed'),('rejected', 'Rejected'), ('cancelled', 'Cancelled')],
        default='scheduled'
    )

    def __str__(self):
        return f"Appointment on {self.date} at {self.time} with Dr. {self.doctor.name}"



class AdminUser(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)  # Hashed password

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.username
    
class Receptionist(models.Model): 
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    reception_id = models.CharField(max_length=20, unique=True)   
    username = models.CharField(max_length=100)   
    phone = models.CharField(max_length=15)   
    password = models.CharField(max_length=100)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.username
    
   

   
class Laboratorist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    lab_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=100)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.name

class LabTest(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.price} ETB)"


class LabTestRequest(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='lab_requests')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_requests')
    test = models.ForeignKey(LabTest, on_delete=models.CASCADE, related_name='requests')
    description = models.TextField(blank=True)
    request_date = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.test_name} for {self.patient.name} by Dr. {self.doctor.name}"


class LabTestResult(models.Model):
    request = models.OneToOneField(LabTestRequest, on_delete=models.CASCADE, related_name='result')
    laboratorist = models.ForeignKey(Laboratorist, on_delete=models.CASCADE, related_name='test_results')
    result_text = models.TextField()
    result_file = models.FileField(upload_to='lab_results/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.test.name} for {self.patient.name} by Dr. {self.doctor.name}"
    



        

class Invoice(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  
    date_issued = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Invoice #{self.id} for {self.patient.name}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.description} - {self.amount}"


