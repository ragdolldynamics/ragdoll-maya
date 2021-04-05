"""Internal functions, don't look"""

import re
import time
import logging
import functools

from maya import cmds
from .vendor import cmdx

log = logging.getLogger("ragdoll")

# Python 2 backwards compatibility
string_types = cmdx.string_types
long = cmdx.long


def with_timing(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        t0 = time.time()

        try:
            return func(*args, **kwargs)
        finally:
            t1 = time.time()
            duration = t1 - t0
            log.info("%s in %.2fms" % (func.__name__, duration * 1000))

    return wrapper


def with_undo_chunk(func):
    """Consider the entire function one big giant undo chunk"""
    @functools.wraps(func)
    def _undo_chunk(*args, **kwargs):
        try:
            cmds.undoInfo(chunkName=func.__name__, openChunk=True)
            return func(*args, **kwargs)
        finally:
            cmds.undoInfo(chunkName=func.__name__, closeChunk=True)

    return _undo_chunk


def shape_name(transform_name):
    """Generate a suitable shape name from `transform_name`

    If a shape node has the name <transform>Shape<number>
    then Maya will keep that name updated as the transform
    name changes.

    """

    components = re.split(r"(\d+)$", transform_name, 1) + [""]
    return "Shape".join(components[:2])


class UserAttributes(object):
    """User attributes appear on the original controllers
     __________________
    |                  |
    |      leftArm_ctl |
    |                  |
    | Translate X  0.0 |
    | Translate Y  0.0 |
    | Translate Z  0.0 |
    |    Rotate X  0.0 |
    |    Rotate Y  0.0 |
    |    Rotate Z  0.0 |
    |                  |
    |          Ragdoll |
    |        Mass  0.0 |  <----- User Attributes
    |    Strength  0.0 |
    |__________________|

    Arguments:
        source (cmdx.DagNode): Original node, e.g. an rdRigid
        target (cmdx.DagNode): Typically the animation control

    """

    def __init__(self, source, target):
        self._source = source
        self._target = target
        self._added = []

    def do_it(self):
        if not self._added:
            pass

        added = []

        while self._added:
            attr = self._added.pop(0)

            if isinstance(attr, cmdx._AbstractAttribute):
                name = attr["name"]

                if self._target.has_attr(name):
                    continue

                with cmdx.DagModifier() as mod:
                    mod.add_attr(self._target, attr)

                plug = self._target[name]

            else:
                attr, long_name, nice_name = attr
                name = long_name or attr

                if self._target.has_attr(name):
                    continue

                plug = self.semi_proxy(attr, long_name, nice_name)

            added += [plug]

        with cmdx.DagModifier() as mod:
            for new_plug in added:
                index = self._source["userAttributes"].next_available_index()
                mod.connect(new_plug, self._source["userAttributes"][index])

                # Can't figure out the next available index until the
                # current index has been occupied. And we can't simply
                # linearly increment the index either, as indices are
                # logical, not physical.
                mod.do_it()

    def proxy(self, attr, long_name=None, nice_name=None):
        """Create a proxy attribute for `name` on `target`"""
        name = long_name or attr

        kwargs = {
            "longName": name,
        }

        if nice_name is not None:
            kwargs["niceName"] = nice_name

        kwargs["proxy"] = self._source[attr].path()
        cmds.addAttr(self._target.path(), **kwargs)

        return self._target[name]

    def semi_proxy(self, attr, long_name=None, nice_name=None):
        """Maya 2019 and 2022 doesn't play well with proxy attributes

        Other Maya versions simply crash ambiguously whenever they are
        used so, stay clear.

        """

        name = long_name or attr
        plug = self._source[attr]

        kwargs = {
            "default": plug.default,
            "keyable": True,
        }

        if nice_name is not None:
            kwargs["label"] = nice_name

        # Figure out the attribute type based on original plug
        def make_plug(plug, kwargs):
            attr = plug.attribute()
            Plug = None

            if attr.apiType() == cmdx.om.MFn.kNumericAttribute:
                innerType = cmdx.om.MFnNumericAttribute(attr).numericType()

                if innerType == cmdx.om.MFnNumericData.kBoolean:
                    Plug = cmdx.Boolean

                elif innerType in (cmdx.om.MFnNumericData.kShort,
                                   cmdx.om.MFnNumericData.kInt,
                                   cmdx.om.MFnNumericData.kLong,
                                   cmdx.om.MFnNumericData.kByte):
                    Plug = cmdx.Int

                elif innerType in (cmdx.om.MFnNumericData.kFloat,
                                   cmdx.om.MFnNumericData.kDouble,
                                   cmdx.om.MFnNumericData.kAddr):
                    Plug = cmdx.Double

            if Plug is None:
                # Worst case, just assume double
                kwargs["default"] = float(kwargs["default"])
                Plug = cmdx.Double

            return Plug(name, **kwargs)

        mattr = make_plug(plug, kwargs)

        with cmdx.DagModifier() as mod:
            mod.add_attr(self._target, mattr)
            mod.do_it()
            mod.connect(self._target[name], self._source[attr])

        return self._target[name]

    def add(self, attr, long_name=None, nice_name=None):
        assert isinstance(attr, string_types), "%s was not a string" % attr
        self._added.append((attr, long_name, nice_name))

    def add_divider(self, label):
        assert isinstance(label, string_types), "%s was not a string" % label
        self._added.append(cmdx.Divider(label))
