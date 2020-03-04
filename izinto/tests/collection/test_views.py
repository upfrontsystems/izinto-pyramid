from pyramid import testing as pyramid_testing
import pyramid.httpexceptions as exc

from izinto.security import Administrator, User
from izinto.tests import BaseTest, dummy_request, add_user, add_collection, add_dashboard
from izinto.views.collection import (create_collection, get_collection_view, edit_collection,
                                    list_collections, delete_collection, paste_collection_view)


class TestCollectionViews(BaseTest):
    
    def test_create_collection(self):
        self.fail()

    def test_get_collection(self):
        self.fail()

    def test_edit_collection(self):
        self.fail()

    def test_list_collections(self):
        admin = add_user(self.session, role=Administrator, firstname='Admin')
        user1 = add_user(self.session, role=User, email='testuser1@email.com', firstname='User1')
        user2 = add_user(self.session, role=User, email='testuser2@email.com', firstname='User2')
        user3 = add_user(self.session, role=User, email='testuser3@email.com', firstname='User3')

        ca = add_collection(self.session, 'Collection A', 'Weather stats', users=[user1, user2])
        cada = add_dashboard(self.session, 'Dash CAA', 'Dashboard CAA', collection_id=ca.id)
        cadb = add_dashboard(self.session, 'Dash CAB', 'Dashboard CAB', collection_id=ca.id)
        cb = add_collection(self.session, 'Collection B', 'Temperature stats', users=[user3])
        cbda = add_dashboard(self.session, 'Dash CBA', 'Dashboard CBA', collection_id=cb.id)
        cbdb = add_dashboard(self.session, 'Dash CBB', 'Dashboard CBB', collection_id=cb.id)

        req = dummy_request(self.session)
        req.params = {}

        self.config.testing_securitypolicy(userid=admin.id, permissive=True)
        lst = list_collections(req)
        self.assertEqual(lst, [ca.as_dict(), cb.as_dict()])

        self.config.testing_securitypolicy(userid=user1.id, permissive=True)
        lst = list_collections(req)
        self.assertEqual(lst, [ca.as_dict()])

        self.config.testing_securitypolicy(userid=user2.id, permissive=True)
        lst = list_collections(req)
        self.assertEqual(lst, [ca.as_dict()])

        self.config.testing_securitypolicy(userid=user3.id, permissive=True)
        lst = list_collections(req)
        self.assertEqual(lst, [cb.as_dict()])

        req.params = {'list_dashboards': True}
        lst = list_collections(req)
        collection = cb.as_dict()
        collection['dashboards'] = [cbda.as_dict(), cbdb.as_dict()]
        self.assertEqual(lst, [collection])

    def test_delete_collection(self):
        self.fail()

    def test_paste_collection(self):
        self.fail()
