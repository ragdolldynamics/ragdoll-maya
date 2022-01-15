<div class="hero-container">
  <img class="hero-image" src=/yoga13.png>
</div>

### API Member Reference

The complete Ragdoll API. :man_raising_hand:

```py
from maya import cmds
import ragdoll.api as rd

box = cmds.polyCube()

solver = rd.createSolver()
marker = rd.assignMarker(box[0], solver)

rd.recordPhysics()
```

{{ api:overview }}

<br>

### Argument Signatures

A more in-depth view on each function.

{{ api:details }}

<br>

### Constants

Some functions take constants for arguments.

```py
from ragdoll import api
api.assign_marker(a, b, opts={"density": api.DensityFlesh})
```

{{ api:constants }}
