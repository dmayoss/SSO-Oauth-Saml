from django import template
from django.template.defaultfilters import stringfilter

from sso.helper import generate_sshkey_fingerprint

register = template.Library()


@register.filter()
@stringfilter
def sshkey_fingerprint(sshkey):
    """
    This will:
    - strip unwanted spaces
    - split on space inside the string, e.g. "ssh-rsa [key] comment"
    - hash the key
    - prettify the fingerprint into xx:xx:xx format
    """

    result = generate_sshkey_fingerprint(sshkey)

    if result["error"]:
        return result["error"]
    else:
        return "{} {} {}".format(
            result["keytype"], result["keyfp"], result["keycomment"]
        )
