import pyramid.httpexceptions as exc

from izinto.security import Administrator
from izinto.security import User as UserRole
from izinto.tests import BaseTest, dummy_request, add_roles_and_permissions, add_user
from izinto.views.user import (create_user, get_user_view, edit_user,
                               list_users, delete_user)


class TestUserViews(BaseTest):

    def setUp(self):
        super(TestUserViews, self).setUp()
        add_roles_and_permissions(self.session)

    def test_create_user(self):
        req = dummy_request(self.session)
        req.json_body = {}

        with self.assertRaises(exc.HTTPBadRequest):
            create_user(req)
        req.json_body = {'email': 'user@email'}
        with self.assertRaises(exc.HTTPBadRequest):
            create_user(req)
        req.json_body = {'email': 'user@email', 'firstname': 'Name', 'surname': 'Surname'}
        with self.assertRaises(exc.HTTPBadRequest):
            create_user(req)

        req.json_body = {'email': 'user@email',
                         'firstname': 'Name',
                         'surname': 'Surname',
                         'role': 'User',
                         'telephone': '01235456',
                         'address': 'address',
                         'password': 'password'}
        resp = create_user(req)
        self.assertIsNotNone(resp['id'])
        self.assertEqual(resp['email'], 'user@email')
        self.assertEqual(resp['role'], 'User')

    def test_get_user(self):
        user = add_user(self.session, role=UserRole, email='testuser@email.com', firstname='User')
        user2 = add_user(self.session, role=UserRole, email='testuser2@email.com', firstname='User')
        admin = add_user(self.session, role=Administrator, email='testadmin@email.com', firstname='Admin')
        req = dummy_request(self.session)
        req.matchdict = {}

        with self.assertRaises(exc.HTTPBadRequest):
            get_user_view(req)
        req.matchdict['id'] = user.id
        self.config.testing_securitypolicy(userid=user2.id, permissive=True)
        with self.assertRaises(exc.HTTPForbidden):
            get_user_view(req)
        self.config.testing_securitypolicy(userid=admin.id, permissive=True)
        req.matchdict['id'] = 100
        with self.assertRaises(exc.HTTPNotFound):
            get_user_view(req)

        req.matchdict['id'] = user.id
        resp = get_user_view(req)
        self.assertEqual(resp, user.as_dict())

    def test_edit_user(self):
        """  Test edit a user """
        user = add_user(self.session,
                        role='User',
                        firstname='Henry',
                        surname='Jones',
                        telephone='098111222',
                        address='1 Never road, Never Never Land',
                        password='password',
                        email='email3@email.com')
        user1 = add_user(self.session, email='email1@email.com', telephone='00000')
        self.session.add(user)
        self.session.flush()
        self.assertIsNotNone(user.id)
        self.config.testing_securitypolicy(userid=user.id, permissive=True)
        req = dummy_request(self.session)
        req.matchdict = {}
        req.json_body = {}
        with self.assertRaises(exc.HTTPBadRequest):
            edit_user(req)
        req.matchdict = {'id': 100}
        req.json_body = {
            'firstname': 'Sarah',
            'surname': 'Johnson',
            'telephone': '021888000',
            'address': '1 New road',
            'password': 'new password',
            # 'email': 'newemail@email.com',
            'role': 'Administrator'
        }
        with self.assertRaises(exc.HTTPNotFound):
            edit_user(req)
        req.matchdict = {'id': user.id}
        with self.assertRaises(exc.HTTPBadRequest):
            edit_user(req)
        req.json_body = {
            # 'firstname': 'Sarah',
            # 'surname': 'Johnson',
            'telephone': '021888000',
            'address': '1 New road',
            'password': 'new password',
            'email': 'newemail@email.com',
            'role': 'Administrator'
        }
        with self.assertRaises(exc.HTTPBadRequest):
            edit_user(req)
        req.json_body = {
            'firstname': 'Sarah',
            'surname': 'Johnson',
            'telephone': '021888000',
            'address': '1 New road',
            'password': 'new password',
            'email': 'newemail@email.com',
            # 'role': 'Administrator'
        }
        with self.assertRaises(exc.HTTPBadRequest):
            edit_user(req)
        req.json_body = {
            'firstname': 'Sarah',
            'surname': 'Johnson',
            'telephone': '00000',
            'address': '1 New road',
            'password': 'new password',
            'email': 'newemail@email.com',
            'role': 'Administrator'
        }

        req.json_body = {
            'firstname': 'Sarah',
            'surname': 'Johnson',
            'telephone': '00000',
            'address': '1 New road',
            'password': 'new password',
            'email': 'newemail@email.com',
            'role': 'Administrator'
        }
        req.json_body = {
            'firstname': 'Sarah',
            'surname': 'Johnson',
            'telephone': '021888000',
            'address': '1 New road',
            'password': 'new password',
            'email': 'email1@email.com',
            'role': 'Administrator'
        }
        with self.assertRaises(exc.HTTPBadRequest):
            edit_user(req)

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
        add_user(self.session, role=UserRole, email='testuser1@email.com', firstname='User')
        add_user(self.session, role=UserRole, email='testuser2@email.com', firstname='User', surname='Filter')
        user = add_user(self.session, role=UserRole, email='testuser3@email.com', firstname='User3')
        user.inactive = True
        add_user(self.session, role=Administrator, firstname='Admin')

        req = dummy_request(self.session)
        users = list_users(req)
        self.assertEqual(len(users), 4)

        # TODO no concat function in sqlite

        req.params = {'role': UserRole}
        users = list_users(req)
        self.assertEqual(len(users), 3)
        req.params = {'name': 'User'}
        users = list_users(req)
        self.assertEqual(len(users), 3)
        req.params = {'name': 'Admin'}
        users = list_users(req)
        self.assertEqual(len(users), 1)
        req.params = {'search': 'Fil'}
        users = list_users(req)
        self.assertEqual(len(users), 1)
        req.params = {'inactive': True}
        users = list_users(req)
        self.assertEqual(len(users), 1)

    def test_delete_user(self):
        user = add_user(self.session, role=UserRole, email='testuser@email.com', firstname='User')
        req = dummy_request(self.session)
        req.matchdict = {}

        with self.assertRaises(exc.HTTPBadRequest):
            delete_user(req)
        req.matchdict['id'] = 100
        with self.assertRaises(exc.HTTPNotFound):
            delete_user(req)

        req.matchdict['id'] = user.id
        delete_user(req)

        with self.assertRaises(exc.HTTPNotFound):
            delete_user(req)
