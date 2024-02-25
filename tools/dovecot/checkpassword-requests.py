#!/usr/bin/env python3
#
# for SSO / Django, requires support in userdb SSO
#
# based on https://github.com/ser/checkpassword-phpbb
# for phpBB 3.1 by Serge Victor
#
# the easiest way for debugging in a command line:
#
# uses requests to ask django because why wouldn't it
# sso_url below should respond with a json containing at least '{ "authenticated": True/False }'

import os
import sys
import traceback
import requests

# These values currently fit the vexim DB's values
config = {
    "email_domain": "email.com",
    "exim_path": "/usr/local/mail",  # check these, e.g. home in vexim DB /usr/local/mail/email.com/firstname.lastname
    "sso_url": "https://sso.email.com/app/special",  # see appdb.urls
    "token": "magictokenhere",  # must match what url above is expecting
    "userdb_uid": "90",  # matches vexim values
    "userdb_gid": "90",  # matches vexim values
}


def verifypass(username, password):
    '''
    uses requests to POST JSON payload
    expects a simple {"authenticated": True/False}
    '''
    payload = {
        "username": username,
        "password": password,
        "token": config["token"],
    }

    r = requests.post('{}'.format(config["sso_url"]), json=payload)
    auth = r.json()

    try:
        result = auth['authenticated']
    except Exception as e:
        result = False

    return result


def main():
    scriptname = os.path.basename(sys.argv[0])
    
    with os.fdopen(3) as infile:
        data = infile.read(512).split('\0')
    
    username, password = data[:2]
    justuser = username.split("@")[0]
    
    try:
        domain = username.split("@")[1]
    except:
        domain = config["email_domain"]

    if verifypass(justuser, password) == False:
       return 1  # password does not match, user cannot be authenticated
    else:
       os.environ['USER'] = "%s@%s" % (justuser, domain)
       os.environ['HOME'] = "%s/%s/%s" % (config["exim_path"], config['email_domain'], justuser)  # Maildir is e.g. /usr/local/mail/email.com/firstname.lastname/Maildir
       os.environ['userdb_uid'] = config["userdb_uid"]
       os.environ['userdb_gid'] = config["userdb_gid"]

       # check if these are set for e.g. all domains in conf.d/auth-sql.conf.ext
       # os.environ['userdb_mail'] = "maildir:~/Maildir:INBOX=~/Maildir/.INBOX:INDEX=/usr/local/mail/email.com/indexes/%d/%n:CONTROL=/usr/local/mail/email.com/control/%d/%n" # adapt it to your needs
       os.environ['userdb_quota_rule'] = "*:storage=0"

       os.environ['INSECURE_SETUID'] = "1"
       os.environ['EXTRA'] = 'userdb_uid userdb_gid'
    os.execvp(sys.argv[1], sys.argv[1:])

try:
    sys.exit(main() or 111)
except KeyboardInterrupt:
    sys.exit(2)
except Exception:
    traceback.print_exc(file=sys.stderr)
    sys.exit(111)
