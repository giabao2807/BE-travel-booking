from api_user.statics import RoleData
from base.permission.permission import MyRolePermission


class AdminPermission(MyRolePermission):
    match_any_roles = [RoleData.ADMIN]


class CustomerPermission(MyRolePermission):
    match_any_roles = [RoleData.CUSTOMER]


class PartnerPermission(MyRolePermission):
    match_any_roles = [RoleData.PARTNER]


class UserPermission(MyRolePermission):
    match_any_roles = [RoleData.ADMIN, RoleData.CUSTOMER, RoleData.PARTNER]