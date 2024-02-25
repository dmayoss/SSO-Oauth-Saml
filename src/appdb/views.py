import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template import loader
from django_otp.decorators import otp_required

from sso.helper import (
    check_ldapuser_objectclasses,
    generate_sshkey_fingerprint,
    user_is_hr,
)
from users.models import CustomUser

from .forms import ldapShellForm, ldapSSHKeyForm, ldapTweakForm, ldapUserForm
from .models import LdapGroup, LdapUser


@user_passes_test(user_is_hr)
@otp_required
def ldapGroupList(request):
    groups = LdapGroup.objects.all()
    template = loader.get_template("appdb/list_groups.html")
    context = {
        "groups": groups,
    }
    return HttpResponse(template.render(context, request))


@user_passes_test(user_is_hr)
@otp_required
def ldapGroupEdit(request, pk):
    users = CustomUser.objects.all().exclude(is_superuser=True)
    # ldap cn = user.username, ldap uid (username) = whatever it gets set to

    ldapgroup = get_object_or_404(LdapGroup, name=pk)

    if request.method == "POST":
        form = ldapTweakForm(request.POST)
        if form.is_valid():
            form_action = form.cleaned_data["action"]
            form_user = form.cleaned_data["value"]

            try:
                if form_action == "add":
                    ldapgroup.members.append(form_user)
                    ldapgroup.save()
                    messages.success(
                        request,
                        "LDAP User '{}' added to group '{}'".format(
                            form_user, ldapgroup
                        ),
                    )
                elif form_action == "del":
                    del ldapgroup.members[ldapgroup.members.index(form_user)]
                    ldapgroup.save()
                    messages.success(
                        request,
                        "LDAP User '{}' removed from group '{}'".format(
                            form_user, ldapgroup
                        ),
                    )
                else:
                    messages.info(request, "No action taken.")
            except Exception as e:
                messages.error(request, "error saving LDAP Group: {}".format(e))

    template = loader.get_template("appdb/group.html")
    context = {
        "group": ldapgroup,
        "users": users,
    }
    return HttpResponse(template.render(context, request))


@user_passes_test(user_is_hr)
@otp_required
def ldapUserList(request):
    ssousers = CustomUser.objects.all().exclude(is_superuser=True)

    # user.username == ldapuser.cn
    ldaplist = LdapUser.objects.all().values_list("cn", flat=True)

    context = {
        "ssousers": ssousers,
        "ldaplist": ldaplist,
    }

    template = loader.get_template("appdb/list_users.html")
    return HttpResponse(template.render(context, request))


@user_passes_test(user_is_hr)
@otp_required
def ldapUserNew(request, pk):
    """
    All LDAP users (ldap CN) are created via their djangouser.username
    Their UID/GID is from their SSO db pk + offset
    - can't be changed

    Their unix username by default is ldapuser.username (ldap uid)
    Their Home is /home/{username} by default
    - can be changed
    """
    djangouser = get_object_or_404(CustomUser, pk=pk)
    offset = 40000

    ldapuser, created = LdapUser.objects.get_or_create(
        cn=djangouser.username,
        defaults={
            "username": djangouser.username,
            "uid": djangouser.pk + offset,
            "gid": djangouser.pk + offset,
            "firstname": djangouser.first_name,
            "lastname": djangouser.last_name,
            "shell": "/bin/sh",
            "homedir": "/home/{}".format(djangouser.username),
        },
    )
    if created:
        messages.success(request, "LDAP User cn='{}' created.".format(ldapuser.cn))
    else:
        messages.info(request, "LDAP User cn='{}' already exists.".format(ldapuser.cn))

    ldapuser, result = check_ldapuser_objectclasses(ldapuser)

    if result["error"]:
        messages.error(request, result["content"])
    else:
        if result["content"]:
            messages.info(request, result["content"])

    return redirect("ldap-user-list")


@user_passes_test(user_is_hr)
@otp_required
def ldapStaffUserEdit(request, pk):
    ldapuser = get_object_or_404(LdapUser, cn=pk)

    ldapuser, result = check_ldapuser_objectclasses(ldapuser)

    if result["error"]:
        messages.error(request, result["content"])
    else:
        if result["content"]:
            messages.info(request, result["content"])

    if request.method == "POST":
        form = ldapUserForm(request.POST)
        if form.is_valid():
            try:
                ldapuser.shell = form.cleaned_data["shell"]
                ldapuser.username = form.cleaned_data["username"]
                ldapuser.homedir = format(form.cleaned_data["homedir"])
                ldapuser.save()
            except Exception as e:
                messages.error(request, "{}".format(e))
            else:
                messages.success(request, "LDAP User '{}' Updated.".format(ldapuser))
    else:
        form = ldapUserForm(initial=model_to_dict(ldapuser))

    context = {
        "ldapuser": ldapuser,
        "form": form,
        "sshform": ldapSSHKeyForm(),
    }

    template = loader.get_template("appdb/staff_ldap_user.html")
    return HttpResponse(template.render(context, request))


@login_required()
@otp_required
def ldapUserEdit(request):
    ldapuser = get_object_or_404(LdapUser, cn=request.user.username)

    ldapuser, result = check_ldapuser_objectclasses(ldapuser)

    if result["error"]:
        messages.error(request, result["content"])
    else:
        if result["content"]:
            messages.info(request, result["content"])

    if request.method == "POST":
        form = ldapShellForm(request.POST)
        if form.is_valid():
            try:
                ldapuser.shell = form.cleaned_data["shell"]
                ldapuser.save()
            except Exception as e:
                messages.error(request, "{}".format(e))
            else:
                messages.success(request, "LDAP User '{}' Updated.".format(ldapuser))
    else:
        form = ldapShellForm()

    context = {
        "form": form,
        "sshform": ldapSSHKeyForm(),
    }

    return redirect("home")


@login_required()
@otp_required
def userSSHKeyAdd(request):
    ldapuser = get_object_or_404(LdapUser, cn=request.user.username)

    ldapuser, result = check_ldapuser_objectclasses(ldapuser)

    if result["error"]:
        messages.error(request, result["content"])
    else:
        if result["content"]:
            messages.info(request, result["content"])

    if request.method == "POST":
        form = ldapSSHKeyForm(request.POST)
        if form.is_valid():
            result = generate_sshkey_fingerprint(form.cleaned_data["sshkey"])
            if result["error"]:
                messages.error(request, result["error"])
            else:
                try:
                    if form.cleaned_data["sshkey"] not in ldapuser.sshkeys:
                        ldapuser.sshkeys.append(form.cleaned_data["sshkey"])
                        ldapuser.save()
                except Exception as e:
                    messages.error(request, "Error with SSH Key: {}".format(e))
                else:
                    messages.success(request, "new SSH Key added.")

    return redirect("ldap-user-edit")


@login_required()
@otp_required
def userSSHKeyDel(request):
    ldapuser = get_object_or_404(LdapUser, cn=request.user.username)

    ldapuser, result = check_ldapuser_objectclasses(ldapuser)

    if result["error"]:
        messages.error(request, result["content"])
    else:
        if result["content"]:
            messages.info(request, result["content"])

    if request.method == "POST":
        form = ldapSSHKeyForm(request.POST)
        if form.is_valid():
            try:
                ldapuser.sshkeys.remove(form.cleaned_data["sshkey"])
                ldapuser.save()
            except Exception as e:
                messages.error(request, "Error updating LDAP User: {}".format(e))
            else:
                messages.success(request, "LDAP User {} updated".format(ldapuser.cn))

    return redirect("ldap-user-edit")


@login_required
@otp_required
def staffLdapCertDel(request, pk):
    if not user_is_hr(request.user):
        raise PermissionError("ENORIGHTS")

    try:
        ldapuser = LdapUser.objects.get(cn=pk)
        ldapuser.sshkeys.clear()
        ldapuser.save()
    except Exception as e:
        messages.error(request, "Error clearing LDAP SSH Keys: {}".format(e))
    else:
        messages.success(request, "cleared all SSH keys for LDAP user {}".format(pk))

    return redirect("staff-user-list")


@login_required
@otp_required
def staffLdapAccountLock(request, pk):
    if not user_is_hr(request.user):
        raise PermissionError("ENORIGHTS")

    try:
        ldapuser = LdapUser.objects.get(cn=pk)

        if ldapuser.lockedTime:
            ldapuser.lockedTime = None
        else:
            ldapuser.lockedTime = "000001010000Z"

        ldapuser.save()
    except Exception as e:
        messages.error(request, "Error locking LDAP Account: {}".format(e))
    else:
        messages.success(request, "Toggled LDAP Account lock for {}".format(pk))

    return redirect("staff-user-list")


'''
# disabled for now, will likely remove --> checkPassword in dovecot is obsolete

@csrf_exempt
def dovecotAuth(request):
    """
    csrf exempt because we won't have one, protecting with token shenanigans
    fetch body of POST

    expect JSON that looks like:    
        {
        "username": "username",
        "password": "password",
        "token": "token",
        }
    
    returns:
        { "authenticated": True/False }
    """

    # here's where I can verify a token via e.g. hashing a date+salt
    # or just loading a token from the DB
    def check_token(token):
        return (token == "magicstringhere")

    # not sure this is any easier than just returning this, but still
    auth_failed = {"authenticated": False}
    auth_succeeded = {"authenticated": True}

    # we only do POST
    if request.method == 'POST':
        auth_attempt = json.loads(request.body)  # json
        
        # basically I want to do tokenauth for the url, without a user attached
        # silently (nicely) fail if we don't get all three
        try:
            token = auth_attempt["token"]
            username = auth_attempt["username"]
            password = auth_attempt["password"]
        except Exception as e:
            return JsonResponse({"authenticated": False, 'error get token/pass/user': str(e)})

        if not check_token(token):
            return JsonResponse({"authenticated": False, 'error check token': "no token"})

        # could use auth_attempt.get("username", None)
        if (username == None) or (password == None):
            return JsonResponse({"authenticated": False, 'error': "no user/pass"})

        # first, if our prospective user is not active, fail at first hurdle
        try:
            user = CustomUser.objects.get(email=username)
        except Exception as e:
            return JsonResponse({"authenticated": False, 'error get user': str(e)})

        if not user.is_active:
            return JsonResponse({"authenticated": False, 'error': "user not active"})
        
        # thirdly, if there's a matching hash in app_list, great
        result = app_check_pass(password, user.apppasswords_set.all())

        if result == True:
            return JsonResponse({"authenticated": True})
        else:
            return JsonResponse({"authenticated": False, "reason": "no results matched"})
'''
