![image](https://user-images.githubusercontent.com/2152766/143775949-7bd67757-2574-43d5-a9c1-e41247255b3e.png)

The `Record Simulation` command consists of 4 steps.

| # | Step      | Description
|:--|:----------|:-----------------------
| 1 | `Extract` | Extract Simulation onto a new joint hierarchy
| 2 | `Attach`  | Constrain rig controls to joint hierarchy
| 3 | `Bake`    | Call `cmds.bakeResults`
| 4 | `Cleanup` | Delete joint hierarchy and constraints

The final result is keyframes on the rig controls, in a new Animation Layer.

<br>

### Manual Record

Here's what it looks like to do manually, for 1 control.

https://user-images.githubusercontent.com/2152766/143776403-2357038a-e899-46a8-8d0f-924487f59575.mp4 controls

Repeat the `Attach` step for each control, and take locked channels into account, and you've entirely replicated what `Record Simulation` does.

<br>

### Custom Attach

The `Attach` step can be overridden to accommodate for custom constraints, for when your studio rigs cannot use the native `cmds.parentConstraint` and `cmds.orientConstraint` nodes that ship with Maya.

Here's how it works.

```py
# 1 - Import the Record Simulation command
from ragdoll.tools import markers_tool as markers

# 2 - Write your own command to attach
def custom_attach(...):
    ...

# 3 - Replace the default attach
markers._Recorder._attach = custom_attach
```

Here's an example of the default implementation, pay special attention to the calls to `cmds.parentConstraint` and `cmds.orientConstraint`; these are the ones you want to replace with your own commands.

```py
from ragdoll.vendor import cmdx
from ragdoll.tools import markers_tool as markers


def custom_attach(self, marker_to_dagnode):
    """Constrain rig controls to simulation

    Arguments:
        marker_to_dagnode (dict): Dictionary with marker: dagnode, the dagnode
            is the animation control, e.g. L_hand_ctl

    Returns:
        new_constraints (list): Newly created constraints as cmdx.Node instances

    """

    # Constraints created by this function
    # This list is used to delete the constraints after recording is complete
    new_constraints = []

    # Attach animation controls at the start time,
    # that's where the simulation and animation overlap
    initial_time = cmdx.current_time()
    cmdx.current_time(self._solver_start_frame)

    for dst, marker in self._dst_to_marker.items():
        src = marker_to_dagnode.get(marker, None)

        if not src:
            continue

        # dst == your rig control
        # src == the extracted transform

        skip_rotate = set()
        skip_translate = set()

        for chan, plug in zip("xyz", dst["rotate"]):
            if plug.locked:
                skip_rotate.add(chan)

        for chan, plug in zip("xyz", dst["translate"]):
            if plug.locked:
                skip_translate.add(chan)

        if skip_translate != {"x", "y", "z"}:

            #
            # REPLACE ME
            #
            pcon = cmds.parentConstraint(
                src.shortest_path(),
                dst.shortest_path(),
                maintainOffset=True,
                skipTranslate=list(skip_translate) or "none",
                skipRotate=list("xyz"),
            )

            # Store reference to this node
            pcon = cmdx.encode(pcon[0])
            new_constraints.append(pcon)

        if skip_rotate != {"x", "y", "z"}:

            #
            # REPLACE ME
            #
            ocon = cmds.orientConstraint(
                src.shortest_path(),
                dst.shortest_path(),
                maintainOffset=True,
                skip=list(skip_rotate) or "none",
            )

            ocon = cmdx.encode(ocon[0])
            new_constraints.append(ocon)

    cmdx.current_time(initial_time)

    return new_constraints


# Store original attach, just in case
try:
    old_attach
except NameError:
    old_attach = markers._Recorder._attach

# Replace with custom implementation
markers._Recorder._attach = custom_attach
```

<br>

#### Usage

Copy/paste the above snippet into your Script Editor and call `Record Simulation`. Nothing should have changed, because the above is a near-exact copy of the original.

From here, start editing the snippet. Keep executing the script in your Script Editor as you make changes, and call `Record Simulation` from the `Ragdoll` menu to try it out.

To restore the original implementation, either use `old_attach` or reload the plug-in.

<br>

#### Variables

The `src` variable is the extracted simulation, the joint. The `dst` variable is your rig control, what you want to constrain to `src`. The `skip_translate` and `skip_rotate` variables are two `sets` containing the channels on your rig controls were locked (if any). Use these if your constraint commands needs them (like `cmds.parentConstraint` does).

<br>

#### Default Constraint Commands

The default implementation uses `cmds.parentConstraint` for the `Translate` channels, and `cmds.orientConstraint` for the `Rotate` channels to accommodate for when one or more `Rotate` channels are *locked*. As it happens, the `cmds.parentConstraint` produces gimbal locks in situations like that.

You may use a single constraint command for all channels, if available, to try and see whether those also run into gimbal issues - such as randomly flipping 180 degrees. If they do, consider using a different constraint for the rotate channel.

<br>

#### Return Value

The command MUST return `new_constraint` which MUST be of `list` type and contain any and all nodes created by this function. In the default implementation, we call on `maya.cmds` to create the constraint, but convert the resulting `string` types to `cmdx.Node` via `cmdx.encode()`. You MUST do the same.

<br>

#### Reference

See the original command, along with available members of `self` on GitHub.

- [`mottosso/ragdoll/ragdoll/tools/markers_tool.py`](https://github.com/mottosso/ragdoll/blob/f7e88f2c9777340409086ed40952c35917d2c64b/ragdoll/tools/markers_tool.py#L827)