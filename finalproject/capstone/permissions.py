from rest_framework.permissions import BasePermission

# class IsAdministratorOrReadOnly(BasePermission):
class IsAdministrator(BasePermission):
    def has_permission(self, request, view):
        # Allow read-only access to all users
        if request.method in ['GET']:
            return True
        
        # Allow administrators full access
        return request.user.role == 'Administrator'
class IsCustomer(BasePermission):
   def has_permission(self, request, view):
        # Allow read-only access to all users
        if request.method == 'GET':
            return True
        
        # Allow customers to create orders
        return request.user.role == 'Customer'


from rest_framework.permissions import BasePermission
class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission to only allow admin users to edit objects.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True


        # Write permissions are only allowed to the admin.
        return request.user and request.user.is_staff
