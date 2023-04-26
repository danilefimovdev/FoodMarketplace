

def detect_user(user):
    if user.role == 1 or user.role == 2:
        redirect_url = 'dashboard'
    elif user.role is None and user.is_superadmin is True:  # case for superuser
        redirect_url = '/admin'
    return redirect_url
