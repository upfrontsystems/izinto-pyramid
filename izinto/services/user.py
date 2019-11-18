from izinto.models import session, User, Role, UserRole


def get_user(user_id=None, telephone=None, email=None, role=None, inactive=None):
    """
    Get a user
    :param user_id:
    :param telephone:
    :param email:
    :param role:
    :param inactive:
    :return:
    """

    query = session.query(User)

    if inactive is not None:
        query = query.filter(User.inactive == inactive)

    if user_id:
        query = query.filter(User.id == user_id)

    if telephone:
        query = query.filter(User.telephone == telephone)

    # case insensitive match by email
    if email:
        query = query.filter(User.email.ilike(email))

    if role:
        query = query.join(User.roles).filter(Role.name == role)

    return query.first()
