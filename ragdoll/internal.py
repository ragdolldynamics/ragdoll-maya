"""Internal functions, don't look"""

import re
import time
import random
import logging
import functools

from maya import cmds
from .vendor import cmdx

log = logging.getLogger("ragdoll")

# Python 2 backwards compatibility
string_types = cmdx.string_types
long = cmdx.long


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


def with_contract(args=None, kwargs=None, returns=None):
    args = args or []
    kwargs = kwargs or {}
    returns = returns or []

    def with_contract_decorator(func):
        @functools.wraps(func)
        def with_contract_wrapper(*_args, **_kwargs):

            assert len(_args) == len(args), (
                "Unexpected number of arguments: %s != %s" % (
                    len(_args), len(args)
                )
            )

            for arg, _arg in zip(_args, args):
                assert isinstance(arg, _arg), (
                    "Type mismatch, %s != %s" % (type(arg), _arg)
                )

            for key, value in kwargs.items():
                assert isinstance(value, (list, tuple)), (
                    "Misformatted contract, kwargs value must be tuple of "
                    "(type, default) pair"
                )

                # If the user didn't pass this kwarg, that's ok.
                if key not in _kwargs:
                    continue

                _value = _kwargs[key]
                typ, default = value
                assert _value is default or isinstance(_value, typ), (
                    "Type mismatch, %s != %s" % (type(_value), typ)
                )

            result = func(*_args, **_kwargs)

            if not returns:
                if result is not None:
                    raise AssertionError(
                        "Function should not have returned anything"
                    )

            else:
                if isinstance(result, (tuple, list)):
                    assert len(result) == len(returns), (
                        "Unexpected number of returned values: %s != %s" % (
                            len(result), len(returns)
                        )
                    )

                    for ret, _ret in zip(result, returns):
                        assert isinstance(ret, _ret), (
                            "Unexpected return type: %s != %s" % (
                                type(ret), _ret
                            )
                        )
                else:
                    assert isinstance(result, returns[0]), (
                        "Unexpected return type: %s != %s" % (
                            type(result, returns[0])
                        )
                    )

            return result

        # Store for someone else to inspect
        with_contract_wrapper.contract = {
            "args": args,
            "kwargs": kwargs,
            "returns": returns,
        }

        return with_contract_wrapper

    return with_contract_decorator


# @with_contract(args=(cmdx.DagNode, cmdx.DagNode),
#                kwargs={"opts": dict},
#                returns=(cmdx.DagNode,))
# def test(parent, child, opts=None):
#     pass


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


def unique_name(name):
    """Internal utility function"""
    if cmdx.exists(name):
        index = 1
        while cmdx.exists("%s%d" % (name, index)):
            index += 1
        name = "%s%d" % (name, index)

    return name


def shape_name(transform_name):
    """Generate a suitable shape name from `transform_name`

    If a shape node has the name <transform>Shape<number>
    then Maya will keep that name updated as the transform
    name changes.

    """

    components = re.split(r"(\d+)$", transform_name, 1) + [""]
    return "Shape".join(components[:2])


def version():
    version = cmds.pluginInfo("ragdoll", query=True, version=True)
    version = "".join(version.split(".")[:3])

    try:
        return int(version.replace(".", ""))
    except ValueError:
        # No version during local or CI testing
        return 0


def random_color():
    """Return a nice random color"""

    # Rather than any old color, limit colors to
    # the first 250 degress, out of 360 total
    # These all fall into a nice pastel-scheme
    # that fits with the overall look of Ragdoll
    hue = int(random.random() * 250)

    value = 0.7
    saturation = 0.7

    color = cmdx.ColorType()
    color.setColor((hue, value, saturation),
                   cmdx.ColorType.kHSV,
                   cmdx.ColorType.kFloat)

    return color


def add_to_set(node, name, mod=None):
    try:
        collection = cmdx.encode(name)
    except cmdx.ExistError:
        with cmdx.DGModifier() as mod:
            collection = mod.create_node(
                "objectSet", name=name
            )

    collection.add(node)
    return collection
