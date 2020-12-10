from izinto.models import session


def get_user_access(model, column, context_id, user_id):
    """
    Return user access role if it exists
    for the logged in user on the dashboard/collection
    """

    user_access = session.query(model).filter(getattr(model, column) == context_id,
                                              model.user_id == user_id).first()
    if user_access:
        return {column: context_id,
                'user_id': user_id,
                'role': user_access.role.name}
    return {}
