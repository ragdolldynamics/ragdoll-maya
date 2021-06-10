import os
import json
import copy
import logging
import datetime
from maya import cmds

from . import __

log = logging.getLogger(__name__)


def _gather_ragdoll():
    data = cmds.ragdollReport(gather=True)
    data = json.loads(data)

    __.telemetry_data["maya"].update(data.get("maya", {}))
    __.telemetry_data["ragdoll"].update(data.get("ragdoll", {}))

    return __.telemetry_data


def _gather_system():
    import sys
    import platform

    device = dict()

    try:
        info = cmds.ogs(deviceInformation=True)

    except AttributeError:
        # Must be running in standalone, prior to standalone.initialize()
        pass

    else:
        try:
            for pair in info:
                key, value = pair.split(":", 1)
                device[key.strip().lower()] = value.strip().rstrip("\n.")
        except Exception:
            pass

    __.telemetry_data["system"].update({
        "time": datetime.datetime.now().strftime(
            "%d-%m-%Y, %H:%M:%S"
        ),

        # E.g. win32
        "os": sys.platform,

        # E.g. AMD64
        "machine": platform.machine(),

        # E.g. AMD64 Family 23 Model 49 Stepping 0, AuthenticAMD
        "processor": platform.processor(),

        # E.g. Geforce RTX 3090/PCIe/SSE2
        "gpu": device.get("adapter", "unknown"),

        "memory_cpu": device.get("cpu memory limit", -1.0),
        "memory_gpu": device.get("gpu memory limit", -1.0),

        # E.g. OpenGL 4.1
        "render_api": device.get("api", "unknown"),
    })


def gather():
    _gather_ragdoll()
    _gather_system()

    return copy.deepcopy(__.telemetry_data)


def save():
    """Write telemetry to ~/.ragdoll/telemetry_<date>.json"""
    date = datetime.datetime.now().strftime("%d-%m-%Y-%H%M%S")
    fname = os.path.expanduser("~/.ragdoll")
    fname = os.path.join(fname, "telemetry_%s.json" % date)

    with open(fname, "w") as f:
        json.dump(__.telemetry_data, f)

    log.debug("Successfully wrote telemetry to %s" % fname)


def upload():
    """Send anonymous telemetry to Ragdoll's server"""
    dump = json.dumps(__.telemetry_data)
    cmds.ragdollReport(json=dump)
