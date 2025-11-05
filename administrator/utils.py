from django.utils import timezone
import pytz
from analysis.models import AppointmentHeader, Meeting_Tracker

def get_ist_dt(dt):
    if dt is None:
        return None
    if timezone.is_naive(dt):
        dt = pytz.UTC.localize(dt)
    ist = pytz.timezone("Asia/Kolkata")
    return dt.astimezone(ist)





def get_payment_details_for_appointment(appt):
    """
    Heuristic based on your existing pattern in Customer serializer:
    uses appt.temporary_transaction_data.first() and looks for stripe/razorpay transactions.
    Adjust field names if they differ.
    """
    payment_info = {
        "payment_required": appt.payment_required,
        "payment_done": appt.payment_done,
        "gateway": None,
        "payment_id": None,
        "amount": None,
        "currency": None,
    }
    # Some of your code referenced appt.temporary_transaction_data.first()
    ttd = getattr(appt, "temporary_transaction_data", None)
    if ttd is not None:
        try:
            t = ttd.first()
        except Exception:
            t = None
        if t:
            payment_info["amount"] = getattr(t, "total_amount", None)
            payment_info["currency"] = getattr(t, "currency", None)
            payment_info["gateway"] = getattr(t, "gateway", None)
            # stripe then razorpay (your existing priority)
            if hasattr(t, "stripe_transactions") and t.stripe_transactions.exists():
                st = t.stripe_transactions.first()
                payment_info["payment_id"] = getattr(st, "stripe_payment_intent_id", None)
            elif hasattr(t, "razorpay_transactions") and t.razorpay_transactions.exists():
                rt = t.razorpay_transactions.first()
                payment_info["payment_id"] = getattr(rt, "razorpay_payment_id", None)
    return payment_info





def get_confirmation_date_from_reminders(appt):
    """
    There is no explicit 'confirmed_on' in AppointmentHeader provided.
    We'll look up Reminder_Sent_History for this appointment and try to infer confirmation date:
      - first reminder with 'confirm' / 'confirmed' / 'confirmation' in subject/body (case-insensitive)
      - otherwise, if appointment_status == 'confirmed', fallback to booked_on or None
    """
    reminders = appt.reminder_sent_history.all().order_by("sent_at")
    for r in reminders:
        s = (r.subject or "") + " " + (r.body or "")
        ss = s.lower()
        if any(k in ss for k in ["confirm", "confirmed", "confirmation"]):
            return r.sent_at
    # fallback:
    if appt.appointment_status == "confirmed":
        return getattr(appt, "booked_on", None)
    return None


# def get_reminder_statuses_for_appointment(appt):
#     """
#     Provide a summary object about reminders: counts and last sent times for email/whatsapp.
#     You can expand this later (e.g., by event type).
#     """
#     out = {
#         "total_sent": 0,
#         "last_whatsapp_sent_at": None,
#         "last_email_sent_at": None,
#         "last_sent_at": None,
#     }
#     reminders = appt.reminder_sent_history.all().order_by("-sent_at")
#     if not reminders:
#         return out
#     out["total_sent"] = reminders.count()
#     # find last whatsapp / email by scanning recent reminders
#     for r in reminders:
#         if out["last_sent_at"] is None:
#             out["last_sent_at"] = r.sent_at
#         if r.whatsapp_number and out["last_whatsapp_sent_at"] is None:
#             out["last_whatsapp_sent_at"] = r.sent_at
#         if r.email and out["last_email_sent_at"] is None:
#             out["last_email_sent_at"] = r.sent_at
#         if out["last_whatsapp_sent_at"] and out["last_email_sent_at"]:
#             break
#     return out


def get_reminder_statuses_for_appointment(appt):
    """
    Returns detailed reminder info grouped into WhatsApp and Email lists.
    Each entry includes time, type, subject, and recipient details.
    """
    reminders = appt.reminder_sent_history.all().order_by("-sent_at")

    whatsapp_reminders = []
    email_reminders = []

    for r in reminders:
        reminder_info = {
            "sent_at": r.sent_at,
            "subject": r.subject,
        }

        if r.whatsapp_number:
            whatsapp_reminders.append({
                **reminder_info,
                "type": "whatsapp",
                "whatsapp_number": r.whatsapp_number,
            })

        if r.email:
            email_reminders.append({
                **reminder_info,
                "type": "email",
                "email": r.email,
            })

    return {
        "total_sent": reminders.count(),
        "whatsapp_reminders": whatsapp_reminders,
        "email_reminders": email_reminders,
    }

from inticure_prime_backend.settings import BACKEND_URL
def get_meeting_links_for_appointment(appt, customer_obj=None):
    """
    Based on your Customer serializer usage:
      tracker = Meeting_Tracker.objects.get(appointment = appt)
      tracker.customer_1_meeting_id / customer_2_meeting_id
    We'll try a safe lookup and return doctor / patient meeting links.
    """
    try:
        tracker = Meeting_Tracker.objects.filter(appointment=appt).first()
    except Meeting_Tracker.DoesNotExist:
        tracker = None

    doctor_link = getattr(appt, "meeting_link", None)  # fallback - sometimes used
    patient_link = None
    

    if tracker:
        # your Meeting_Tracker fields used earlier: customer_1_meeting_id / customer_2_meeting_id
        if customer_obj:
            if tracker.customer_1 == customer_obj:
                patient_link = tracker.customer_1_meeting_id
            elif tracker.customer_2 == customer_obj:
                patient_link = tracker.customer_2_meeting_id
        # doctor meeting id fields might be present
        doctor_link = getattr(tracker, "doctor_meeting_id", doctor_link) or doctor_link

    return {
        "doctor_meeting_link": BACKEND_URL+"meet/join/"+str(doctor_link),
        "patient_meeting_link": BACKEND_URL+"meet/join/"+str(patient_link)
        }

