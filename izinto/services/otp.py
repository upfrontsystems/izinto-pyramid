import datetime
import logging
import random
import string
import uuid

import html2text
import requests
from pyramid.renderers import render
from pyramid import httpexceptions as exc
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from requests import ConnectionError
from sqlalchemy.exc import DBAPIError
from izinto.models import session, OTP, User
from izinto.utils import is_email_address, parse_and_correct
log = logging.getLogger(__name__)


def generate_and_send_otp(request, user, page_url='otp'):
    """
    Sends a one time pin to a user by email or telephone
    :param request:
    :param user:
    :param page_url:
    :return:
    """
    telephone_secret = None
    email_secret = None

    if user.email:
        otp = generate(user.email, user.id)
        send(request, otp, page_url)
        email_secret = otp.secret
    elif user.telephone:
        otp = generate(user.telephone, user.id)
        send(request, otp, page_url)
        telephone_secret = otp.secret
    return {'emailsecret': email_secret, 'telephonesecret': telephone_secret}


def generate(identifier, user_id, max_age=12):
    """
    Generate a random 5 letter string for a One Time Pin.

    max_age: Integer or Float. If max_age is not given,
    it will default to 12 hours. OTPs will
    be regenerated if older than this amount.
    """
    # Check OTP table for this identifier
    old_otp = session.query(OTP). \
        filter(OTP.identifier == OTP.clean_identifier(identifier)). \
        order_by(OTP.timestamp).all()

    # if a previous otp has been sent and it is younger than max_age
    # then send that one
    if old_otp:
        old_otp = old_otp[-1]

        age = datetime.datetime.utcnow() - old_otp.timestamp

        if age < datetime.timedelta(max_age / 24.0):
            return old_otp

    otp_string = ''.join(random.sample(string.ascii_uppercase, 5))
    secret = str(uuid.uuid4())
    identifier = OTP.clean_identifier(identifier)

    otp = OTP(
        otp=otp_string,
        secret=str(uuid.uuid4()),
        identifier=identifier,
        timestamp=datetime.datetime.utcnow(),
        user_id=user_id)

    session.add(otp)
    session.flush()
    log.info("Generated OTP/Secret: {} / {}".format(otp_string, secret))

    return otp


def get_from_secret(secret):
    """Return the OTP that matches the given secret."""
    try:
        otp = session.query(OTP).filter(OTP.secret == secret).first()
    except DBAPIError as DBE:
        log.info("There was a database error: {}".format(DBE))
        raise

    return otp


def get_identifier_from_secret(secret):
    """Return the OTP that matches the given secret."""
    otp = get_from_secret(secret)
    return otp.identifier


def confirm_user_otp(otp_str, otp_secret):
    """
    Confirm user registration from OTP
    :param otp_str:
    :param otp_secret:
    :return:
    """
    otp = session.query(OTP).filter(OTP.otp == otp_str.strip()).first()
    if not otp:
        raise exc.HTTPBadRequest(json_body={'message': 'Incorrect OTP.'})
    identifier = validate(otp_str, otp_secret)
    if not identifier:
        raise exc.HTTPBadRequest(json_body={'message': 'Invalid OTP or expired OTP.'})
    user = session.query(User).get(otp.user_id)
    if not user:
        return None
    user.confirmed_registration = True
    session.add(user)
    session.flush()
    delete(otp)
    return user


def confirm_user_registration(otp_str, otp_secret):
    """
    Confirm user registration from OTP
    :param otp_str:
    :param otp_secret:
    :return:
    """
    otp = session.query(OTP).filter(OTP.otp == otp_str.strip()).first()
    if not otp:
        raise exc.HTTPBadRequest(json_body={'message': 'Incorrect OTP.'})
    identifier = validate(otp_str, otp_secret)
    if not identifier:
        raise exc.HTTPBadRequest(json_body={'message': 'Invalid OTP or expired OTP.'})
    user = session.query(User).get(otp.user_id)
    if not user:
        return None
    user.confirmed_registration = True
    session.add(user)
    session.flush()
    delete(otp)
    return user


def validate(otp, secret):
    """
    Check if database contains a record where OTP and secret matches.

    Returns the identifier of the record if a match is found, else None
    """
    otp = otp.upper().strip()

    try:
        query = session.query(OTP)
        query = query.filter(OTP.otp == otp.upper()).filter(
            OTP.secret == secret).first()
    except DBAPIError as DBE:
        log.info("There was a database error: {}".format(DBE))
        raise

    if query:
        return query.identifier
    else:
        return None


def send(request, otp, page_url):
    """Send the OTP using whichever channel seems appropriate."""
    url = '%s/authentication/%s/%s' % (request.json_body['application_url'], page_url, otp.secret)
    if is_email_address(otp.identifier):
        try:
            _send_email_otp(request, otp, url)
        except ConnectionError:
            log.critical("SMTP Server cannot be reached")
    else:
        try:
            _send_cellphone_otp(request, otp, url)
        except ConnectionError:
            log.critical("SMS Gateway cannot be reached")


def delete(otp):
    """Remove OTP/Secret pair from the database."""
    session.delete(otp)
    session.flush()


def _send_email_otp(request, otp, url):
    email = otp.identifier
    mailer = get_mailer(request)
    sender = request.registry.settings.get('sender.address')
    html_body = render('templates/otp-email.jinja2', {'otp': otp.otp, 'link': url})

    text_body = html2text.html2text(html_body)
    message = Message(subject="Reset your Izinto password",
                      sender=sender,
                      recipients=[email],
                      body=text_body,
                      html=html_body)
    try:
        mailer.send_immediately(message)
        log.info("Sent OTP: {otp} to {id}".format(
            otp=otp.otp, id=email))

    except Exception as exc:
        log.info(
            "OTP email failed: {otp} to {id}: \nMessage: {msg}".format(
                otp=otp.otp, id=email, msg=exc))


def _send_cellphone_otp(request, otp, url):
    telephone = otp.identifier

    smsgateway = request.registry.settings.get('smsgateway.url')
    username = request.registry.settings.get('smsgateway.username')
    password = request.registry.settings.get('smsgateway.password')
    message = render('templates/otp-sms.jinja2', {'otp': otp.otp, 'link': url})

    params = {'username': username,
              'password': password,
              'message': message,
              # parse and correct changes telephone number
              # from 0xx xxx xxxx to 27xx xxx xxxx format
              'msisdn': parse_and_correct(telephone)}
    try:
        log.info('SMS OTP | {} | SENT | Gateway: {} | Params: {}'.format(
            telephone, smsgateway, params))

        gateway_response = requests.post(smsgateway, params=params)

        log.info(
            'SMS OTP | {} | RECEIVED | Response Text: {} | '
            'Full Response {}'.format(
                telephone, gateway_response.text,
                gateway_response.__dict__))

        log.info("Sent OTP: {otp} to {id}".format(
            otp=otp.otp, id=telephone))
    except ConnectionError:
        log.info("Cannot connect to the SMS Gateway server")
        raise ConnectionError("Cannot connect to sms gateway server")

    response_codes = gateway_response.text.split('|')
    log.info("SMS Gateway Response code: {}".format(', '.join(
        response_codes)))
    # bulksms is not clear on their return string.
    # Their code sample suggests that there's always 3 values
    # if statusCode == 0
    # From their website:
    #   status_code|status_description|batch_id (where batch_id is
    #   optional, depending on the error)
    #   Possible values for status_code are:
    #
    #   0:   In progress (a normal message submission, with no error
    #        encountered so far).
    #   1:   Scheduled (see Scheduling below).
    #   22:  Internal fatal error
    #   23:  Authentication failure
    #   24:  Data validation failed
    #   25:  You do not have sufficient credits
    #   26:  Upstream credits not available
    #   27:  You have exceeded your daily quota
    #   28:  Upstream quota exceeded
    #   40:  Temporarily unavailable
    #   201: Maximum batch size exceeded

    log.info('statusCode: {}'.format(response_codes[0]))
    log.info('statusString: {}'.format(response_codes[1]))
