from pyramid import testing as pyramid_testing
import pyramid.httpexceptions as exc

from izinto.models import User
from izinto.tests import BaseTest, dummy_request, add_roles_and_permissions, add_user
from izinto.views.user import (create_user, get_user_view, edit_user,
                               list_users, delete_user)


class TestUserViews(BaseTest):

    def test_create_user(self):
        self.fail()

    def test_get_user(self):
        self.fail()

    def test_edit_user(self):
        """  Test edit a user """
        add_roles_and_permissions(self.session)
        user = add_user(self.session,
                        role='User',
                        firstname='Henry',
                        surname='Jones',
                        telephone='098111222',
                        address='1 Never road, Never Never Land',
                        password='password',
                        email='email3@email.com')
        self.session.add(user)
        self.session.flush()
        self.assertIsNotNone(user.id)
        self.config.testing_securitypolicy(userid=user.id, permissive=True)
        req = dummy_request(self.session)
        req.matchdict = {'id': user.id}
        req.json_body = {
            'firstname': 'Sarah',
            'surname': 'Johnson',
            'telephone': '021888000',
            'address': '1 New road',
            'password': 'new password',
            'email': 'newemail@email.com',
            'role': 'Administrator'
        }
        edit_user(req)
        self.assertEqual(user.firstname, req.json_body['firstname'])
        self.assertEqual(user.surname, req.json_body['surname'])
        self.assertEqual(user.telephone, req.json_body['telephone'])
        self.assertEqual(user.email, req.json_body['email'])
        self.assertEqual(user.address, req.json_body['address'])
        self.assertEqual(user.roles[0].name, req.json_body['role'])
        self.assertTrue(user.validate_password(req.json_body['password']))

    def test_list_users(self):
        self.fail()

    def test_delete_user(self):
        self.fail()
