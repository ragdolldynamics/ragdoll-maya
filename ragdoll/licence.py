"""Ragdoll Licence API"""

import logging

STATUS_OK = 0                  # All OK
STATUS_FAIL = 1                # General error
STATUS_ACTIVATE = 3            # The product needs to be activated.
STATUS_ALREADY_ACTIVATED = 26  # No action needed
STATUS_INET = 4                # Connection to the server failed.
STATUS_INET_DELAYED = 21       # Waiting 5 hours to reconnect with server
STATUS_INUSE = 5               # Maximum number of activations reached

log = logging.getLogger("ragdoll")
binding = None


def install(key=None):
    """Initialise licence mechanism

    This must be called prior to calling anything licence related.

    Arguments:
        key (str, optional): Automatically activate upon install

    """

    # Binding is special. It has initialisation code
    # that cannot be executed until *after* the Maya plug-in
    # has been loaded. Hence we cannot import it at module-level
    # without limiting when and where `licence.py` can be imported
    global binding
    from . import binding

    status = binding.init_licence()

    if status == STATUS_OK:
        log.debug("Successfully initialised Ragdoll licence.")

    elif status == STATUS_INET or status == STATUS_INET_DELAYED:
        log.warning(
            "Ragdoll is activated, but failed to verify the activation\n"
            "with the licence servers. You can still use the app for the\n"
            "duration of the grace period."
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

    else:
        log.error(
            "Unexpected error occurred with licencing, "
            "this is a bug. Tell someone."
        )

    if key is not None and not binding.is_licence_activated():
        log.info("Automatically activating Ragdoll licence")
        return activate(key)

    return status


def current_key():
    """Return the currently activated key, if any"""
    return binding.licence_key()


def activate(key):
    """Register your key with the Ragdoll licence server

    Provide your key here to win a prize, the prize of being
    able to use Ragdoll forever and ever!

    """

    status = binding.activate_licence(key)

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

    status = binding.deactivate_licence()

    if status == STATUS_OK:
        log.info("Successfully deactivated Ragdoll licence")
    else:
        log.error("Couldn't deactivate Ragdoll licence.")

    return status


def reverify():
    return binding.reverify_licence()


def data():
    """Return overall information about the current Ragdoll licence"""
    return dict(
        key=binding.licence_key(),

        # Which edition of Ragdoll is this?
        # Standard or Enterprise
        edition="Enterprise",

        # Node-locked or floating
        floating=False,

        # Is the current licence activated?
        isActivated=binding.is_licence_activated(),

        # Is the current licence a trial licence?
        isTrial=binding.is_licence_trial(),

        # Has the licence not been tampered with?
        isGenuine=binding.is_licence_genuine(),

        # Has the licence been verified with the server
        # (requires a connection to the internet)?
        isVerified=binding.is_licence_verified(),

        # How many days until this trial expires?
        trialDays=binding.licence_trial_days(),

        # How many magic days are left?
        magicDays=binding.licence_magic_days(),
    )
