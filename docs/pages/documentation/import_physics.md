---
title: Import Physics
icon: "save_black.png"
---

<div class="hero-container">
    <img class="hero-image" src=/yoga12.png>
</div>

Import physics onto existing controllers from disk.

<br>

### Import

You can *import* a Ragdoll setup exported from Maya, back into Maya. It'll re-create everything just the way it was.

??? question "What is included in the export?"
    Just about everything.

    - Solvers
    - Groups
    - Markers
    - Constraints
    - Colors
    - Attribute changes
    - Retargeting
    - Reparenting
    - Replaced meshes
    - Thumbnail of your viewport

??? question "What isn't included in the export?"
    Very little.

    - The mesh itself is *not* stored, the mesh is expected to come from your rig. Including any mesh you replace. This may be added in a future release.
    - The cached simulation, although it will be soon.

??? question "Will I get identical results when simulating an imported scene?"
    Yes, anything else is a bug.

    More precisely, determinism depends on (1) the type and number of items in the solver along with (2) the order in which these are created. Both of these are part of the exported file format and is taken into account during import. Meaning you should get identical results so long as the content is the same.

<br>

#### Example

Here's an exported Ragdoll setup for the free CG Spectrum Tiger rig.

- [Download Ragdoll file (`2.8 mb`)](https://gist.github.com/mottosso/7cfbf29681f6807ab4493a41d37155fa/raw/a093794fdaafa05fcb28c1b82f60f8ae3a41cf0b/cgspectrum_tiger.rag)
- [Download Rig](https://www.cgspectrum.com/resources/tiger-animation-rig)

To use it, download the rig and import the Ragdoll file.

![image](https://user-images.githubusercontent.com/2152766/149620136-7178ce52-6235-40cc-bf45-289a25b52649.png)
![image](https://user-images.githubusercontent.com/2152766/149323893-f80dba31-83fe-4fe2-9e00-a062dee5ed09.png)

It contains 2 [levels of detail](/releases/2022.01.17/#level-of-detail).

| Level   | Content
|:--------|:----
| Level 0 | Body and feet
| Level 1 | Everything on Level 0, plus toes

https://user-images.githubusercontent.com/2152766/149409408-c76f19c2-de4c-4baa-8a1c-8f7d45a5bb40.mp4 controls


<br>

#### Workflow

Here's the rundown.

1. Assign markers
2. Tweak values
2. Export
3. Open a new scene, with the same character
4. Import

On import, Ragdoll will try and find the names of what you exported in your currently opened scene.

- If all names match, import should go smoothly. Preserving all of your hard work!
- If names do not match, if for example the namespace differs, there is an option to override the namespace from the file via the `Namespace` dropdown menu.
- If names don't match *at all*, if for example it was grouped differently on export or it is a different character altogether, then you can try using the `Search and Replace` fields to modify the names searched for by Ragdoll.

**Export**

Once you're happy with your character, it's time to export. Towards the bottom of the UI, you'll get a preview of what is about to be exported. This can help clarify that what ends up on disk is what you expect.

https://user-images.githubusercontent.com/2152766/149382978-6063bdc2-80de-4d9c-9a3c-eec5682afa3f.mp4 controls

**Import**

In a new scene, with the same character, same names and everything, import as you'd expect. At the bottom of this UI, you'll get a preview of what's in the file on disk, along with how it will associate the node names found in the file with what you have on disk.

https://user-images.githubusercontent.com/2152766/149382981-a48f105c-a0f8-421e-ad3d-e8fcaaef4bbc.mp4 controls

<br>

#### Namespace from File

Odds are, the character you're importing either has no namespace, or has a different namespace to what you've currently got in your scene. As in this example here, with 3 copies of the same character, each with its own namespace.

Use the `Namespace` dropdown to select one of the current namespaces in your scene, or `Custom` to type one in yourself.

https://user-images.githubusercontent.com/2152766/149382984-3c2527e2-9c62-4354-8b9f-6656a66643a8.mp4 controls

<br>

#### Solver from File

Per default, Ragdoll will import the file into the current solver in your scene, if any. Or, you can import the original solver from the source file.

https://user-images.githubusercontent.com/2152766/149382990-85ac7402-7588-46a2-9c23-7c3f14f7d6af.mp4 controls

<br>

#### Known Limitations

Here are a few things that will be addressed over time. Let us know if you encounter anything else!

- https://ragdolldynamics.com/chat

| Limitation | Result
|:-----------|:---------
| Missing Replaced Mesh | If you replace the mesh of a marker, but this mesh isn't present in the scene during import, you'll get a Capsule instead. The vertices of the geometry isn't stored in the exported file, only the name of the mesh you replaced with.
| Linked Solvers | These turn into a single, unified solver on import.
