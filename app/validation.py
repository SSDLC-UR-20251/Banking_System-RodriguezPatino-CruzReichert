import datetime
import re
import unicodedata


def normalize_input(data):
    return unicodedata.normalize("NFKD",data)

def validate_email(email):
    email = normalize_input(email)
    valid = email.endswith("@urosario.edu.co") and email.split('@')[0] != ""
    return valid

def validate_dob(dob):
    today = datetime.date.today()
    ago = datetime.date(today.year - 16, today.month, today.day)
    birth = datetime.datetime.strptime(dob, '%Y-%m-%d').date()

    if birth <= ago:
        return True
    return False

def validate_user(user):
    if user.count('.') == 1:
        part1, part2 = user.split('.')
        valid = part1.isalpha() and part2.isalpha()
    else:
        valid = False
    return valid


def validate_dni(dni):
    valid = all(c.isnumeric() for c in dni) and len(dni) < 11 and dni[0] == '1'
    return valid

def validate_pswd(pswd):
    valid = any(c.isupper() for c in pswd) and any(c.islower() for c in pswd) and any(c.isnumeric() for c in pswd) and any(c in "#*@$%&-!+=?" for c in pswd) and 7 < len(pswd) < 36
    return valid


def validate_name(name):
    return name.isalpha()
