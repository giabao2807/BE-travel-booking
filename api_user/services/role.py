from api_user.models import Role
from api_user.statics import RoleData


class RoleService:
    @classmethod
    def get_role_customer(cls) -> Role:
        """
        Get the customer role.
        Role model have to have a customer role. If not, pls contact your leader now!!!

        :return: The customer role.
        """
        role = Role.objects.by_id(role_id=RoleData.CUSTOMER.value.get('id'))
        if not role:
            raise Exception('Missing default role')
        return role

    @classmethod
    def get_role_partner(cls) -> Role:
        """
        Get the employee role.
        Role model have to have a customer role. If not, pls contact your leader now!!!

        :return: The employee role.
        """
        role = Role.objects.by_id(role_id=RoleData.PARTNER.value.get('id'))
        if not role:
            raise Exception('Missing partner role')
        return role
