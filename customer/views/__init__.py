# customer/views/__init__.py
from .dashboard_view import CustomerDashboardView
from .appointment_view import (
    DoctorAvailabilityView, AppointmentRescheduleView, 
    CancelAppointmentView, add_appointment_slot, relieve_package
)
from .profile_view import (
    ContactDetailsView, PartnerExistenceView, 
    create_partner,CustomerProfileUpdateView
)
from .prescription_view import (
    PrescriptionsView, PrescriptionPDFView,
    get_specializations, get_specialization_by_id, get_doctor_packages
)

__all__ = [
    'CustomerDashboardView',
    'DoctorAvailabilityView', 
    'AppointmentRescheduleView',
    'CancelAppointmentView',
    'add_appointment_slot',
    'relieve_package',
    'ContactDetailsView',
    'PartnerExistenceView', 
    'create_partner',
    'update_contact_info',
    'PrescriptionsView',
    'PrescriptionPDFView',
    'get_specializations',
    'get_specialization_by_id',
    'get_doctor_packages'
]

