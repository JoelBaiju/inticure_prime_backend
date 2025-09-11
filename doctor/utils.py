



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
