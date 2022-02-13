# Register your models here.
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import SignupCode

# from .forms import UserAdminCreationForm, UserAdminChangeForm

User = get_user_model()

# Remove Group Model from admin. We're not using it.
admin.site.unregister(Group)


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    # form = UserAdminChangeForm
    # add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ['email', 'admin']
    list_filter = ['admin']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ()}),
        ('Permissions', {'fields': ('admin',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
         ),
    )
    search_fields = ['email']
    ordering = ['email']
    filter_horizontal = ()


class SignupCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'user', 'ipaddr', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('user', 'code', 'ipaddr')

    def has_add_permission(self, request, obj=None):
        return False


class SignupCodeInline(admin.TabularInline):
    model = SignupCode
    fieldsets = (
        (None, {
            'fields': ('code', 'ipaddr', 'created_at')
        }),
    )
    readonly_fields = ('code', 'ipaddr', 'created_at')

    def has_add_permission(self, request, obj=None):
        return False


admin.site.register(SignupCode, SignupCodeAdmin)
admin.site.register(User, UserAdmin)
