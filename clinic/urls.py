from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admiin/login/', views.login_admin, name='login_admiin'),
    path('admiin/invoice-summary/', views.admin_invoice_summary, name='admin_invoice_summary'),
    path('admiin/approve/', views.approve_users, name='approve_users'),
    path('register/receptionist/', views.register_receptionist, name='register_receptionist'),
    path('admiin/lab_tests/', views.lab_test_list, name='lab_test_list'),
    path('admiin/lab_tests/add/', views.lab_test_create, name='lab_test_create'),
    path('admiin/lab_tests/<int:test_id>/edit/', views.lab_test_edit, name='lab_test_edit'),
    path('admiin/dashboard/', views.admin_dashboard, name='admiin_dashboard'),
    path('laboratorist/register/', views.laboratorist_register, name='laboratorist_register'),
    path('admiin/users/', views.all_users, name='all_users'),

    path('login/patient/', views.login_patient, name='login_patient'),
    path('dashboard/patient/', views.patient_dashboard, name='patient_dashboard'),



    path('register/patient/', views.register_patient, name='register_patient'),
    path('register/doctor/', views.register_doctor, name='register_doctor'),
    path('login/doctor/', views.login_doctor, name='login_doctor'),
    path('appointments/view/', views.view_appointments, name='view_appointments'),
  
    path('dashboard/doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('schedule/doctor/', views.doctor_schedule_view, name='doctor_schedule'),


    path('login/', views.login, name='login'),

    path('patients/', views.patient_list, name='patients'),
    path('doctor/schedule/', views.doctor_schedule_view, name='doctor_schedule'),
    path('doctor/appointment/<int:appointment_id>/<str:action>/', views.update_appointment_status, name='update_appointment_status'),
    path('appointment/completed/', views.completed_appointments, name='completed_appointments'),
    path('appointment/delete/<int:pk>/', views.delete_appointment, name='delete_appointment'),
    path('doctor/upload-medical-record/', views.upload_medical_record, name='upload_medical_record'),





    path('receptionist/dashboard/', views.receptionist_dashboard, name='receptionist_dashboard'),


    path('schedule/appointment/', views.schedule_appointment, name='schedule_appointment'),

    path('patient/medical-records/', views.patient_medical_records, name='patient_medical_records'),



    path('laboratorist/login/', views.login, name='laboratorist_login'),
    path('logout/', views.logout, name='logout'),
    path('lab/request-form/', views.request_lab_test, name='lab_request_form'),
    path('lab/pending-requests/', views.pending_lab_requests, name='pending_lab_requests'),
    path('lab/submit-result/<int:request_id>/', views.submit_lab_result, name='submit_lab_result'),
    path('lab/results/', views.doctor_view_results, name='doctor_view_results'),


    
path('doctor/request-lab-test/', views.request_lab_test, name='request_lab_test'),







]