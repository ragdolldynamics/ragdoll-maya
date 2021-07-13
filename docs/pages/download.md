<div class="hero-container">
    <img class="hero-image" src=/car14.png>
</div>

> At the time of this writing, Ragdoll is still in early access. [Reach out](https://ragdolldynamics.com/contact) for access.

<br>
<br>

<div class="vboxlayout align-center justify-center">
    <div class="hboxlayout align-center">
        <a href="https://files.ragdolldynamics.com" class="button red"><b>Download</b></a>
        <p>Ragdoll <b>{{ config.ragdoll_version }}</b> awaits.<br>
        <i>Click here to get started.</i></p>
    </div>
    <a class="padding-top" href="https://files.ragdolldynamics.com/files/distribution">Previous versions</a>
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
    Fair enough, let's go deeper.

    ```py
    from os.path import join
    modules_path = r"c:\Users\marcus\Documents\maya\modules"
    ragdoll_path = join(modules_path, "Ragdoll-Maya-2021_06_06\scripts")

    import sys
    sys.path.insert(0, ragdoll_path)

    from ragdoll import interactive
    interactive.install()
    ```

    Make sure you replace the version number (date) with the version you are using. At this point, I expect you've uncovered why your module wasn't working in the first place and should probably revisit that as this process would require you to manually update the version number in that path each time you upgrade. No fun.

??? bug "Something else happened"
    Oh no! I'd like to know about what happened, please let me know [here](mailto:marcus@ragdolldynamics.com).

<br>

## FAQ

??? question "What are my workstation requirements?"
    Anything capable of running Maya can run Ragdoll.

    - Windows 10+ or CentOS 7+
    - 64-bit Intel® or AMD® processor
    - 4 GB of RAM
    - Maya 2018-2022

??? question "What are my licensing options?"
    - `Trial` - 30 days of non-commercial use, no strings attached
    - `NodeLocked` - Any number of users, one machine per licence
    - `Floating` - Any number of machines, one user per licence
    - `Headless` - A cost-effective alternative for distributed simulations

??? question "What happens when my licence runs out?"
    Your scenes will still open, but the solver will be disabled. Contact [licence@ragdolldynamics.com](mailto:licence@ragdolldynamics.com) for renewal of your licence.

??? question "What happens when I skip frames?"
    The simulation gracefully pauses until you revisit the last simulated frame.

??? question "How do I disable the ground?"
    A static collider is automatically added on the Maya grid per default, it can be disabled on the `rdScene` node via the `.useGround` attribute.

??? question "Why not use nHair for overlapping animation?"
    Yes, and while your at it, why not stick razor blades in your eyes?

    Seriously though, Ragdoll simulates your translate and rotate channels, whereas nHair simulates point geometry. You can convert those points into translation and rotation, but given the choice why would you? Besides, Ragdoll has far more robust collisions, control and constraints than nHair or nCloth could ever hope to achieve, at much greater performance.

<br>

## Limitations

As of `Ragdoll {{ config.ragdoll_version }}` these are the current known limitations of Ragdoll.

- Must visit start frame on scene open
- When weight painting rigid joints, cannot right-click "Select influence" (see [workaround](https://forums.ragdolldynamics.com/t/swing-physics-test/40/2))
- More since [2021.04.23](/releases/2021.04.23#known-issues)
