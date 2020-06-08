from pyramid import testing as pyramid_testing
import pyramid.httpexceptions as exc

from izinto.security import Administrator, User
from izinto.tests import BaseTest, dummy_request, add_user, add_collection, add_dashboard
from izinto.views.collection import (create_collection, get_collection_view, edit_collection,
                                    list_collections, delete_collection, paste_collection_view)


class TestCollectionViews(BaseTest):
    
    def test_create_collection(self):
        admin = add_user(self.session, role=Administrator, firstname='Admin')
        user1 = add_user(self.session, role=User, email='testuser1@email.com', firstname='User1')
        self.config.testing_securitypolicy(userid=admin.id, permissive=True)

        req = dummy_request(self.session)
        req.json_body = {}
        with self.assertRaises(exc.HTTPBadRequest):
            create_collection(req)

        req.json_body = {'title': 'Collection',
                         'description': 'Description',
                         'users': [user1.as_dict()]}
        collection = create_collection(req)

        self.assertIsNotNone(collection['id'])
        self.assertEqual(collection['title'], 'Collection')
        self.assertEqual(len(collection['users']), 2)

    def test_get_collection(self):
        user1 = add_user(self.session, role=User, email='testuser1@email.com', firstname='User1')
        user2 = add_user(self.session, role=User, email='testuser2@email.com', firstname='User2')

        collection = add_collection(self.session, 'Collection', 'Description', users=[user1, user2])
        dash = add_dashboard(self.session, 'Dash', 'Dashboard', collection_id=collection.id)

        req = dummy_request(self.session)
        req.matchdict = {}

        with self.assertRaises(exc.HTTPBadRequest):
            get_collection_view(req)

        with self.assertRaises(exc.HTTPNotFound):
            req.matchdict['id'] = 100
            get_collection_view(req)

        req.matchdict['id'] = collection.id
        resp = get_collection_view(req)

        self.assertEqual(resp['id'], collection.id)
        self.assertEqual(resp['title'], 'Collection')
        self.assertEqual(resp['dashboards'][0], dash.as_dict())

    def test_edit_collection(self):
        user1 = add_user(self.session, role=User, email='testuser1@email.com', firstname='User1')
        user2 = add_user(self.session, role=User, email='testuser2@email.com', firstname='User2')

        collection = add_collection(self.session, 'Collection', 'Description', users=[user1])
        self.assertEqual(collection.users[0], user1)

        req = dummy_request(self.session)
        req.matchdict = {}

        with self.assertRaises(exc.HTTPBadRequest):
            req.json_body = {}
            edit_collection(req)
        with self.assertRaises(exc.HTTPNotFound):
            req.matchdict['id'] = 100
            req.json_body = {'title': 'Edited title', 'description': 'Edited description', 'users': [user2.as_dict()]}
            edit_collection(req)
        with self.assertRaises(exc.HTTPBadRequest):
            req.matchdict['id'] = collection.id
            req.json_body = {'description': 'Description'}
            edit_collection(req)

        req.json_body = {'title': 'Edited title', 'description': 'Edited description', 'users': [user2.as_dict()]}
        resp = edit_collection(req)
        self.assertEqual(resp['title'], 'Edited title')
        self.assertEqual(resp['users'][0], user2.as_dict())

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
        collection = add_collection(self.session, 'Collection', 'Description')
        collection_id = collection.id

        req = dummy_request(self.session)
        with self.assertRaises(exc.HTTPNotFound):
            req.matchdict = {}
            delete_collection(req)

        req.matchdict['id'] = collection_id
        delete_collection(req)

        with self.assertRaises(exc.HTTPNotFound):
            get_collection_view(req)

    def test_paste_collection(self):
        user1 = add_user(self.session, role=User, email='testuser1@email.com', firstname='User1')
        user2 = add_user(self.session, role=User, email='testuser2@email.com', firstname='User2')

        collection = add_collection(self.session, 'Collection', 'Description', users=[user1, user2])
        add_dashboard(self.session, 'Dash', 'Dashboard', collection_id=collection.id)
        collection_id = collection.id

        req = dummy_request(self.session)
        req.json_body = {}
        with self.assertRaises(exc.HTTPBadRequest):
            paste_collection_view(req)

        req.matchdict['id'] = collection_id
        pasted = paste_collection_view(req)
        self.assertEqual(pasted['title'], 'Copy of Collection')
        self.assertEqual(len(pasted['users']), len(collection.users))

        pasted = paste_collection_view(req)
        self.assertEqual(pasted['title'], 'Copy of Collection (2)')
        pasted = paste_collection_view(req)
        self.assertEqual(pasted['title'], 'Copy of Collection (3)')
