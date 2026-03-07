from django.contrib.auth import get_User_model
User=get_user_model()

def get_user_by_email(email):
    return User.objects.filter(email=email).first()