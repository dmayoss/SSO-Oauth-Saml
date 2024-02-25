import ldapdb.models
from ldapdb.models.fields import CharField, IntegerField, ListField

from sso.secrets import LDAP_GROUPS_BASE, LDAP_USERS_BASE


def getLdapGroupMembership(ldapuser):
    groups = LdapGroup.objects.filter(members=ldapuser)
    return groups


def getLdapUserInfo(ldapuser):
    try:
        userinfo = LdapUser.objects.get(cn=ldapuser)
    except:
        return None
    else:
        return userinfo


class LdapGroup(ldapdb.models.Model):
    """
    Class for representing an LDAP group entry.
    """

    # LDAP meta-data
    base_dn = LDAP_GROUPS_BASE

    # need posixGroup for the gid/name field
    object_classes = [
        "posixGroup",
    ]

    gid = IntegerField(db_column="gidNumber", unique=True)
    name = CharField(db_column="cn", max_length=64, primary_key=True)
    members = ListField(db_column="memberUid")

    # stops migrations (and tables) being created, otherwise multiple primary_key
    class Meta:
        abstract = False
        managed = False

    def __str__(self):
        return "{} | {}".format(self.name, self.gid)


class LdapUser(ldapdb.models.Model):
    """
    Class for shadowing User (CustomUser) objects
    """

    base_dn = LDAP_USERS_BASE

    object_classes = ["inetOrgPerson", "posixAccount", "ldapPublicKey"]

    cn = CharField(db_column="cn", max_length=256, primary_key=True)
    username = CharField(db_column="uid", max_length=64)
    uid = IntegerField(db_column="uidNumber")
    gid = IntegerField(db_column="gidNumber")
    firstname = CharField(
        db_column="givenName", max_length=64, null=False, blank=True, default=""
    )
    lastname = CharField(
        db_column="sn", max_length=64, null=False, blank=True, default=""
    )
    homedir = CharField(
        db_column="homeDirectory", max_length=64, null=False, blank=True, default=""
    )
    shell = CharField(
        db_column="loginShell", max_length=64, null=False, blank=True, default=""
    )

    # do not touch in admin
    sshkeys = ListField(db_column="sshPublicKey")
    objectclass = ListField(db_column="objectClass")

    # shouldn't need this, we use ssh keys
    # unixpass = CharField(db_column='userPassword', max_length=256, blank=True, null=False)
    # Do need this one to lock accounts via policy overlay. set to '000001010000Z' to disable
    lockedTime = CharField(db_column="pwdAccountLockedTime", null=True)

    @property
    def ldapgroups(self):
        return getLdapGroupMembership(self.cn)

    # stops migrations (and tables) being created, otherwise multiple primary_key
    class Meta:
        abstract = False
        managed = False

    def __str__(self):
        return "{}".format(self.cn)
