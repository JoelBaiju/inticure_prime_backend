# Generated by Django 5.2.1 on 2025-05-27 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AnalysisInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment_id', models.BigIntegerField()),
                ('doctor_id', models.BigIntegerField(null=True)),
                ('uploaded_time', models.TimeField(auto_now=True)),
                ('uploaded_date', models.DateField(auto_now=True)),
                ('analysis_info_text', models.TextField(null=True)),
                ('analysis_info_path', models.TextField(null=True)),
                ('file_name', models.TextField(null=True)),
                ('file_size', models.CharField(max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AppointmentCancellationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment_id', models.BigIntegerField()),
                ('cancelled_date', models.DateField(auto_now=True)),
                ('cancelled_time', models.TimeField(auto_now=True)),
                ('cancelled_by', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='AppointmentDiscussion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment_id', models.BigIntegerField(null=True)),
                ('content', models.TextField(null=True)),
                ('is_query', models.IntegerField(default=0)),
                ('is_reply', models.IntegerField(default=0)),
                ('created_date', models.DateField(auto_now=True)),
                ('created_time', models.TimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='AppointmentReshedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment_id', models.BigIntegerField()),
                ('user_id', models.BigIntegerField()),
                ('reschedule_count', models.IntegerField(default=0)),
                ('time_slot', models.CharField(max_length=30, null=True)),
                ('rescheduled_time', models.TimeField(null=True)),
                ('rescheduled_date', models.DateField(null=True)),
                ('doctor_id', models.BigIntegerField(null=True)),
                ('sr_rescheduled_time', models.CharField(max_length=30, null=True)),
                ('sr_rescheduled_date', models.DateField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AppointmentTransferHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment_id', models.BigIntegerField(null=True)),
                ('new_doctor', models.IntegerField(null=True)),
                ('old_doctor', models.IntegerField(null=True)),
                ('transfered_time', models.TimeField(auto_now=True)),
                ('transfered_date', models.DateField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='CommonFileUploader',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uploaded_time', models.TimeField(auto_now=True, null=True)),
                ('uploaded_date', models.DateField(auto_now=True, null=True)),
                ('common_file', models.FileField(upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='ConsumptionTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medication_id', models.BigIntegerField()),
                ('prescription_id', models.BigIntegerField(null=True)),
                ('consumption_time', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='DoctorAddedTimeSlots',
            fields=[
                ('doctor_time_slots_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('doctor_id', models.IntegerField()),
                ('slot', models.IntegerField()),
                ('date', models.DateField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DoctorAvailableDates',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doctor_id', models.BigIntegerField(null=True)),
                ('date', models.DateField(null=True)),
                ('day', models.CharField(max_length=30, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DoctorAvailableTimeslots',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doctor_id', models.BigIntegerField(null=True)),
                ('day', models.CharField(max_length=30, null=True)),
                ('time_slot_from', models.IntegerField(null=True)),
                ('time_slot_to', models.IntegerField(null=True)),
                ('slot_counter', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DoctorCalenderUpdate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doctor_id', models.BigIntegerField(null=True)),
                ('date', models.DateField(null=True)),
                ('day', models.CharField(max_length=30, null=True)),
                ('time_slot_from', models.IntegerField(null=True)),
                ('time_slot_to', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DoctorLanguages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doctor_id', models.BigIntegerField(null=True)),
                ('languages', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DoctorMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment_id', models.BigIntegerField(null=True)),
                ('mapped_doctor', models.IntegerField(null=True)),
                ('doctor_flag', models.CharField(max_length=10, null=True)),
                ('added_doctor', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='DoctorProfiles',
            fields=[
                ('doctor_profile_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('user_id', models.BigIntegerField()),
                ('location', models.CharField(max_length=30)),
                ('department', models.CharField(max_length=20)),
                ('specialization', models.CharField(max_length=20)),
                ('doctor_flag', models.CharField(max_length=10)),
                ('mobile_number', models.CharField(max_length=12)),
                ('gender', models.CharField(max_length=10, null=True)),
                ('working_date_frm', models.DateField(null=True)),
                ('working_date_to', models.DateField(null=True)),
                ('time_slot_from', models.IntegerField(null=True)),
                ('time_slot_to', models.IntegerField(null=True)),
                ('qualification', models.TextField(null=True)),
                ('address', models.TextField(null=True)),
                ('is_accepted', models.IntegerField(null=True)),
                ('registration_certificate', models.TextField(null=True)),
                ('address_proof', models.TextField(null=True)),
                ('sign_file_name', models.TextField(null=True)),
                ('sign_file_size', models.CharField(max_length=20, null=True)),
                ('reg_file_name', models.TextField(null=True)),
                ('reg_file_size', models.CharField(max_length=20, null=True)),
                ('addr_file_name', models.TextField(null=True)),
                ('addr_file_size', models.CharField(max_length=20, null=True)),
                ('signature', models.TextField(null=True)),
                ('certificate_no', models.TextField(null=True)),
                ('profile_pic', models.TextField(null=True)),
                ('profile_file_name', models.TextField(null=True)),
                ('profile_file_size', models.TextField(null=True)),
                ('doctor_bio', models.CharField(max_length=10000, null=True)),
                ('registration_year', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DoctorSpecializations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('specialization', models.CharField(max_length=100)),
                ('time_duration', models.IntegerField(null=True)),
                ('description', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='FollowUpReminder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment_id', models.BigIntegerField(null=True)),
                ('follow_up_for', models.CharField(max_length=100, null=True)),
                ('remarks', models.TextField(null=True)),
                ('duration', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='JrDoctorEngagement',
            fields=[
                ('doc_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('appointment_id', models.BigIntegerField(null=True)),
                ('user_id', models.BigIntegerField()),
                ('date', models.DateField()),
                ('time_slot', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='JuniorDoctorSlots',
            fields=[
                ('junior_doctor_slot_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('doctor_id', models.IntegerField()),
                ('date', models.DateField()),
                ('time_slot', models.CharField(max_length=200)),
                ('is_active', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Medications',
            fields=[
                ('medication_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('prescription_id', models.BigIntegerField()),
                ('medication', models.TextField()),
                ('duration_number', models.TextField()),
                ('duration', models.TextField()),
                ('side_effects', models.TextField()),
                ('consumption_detail', models.TextField()),
                ('can_substitute', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Obeservations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment_id', models.BigIntegerField()),
                ('user_id', models.BigIntegerField(default=None, null=True)),
                ('doctor_id', models.BigIntegerField(null=True)),
                ('uploaded_time', models.TimeField(auto_now=True)),
                ('uploaded_date', models.DateField(auto_now=True)),
                ('observe', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='PatientMedicalHistory',
            fields=[
                ('patient_medical_history_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('doctor_id', models.IntegerField()),
                ('doctor_flag', models.IntegerField()),
                ('appointment_id', models.IntegerField()),
                ('user_id', models.IntegerField()),
                ('height', models.CharField(max_length=20)),
                ('height_unit', models.CharField(default='cm', max_length=20)),
                ('weight', models.CharField(max_length=20)),
                ('weight_unit', models.CharField(default='kg', max_length=20)),
                ('is_allergic', models.CharField(max_length=200)),
                ('medical_history', models.CharField(max_length=200)),
                ('prescription_history', models.CharField(max_length=200)),
                ('other_suppliments_history', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Prescriptions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment_id', models.BigIntegerField()),
                ('user_id', models.BigIntegerField(default=None, null=True)),
                ('uploaded_time', models.TimeField(auto_now=True, null=True)),
                ('uploaded_date', models.DateField(auto_now=True, null=True)),
                ('prescription', models.TextField(null=True)),
                ('prescript_file_name', models.TextField(null=True)),
                ('prescript_file_size', models.CharField(max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PrescriptionsDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment_id', models.BigIntegerField()),
                ('user_id', models.BigIntegerField(default=None, null=True)),
                ('doctor_id', models.IntegerField(null=True)),
                ('uploaded_time', models.TimeField(auto_now=True)),
                ('uploaded_date', models.DateField(auto_now=True)),
                ('prescriptions_text', models.TextField(null=True)),
                ('tests_to_be_done', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RescheduleHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment_id', models.BigIntegerField()),
                ('user_id', models.BigIntegerField()),
                ('time_slot', models.CharField(max_length=30, null=True)),
                ('rescheduled_time', models.TimeField(null=True)),
                ('doctor_id', models.CharField(max_length=100, null=True)),
                ('rescheduled_date', models.DateField(null=True)),
                ('sr_rescheduled_time', models.CharField(max_length=30, null=True)),
                ('sr_rescheduled_date', models.DateField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SeniorDoctorAvailableTimeSLots',
            fields=[
                ('senior_doctor_timeslot_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('doctor_id', models.IntegerField()),
                ('date', models.DateField()),
                ('time_slot', models.CharField(max_length=200)),
                ('is_active', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='SrDoctorEngagement',
            fields=[
                ('doc_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('appointment_id', models.BigIntegerField(null=True)),
                ('user_id', models.BigIntegerField()),
                ('date', models.DateField()),
                ('time_slot', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Time',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.CharField(max_length=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Timeslots',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_slots', models.CharField(max_length=30)),
            ],
        ),
    ]
