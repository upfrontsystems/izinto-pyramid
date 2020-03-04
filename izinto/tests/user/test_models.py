from izinto.models import Role, UserRole
from izinto.security import Administrator
from izinto.tests import BaseTest, add_roles_and_permissions, add_user
from izinto.models.user import User


class UserTestModels(BaseTest):
    """
    Test User models
    """

    def test_add_user(self):
        """ Test add a user """
        user = User(firstname='Henry',
                    surname='Jones',
                    telephone='098111222',
                    address='1 Never road, Never Never Land',
                    password='new password',
                    email='email1@email.com')
        self.session.add(user)
        self.session.flush()
        self.assertIsNotNone(user.id)
        self.assertEqual(user.password, 'new password')

    def test_add_user_role(self):
        """ Test add a user with a role """
        add_roles_and_permissions(self.session)
        user = User(firstname='Henry',
                    surname='Jones',
                    telephone='098111222',
                    address='1 Never road, Never Never Land',
                    password='new password',
                    email='email2@email.com')
        self.session.add(user)
        self.session.flush()
        role = self.session.query(Role).filter(
            Role.name == 'User').first()
        user.roles.append(role)
        self.session.add(user)
        self.session.flush()
        user_role = self.session.query(UserRole).filter(
            UserRole.user_id == user.id,
            UserRole.role_id == role.id).first()
        self.assertIsNotNone(user_role)

    def test_add_user_registrations(self):
        """ Test add a user with user registrations """
        user = User(firstname='Henry',
                    surname='Jones',
                    telephone='098111222',
                    address='1 Never road, Never Never Land',
                    password='new password',
                    email='email3@email.com')
        self.session.add(user)
        self.session.flush()
        user_id = user.id
        self.assertIsNotNone(user_id)

        user = User(firstname='Henry',
                    surname='Jones',
                    telephone='098111222',
                    address='1 Never road, Never Never Land',
                    password='new password',
                    email='email4@email.com')
        self.session.add(user)
        self.session.flush()
        user_id = user.id
        self.assertIsNotNone(user_id)

        user = self.session.query(User).filter(User.id == user_id).first()
        self.session.delete(user)
        self.session.flush()

    def test_has_role(self):
        admin = add_user(self.session, Administrator)
        self.assertTrue(admin.has_role(Administrator))
        self.assertFalse(admin.has_role(User))
