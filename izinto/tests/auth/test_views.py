import pyramid.httpexceptions as exc
from pyramid import testing as pyramid_testing

from izinto.models import OTP
from izinto.services.otp import generate_and_send_otp
from izinto.tests import BaseTest, add_user, add_roles_and_permissions, dummy_request, mock_otp
from izinto.views import get_user
from izinto.views.auth import register_user, confirm_otp_registration, set_new_password, login, reset_password


class TestAuthViews(BaseTest):
    """ Class for testing auth views """

    def test_register_user(self):
        mock_otp()
        add_roles_and_permissions(self.session)
        req = dummy_request(self.session)

        # Test error validation
        with self.assertRaises(exc.HTTPBadRequest):
            req.json_body = {
                'surname': 'Jones',
                'email': 'test@test.com',
                'password': 'pass',
                'role': 'User'
            }
            register_user(req)

        with self.assertRaises(exc.HTTPBadRequest):
            req.json_body = {
                'firstname': 'Julius',
                'email': 'test@test.com',
                'password': 'pass',
                'role': 'User'
            }
            register_user(req)

        with self.assertRaises(exc.HTTPBadRequest):
            req.json_body = {
                'firstname': 'Julius',
                'surname': 'Jones',
                'password': 'pass',
                'role': 'User'
            }
            register_user(req)

        with self.assertRaises(exc.HTTPBadRequest):
            req.json_body = {
                'firstname': 'Julius',
                'surname': 'Jones',
                'password': 'pass',
                'role': 'User'
            }
            register_user(req)

        with self.assertRaises(exc.HTTPBadRequest):
            req.json_body = {
                'firstname': 'Julius',
                'surname': 'Jones',
                'email': 'test@test.com',
                'role': 'User'
            }
            register_user(req)

        with self.assertRaises(exc.HTTPBadRequest):
            req.json_body = {
                'firstname': 'Julius',
                'surname': 'Jones',
                'email': 'test@test.com',
                'password': 'pass',
            }
            register_user(req)

        req.json_body = {
            'firstname': 'Julius',
            'surname': 'Jones',
            'email': 'test@test.com',
            'password': 'pass',
            'role': 'User',
            'application_url': 'api'
        }

        secrets = register_user(req)
        self.assertIsNotNone(secrets.get('emailsecret'))

        user = get_user(email='test@test.com').as_dict()
        self.assertEqual(user.get('firstname'), 'Julius')
        self.assertEqual(user.get('surname'), 'Jones')
        self.assertEqual(user.get('email'), 'test@test.com')
        self.assertEqual(user.get('role'), 'User')

        with self.assertRaises(exc.HTTPBadRequest):
            register_user(req)

    def test_confirm_registration(self):
        mock_otp()
        add_roles_and_permissions(self.session)
        req = dummy_request(self.session)

        req.json_body = {
            'firstname': 'Julius',
            'surname': 'Jones',
            'email': 'test@test.com',
            'password': 'pass',
            'role': 'User',
            'application_url': '/'
        }

        secrets = register_user(req)
        self.assertIsNotNone(secrets.get('emailsecret'))

        user = get_user(email='test@test.com')
        otp = self.session.query(OTP).filter(OTP.user_id == user.id).first()

        req.json_body = {'otp': otp.otp, 'secret': secrets['emailsecret']}
        response = confirm_otp_registration(req)
        user = get_user(user_id=response.get('user_id'))
        self.assertEqual(user.confirmed_registration, True)

    def test_set_new_password(self):
        mock_otp()
        add_roles_and_permissions(self.session)
        req = dummy_request(self.session)
        user = add_user(self.session)
        req.json_body = {'application_url': '/'}

        secrets = generate_and_send_otp(req, user)
        otp = self.session.query(OTP).filter(OTP.user_id == user.id).first()

        req.json_body = {
            'user_id': user.id,
            'password': 'new_password',
            'otp': otp.otp,
            'secret': secrets.get('emailsecret'),
        }

        response = set_new_password(req)
        user = get_user(user_id=response.get('id'))
        self.assertTrue(user.validate_password('new_password'))

    def test_user_login(self):
        mock_otp()
        user = add_user(self.session, email='user@email.com', password='pass')
        user2 = add_user(self.session, email='user2@email.com', telephone='02188911', password='new_password')
        req = dummy_request(self.session)
        req.method = 'POST'

        with self.assertRaises(exc.HTTPBadRequest):
            req.json_body = {}
            login(req)

        # Attempt to login to account with no password set
        with self.assertRaises(exc.HTTPBadRequest):
            req.json_body = {
                'email': user2.email,
                'application_url': '/'
            }
            login(req)

        # Attempt successful login
        req.json_body = {
            'email': user2.email,
            'password': 'new_password'
        }
        response = login(req)
        self.assertIsNotNone(response.get('access_token'))

        # Check that log in with email is case insensitive
        req.json_body = {
            'email': user2.email.upper(),
            'password': 'new_password'
        }
        response = login(req)
        self.assertIsNotNone(response.get('access_token'))

        # Attempt to login to invalid account
        user3 = add_user(self.session, email='user3@email.com', password='pass', confirmed_registration=False)
        req.json_body = {
            'email': user3.email,
            'application_url': '/'
        }
        response = login(req)
        self.assertEqual(response.get('message'),
                         'You have not yet confirmed your account. Please check your email for further instructions.')

        # Validate account
        otp = self.session.query(OTP).filter(OTP.user_id == user3.id).first()
        req.json_body = {'otp': otp.otp, 'secret': response.get('secrets').get('emailsecret')}
        response = confirm_otp_registration(req)
        self.assertIsNotNone(response.get('id'))
        user3 = get_user(user_id=response.get('id'))
        self.assertEqual(user3.confirmed_registration, True)

        # Attempt missing password login
        req.json_body = {
            'email': user.email,
            'password': ''
        }
        with self.assertRaises(exc.HTTPBadRequest):
            login(req)

        # Attempt wrong password login
        req.json_body = {
            'email': user.email,
            'password': 'wrong_password'
        }
        with self.assertRaises(exc.HTTPBadRequest):
            login(req)

        # Attempt successful login
        req.json_body = {
            'email': user.email,
            'password': 'pass'
        }
        response = login(req)
        self.assertEqual(response.get('id'), user.id)
        self.assertEqual(response.get('firstname'), user.firstname)
        self.assertEqual(response.get('surname'), user.surname)

        # Attempt login with case insensitive email
        req.json_body = {
            'email': 'UsEr@EmaIl.cOm',
            'password': 'pass'
        }
        response = login(req)
        self.assertEqual(response.get('id'), user.id)


class TestResetPassword(BaseTest):
    """ Test resetting password """

    def setUp(self):
        super(TestResetPassword, self).setUp()
        self.config = pyramid_testing.setUp()
        self.config.include('pyramid_mailer.testing')
        self.config.include('pyramid_jinja2')
        self.request = dummy_request(self.session)
        self.request.registry.settings['izinto.app.secret'] = 'testsecret'
        add_roles_and_permissions(self.session)

    def test_reset_view(self):
        """ Test the reset view """
        self.request.json_body = {
            'firstname': 'Julius',
            'surname': 'Jones',
            'email': 'test@test.com',
            'password': 'pass',
            'role': 'User',
            'application_url': '/'
        }

        register_user(self.request)
        request = self.request
        request.json_body = {'email': 'test@test.com', 'application_url': '/'}
        response = reset_password(request)
        self.assertIsNotNone(response['secrets']['emailsecret'])

    def test_set_new_password(self):
        """ test setting a new password. """
        self.request.json_body = {
            'firstname': 'Julius',
            'surname': 'Jones',
            'email': 'test@test.com',
            'password': 'pass',
            'role': 'User',
            'application_url': '/'
        }

        register_user(self.request)
        user = get_user(email='test@test.com')
        self.request.json_body = {'email': user.email, 'application_url': '/'}
        response = reset_password(self.request)
        secret = response['secrets']['emailsecret']
        otp = self.session.query(OTP).filter(OTP.user_id == user.id).first()
        self.request.method = 'POST'
        self.request.json_body = {'secret': secret,
                                  'otp': otp.otp,
                                  'user_id': user.id,
                                  'password': 'new_password'}
        response = set_new_password(self.request)
        self.assertIn('email', list(response.keys()))
        user = get_user(user_id=user.id)
        self.assertTrue(user.validate_password('new_password'))

        # test forgetting password with case insensitive email
        self.request.json_body = {'email': 'TeSt@Test.Com', 'application_url': '/'}
        response = reset_password(self.request)
        secret = response['secrets']['emailsecret']
        otp = self.session.query(OTP).filter(OTP.user_id == user.id).first()
        self.request.method = 'POST'
        self.request.json_body = {'secret': secret,
                                  'otp': otp.otp,
                                  'user_id': user.id,
                                  'password': 'new_password'}
        response = set_new_password(self.request)
        self.assertEqual(response['email'], user.email)
