from django.contrib import admin

from .models import LdapGroup, LdapUser


class LDAPGroupAdmin(admin.ModelAdmin):
    exclude = [
        "dn",
        "objectClass",
        "members",
    ]  # members: listField doesn't work properly in Admin
    list_display = ["gid", "name"]


class LDAPUserAdmin(admin.ModelAdmin):
    exclude = ["dn", "objectclass", "sshkeys", "unixpass", "lockedTime"]
    list_display = ["cn", "username", "uid", "gid"]


admin.site.register(LdapGroup, LDAPGroupAdmin)
admin.site.register(LdapUser, LDAPUserAdmin)
