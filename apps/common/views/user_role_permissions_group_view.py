from utils.customview import CustomView
from ..modelss.roles_permissions_group import Role, Permission, Group
from ..models import User
from ..sers.user_roles_permissions_group_ser import UserSer, PermissionSer, RoleSer, GroupSer


class UserView(CustomView):
    queryset = User.objects.all()
    serializer_class = UserSer
    # pagination_class = BasePage
    permission_classes = []


class PermissionView(CustomView):
    queryset = Permission.objects.all()
    serializer_class = PermissionSer
    permission_classes = []


class GroupView(CustomView):
    queryset = Group.objects.all()
    serializer_class = GroupSer
    permission_classes = []


class RoleView(CustomView):
    queryset = Role.objects.all()
    serializer_class = RoleSer
    permission_classes = []
