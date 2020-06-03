from izinto.tests import BaseTest, add_dashboard, add_user
from izinto.models.collection import Collection
from izinto.models.data_source import DataSource


class TestCollectionModel(BaseTest):
    """
    Test collection model
    """

    def test_add_collection(self):
        """ Test add a collection """
        dashboard = add_dashboard(self.session, 'Dashboard')
        user = add_user(self.session)
        collection = Collection(title="Collection", description="Description")
        collection.dashboards.append(dashboard)
        collection.users.append(user)
        self.session.add(collection)
        self.session.flush()
        collection_id = collection.id
        collection = self.session.query(Collection).get(collection_id)
        self.assertIsNotNone(collection.id)
        self.assertEqual(collection.title, 'Collection')
        self.assertEqual(collection.description, 'Description')
        self.assertEqual(collection.dashboards[0], dashboard)
        self.assertEqual(collection.users[0], user)
        self.assertEqual(collection.__repr__(), 'Collection<id: %s, title: "Collection">' % collection_id)

    def test_as_dict(self):
        """ Test as_dict method """
        user = add_user(self.session)
        collection = Collection(title="Collection", description="Description")
        collection.users.append(user)
        self.session.add(collection)
        self.session.flush()
        collection_id = collection.id
        collection = self.session.query(Collection).get(collection_id)

        self.assertEqual(collection.as_dict(), {
            'id': collection.id,
            'title': "Collection",
            'description': "Description",
            'users': [user.as_dict()]
        })

    def test__repr__(self):
        """ Test __repr__ method """
        collection = Collection(title="Collection", description="Description")
        self.session.add(collection)
        self.session.flush()
        collection_id = collection.id
        collection = self.session.query(Collection).get(collection_id)
        self.assertIsNotNone(collection.id)
        self.assertEqual(collection.__repr__(), 'Collection<id: %s, title: "Collection">' % collection_id)
