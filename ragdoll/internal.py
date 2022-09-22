"""Internal functions, don't look"""

import re
import os
import json
import time
import random
import logging
import tempfile
import functools
import contextlib

from maya import cmds

from .vendor import cmdx
from . import constants

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
        self.message = message


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

        if nice_name:
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
    type=constants.SphereShape,
    extents=cmdx.Vector(1, 1, 1),
    radius=0.0,
    length=0.0,
    orient=cmdx.Quaternion(),
    offset=cmdx.Vector(),
    rotation=cmdx.Vector(),
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
    def __init__(self, name="", verbose=False):
        self._name = name
        self._t0 = 0
        self._t1 = 0
        self._verbose = verbose
        self._duration = 0.0

    @property
    def name(self):
        return self._name

    @property
    def s(self):
        return self._duration

    @property
    def ms(self):
        return self.s * 1000

    def start(self):
        self._t0 = time.time()

    def finish(self):
        self._t1 = time.time()
        self._duration += self._t1 - self._t0

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.finish()

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


def maintain_selection(func):
    @functools.wraps(func)
    def _maintain_selection(*args, **kwargs):
        try:
            selection = cmds.ls(selection=True)
            return func(*args, **kwargs)
        finally:
            cmds.select(selection)

    return _maintain_selection


@contextlib.contextmanager
def maintained_selection():
    try:
        selection = cmds.ls(selection=True)
        yield
    finally:
        cmds.select(selection)


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


def unique_namespace(name):
    """Internal utility function"""
    if cmds.namespace(exists=name):
        index = 1
        while cmds.namespace(exists="%s%d" % (name, index)):
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


def write_svg(infname, outfname):
    from maya.debug import GraphVizManager
    gv = GraphVizManager.GraphVizManager(False)
    gv.convert_dot_to(
        input_file_name=infname,
        output_file_name=outfname,
        transitive_reduction=True
    )

    print("Graph written to %s" % outfname)


def write_graph():
    from maya.debug import em_debug_utilities
    tmp = tempfile.gettempdir()
    dot = os.path.join(tmp, "graph.dot")
    svg = os.path.join(tmp, "graph.svg")

    em_debug_utilities.dbg_graph_to_dot(
        include_plugs=True,
        use_selection=False,
        selection_depth=1,
        out_dot=dot
    )

    write_svg(dot, svg)

    return svg


def write_scheduling_graph():
    from maya.debug import em_debug_utilities
    tmp = tempfile.gettempdir()
    dot = os.path.join(tmp, "graph.dot")
    svg = os.path.join(tmp, "graph.svg")

    em_debug_utilities.dbg_scheduling_graph_to_dot(
        include_clusters=True,
        use_selection=False,
        selection_depth=1,
        out_dot=dot
    )

    write_svg(dot, svg)

    return svg


def sort_by_evaluation_order(nodes, minimal=False):
    """Return `nodes` sorted by the order in which they are evaluated

    Reach into Maya's evaluation graph for hints about the execution
    order, accessible via cmds.dbpeek. This won't work for DG evaluation
    however..

    Arguments:
        node (list): Of any kind of DG or DagNode
        minimal (bool, optional): Only look at `nodes`, default False

    """

    peek_args = {
        "op": "graph",
        "evaluationGraph": True,
        "argument": ["scheduling", "verbose"]
    }

    data = cmds.dbpeek(
        [node.shortest_path() for node in nodes]
        if minimal else [],
        **peek_args
    )

    if data.startswith("\nERROR"):
        # This only works in Parallel/Serial modes
        raise RuntimeError("No valid graph")

    scheduling = json.loads(data)["scheduling"]

    keys = {node.shortest_path().encode("ascii"): node for node in nodes}
    nodes = {key: 0 for key in keys.keys()}

    def walk(key, value, depth=0):
        # Include evaluators, e.g. CycleLayer[2,_:R_leftFoot_ctl]
        # and e.g. pruneRoots|CustomEvaluatorLayer[2,_:L_hand_ctl]
        key = key.rsplit(",", 1)[-1].rstrip("]")

        if key in nodes:
            nodes[key] += depth

        for key, value in value.items():
            walk(key, value, depth + 1)

    with Timer() as t:
        # The execution order is a depth-first dictionary
        # of the order in which nodes execute.
        walk("", scheduling["executionOrder"])

    log.debug("sort_by_evaluation_order: %.2fms" % t.ms)

    # Turn back into objects
    items = sorted(nodes.items(), key=lambda item: item[1])
    return list(keys[item[0]] for item in items)


def markers_from_solver(solver):
    markers = []

    for entity in (el.input() for el in solver["inputStart"]):
        if entity is None:
            continue

        if entity.isA("rdMarker"):
            markers.append(entity)

        elif entity.isA("rdGroup"):
            markers.extend(markers_from_solver(entity))

        elif entity.isA("rdSolver"):
            markers.extend(markers_from_solver(entity))

    return markers


def sort_by_hierarchy(dagnodes):
    pass


def sort_by_parent(markers):
    """Figure out kinematic hierarchy of `markers`

    Look to the parent marker for a hint about its evaluation order.

    What we want is for Maya to finish computing anything out marker
    depends on, like the Maya parent hierarchy. This will *normally*
    align with the marker hierarchy, but not always.
    It's possible for the user to create a marker hierarchy in the
    opposite order of Maya's hierarchy, or for an e.g. pole-vector
    to be parented to an IK control in which case the order will
    not be correct.

    """

    assert isinstance(markers, (list, tuple)), (
        "%s was not a list of markers" % str(markers)
    )

    orders = {marker: 0 for marker in markers}

    with Timer() as t:
        for marker, order in orders.items():
            parent = marker["parentMarker"].input(type="rdMarker")

            while parent:
                order += 1
                parent = parent["parentMarker"].input()

            orders[marker] = order

    log.debug("sort_by_parent: %.2fms" % t.ms)

    return list(sorted(orders.keys(), key=lambda key: orders[key]))


# From https://docs.python.org/3/library/itertools.html#itertools-recipes
def filterfalse(predicate, iterable):
    # filterfalse(lambda x: x%2, range(10)) --> 0 2 4 6 8
    if predicate is None:
        predicate = bool
    for x in iterable:
        if not predicate(x):
            yield x


def unique_everseen(iterable, key=None):
    """List unique elements, preserving order"""

    # unique_everseen('AAAABBBCCDAABBB') --> A B C D
    # unique_everseen('ABBCcAD', str.lower) --> A B C D

    seen = set()
    seen_add = seen.add
    if key is None:
        for element in filterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element


def compute_solver_size(solver):
    """Compute the size of a solver by counting it's internal entities

    This is a replacement of parsing ragdollDump().

    The size of a solver is computed by counting the amount of <SceneComponent>
    that linked to the same solver. You could compute all solver sizes by
    adding up entities you found in ragdoll registry (parsed from ragdollDump)
    like following example:

    ```python
    solvers = list(registry.view("SolverComponent"))
    solver_size = dict.fromkeys(solvers, 0)
    for entity in registry.view():
        scene_comp = registry.get(entity, "SceneComponent")
        solver_size[scene_comp["entity"]] += 1
    ```

    However the above code wouldn't work if the end user licence is not
    Unlimited one (10 markers export limit). Hence this function.

    Args:
        solver (cmdx.Node): A solver node

    Returns:
        (int): the size of solver

    """
    size = 1  # solver itself counts as one.

    for entity in [el.input() for el in solver["inputStart"]]:
        if entity is None:
            continue

        if entity.isA("rdMarker"):
            size += 3  # markers has 3: Rigid, Relative and Absolute Joint

        elif entity.isA("rdGroup"):
            size += compute_solver_size(entity)

        elif entity.isA("rdSolver"):
            # a linked solver
            size += compute_solver_size(entity)
            size -= 1

        elif entity.isA([
            "rdEnvironment",
            "rdPinConstraint",
            "rdFixedConstraint",
            "rdDistanceConstraint",
        ]):
            size += 1

    return size


def promote_linked_solvers(solvers):
    promoted = set()

    for solver in solvers:
        linked = solver["startState"].output(type="rdSolver")
        while linked:
            also_linked = linked["startState"].output(type="rdSolver")
            if also_linked:
                linked = also_linked
            else:
                promoted.add(linked)
                break
        else:
            promoted.add(solver)

    return tuple(promoted)
