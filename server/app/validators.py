import re


def not_empty(data):
    """Checks if not empty"""
    if data != '':
        return True
    else:
        return False


def is_email(data):
    """Checks if email format"""
    return re.match(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', data)


def check_length(data, length):
    """Checks length"""
    if len(data) <= length:
        return True
    else:
        return False


def is_password(password1):
    """Checks password requirements"""
    if len(password1) >= 8 and \
       re.search('[0-9]', password1) is not None and \
       re.search('[a-z]', password1) is not None and \
       re.search('[A-Z]', password1) is not None and \
       password1 != '':
        return True
    else:
        return False
