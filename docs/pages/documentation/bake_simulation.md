---
title: Bake Simulation
icon: "bake_black.png"
---

Convert physics into regular keyframes with `Bake Simulation`.

<br>

### Usage

From the Ragdoll menu, select the `Bake Simulation` from the `Animation` sub-menu.

![bakesimulation](https://user-images.githubusercontent.com/2152766/116553048-9c6e6f80-a8f1-11eb-8c6a-2242b6e67d83.gif)

Learn more with this tutorial on YouTube.

<a href="https://youtu.be/PN6HaZtAKmQ" target="_blank"><img class="boxshadow" style="max-width: 500px;" src=https://user-images.githubusercontent.com/2152766/117301392-85d89300-ae72-11eb-9073-542929c60483.png></a>

<br>

#### Bake Duration

On completion of a bake, it'll tell you how long it took.

??? hint "Not showing up?"
    The message is an "in-view" message that needs to be enabled for anything to appear. Head into the Maya Preferences, under `Interface | Help`.

    Or run this from your `Script Editor`.

    ```py
    from maya import cmds
    cmds.optionVar(intValue=("inViewMessageEnable", 1))
    ```

![headsupmessage](https://user-images.githubusercontent.com/2152766/117143200-7db42100-ada8-11eb-8ee7-1894b017e92c.gif)

<br>

#### Bake Options

Find a few more options in the Options dialog. Hover over each item to learn more about it.

![image](https://user-images.githubusercontent.com/2152766/117143294-945a7800-ada8-11eb-8c73-3fe479650a16.png)

<br>

#### Bake Selected Scenes

Sometimes your simulation is split across multiple scenes. Use this option to bake only the selected scenes, leaving the others active.

![image](https://user-images.githubusercontent.com/2152766/124235049-b6544a80-db0c-11eb-8bb6-4ae17f81313a.png)
