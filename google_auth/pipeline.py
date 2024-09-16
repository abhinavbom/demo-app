
def save_profile(backend, user, response, *args, **kwargs):
    """
    Save user profile details to the User model
    """
    if backend.name == 'google-oauth2':
        user.email = response.get('email')
        user.first_name = response.get('given_name')
        user.last_name = response.get('family_name')
        user.save()
