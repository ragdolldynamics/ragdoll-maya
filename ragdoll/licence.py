"""Ragdoll Licence API"""

import os
import sys
from maya import cmds
import logging
from . import constants

STATUS_OK = 0                   # All OK
STATUS_FAIL = 1                 # General error
STATUS_ACTIVATE = 3             # The product needs to be activated.
STATUS_ALREADY_ACTIVATED = 26   # No action needed
STATUS_INET = 4                 # Connection to the server failed.
STATUS_KEY_FOR_TURBOFLOAT = 20  # Used a floating key to activate node-locked
STATUS_INET_DELAYED = 21        # Waiting 5 hours to reconnect with server
STATUS_INUSE = 5                # Maximum number of activations reached
STATUS_FEATURES_CHANGED = 22    # Licence fields have changed
STATUS_TRIAL_EXPIRED = 30       # Trial expired
STATUS_NO_FREE_LEASES = 5       # Maximum number of leases reached

log = logging.getLogger("ragdoll")
self = sys.modules[__name__]
self._last_status = -1


def install(key=None):
    """Initialise licence mechanism

    This must be called prior to calling anything licence related.

    Arguments:
        key (str, optional): Automatically activate upon install

    """

    if os.getenv("RAGDOLL_FLOATING"):
        status = _install_floating()
    else:
        status = _install_nodelocked(key)

    self._last_status = status

    return status


def _parse_environment():
    floating = os.getenv("RAGDOLL_FLOATING")

    ip, port = (floating.rsplit(":") + ["13"])[:2]

    try:
        port = int(port)
    except ValueError:
        raise ValueError(
            "RAGDOLL_FLOATING misformatted '%s', should be <ip>:<port>, "
            "e.g. 127.0.0.1:13" % floating
        )

    return ip, port


def _install_floating():
    ip, port = _parse_environment()
    status = cmds.ragdollLicence(initFloating=True)

    if status == STATUS_OK:
        log.debug("Successfully leased a Ragdoll licence.")

    elif status == STATUS_INET:
        log.warning("Could not connect to licence server")

    else:
        log.error(
            "Failed to initialise floating licence, error code '%d'"
            % status
        )

    return status


def _install_nodelocked(key=None):
    status = cmds.ragdollLicence(init=True)

    if status in (STATUS_OK, STATUS_FEATURES_CHANGED):
        log.debug("Successfully initialised Ragdoll licence.")

        if key is not None and not cmds.ragdollLicence(isActivated=True):
            log.info("Automatically activating Ragdoll licence")
            return activate(key)

    elif status == STATUS_INET or status == STATUS_INET_DELAYED:
        log.warning(
            "Failed to connect to the internet for activation."
        )

    elif status == STATUS_ACTIVATE:
        log.warning(
            "Ragdoll is registered, but needs to reconnect with the\n"
            "licence server before continuing. Make sure your computer\n"
            "is connected to the internet, and try again."
        )

    elif status == STATUS_FAIL:
        log.warning(
            "Couldn't figure out licencing, "
            "this is a bug. Tell someone."
        )

    elif status == STATUS_TRIAL_EXPIRED:
        log.warning(
            "Ragdoll trial has expired, head into the chat and tell someone!"
        )

    else:
        log.error(
            "Unexpected error occurred with licencing, "
            "this is a bug. Tell someone."
        )

    return status


def current_key():
    """Return the currently activated key, if any"""
    return cmds.ragdollLicence(serial=True)


def request_lease(ip=None, port=None):
    """Request a licence from `ip` on `port`"""

    if not (ip and port):
        try:
            ip, port = constants.RAGDOLL_FLOATING.split(":")
            port = int(port)
        except Exception:
            raise ValueError(
                "Malformatted RAGDOLL_FLOATING environment variable: "
                % constants.RAGDOLL_FLOATING
            )

    status = cmds.ragdollLicence(requestLease=(ip, port))

    if status == STATUS_OK:
        log.debug("Successfully acquired a lease")

    elif status == STATUS_NO_FREE_LEASES:
        log.warning("All available licences are occupied")

    else:
        log.warning("Failed to acquire a lease")

    return status


def drop_lease():
    status = cmds.ragdollLicence(dropLease=True)

    if status == STATUS_OK:
        log.debug("Successfully dropped lease")

    else:
        log.warning("Failed to drop lease")

    return status


def activate(key):
    """Register your key with the Ragdoll licence server

    Provide your key here to win a prize, the prize of being
    able to use Ragdoll forever and ever!

    """

    status = cmds.ragdollLicence(activate=key)

    if status == STATUS_OK:
        log.info("Successfully activated your Ragdoll licence.")

    elif status == STATUS_FAIL:
        log.error("Failed to activate licence, check your product key.")

    elif status == STATUS_ALREADY_ACTIVATED:
        log.error(
            "Already activated. To activate with a new "
            "key, call deactivate() first."
        )

    elif status == STATUS_INET:
        log.error(
            "An internet connection is required to activate."
        )

    elif status == STATUS_KEY_FOR_TURBOFLOAT:
        log.error(
            "The key provided is meant for a floating licence server, "
            "this here is for node-locked activation only."
        )

    elif status == STATUS_INUSE:
        log.error(
            "Maximum number of activations used.\n"
            "Try deactivating any previously activated licence.\n"
            "If you can no longer access the previously activated "
            "licence, contact licencing@ragdolldynamics.com for "
            "manual activation.")

    else:
        log.error("Unknown error (%d) occurred, this is a bug." % status)

    return status


def deactivate():
    """Release currently activated key from this machine

    Moving to another machine? Call this to enable activation
    on another machine.

    """

    status = cmds.ragdollLicence(deactivate=True)

    if status == STATUS_OK:
        log.info("Successfully deactivated Ragdoll licence.")

    elif status == STATUS_TRIAL_EXPIRED:
        log.info("Successfully deactivated Ragdoll licence, "
                 "but your trial has expired.")

    else:
        log.error("Couldn't deactivate Ragdoll licence "
                  "(error code: %s)." % status)

    return status


def activation_request_to_file(key, fname):
    fname = fname.replace("\\", "/")  # Just in case
    status = cmds.ragdollLicence(activationRequestToFile=(key, fname))

    if status == STATUS_OK:
        log.info(
            "Successfully generated '%s'\n"
            "Send this file to licencing@ragdolldynamics.com"
            % fname
        )

    elif not os.path.exists(os.path.dirname(fname)):
        log.error("The directory at '%s' does not appear to exist" % fname)

    else:
        log.error(
            "There was a problem with '%s'! "
            "Send this error message (%s) "
            "and the steps you took to get here to "
            "licencing@ragdolldynamics.com." % (
                fname, status)
        )

    return status


def activate_from_file(fname):
    status = cmds.ragdollLicence(activateFromFile=fname)

    if status == STATUS_OK:
        log.info("Successfully activated Ragdoll!")

    elif not os.path.exists(fname):
        log.error("%s does not appear to exist!" % fname)

    else:
        log.error(
            "There was a problem with '%s'! It seems to exist, "
            "but may not be valid. Send us this error message (%s) "
            "and tell us the steps you took to get here." % (
                fname, status)
        )

    return status


def deactivation_request_to_file(fname):
    status = cmds.ragdollLicence(deactivationRequestToFile=fname)

    if status == STATUS_OK:
        log.info(
            "Successfully deactivated Ragdoll and generated %s\n"
            "Send this to licencing@ragdolldynamics.com" % fname
        )

    else:
        log.error(
            "There was a problem! Send us this error code "
            "(%s) and tell us what you did." % status
        )

    return status


def reverify():
    return cmds.ragdollLicence(reverify=True)


def data():
    """Return overall information about the current Ragdoll licence"""

    if self._last_status < 0:
        install()

    return dict(
        lastStatus=self._last_status,

        key=cmds.ragdollLicence(serial=True, query=True),

        # Which edition of Ragdoll is this?
        # trial, personal, complete, unlimited or batch
        product=cmds.ragdollLicence(product=True, query=True),

        # Node-locked or floating
        isFloating=cmds.ragdollLicence(isFloating=True, query=True),

        # Is a licence currently leased?
        hasLease=cmds.ragdollLicence(hasLease=True, query=True),

        # Is the current licence activated?
        isActivated=cmds.ragdollLicence(isActivated=True, query=True),

        # Is the current licence a trial licence?
        isTrial=cmds.ragdollLicence(isTrial=True, query=True),

        # Has the licence not been tampered with?
        isGenuine=cmds.ragdollLicence(isGenuine=True, query=True),

        # Has the licence been verified with the server
        # (requires a connection to the internet)?
        isVerified=cmds.ragdollLicence(isVerified=True, query=True),

        # How many days until this trial expires?
        trialDays=cmds.ragdollLicence(trialDays=True, query=True),

        # It's either a Trial or Personal licence
        isNonCommercial=cmds.ragdollLicence(isNonCommercial=True, query=True),

        # How many days until expiration
        expires=cmds.ragdollLicence(expires=True, query=True),
        expiryDays=cmds.ragdollLicence(expiryDays=True, query=True),
        expiry=cmds.ragdollLicence(expiry=True, query=True),

        # Date of Annual Upgrade Program end
        annualUpgradeProgram=cmds.ragdollLicence(
            annualUpgradeProgram=True, query=True),

        # Special flag for anyone having purchased Ragdoll prior to 2022.01.17
        isEarlyBird=cmds.ragdollLicence(isEarlyBird=True, query=True),
    )


def non_commercial():
    return cmds.ragdollLicence(isNonCommercial=True, query=True)


def commercial():
    return not non_commercial()


def early_bird():
    return cmds.ragdollLicence(isEarlyBird=True, query=True)
