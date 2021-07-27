<div class="hero-container">
    <img class="hero-image" src=/car14.png>
</div>

<br>

<div class="vboxlayout align-center justify-center">
    <!-- <h3>Download</h3> -->
    <b>Download</b>
    <p>If you agree with the <a href="https://ragdolldynamics.com/eula"><u>Ragdoll Dynamics EULA</u></a>, you may select a platform below.</p>
    <div class="hboxlayout align-center">
        <a style="max-height: 40px;" href="https://ragdolldynamics.com/download?platform=windows" class="button red"><div class="image"><img src=https://user-images.githubusercontent.com/2152766/126961293-8ab863bf-65c8-4e89-a25d-9bcbe4a63627.png></div><b>Windows</b></a>
        <a style="max-height: 40px;" href="https://ragdolldynamics.com/download?platform=linux" class="button blue"><div class="image"><img src=https://user-images.githubusercontent.com/2152766/126961293-8ab863bf-65c8-4e89-a25d-9bcbe4a63627.png></div><b>Linux</b></a>
    </div>
    <p class="text-align-center">Ragdoll <b>{{ config.latest_version }}</b> awaits.<br>
    <a href="https://files.ragdolldynamics.com">Previous versions</a>
</div>

<br>
<br>

## Install

Ragdoll ships as a Maya [Module](https://around-the-corner.typepad.com/adn/2012/07/distributing-files-on-maya-maya-modules.html) for Windows and Linux.

!!! info "Installation for Windows"
    On the Windows platform, there's an executable you can run.

    1. Run the `.msi` installer
    2. Restart Maya

    Alternatively, unzip Ragdoll into your `~/maya` directory. You should end up with something like this.

    ```bash
    c:\Users\marcus\Documents\maya\modules\Ragdoll.mod
    ```

??? info "Installation for Linux"
    On Linux, installation and upgrades are done in the same fashion.

    1. Unzip the `.zip` into your `~/maya` directory
    2. Restart Maya

    You should end up with something like this.

    ```bash
    /home/marcus/maya/modules/Ragdoll.mod
    ```

??? info "Installation for MacOS"
    Sorry, MacOS is currently *not supported*.

    Let us know this is important to you, and priorities can be shifted.

    contact@ragdolldynamics.com

The plug-in is now available via the Plug-in Manager.

<img class="boxshadow" src=https://user-images.githubusercontent.com/2152766/111457614-55953380-8710-11eb-99a4-f2fb7cc67771.gif>

- See [Release History](/releases)

<br>

**Everything ok?**

??? bug "No menu"
    You've booted up Maya, but there is no menu, what gives?

    Maya Modules work in mysterious ways. Try installing it the old fashioned way.

    ```py
    from ragdoll import interactive
    interactive.install()
    ```

??? bug "No module named 'ragdoll'"
    A clue! Let's go deeper.

    ```py
    import os
    modules_path = r"c:\Users\marcus\Documents\maya\modules"
    ragdoll_path = os.path.join(modules_path, "Ragdoll-Maya-2021_11_06\scripts")

    import sys
    sys.path.insert(0, ragdoll_path)

    from ragdoll import interactive
    interactive.install()
    ```

    Make sure you replace the version number (date) with the version you are using. At this point, I expect you've uncovered why your module wasn't working in the first place and should probably revisit that as this process would require you to manually update the version number in that path each time you upgrade. No fun.

??? bug "Something else happened"
    Oh no! I'd like to know about what happened, please let me know [here](mailto:support@ragdolldynamics.com).

<br>

## FAQ

??? question "What are my workstation requirements?"
    Anything capable of running Maya can run Ragdoll.

    - Windows 10+ or CentOS 7+
    - 64-bit Intel® or AMD® processor
    - 4 GB of RAM
    - Maya 2018-2022

??? question "What are my licensing options?"
    See [Pricing](https://ragdolldynamics.com/pricing).

??? question "What happens when my licence runs out?"
    Your scenes will still open, but the solver will be disabled. Contact [licence@ragdolldynamics.com](mailto:licence@ragdolldynamics.com) for renewal of your licence.

??? question "What happens when I skip frames?"
    The simulation gracefully pauses until you revisit the last simulated frame.

??? question "How do I disable the ground?"
    A static collider is automatically added on the Maya grid per default, it can be disabled on the `rdScene` node via the `.useGround` attribute.

??? question "Can I use Rez?"
    Yes, the only environment variable needed for Rez is `MAYA_MODULE_PATH`, such as:

    ```py
    env["MAYA_MODULE_PATH"].append("{root}")
    ```

    Where the `Ragdoll-2021_07_28` folder and `Ragdoll-2021_07_28.mod` file resides at `{root}`.

??? question "Why not use nHair for overlapping animation?"
    Ragdoll simulates your translate and rotate channels, whereas nHair simulates point geometry. You can convert those points into translation and rotation, but given the choice why would you? Besides, Ragdoll has far more robust collisions, control and constraints than nHair or nCloth could ever hope to achieve, at much greater performance.

<br>

## Limitations

As of `Ragdoll {{ config.latest_version }}` these are the current known limitations of Ragdoll.

- Must visit start frame on scene open
- Maya 2022 crashes when calling `Delete Physics`

<div class="hboxlayout align-center">
    <a href="/releases/2021.04.23#known-issues" class="button blue"><b>More</b></a>
</div>
