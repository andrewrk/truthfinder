from google.appengine.api import users

def auth(request):
    return {
        'user': users.get_current_user(),
        'login_url': users.create_login_url(request.path),
        'logout_url': users.create_logout_url(request.path),
    }
