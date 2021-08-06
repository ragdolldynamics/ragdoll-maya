---
icon: "save_black.png"
---

<div class="hero-container">
    <img class="hero-image" src=/yoga12.png>
</div>

Import physics onto existing controllers from disk.

<br>

### Usage

From the Ragdoll menu, select the `Import Physics` option in the `Animation` sub-menu.

![ragdollimporttiger](https://user-images.githubusercontent.com/2152766/114277018-40ff3f00-9a21-11eb-92d7-f028bdaf249e.gif)

<br>

#### Examples

**Import onto Selected Character**

![ragdollimportall](https://user-images.githubusercontent.com/2152766/114277580-a6ecc600-9a23-11eb-9e9b-d440a39d1c51.gif)

**Import onto the Ragcar**

![ragcarimport](https://user-images.githubusercontent.com/2152766/114273737-35a51700-9a13-11eb-9d46-9afcb0bc153e.gif)

<br>

### Import Physics

Animators can now setup physics one character, export it, and then import onto another.

The usecase is having spent time setting up a perfect ragdoll and then wanting to reuse this setup across multiple scenes, on multiple instances of the same referenced character, or on characters with similar naming scheme and anatomy. It can also be used to import parts of a character or individual objects.

**Demo**

Here's an **18 second** run-down of the complete workflow, from authoring to import.

![ragdollimportquick2](https://user-images.githubusercontent.com/2152766/114265098-d6311200-99e6-11eb-9b5f-8d2396d0506a.gif)

<br>

#### Features

Anything you can apply physics to can be exported.

The nodes onto which physics is *imported*..

- ✔️ Can have a different namespace
- ✔️ Can have a different naming convention
- ✔️ Can have a different pose
- ✔️ Can have a different scale
- ✔️ Can be animated
- ✔️ Can be referenced
- ✔️ Can be imported in pieces, based on what is currently selected

It will remember..

- ✔️ All edited attributes, like `Guide Strength`
- ✔️ All edited constraints, like their limits and frames

It will *not* remember..

- ❌ The vertices of the `Mesh` shape type (not part of the exported file)
- ❌ Controls (i.e. Soft Pin, Hard Pin and Mimic)

??? info "About those 'Convex Hulls'.."
    Convex hulls, those triangulated versions of your Maya shapes - the `Mesh` shape type - are re-generated onto whatever character you import onto. This is probably what you want, and enables you to apply physics onto characters with *different* geometry from when you originally authored the physics. Although sometimes it's not, which is why this we be augmented in a future release.

And that's about it! It doesn't even have to be a "character", any combination of Maya nodes you can apply physics to can have their physics exported. Like a (rag)car, or just a (rag)box.

<br>

#### User Interface

Use the UI to visualise the contents of an exported `.rag` file and customise the import.

![](https://user-images.githubusercontent.com/2152766/114264876-69694800-99e5-11eb-99d6-7df8a5976751.gif)

The UI resembles native Maya and Ragdoll option dialogs, with two interesting bits.

<img class="boxshadow" style="max-height: 600px;" src=https://user-images.githubusercontent.com/2152766/114264932-c36a0d80-99e5-11eb-874d-f81bb92eb0ca.png>

<br>

##### 1. File Browser

The top part displays other Ragdoll scene (`.rag`) files in the same directory as the selected file, along with the thumbnail stored during the time of export. The thumbnail currently isn't visible *during* export, it is captured from the currently active viewport. An Export UI with thumbnail preview (and more!) will be added in a future release.

<img class="boxshadow" src=https://user-images.githubusercontent.com/2152766/114264973-01673180-99e6-11eb-9890-fbfb463f2a85.png>

<br>

##### 2. Content Preview

This sections shows you the *contents* of the physics scene, ahead of actually importing it.

It will visualise a number of things.

1. Which Maya nodes will be "physicalised"?
2. Which nodes present during export are *not* present in the currently opened scene?
2. What was the original path of a node during export?
3. What is the *destination* path of the node being imported?
4. *Is there* a destination node?
5. Is the destination *already* physicalised?
6. What was the original node *icon*, e.g. `nurbsCurve` or `mesh`?
7. What is the `Shape Type` of the exported rigid, e.g `Capsule`?

<img class="boxshadow" src=https://user-images.githubusercontent.com/2152766/114264972-fc09e700-99e5-11eb-979c-0093b9086497.png>

<br>

### Introduction

The export-format is identical to what game developers use to author physics in Maya and import it into their game engine. It contains *all* data managed by Ragdoll, in full detail. Enough detail to reverse-engineer it back into a Maya scene, which is exactly what's going on here.

**Example Files**

- [`mytiger.rag`](/guides/mytiger_rag)
- [`mycharacter.rag`](/guides/mycharacter_rag)
- [`ragcar.rag`](/guides/mycar_rag)

It means some information is lost, in particular any custom connections made or custom attributes added or removed. It will use the same menu items you used to author a ragdoll, and nothing else. So things not possible with those commands will not be captured in the exported file format.

<br>

#### Thumbnail

Each export captures the currently active 3d viewport for use as a thumbnail. So, whenever you export, remember to smile and wave! :D

![thumbnail5](https://user-images.githubusercontent.com/2152766/114277347-b6b7da80-9a22-11eb-96d0-e85b557e1395.gif)

<br>

#### Context Sensitive

The visualisations will update as you select different nodes and edit the various options in the UI.

To illustrate this, let's import onto the same scene we exported.

**Export**

Only one character is physicalised and exported.

![ragdoll_sacmescene_export](https://user-images.githubusercontent.com/2152766/114266161-aedd4380-99ec-11eb-8502-a78f025d718d.gif)

**Import**

Notice that importing is not possible, since the character is already physicalised. Unless we replace the namespace, by selecting another character.

![ragdoll_sacmescene_autonamespace](https://user-images.githubusercontent.com/2152766/114266157-a553db80-99ec-11eb-89e2-408018b5e7ff.gif)

<br>

#### Use Selection

Import onto selected nodes with `Use Selection` toggled (it's the default).

![partialimport](https://user-images.githubusercontent.com/2152766/114277027-4f4d5b00-9a21-11eb-96c8-8d486cfb025a.gif)

<br>

#### Search and Replace

Every node is stored along with its full path, such as..

```
|root_grp|spine_grp|spine_ctrl
```

And in most cases can get quite long, with one or more namespaces and tens to hundreds of levels deep in hierarchy.

```
|_:Group|_:Main|_:DeformationSystem|_:Root_M|_:RootPart1_M|_:RootPart2_M|_:Spine1_M|_:Spine1Part1_M|_:Spine1Part2_M|_:Chest_M|_:Scapula_L|_:Shoulder_L|_:ShoulderPart1_L|_:ShoulderPart2_L|_:Elbow_L|_:ElbowPart1_L|_:ElbowPart2_L|_:Wrist_L|_:IndexFinger1_L
```

> Here, the namespace is simply `_:`

The `Search and Replace` boxes of the UI can be used to replace parts of each path, to try and map the original path to whatever path is currently available in the scene.

![ragdollsearchreplace2](https://user-images.githubusercontent.com/2152766/114266420-36778200-99ee-11eb-9b2e-643215d8213e.gif)

<br>

#### Auto Namespace

One challenge with export/import it remapping names from the original scene onto your new scene. Ragdoll solves the typical case of only the namespace being different with "Auto Namespace".

![autonamespace](https://user-images.githubusercontent.com/2152766/113845947-eac69d80-978d-11eb-8346-3e73bce1f2be.gif)

"Auto Namespace" will replace any namespace in the original file with whatever namespace is currently selected. Neat! If there are *multiple* namespaces, it'll use the last namespace.

<br>

#### Auto Scene

Locate and use the original physics scene from the original file, so as to preserve your multi-scene setups.

For example, if your one character has 3 physics scenes - one for the right arm, one for the left and a single one for both legs - then "Auto Scene" will preserve these scenes for you.

!!! hint "Performance Tip"
    Using more than one scene can improve performance significantly, as Ragdoll will *parallelise* each invidual scene. The caveat is that rigids in different scenes cannot interact with each other.

<br>

#### Ragdoll Clean

Here's a quick way you can use this feature to "clean" a physics scene.

1. Export
2. Delete All
3. Import

The resulting scene will be "clean" in that it will have been broken down into its componens and reassembled again, not taking into account anything Ragdoll doesn't know about.

![ragdoll_clean](https://user-images.githubusercontent.com/2152766/114266336-b6511c80-99ed-11eb-841c-aa8bca7bf304.gif)

(I may just add a menu item for this, called `Clean` to do this in one go :)

<br>

### Import Python API

Anything the UI can do can be done via Python, using the new `dump.Loader` object.

```py
from ragdoll import dump
loader = dump.Loader()
loader.read(r"c:\path\to\myRagdoll.rag")

# Search and replace these terms from the full node path
# E.g. |root_grp|arm_left -> |root_grp|arm_right
loader.set_replace((
    ("_left", "_right"),
    ("_ik", "_fk"),
))

# An automatic method of search-and-replace, that replaces
# any namespaces found in the file with this.
# E.g. |char1:root_grp -> |char2:root_grp
loader.set_namespace("char2:")

# Limit imported nodes to those with an absolute path 
# starting with *any* of these
loader.set_roots((
    "|char1:root_grp",
    "|char2:root_grp"
))

# Deconstruct the provided `.rag` file
# (This is what is visualised in the UI)
# (The exact layout of this data may change)
analysis = loader.analyse()
assert isinstance(analysis, dict)

# Print a brief human-readable summary of the current analysis
loader.report()
```

!!! hint "Heads up"
    Consider this a version 0.1 of the API, it will likely change in the future.
