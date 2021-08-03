"""Internal functions, don't look"""

import re
import json
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

tolerance = 0.001


class CycleError(RuntimeError):
    pass


class UserWarning(UserWarning):
    def __init__(self, title, message):
        super(UserWarning, self).__init__(message)
        self.title = title


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
        owner (cmdx.DagNode, optional): When this node dies,
            the attribute is deleted. Defaults to `source`

    """

    def __init__(self, source, target, owner=None):
        self._source = source
        self._target = target
        self._owner = owner or source
        self._added = []

    def do_it(self):
        # Avoid cyclic import by importing on-demand
        from . import options

        if not self._added:
            pass

        added = []

        while self._added:
            attr = self._added.pop(0)

            if isinstance(attr, cmdx._AbstractAttribute):
                name = attr["name"]

                if not self._target.has_attr(name):
                    with cmdx.DagModifier() as mod:
                        mod.add_attr(self._target, attr)

                plug = self._target[name]

            else:
                attr, long_name, nice_name = attr
                name = long_name or attr

                if options.read("useProxyAttributes"):
                    plug = self.proxy(attr, long_name, nice_name)
                else:
                    plug = self.semi_proxy(attr, long_name, nice_name)

            added += [plug]

        with cmdx.DagModifier() as mod:
            for new_plug in added:
                index = self._owner["userAttributes"].next_available_index()
                mod.connect(new_plug, self._owner["userAttributes"][index])

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
        clone = plug.clone(name, niceName=nice_name)
        clone["keyable"] = True

        value = plug.read()
        clone["default"] = value

        with cmdx.DagModifier() as mod:
            if name not in self._target:
                mod.add_attr(self._target, clone)
                mod.do_it()

            # Maintain current value
            mod.set_attr(self._target[name], value)

            mod.connect(self._target[name], self._source[attr])

        return self._target[name]

    def add(self, attr, long_name=None, nice_name=None):
        assert isinstance(attr, string_types), "%s was not a string" % attr
        self._added.append((attr, long_name, nice_name))

    def add_divider(self, label):
        assert isinstance(label, string_types), "%s was not a string" % label
        self._added.append(cmdx.Divider(label))


def struct(name, **kwargs):
    """Serialisable and strongly-typed data container"""

    class Struct(object):
        __slots__ = list(kwargs.keys())

        def __init__(self):
            for key, value in kwargs.items():
                setattr(self, key, value)

        def __str__(self):
            return (
                "Struct(\n%s\n)" % "\n".join(
                    "  %s=%s" % (key, getattr(self, key))
                    for key in self.__slots__
                )
            )

        def copy(self, name):
            kwargs = {}
            for slot in self.__slots__:
                kwargs[slot] = getattr(self, slot)
            return struct(name, **kwargs)

        def dump(self):
            def _euler(value):
                return {
                    "type": "MEulerRotation",
                    "values": [value.x, value.y, value.z],
                    "order": value.order
                }

            def _vector(value):
                return {
                    "type": "MVector",
                    "values": [value.x, value.y, value.z]
                }

            def _quaternion(value):
                return {
                    "type": "MQuaternion",
                    "values": [value.x, value.y, value.z, value.w]
                }

            def serialise(value):
                if isinstance(value, (int, float, str, bool)):
                    return value

                elif isinstance(value, cmdx.om.MEulerRotation):
                    return _euler(value)

                elif isinstance(value, cmdx.om.MVector):
                    return _vector(value)

                elif isinstance(value, cmdx.om.MQuaternion):
                    return _quaternion(value)

                else:
                    raise TypeError("Cannot serialise %s" % value)

            return json.dumps({
                slot: serialise(getattr(self, slot))
                for slot in self.__slots__
                if not callable(getattr(self, slot))
            })

        def load(self, dump):
            def _euler(value):
                values = value["values"]
                return cmdx.Euler(
                    values[0], values[1], values[2], value["order"]
                )

            def _vector(value):
                values = value["values"]
                return cmdx.Vector(
                    values[0], values[1], values[2]
                )

            def _quaternion(value):
                values = value["values"]
                return cmdx.Quaternion(
                    values[0], values[1], values[2], values[3]
                )

            def deserialise(value):
                if isinstance(value, dict):
                    if value["type"] == "MEulerRotation":
                        return _euler(value)

                    elif value["type"] == "MVector":
                        return _vector(value)

                    elif value["type"] == "MQuaternion":
                        return _quaternion(value)

                    else:
                        raise TypeError("Cannot deserialise %s" % value)

                else:
                    return value

            for slot, value in json.loads(dump).items():
                setattr(self, slot, deserialise(value))

            return self

    return Struct


# Components
Geometry = struct(
    "Geometry",
    orient=cmdx.Quaternion(),
    extents=cmdx.Vector(1, 1, 1),
    length=0.0,
    radius=0.0,
    shape_offset=cmdx.Vector(),
    shape_rotation=cmdx.Vector(),
    compute_mass=lambda self: (
        self.extents.x *
        self.extents.y *
        self.extents.z *
        0.01
    )
)


def with_contract(args=None, kwargs=None, returns=None, opts=None):
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


def with_timing(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        t0 = time.time()

        try:
            return func(*args, **kwargs)
        finally:
            t1 = time.time()
            duration = t1 - t0
            log.debug("%s in %.2fms" % (func.__name__, duration * 1000))

    return wrapper


class Timer(object):
    def __init__(self, name, verbose=True):
        self._name = name
        self._t0 = 0
        self._t1 = 0
        self._verbose = verbose

    @property
    def s(self):
        return self._t1 - self._t0

    @property
    def ms(self):
        return self.s * 1000

    def __enter__(self):
        self._t0 = time.time()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self._t1 = time.time()

        if self._verbose:
            log.debug("%s in %.2fms" % (self._name, self.ms))


def with_refresh_suspended(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not kwargs.get("dry_run", False):
            cmds.refresh(suspend=True)

        try:
            return func(*args, **kwargs)
        finally:
            if not kwargs.get("dry_run", False):
                cmds.refresh(suspend=False)

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


def sort_filenames(fnames, suffix=".rag"):
    """Sort by numbered suffix

    From:
      -o filename10
      -o filename8
      -o filename9

    To:
      -o filename8
      -o filename9
      -o filename10

    """

    # Separate name from numbered suffix,
    # filename10 -> (filename, 10)
    fnames = [
        re.split(r"(\d+)$", item.rsplit(suffix)[0])
        for item in fnames
    ]

    # (filename, 10, '') -> (filename, "10")
    fnames = [
        tuple(filter(None, item))
        for item in fnames
    ]

    # Sort by suffix first, alphabetical second
    def sort(item):
        if len(item) == 2:
            return item[0], int(item[-1])
        else:
            return item

    fnames = sorted(fnames, key=sort)

    # Re-assemble
    # (filename, 10) -> f
    return [
        "".join(item) + suffix for item in fnames
    ]


def unique_name(name):
    """Internal utility function"""
    if cmdx.exists(name, strict=False):
        index = 1
        while cmdx.exists("%s%d" % (name, index), strict=False):
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


def is_dynamic(transform, scene):
    """Does `transform` in any way affect `scene`?"""
    scene["clean"] = True

    # Pull, but do not bother actually serialising it
    transform["worldMatrix"].pull()

    return not scene["clean"].read()
