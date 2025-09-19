import uuid
import pytz
import secrets
import string
from analysis.models import Meeting_Tracker
from django.conf import settings
from analysis.models import Appointment_customers, AppointmentHeader
from doctor.models import DoctorAppointment
from datetime import datetime, time
from django.db.models import Q
from doctor.models import DoctorAvailableHours, DoctorAppointment, DoctorProfiles
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from datetime import timezone
from django.utils import timezone as dj_timezone
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from dateutil import parser
from zoneinfo import ZoneInfo
from datetime import timezone as dt_timezone
import logging
logger = logging.getLogger(__name__)




def generate_random_otp(length=6):
    otp=''.join(secrets.choice(string.digits) for _ in range(length))
    print(otp)
    return otp


def send_otp_email(firstname,otp,toemail):
    try:

        subject = 'Your OTP for Email Verification'
        html_message = render_to_string('email_otp.html', {
        'name': firstname,
        'otp': otp
        })
        plain_message = strip_tags(html_message)

        email = EmailMultiAlternatives(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,  # Use the default from email
        [toemail]    
        )
        email.attach_alternative(html_message, 'text/html')
        logger.debug(f"Sending OTP email to {toemail}")
        logger.debug(email.send())
    
    except Exception as e:
        logger.debug(f"Failed to send OTP email to {toemail}: {str(e)}")
        logger.debug(f"Email sending failed: {e}")



def send_appointment_confirmation_email(
    name,
    date,
    time,
    doctor_name,
    meet_link,
    to_email,
    doctor_flag=0
):
  
    subject = 'Your Appointment Confirmation with Inticure'
    
    # Render the HTML template with all parameters
    html_message = render_to_string('order_confirmation_customer.html', {
        'doctor_flag': doctor_flag,
        'name': name,
        'date': date,
        'time': time,
        'doctor_name': doctor_name,
        'meet_link': meet_link
    })
    
    # Create plain text version by stripping HTML tags
    plain_message = strip_tags(html_message)
    
    # Create the email object
    email = EmailMultiAlternatives(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [to_email]
    )
    
    # Attach the HTML version
    email.attach_alternative(html_message, 'text/html')
    
    try:
        # Send the email
        result = email.send()
        print(f"Appointment confirmation email sent to {to_email}. Result: {result}")
        return result
    except Exception as e:
        print(f"Failed to send appointment confirmation email to {to_email}. Error: {str(e)}")
        return False
    








def is_doctor_available(doctor_id, from_time, to_time):
    # Combine date and time for proper comparison

    
    # Check if doctor has any availability that overlaps with requested time
    print(from_time , to_time)
    has_availability = DoctorAvailableHours.objects.filter(
        doctor_id=doctor_id,
        start_time__lt=to_time,
        end_time__gt=from_time,
    ).exists()
    
    if not has_availability:
        return False

    # Check for overlapping confirmed appointments
    has_conflicting_appointments = DoctorAppointment.objects.filter(
        doctor_id=doctor_id,
        confirmed=True,
        start_time__lt=to_time,
        end_time__gt=from_time,
    ).exists()
    
    return not has_conflicting_appointments

def Appointment_actions(appointment_id):
    appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
    actions = {'slot': False, 'payment': False , 'partner': False}

    if appointment.is_couple and not appointment.customer.partner:
        actions['partner'] = True
    if appointment.appointment_status == "pending_payment":
        if not DoctorAppointment.objects.filter(appointment=appointment).exists():
            is_available = is_doctor_available(
                appointment.doctor.doctor_profile_id,
                appointment.start_time,
                appointment.end_time
            )
            print('is available',is_available)
            if not is_available:
                actions['slot'] = True
                actions['payment'] = True
        actions['payment'] = True

    elif appointment.appointment_status in ['initiated_by_doctor', 'pending_slot', 'rescheduled_by_doctor', 'rescheduled_by_customer']:
        actions['slot'] = True
        if appointment.appointment_status == 'initiated_by_doctor':
            actions['payment'] = True

    return actions



def generate_three_unique_ids():
    """Generate two different UUIDs."""
    while True:
        doctor_id = uuid.uuid4()
        customer_1_id = uuid.uuid4()
        customer_2_id = uuid.uuid4()
        if doctor_id != customer_1_id and doctor_id != customer_2_id and customer_1_id != customer_2_id:
            return doctor_id, customer_1_id , customer_2_id


def create_meeting_link(meeting_id):
    return f"{settings.BACKEND_URL}/meet/join/{meeting_id}/"



def track_map_meeting(appointment_id, meeting_link, meeting_code):
    """Create a Meeting_Tracker entry with unique IDs and links."""
    appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
    appointment_customer = Appointment_customers.objects.filter(appointment=appointment)
    doctor_id, customer_1_id, customer_2_id = generate_three_unique_ids()

    if Meeting_Tracker.objects.filter(appointment=appointment).exists():
        return

    # Default values
    customer_1= appointment.customer
    customer_2 = None
    customer_2_meeting_link = None

    if appointment.is_couple:
        # customer_2 = ( customer.customer for  customer in appointment_customer  if customer.customer != customer_1)
        customer_2 = next((c.customer for c in appointment_customer if c.customer != customer_1), None)
        customer_2_meeting_link = create_meeting_link(str(customer_2_id))

    meeting_tracker = Meeting_Tracker.objects.create(
        appointment=appointment,
        meeting_link=meeting_link,
        meeting_code=meeting_code,
        doctor_meeting_id=doctor_id,
        customer_1=customer_1,
        customer_2=customer_2,
        customer_1_meeting_id=customer_1_id,
        customer_2_meeting_id=customer_2_id if appointment.is_couple else None,
        doctor_meeting_link=create_meeting_link(str(doctor_id)),
        customer_1_meeting_link=create_meeting_link(str(customer_1_id)),
        customer_2_meeting_link=customer_2_meeting_link,
    )
    return meeting_tracker



from .gmeet.gmeet import fetch_meet_logs


def get_meet_logs(q_meeting_code):

    logs = []
    print('started log fetching')
    for item in fetch_meet_logs():
        actor_email = item.get('actor', {}).get('email')
        event = item.get('events', [])[0]
        event_name = event.get('name')
        parameters = event.get('parameters', [])

        display_name = None
        identifier = actor_email
        start_timestamp = None
        duration_seconds = None
        meeting_code = None
        for param in parameters:
            name = param.get('name')
            if name == 'display_name':
                display_name = param.get('value')
            elif name == 'identifier':
                identifier = param.get('value')
            elif name == 'meeting_code':
                meeting_code = param.get('value')
            elif name == 'start_timestamp_seconds':
                start_timestamp = int(param.get('intValue'))
            elif name == 'duration_seconds':
                duration_seconds = int(param.get('intValue'))
        if q_meeting_code:
            if q_meeting_code != meeting_code:
                continue

        # Calculate joined and left time
        joined_at = None
        left_at = None
        if start_timestamp:
            joined_at = datetime.utcfromtimestamp(start_timestamp).isoformat()
        if start_timestamp and duration_seconds:
            left_at = datetime.utcfromtimestamp(start_timestamp + duration_seconds).isoformat()

        logs.append({
            'display_name': display_name,
            'identifier': identifier,
            'joined_at': joined_at,
            'left_at': left_at,
            'meeting_code':meeting_code
        })

    return  logs





def seconds_until_in_timezone(target_utc_datetime, timezone_str):
    """
    Calculate the seconds remaining until a UTC datetime in a specific timezone.
    
    Args:
        target_utc_datetime (datetime): A datetime object in UTC timezone
        timezone_str (str): A string representing the target timezone (e.g., 'America/New_York')
    
    Returns:
        int: Seconds remaining until the target datetime in the specified timezone
             Returns negative if the datetime has already passed
    """
    try:
        # Convert the target timezone string to a timezone object
        target_tz = pytz.timezone(timezone_str)
        
        # Get current time in UTC
        now_utc = datetime.now(pytz.UTC)
        
        # Convert target UTC datetime to the specified timezone
        target_in_tz = target_utc_datetime.astimezone(target_tz)
        
        # Get current time in the target timezone
        now_in_tz = now_utc.astimezone(target_tz)
        
        # Calculate the difference in seconds
        time_difference = target_in_tz - now_in_tz
        seconds_remaining = time_difference.total_seconds()
        
        return int(seconds_remaining)
    
    except Exception as e:
        raise ValueError(f"Error calculating time difference: {str(e)}")






def get_user_timezone(user):
    """
    Get the timezone string from a user's country details.
    
    Parameters:
    - user: The user object from the request
    
    Returns:
    - A timezone string (e.g., 'America/New_York', 'UTC')
    """
    from customer.models import CustomerProfile
    
    # Get the customer profile associated with the user
    try:
        customer_profile = CustomerProfile.objects.get(user=user)
        
        # Get the country details and timezone
        if customer_profile.country_details and customer_profile.country_details.time_zone:
            return customer_profile.time_zone
        else:
            # Default to UTC if no timezone is specified
            return 'UTC'
            
    except CustomerProfile.DoesNotExist:
        # Default to UTC if customer profile doesn't exist
        return 'UTC'



def convert_utc_to_local(date_time_str, timezone_str):
    # Parse any ISO 8601 datetime string
    utc_dt = parser.isoparse(date_time_str)
    
    # Make sure it’s in UTC
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=dt_timezone.utc)
    else:
        utc_dt = utc_dt.astimezone(dt_timezone.utc)

    # Convert to the given local timezone
    local_dt = utc_dt.astimezone(ZoneInfo(timezone_str))

    return local_dt.isoformat()







def convert_utc_to_doctor_timezone(utc_dt, doctor):
    """
    Convert a UTC datetime to the doctor's local timezone.
    
    Parameters:
    - utc_dt: A timezone-aware datetime object in UTC
    - doctor: The DoctorProfiles instance
    
    Returns:
    - A timezone-aware datetime object in the doctor's local timezone
    """
    from zoneinfo import ZoneInfo
    
    # Get the doctor's timezone
    timezone_str = get_doctor_timezone(doctor)
    
    # Convert UTC to doctor's local timezone
    return utc_dt.astimezone(ZoneInfo(timezone_str))



def get_doctor_timezone(doctor):
    """
    Get the timezone string from a doctor's country details.
    Parameters:
    - doctor: The DoctorProfiles instance
    Returns:
    - A timezone string (e.g., 'America/New_York', 'UTC')
    """
    # Get timezone from doctor's country field
    if hasattr(doctor, 'time_zone') and doctor.time_zone :
        return doctor.time_zone
    return 'UTC'

def convert_doctor_request_datetime_to_utc(date_str, time_str, doctor):
    """
    Convert datetime data from request parameters to UTC based on the doctor's country timezone.
    Parameters:
    - date_str: Date string in format 'YYYY-MM-DD'
    - time_str: Time string in format 'HH:MM' or 'HH:MM:SS'
    - doctor: The DoctorProfiles instance
    Returns:
    - A timezone-aware datetime object in UTC
    """
    from datetime import datetime
    if time_str is None or time_str == "00:00":
        time_str = "00:01"
    if ':' in time_str and len(time_str.split(':')) > 2:
        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    else:
        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    timezone_str = get_doctor_timezone(doctor)
    from zoneinfo import ZoneInfo
    local_tz = ZoneInfo(timezone_str)
    dt = dt.replace(tzinfo=local_tz)
    return dt.astimezone(ZoneInfo("UTC"))

def get_doctor_from_user(user):
    """
    Get the doctor profile from a user object.
    
    Parameters:
    - user: The user object from the request
    
    Returns:
    - DoctorProfiles instance or None if not found
    """
    from doctor.models import DoctorProfiles
    
    try:
        return DoctorProfiles.objects.get(user=user)
    except DoctorProfiles.DoesNotExist:
        return None




def get_current_time_in_utc_from_tz(tz_str):
    """
    Given a timezone string, gets the current time in that timezone
    and returns it converted to UTC.
    """

    target_tz = ZoneInfo(tz_str)
    print(tz_str)
    # Get current time in the target timezone
    now_in_target_tz = dj_timezone.now().astimezone(target_tz)
    print('\n now in target tz' ,now_in_target_tz)
    end_in_target_tz = now_in_target_tz.replace(hour=23, minute=59, second=59, microsecond=999999)
    print('\n end in target tz' ,end_in_target_tz)

    now_in_utc = now_in_target_tz.astimezone(timezone.utc)
    end_in_utc = end_in_target_tz.astimezone(timezone.utc)
    print('\n now converted to utc' , now_in_utc)
    print('\n end converted to utc' , end_in_utc)
    return now_in_utc, end_in_utc



def get_today_start_end_for_doctor_tz(tz_str):
    """
    Given a timezone string, gets the current time in that timezone
    and returns it converted to UTC.
    """

    target_tz = ZoneInfo(tz_str)
    print(tz_str)
    # Get current time in the target timezone
    now_in_target_tz = dj_timezone.now().astimezone(target_tz)
    current_date_in_target_tz = now_in_target_tz.date()
    print('\n now in target tz' ,now_in_target_tz)
    start_of_day_in_target_tz = datetime.combine(current_date_in_target_tz, time(0, 0), tzinfo=target_tz)
    end_of_day_in_target_tz = datetime.combine(current_date_in_target_tz, time(23, 59, 59, 999999), tzinfo=target_tz)
    print('\n start of day in target tz' , start_of_day_in_target_tz)
    start_of_day_in_utc = start_of_day_in_target_tz.astimezone(timezone.utc)
    end_of_day_in_utc = end_of_day_in_target_tz.astimezone(timezone.utc)
    print('\n start of day converted to utc' , start_of_day_in_utc)
    return start_of_day_in_utc, end_of_day_in_utc



from datetime import datetime, timedelta

def round_up_to_nearest_five(dt: datetime) -> datetime:
    """Round UP to the next multiple of 5 minutes."""
    dt = dt.replace(second=0, microsecond=0)
    remainder = dt.minute % 5
    if remainder != 0:
        dt += timedelta(minutes=(5 - remainder))
    return dt

def round_down_to_nearest_five(dt: datetime) -> datetime:
    """Round DOWN to the previous multiple of 5 minutes."""
    dt = dt.replace(second=0, microsecond=0)
    remainder = dt.minute % 5
    if remainder != 0:
        dt -= timedelta(minutes=remainder)
    return dt


from doctor.models import DoctorProfiles
def get_doctor_timezone_from_user(user):
    """
    Get the timezone string from a doctor's country details.
    
    Parameters:
    - doctor: The DoctorProfiles instance
    
    Returns:
    - A timezone string (e.g., 'America/New_York', 'UTC')
    """
    doctor = get_doctor_from_user(user)
    if doctor and hasattr(doctor,"time_zone") and doctor.time_zone:
        return doctor.time_zone
    




from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from dateutil import parser

def convert_local_dt_to_utc(date_time_str, tz_str='UTC'):
    """
    Converts a local datetime string to UTC datetime object.
    Supports both 'YYYY-MM-DD HH:MM:SS' and 'YYYY-MM-DDTHH:MM:SS' formats.
    
    Args:
        date_time_str: Datetime string in local time
        tz_str: Timezone string (e.g., 'America/New_York')
    
    Returns:
        timezone-aware datetime object in UTC
    """
    try:
        # Parse the datetime string automatically
        local_dt = parser.isoparse(date_time_str)
        
        # Attach local timezone
        local_dt = local_dt.replace(tzinfo=ZoneInfo(tz_str))

        # Convert to UTC
        return local_dt.astimezone(timezone.utc)
    except Exception as e:
        raise ValueError(f"Invalid datetime or timezone: {str(e)}")

def get_customer_timezone(user):
    """
    Get the timezone string from a user's country details.
    
    Parameters:
    - user: The user object from the request
    
    Returns:
    - A timezone string (e.g., 'America/New_York', 'UTC')
    """
    from customer.models import CustomerProfile
    
    # Get the customer profile associated with the user
    try:
        customer_profile = CustomerProfile.objects.get(user=user)
        
        # Get the country details and timezone
        if customer_profile and customer_profile.time_zone:
            return customer_profile.time_zone
        else:
            # Default to UTC if no timezone is specified
            return 'UTC'
            
    except CustomerProfile.DoesNotExist:
        # Default to UTC if customer profile doesn't exist
        return 'UTC'
    





from datetime import timezone as dt_timezone

def convert_utc_to_local(date_time_val, timezone_str):
    # If it's a string, parse it
    if isinstance(date_time_val, str):
        utc_dt = parser.isoparse(date_time_val)
    elif isinstance(date_time_val, datetime):
        utc_dt = date_time_val
    else:
        raise TypeError(f"Unsupported type for date_time_val: {type(date_time_val)}")

    # Make sure it’s timezone-aware in UTC
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=dt_timezone.utc)
    else:
        utc_dt = utc_dt.astimezone(dt_timezone.utc)

    # Convert to the given local timezone
    local_dt = utc_dt.astimezone(ZoneInfo(timezone_str))

    return local_dt.isoformat()


def convert_utc_to_local_return_dt(date_time_val, timezone_str):
    # Parse only if it's a string
    if isinstance(date_time_val, str):
        utc_dt = parser.isoparse(date_time_val)
    elif isinstance(date_time_val, datetime):
        utc_dt = date_time_val
    else:
        raise TypeError(f"Unsupported type: {type(date_time_val)}")

    # Make timezone-aware in UTC
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=dt_timezone.utc)
    else:
        utc_dt = utc_dt.astimezone(dt_timezone.utc)

    # Convert to given timezone
    local_dt = utc_dt.astimezone(ZoneInfo(timezone_str))

    return local_dt  # ✅ return datetime, not string



def convert_local_dt_to_utc_return_dt(date_time_str, tz_str='UTC'):
    """
    Converts a local datetime string to a UTC-aware datetime object.
    """
    try:
        # If already datetime, skip parsing
        if not isinstance(date_time_str, str):
            raise TypeError("convert_local_dt_to_utc expects a string, got datetime object")

        # Parse string into datetime
        local_dt = parser.isoparse(date_time_str)

        # Attach local timezone (only if not already aware)
        if local_dt.tzinfo is None:
            local_dt = local_dt.replace(tzinfo=ZoneInfo(tz_str))

        # Convert to UTC datetime object
        return local_dt.astimezone(timezone.utc)

    except Exception as e:
        raise ValueError(f"Invalid datetime or timezone: {str(e)}")



def get_utc_day_bounds(date_str, tz_str):
    """
    Given a UTC date and a timezone string, returns the UTC datetimes for:
    - Start of day (00:00 local time)
    - End of day (23:59 local time)
    
    Args:
        date_str (str): Date string in format 'YYYY-MM-DD' (in UTC)
        tz_str (str): Timezone string (e.g., 'Asia/Kolkata')
    
    Returns:
        tuple: (start_of_day_utc, end_of_day_utc) as datetime objects
    """
    try:
        # Parse the input date
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        # Create local timezone object
        local_tz = ZoneInfo(tz_str)
        
        # Local start and end of day
        local_start = datetime.combine(date_obj, time(0, 0), tzinfo=local_tz)
        local_end = datetime.combine(date_obj, time(23, 59), tzinfo=local_tz)
        
        # Convert to UTC
        start_utc = local_start.astimezone(timezone.utc)
        end_utc = local_end.astimezone(timezone.utc)
        
        return start_utc, end_utc
    except Exception as e:
        raise ValueError(f"Invalid date or timezone: {str(e)}")






def convert_datetime_to_words_in_local_tz(dt , tz_str='UTC'):
    """
    Converts a utc datetime object to local tz and then to words
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(tz_str))
    else:
        dt = dt.astimezone(ZoneInfo(tz_str))
    return dt.strftime("%A, %B %d, %Y at %I:%M %p")