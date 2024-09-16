



def get_user_data(user):
    """accept the user object and return the user's data into json"""
    
    
    data = {
            "google_id" : user.google_id,
            "email" : user.email,
            "name" : user.name,
            "profile_url" : user.picture_url
        }
    
    return data