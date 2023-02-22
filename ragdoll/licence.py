"""Ragdoll Licence API"""

import os
import sys
from maya import cmds
import logging
from . import constants

# Common code
STATUS_OK = 0                       # All OK
STATUS_FAIL = 1                     # General error
STATUS_INET = 4                     # Connection to the server failed
STATUS_COM = 11                     # Bad COM. Windows only error
STATUS_NETWORK_ADAPTERS = 28        # Some network adapters are disabled
STATUS_INET_TLS = 36                # Failed to connect due to TLS or cert err

# Node-Locked specific code
STATUS_PKEY = 2                     # Invalid product key
STATUS_ACTIVATE = 3                 # The product needs to be activated.
STATUS_INUSE = 5                    # Maximum number of activations reached
STATUS_REVOKED = 6                  # The product key has been revoked
STATUS_EXPIRED = 13                 # Activation expired
STATUS_IN_VM = 17                   # Activating within a VM
STATUS_KEY_FOR_TURBOFLOAT = 20      # Activating node-locked with floating key
STATUS_INET_DELAYED = 21            # Waiting 5 hours to reconnect with server
STATUS_FEATURES_CHANGED = 22        # Licence fields have changed
STATUS_NO_MORE_DEACTIVATIONS = 24   # Limited deactivation count reached
STATUS_ACCOUNT_CANCELED = 25        # The end of the world
STATUS_ALREADY_ACTIVATED = 26       # No action needed
STATUS_TRIAL_EXPIRED = 30           # Trial expired
STATUS_INET_TIMEOUT = 35            # Server connection timeout

# Floating specific code
STATUS_F_SERVER = 2                 # No server specified
STATUS_F_NO_FREE_LEASES = 5         # Maximum number of leases reached
STATUS_F_ALREADY_LEASED = 6         # Lease already attained
STATUS_F_WRONG_TIME = 7             # System time has 5+ min diff from server
STATUS_F_NO_LEASE = 10              # No lease to drop
STATUS_F_WRONG_SERVER_PRODUCT = 15  # Wrong server to request lease from
STATUS_F_INET_TIMEOUT = 16          # Server connection timeout
STATUS_F_USERNAME_NOT_ALLOWED = 18  # This user is not in server whitelist


log = logging.getLogger("ragdoll")
self = sys.modules[__name__]
self._last_status = -1
self._installed = False


def install(key=None):
    """Initialise licence mechanism

    This must be called prior to calling anything licence related.

    Arguments:
        key (str, optional): Automatically activate upon install

    """

    if self._installed:
        return log.debug("Licence already installed")

    if os.getenv("RAGDOLL_FLOATING"):
        status = _install_floating()
    else:
        status = _install_nodelocked(key)

    self._last_status = status
    self._installed = True

    return status


def uninstall():
    if not self._installed:
        return log.debug("Licence not yet installed")

    self._installed = False


def _parse_ip_port(server):
    ip, port = (server.rsplit(":") + ["13"])[:2]

    try:
        port = int(port)
    except ValueError:
        raise ValueError(
            "RAGDOLL_FLOATING misformatted '%s', should be <ip>:<port>, "
            "e.g. 127.0.0.1:13" % server
        )

    return ip, port


def _parse_server_from_environment():
    floating = os.getenv("RAGDOLL_FLOATING", "")
    ip, port = _parse_ip_port(floating)

    constants.RAGDOLL_FLOATING = floating  # update constant
    return ip, port


def _parse_server_from_constant():
    floating = constants.RAGDOLL_FLOATING or ""
    ip, port = _parse_ip_port(floating)

    return ip, port


def _install_floating():
    ip, port = _parse_server_from_environment()
    status = cmds.ragdollLicence(initFloating=True)

    if status == STATUS_OK:
        log.debug("Successfully leased a Ragdoll licence.")

    else:
        _prompt_error(
            "Failed to initialise floating licence",
            status_code_explained(status).format(server="%s:%d" % (ip, port))
        )

    return status


def _install_nodelocked(key=None):
    status = cmds.ragdollLicence(init=True)

    if status in (STATUS_OK, STATUS_FEATURES_CHANGED):
        log.debug("Successfully initialised Ragdoll licence.")

        if key is not None and not cmds.ragdollLicence(isActivated=True):
            log.info("Automatically activating Ragdoll licence")
            return activate(key)

    else:
        _prompt_error(
            "Failed to initialise node-locked licence",
            status_code_explained(status)
        )

    return status


def current_key():
    """Return the currently activated key, if any"""
    return cmds.ragdollLicence(serial=True)


def _is_interactive():
    is_standalone = not hasattr(cmds, "about") or cmds.about(batch=True)
    return not is_standalone


def _get_welcome_window(ensure_shown=False):
    from . import widgets, ui, interactive

    if _is_interactive() and not os.getenv("RAGDOLL_LEGACY_GREETS"):
        ref = widgets.WelcomeWindow.instance_weak
        if ref and ui.isValid(ref()):
            welcome_window = ref()
            if welcome_window.isVisible():
                return welcome_window

        if ensure_shown:
            return interactive.welcome_user()


def _prompt_error(context, message, ensure_welcome=False):
    title = message.split("\n")[0]
    message = "  " + "\n  ".join(message.split("\n")[1:])

    log.warning("\nRagdoll Licence Error: " + title)
    log.warning(message + "\n")
    log.warning(
        "If you have trouble resolving this, please contact us at:\n"
        "licencing@ragdolldynamics.com\n"
        "Please include any error messages and with\n"
        "any steps required to reproduce the error.\n"
    )
    # The last single line error to display in Maya Command Line
    log.error("%s. Please see Script Editor." % context)

    if not _is_interactive():
        return

    welcome_window = _get_welcome_window(ensure_shown=ensure_welcome)
    if welcome_window:
        welcome_window.notify("Error",
                              title + ". See Script Editor.",
                              location="LicencePlate",
                              persistent=True)


def check_init_status():
    trial_err = cmds.ragdollLicence(trialError=True, query=True)
    init_err = cmds.ragdollLicence(initError=True, query=True)

    if trial_err != STATUS_OK:

        if trial_err == STATUS_INET:
            _prompt_error(
                "Requires internet to start trial",
                "Failed to connect to the Ragdoll server over internet for "
                "trial activation.",
                ensure_welcome=True
            )
        else:
            _prompt_error(
                "Failed to start trial",
                status_code_explained(trial_err),
                ensure_welcome=True
            )

    elif init_err != STATUS_OK:
        _prompt_error(
            "Licence failed to initialise",
            status_code_explained(init_err),
            ensure_welcome=True
        )


def status_callback(action, status, server, fname):
    if _is_interactive():
        welcome_window = _get_welcome_window()
        if welcome_window:
            from . import ui
            ui.Notification.clear_instance()
            welcome_window.show()  # trigger licence data update

    if action == "requestLease":
        if status == STATUS_OK:
            if cmds.ragdollLicence(hasLease=True):
                log.info("Successfully acquired a lease")
            else:
                _prompt_error(
                    "Failed to acquire a lease",
                    status_code_explained(STATUS_EXPIRED).format(server=server)
                )
        else:
            _prompt_error(
                "Failed to acquire a lease",
                status_code_explained(status).format(server=server)
            )

    elif action == "dropLease":
        if status == STATUS_OK:
            log.info("Successfully dropped lease")
        else:
            _prompt_error(
                "Failed to drop a lease",
                status_code_explained(status)
            )

    elif action == "activate":
        if status == STATUS_OK:
            log.info("Successfully activated your Ragdoll licence.")

        elif status == STATUS_INET:
            log.info("No internet, use offline activation.")

        else:
            _prompt_error(
                "Failed to activate licence, please check product key",
                status_code_explained(status)
            )

    elif action == "activateFromFile":
        if status == STATUS_OK:
            log.info("Successfully activated Ragdoll!")

        elif not os.path.exists(fname):
            message = (
                "Activation file not exist\n"

                "Activation file does not exists, please check if you have "
                "right permission to save file in that location.\n"
                "Activation file path: %s" % fname
            )
            _prompt_error(
                "Failed to activate from file",
                message
            )

        elif status == STATUS_FAIL:
            message = (
                "There was a problem with activation file\n"

                "Please make sure that you have got activation "
                "respond code right and try again.\n"
                "Activation file path: %s" % fname
            )
            _prompt_error(
                "Failed to activate from file",
                message
            )

        else:
            _prompt_error(
                "Failed to activate from file",
                "%s\nActivation file path: %s" % (
                    status_code_explained(status), fname
                )
            )

    elif action == "activationRequestToFile":
        if status == STATUS_OK:
            log.info("Successfully generated '%s'\n" % fname)

        elif not os.path.exists(os.path.dirname(fname)):
            message = (
                "Failed to save activation request to file\n"

                "The directory at '%s' does not appear to exist.\n"
                "Request file path: %s" % (os.path.dirname(fname), fname)
            )
            _prompt_error(
                "Failed to save activation request",
                message
            )

        else:
            _prompt_error(
                "Failed to create activation request file",
                "%s\nRequest file path: %s" % (
                    status_code_explained(status), fname
                )
            )

    elif action == "deactivationRequestToFile":
        if status == STATUS_OK:
            log.info(
                "Successfully deactivated Ragdoll and generated %s" % fname
            )

        else:
            _prompt_error(
                "Failed to create deactivation request file",
                "%s\nRequest file path: %s" % (
                    status_code_explained(status), fname
                )
            )

    elif action == "deactivate":
        if status == STATUS_OK:
            log.info("Successfully deactivated Ragdoll licence.")

        elif status == STATUS_INET:
            log.info("No internet, use offline deactivation.")

        elif status == STATUS_TRIAL_EXPIRED:
            log.warning("Successfully deactivated Ragdoll licence, "
                        "but your trial has expired.")
        else:
            _prompt_error(
                "Failed to deactivate licence",
                status_code_explained(status)
            )

    elif action == "extendTrial":
        if status == STATUS_OK:
            log.info("Successfully extended Ragdoll trial.")
        else:
            _prompt_error(
                "Failed to extended trial",
                status_code_explained(status)
            )


def request_lease(ip=None, port=None):
    """Request a licence from `ip` on `port`"""
    if not self._installed:
        # Lease is automatically attained during install
        return self.install()

    if not (ip and port):
        ip, port = _parse_server_from_constant()

    status = cmds.ragdollLicence(requestLease=(ip, port))
    return status


def drop_lease():
    """Drop current leased licence"""
    status = cmds.ragdollLicence(dropLease=True)
    return status


def activate(key):
    """Register your key with the Ragdoll licence server

    Provide your key here to win a prize, the prize of being
    able to use Ragdoll forever and ever!

    """
    status = cmds.ragdollLicence(activate=key)
    return status


def deactivate():
    """Release currently activated key from this machine

    Moving to another machine? Call this to enable activation
    on another machine.

    """
    status = cmds.ragdollLicence(deactivate=True)
    return status


def activation_request_to_file(key, fname):
    fname = fname.replace("\\", "/")  # Just in case
    status = cmds.ragdollLicence(activationRequestToFile=(key, fname))
    return status


def activate_from_file(fname):
    status = cmds.ragdollLicence(activateFromFile=fname)
    return status


def deactivation_request_to_file(fname):
    status = cmds.ragdollLicence(deactivationRequestToFile=fname)
    return status


def reverify():
    return cmds.ragdollLicence(reverify=True)


def data():
    """Return overall information about the current Ragdoll licence"""

    if not self._installed:
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

        # Trial activation error, if any
        trialError=cmds.ragdollLicence(trialError=True, query=True),

        # Licence init error, if any
        initError=cmds.ragdollLicence(initError=True, query=True),

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


def status_code_explained(status):
    """Translate licencing error code into English

    Note: First line of message will be used as dialog title in GUI.

    """

    floating = cmds.ragdollLicence(isFloating=True, query=True)

    ok = status == STATUS_OK or (
        not floating and status == STATUS_FEATURES_CHANGED
    )

    if ok:
        # Not an error
        return

    elif status == STATUS_COM:
        message = """\
Windows COM setup problem"

The hardware id couldn't be generated due to an error in the COM setup
Re-enable Windows Management Instrumentation (WMI) in your group
policy editor or reset the local group policy to the default values
Please contact your system admin for more information
"""

    elif status == STATUS_NETWORK_ADAPTERS:
        message = """\
Disabled network adapters

There are network adapters on the system that are disabled and
TurboActivate couldn't read their hardware properties (even after trying
and failing to enable the adapters automatically). Enable the network adapters,
re-run the function, and TurboActivate will be able to "remember" the adapters
even if the adapters are disabled in the future.

Note: The network adapters do not need an active Internet connections.
      They just need to not be disabled. Whether they are or are not
      connected to the internet/intranet is not important and does not
      affect this error code at all.
"""
        # See: https://wyday.com/limelm/help/faq/#disabled-adapters

    elif status == STATUS_INET_TLS:
        message = (
            "Cannot establish secure connection\n"

            "The secure connection to the activation servers failed due to "
            "a TLS or certificate error."
        )
        # More information here:
        # https://wyday.com/limelm/help/faq/#internet-error

    else:

        if floating:
            message = _status_code_floating(status)
        else:
            message = _status_code_nodelocked(status)

    # Untranslated code
    if not message:
        message = "Uninterpreted error code (%d), please contact us." % status

    return message


def _status_code_nodelocked(status):
    message = ""

    if status == STATUS_PKEY:
        message = "Invalid product key."

    elif status == STATUS_ACTIVATE:
        message = (
            "Require internet connection\n"

            "Ragdoll is registered, but needs to reconnect with the "
            "licence server before continuing.\n"
            "Make sure your computer is connected to the internet, "
            "and try again."
        )

    elif status == STATUS_INUSE:
        message = (
            "Maximum number of activations used\n"

            "Try deactivating any previously activated licence.\n"
            "If you can no longer access the previously activated "
            "licence, contact licencing@ragdolldynamics.com for "
            "manual activation."
        )

    elif status == STATUS_REVOKED:
        message = (
            "Product key revoked\n"

            "The product key has been revoked and cannot be used."
        )

    elif status == STATUS_EXPIRED:
        message = (
            "Licence expired\n"

            "The activation has expired or, the computer time and/or "
            "date/timezone is incorrect.\n"
            "If this should not happen, "
            "please make sure the current time is correct as Ragdoll uses "
            "this to validate your licence.\n"
            "You may need to reboot your computer after date/timezone has "
            "corrected."
        )

    elif status == STATUS_IN_VM:
        message = """\
Running in a virtual machine

Ragdoll believes your machine is a 'virtual machine' which
is not supported by your serial number.

If you believe this is a mistake, please reach out to us
at licencing@ragdolldynamics.com
"""

    elif status == STATUS_KEY_FOR_TURBOFLOAT:
        message = (
            "Not a node-locked product key\n"

            "The key provided is meant for a floating licence server, "
            "this here is for node-locked activation only."
        )

    elif status == STATUS_NO_MORE_DEACTIVATIONS:
        message = (
            "Deactivation limit reached\n"

            "This product key had a limited number of allowed deactivations, "
            "and the limitation has reached.\n"
            "This product is still activated on this computer."
        )

    elif status == STATUS_ACCOUNT_CANCELED:
        message = (
            "The end of the world\n"

            "Can't activate or start a verified trial because, something "
            "really bad happened."
        )

    elif status == STATUS_ALREADY_ACTIVATED:
        message = (
            "Already activated\n"

            "To activate with a new key, call deactivate() first."
        )

    elif status == STATUS_TRIAL_EXPIRED:
        message = (
            "Trial expired\n"

            "Ragdoll trial has expired, head into the chat and tell "
            "someone!"
        )

    elif status == STATUS_INET:
        message = (
            "No internet for activation\n"

            "Failed to connect to the Ragdoll server over internet for "
            "activation."
        )

    elif status == STATUS_INET_DELAYED:
        message = (
            "Licence verification pending\n"

            "Previously was not able to connect to the internet for "
            "activation, will recheck within 5 hours."
        )

    elif status == STATUS_INET_TIMEOUT:
        message = (
            "Server connection timeout\n"

            "The connection to the server timed out because a long period "
            "of time elapsed since the last data was sent or received."
        )

    else:
        message = "Unknown status code: %s" % str(status)

    return message


def _status_code_floating(status):
    message = ""

    if status == STATUS_F_SERVER:
        message = (
            "No server specified\n"

            "There's no floating server specified."
        )

    elif status == STATUS_F_NO_FREE_LEASES:
        message = (
            "No more licence\n"

            "All available licences are occupied.\n"
            "Connecting server: {server}"
        )

    elif status == STATUS_F_ALREADY_LEASED:
        message = (
            "Already leased\n"

            "You already have a licence leased from server.\n"
            "Connecting server: {server}"
        )

    elif status == STATUS_F_WRONG_TIME:
        message = (
            "System datetime/timezone mismatched.\n"

            "This computer's system time is more than 5 minutes "
            "(before/after) different from the floating server system time.\n"
            "Please make sure the Date, Time, and Timezone are all set "
            "correctly on this computer and the server.\n"
            "Connecting server: {server}"
        )

    elif status == STATUS_F_NO_LEASE:
        message = (
            "No lease to drop\n"

            "There's no lease to drop."
        )

    elif status == STATUS_F_WRONG_SERVER_PRODUCT:
        message = (
            "Wrong server product\n"

            "The floating server you have connected cannot give licence "
            "leases for this product version.\n"
            "Connecting server: {server}"
        )

    elif status == STATUS_INET:
        message = (
            "Server not connected\n"

            "Failed to connect to floating licence server\n"
            "Connecting server: {server}"
        )

    elif status == STATUS_F_INET_TIMEOUT:
        message = (
            "Server connection timeout\n"

            "The connection to the server timed out because a long period of "
            "time elapsed since the last data was sent or received.\n"
            "Connecting server: {server}"
        )

    elif status == STATUS_F_USERNAME_NOT_ALLOWED:
        message = (
            "Username blocked\n"

            "You were not able to request a license lease from the server "
            "because your username has not been added to the whitelist of "
            "approved usernames.\n"
            "Connecting server: {server}"
        )

    elif status == STATUS_EXPIRED:
        message = (
            "Licence expired\n"

            "The floating server's activation has expired or, the server "
            "system time and/or date/timezone is incorrect.\n"
            "Please contact your floating server admin."
        )

    return message
