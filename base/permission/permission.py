from rest_framework.permissions import BasePermission

from api_user.statics import RoleData
from core.settings import SCOPES


class MyRolePermission(BasePermission):
    match_any_roles = []

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if not self.match_any_roles:
            return True

        for role in self.match_any_roles:
            if request.user.role_id.hex == role.value.get('id'):
                return True
        return False


class MyActionPermission(BasePermission):
    def has_permission(self, request, view):
        token = request.auth

        if not token:
            return False

        user_roles = request.user.roles
        user_scopes = self.get_scopes_user_role(user_roles)

        required_alternate_scopes = getattr(view, "required_alternate_scopes")
        action = view.action.lower()
        if action in required_alternate_scopes:
            return any(
                scope in user_scopes for scope in required_alternate_scopes[action]
            )
        else:
            return True

    @classmethod
    def get_scopes_user_role(cls, roles):
        user_scopes = []
        if roles:
            for role in roles.all():
                scope_text = role.scope_text
                if role.name == RoleData.ADMIN.value.get('name'):
                    return list(SCOPES.keys())
                user_scopes.append(scope for scope in scope_text.split(' '))
        return user_scopes
