from flask import session, request

from models import User


def check_login():
    """
    This function will check session and
    cookies for active login
    :return: User or None
    """
    if 'username' in session and 'email' in session:
        active_user = User.query.filter(
            User.email == session['email']).first()
        if active_user is not None:
            return active_user
    else:
        uid = request.cookies.get('id')
        password = request.cookies.get('password')
        active_user = User.query.filter(User.id == int(uid)
                                        ).filter(User.password_hash == password
                                          ).first()
        if active_user is not None:
            return active_user
    return None