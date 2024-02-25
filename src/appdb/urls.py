from django.urls import path

from .views import (
    ldapGroupEdit,
    ldapGroupList,
    ldapStaffUserEdit,
    ldapUserEdit,
    ldapUserList,
    ldapUserNew,
    staffLdapAccountLock,
    staffLdapCertDel,
    userSSHKeyAdd,
    userSSHKeyDel,
)

urlpatterns = [
    path("admin", ldapUserList, name="ldap-user-list"),
    path("admin/<pk>", ldapStaffUserEdit, name="ldap-staff-user-edit"),
    path("admin/clean/<pk>", staffLdapCertDel, name="ldap-sshkey-clear"),
    path("admin/create/<pk>", ldapUserNew, name="ldap-user-new"),
    path("admin/lock/<pk>", staffLdapAccountLock, name="ldap-user-lock"),
    path("", ldapUserEdit, name="ldap-user-edit"),
    path("sshkey/add", userSSHKeyAdd, name="ldap-sshkey-add"),
    path("sshkey/del", userSSHKeyDel, name="ldap-sshkey-del"),
    path("groups", ldapGroupList, name="ldap-group-list"),
    path("groups/<pk>", ldapGroupEdit, name="ldap-group-edit"),
]
