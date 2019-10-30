import logging
import re
import random

logger = logging.getLogger(__name__)


def is_email_address(email=None):
    """ Returns true if given string looks like an email address """

    # from http://nbviewer.ipython.org/github/rasbt/python_reference/blob/
    #   master/tutorials/useful_regex.ipynb#Checking-for-valid-email-addresses
    pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

    if email:
        return bool(re.match(pattern, email))
    else:
        return False


def parse_and_correct(telephone, country=None):
    """
    Checks if number is in the format needed for sms gateway and corrects it if
    is is not.
    """
    oldnumber = telephone

    country = country or '27'

    if (len(telephone) == 10) and (telephone.startswith('0')):
        telephone = country + telephone[1:]
        logger.info("Changed mobile number from {old} to {new}".format(
            old=oldnumber, new=telephone))

    elif (len(telephone) == 11) and (telephone.startswith('27')):
        logger.info("Mobile number unchanged: {new}".format(new=telephone))

    return telephone


def generate_password():
    """ Generate simple random password """

    sample = 'abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?'
    return ''.join(random.sample(sample, 8))


def row_as_dict(row):
    d = {}
    for field_name in row._fields:
        d[field_name] = getattr(row, field_name)
    return d
