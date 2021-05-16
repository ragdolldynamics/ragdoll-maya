![activatelease](https://user-images.githubusercontent.com/2152766/117956343-db98b980-b310-11eb-9bdf-80ba6fc949f7.gif)

Congratulations on your purchase of a floating licence for **Ragdoll Dynamics**!

This page will help you get set-up with a licence server, on-premise, and instruct Ragdoll to "lease" a licence from it. The server itself can run on any machine and any platform, including Windows, Linux and MacOS, so long as it is accessible from the machine running Ragdoll.

??? into "Test Connectivity"
    To test whether machine A is accessible from machine B, try `ping`.

    ```bash
    ping 10.0.0.13
    # Reply from 10.0.0.13: bytes=32 time=1ms TTL=117
    ```

On each platform, the procedure is the same.

1. Download the server software
2. Optionally edit the configuration file
3. Activate the server with your `Product Key`
4. Start it up

The server will need to remain running in order for Ragdoll to lease licences.

<br>

## Linux

Here's a typical series of commands for an x64 system, look inside [the .zip](https://files.ragdolldynamics.com/api/public/dl/hAlavAOP/TurboFloat-Server-Linux.zip) for alternative Linux-based platforms.

!!! hint "Requirements"
    Make sure you have `unzip` and `wget` at the ready, or use alternatives like `curl` and `tar` at your own leisure.

```bash
mkdir turbofloat
cd turbofloat
wget https://files.ragdolldynamics.com/api/public/dl/hAlavAOP/TurboFloat-Server-Linux.zip
wget https://files.ragdolldynamics.com/api/public/dl/6lMDDMdn/TurboActivate.dat
unzip TurboFloat-Server-Linux.zip
mv bin-linux/x64/turbofloatserver ./
chmod +x turbofloatserver
./turbofloatserver -a="YOUR-SERIAL-NUMBER"
./turbofloatserver -x
# Floating license server for Ragdoll Dynamics (TFS v4.4.4.0)
```

> You can optionally pass `-silent` after `-x` for less verbosity.

??? question "No internet?"
    The licence server can be activated offline.

    - See [Can I activate my server offline?](#can-i-activate-my-server-offline)

From here, you'll likely want `turbofloatserver -x` called automatically on reboot, such that Ragdoll and Maya can lease licences from it. The exact procedure varies between Linux distributions and company preferences, so I won't go into details here except to say that [systemd](https://www.linux.com/training-tutorials/understanding-and-using-systemd/) is a common option.

**More Details**

- [Installation Options](https://wyday.com/limelm/help/turbofloat-server/#install)
- [Configuration Options](https://wyday.com/limelm/help/turbofloat-server/#config)

<br>

## Windows

Here's what you need to do in order to run the licence server on the Windows platform.

<br>

### Download

You'll need both of these.

- [`TurboFloat-Server-Windows.zip`](https://files.ragdolldynamics.com/api/public/dl/PdFO00Vv/TurboFloat-Server-Windows.zip)
- [`TurboActivate.dat`](https://files.ragdolldynamics.com/api/public/dl/6lMDDMdn/TurboActivate.dat)

Unzip into a folder that looks like this.

![image](https://user-images.githubusercontent.com/2152766/117801629-73809f80-b24c-11eb-83ee-c5b548a8c2f0.png)

<br>

### Activate

Next we'll need to activate the server.

```bash
TurboFloatServer.exe -a="YOUR-SERIAL-NUMBER"
```

There should be no output from the command, unless there's a problem.

??? question "No internet?"
    The licence server can be activated offline.

    - See [Can I activate my server offline?](#can-i-activate-my-server-offline)

Now you're ready to launch the server!

<br>

### Start

This next command will launch the server in the current PowerShell or cmd.exe terminal you are in.

```bash
TurboFloatServer.exe -x
# Floating license server for Ragdoll Dynamics (TFS v4.4.3.0)
```

!!! hint "Test"
    This is a good place to test Ragdoll from within Maya, so [scroll to the Maya section](#maya), test it out and then come back here to finish things up.

All good? Great.

In order for the server to run in the background, and restart itself whenever the machine reboots, you'll need to install it as a "service".

```bash
TurboFloatServer.exe -i
# 2021-05-12, 07:47:26 <error>: OpenSCManager failed (5)
```

To do that, you'll need to launch PowerShell/cmd as **Administrator**.

```bash
# As Administrator
TurboFloatServer.exe -i
# 2021-05-12, 07:48:40 <notification>: Service installed successfully.
```

From here you can try launching Ragdoll Dynamics in Maya to see whether it manages to successfully lease a licence.

**More Details**

- [Installation Options](https://wyday.com/limelm/help/turbofloat-server/#install)
- [Configuration Options](https://wyday.com/limelm/help/turbofloat-server/#config)

<br>

## Maya

With a licence server running, your next step is having Ragdoll connect to it.

On each platform, the procedure is the same.

- Set `RAGDOLL_FLOATING`
- Load plug-in

**Example**

```py
# From Python
os.environ["RAGDOLL_FLOATING"] = "127.0.0.1:13"
cmds.loadPlugin("ragdoll")
```

```bash
# From an environment like bash
export RAGDOLL_FLOATING=127.0.0.1:13
maya
```

The format of `RAGDOLL_FLOATING` is `<ip-address>:<port-number>`.

<br>

## Python

Just like with a node-locked licence, you can control the leasing of licences via Python.

```py
from ragdoll import licence

# Activate this machine
licence.request_lease()

# Deactivate this machine
licence.drop_lease()
```

<br>

## FAQ

Let's cover some common scenarios.

<br>

### Can I activate my server offline?

Yes.

Like node-locked licences, the floating licence server can be activated without an internet connection to the machine running the server.

The procedure is the same on each platform.

1. Generate an activation request
2. Send activation request to licencing@ragdolldynamics.com
3. Activate with activation response

```bash
./turbofloatserver -areq="~/ActivationRequest.xml" -a="YOUR-SERIAL-NUMBER" 
./turbofloatserver -aresp="~/ActivationResponse.xml" -a
```

<br>

### What happens when my server is offline?

Leasing will attempt to connect for about 2 seconds until giving up. During that time, Maya may appear frozen.

<br>

### What happens when my server *goes* offline?

Leasing is re-done once every 30 minutes.

30 minutes is the default value (see below), which means that if the server goes down whilst an artist is using it, the solver will be disabled within 30 minutes.

The duration can be adjusted, however it is a balance since the time is also how long it takes for the server to free a realise as a result of a Maya crash.

- See [What happens to a lease when Maya crashes?](#what-happens-to-a-lease-when-maya-crashes)

<br>

### Can I change the port used by the server?

Yes.

The default port is `13` and can be edited via the `TurboFloatServer-config.xml` file residing in the same directory as the server executable.

```xml
<?xml version="1.0" encoding="utf-8"?>
<config>
    ...
    <bind port="666"/>
    ...
</config>
```

- [More Configuration Options](https://wyday.com/limelm/help/turbofloat-server/#config)

<br>

### Can I disable the splash screen?

Yes.

Consumers of floating licences generally won't need to manage licenses themselves, and so the startup dialog can be avoided altogether for a smoother experience when inside of Maya.

```bash
export RAGDOLL_NO_STARTUP_DIALOG=1
maya
```

- See [Environment Variables](/api/#environment-variables) for details

<br>

### What happens to a lease when Maya crashes?

A lease is automatically dropped upon unloading the plug-in or shutting down Maya. In the event of a Maya crash, a lease will automatically drop after 30 minutes per default.

The time can be edited via the configuration file; a lower time means more compute and file resources are consumed on the server, the lowest value is 30 seconds.

```xml
<?xml version="1.0" encoding="utf-8"?>
<config>
    ...
    <lease length="30"/><!-- seconds -->
    ...
</config>
```

<br>

### Can I fall back to a node-locked licence?

Yes.

Remove the `RAGDOLL_FLOATING` environment variable and reload the plug-in or restart Maya to attempt activation of a node-locked licence.

<br>

### Can I monitor my licence server?

Yes.

With a logging level set to "notification", you'll get real-time output from the server whenever a lease is requested and dropped, including..

1. Time of event
1. Expiry time
1. IP
1. Username
1. PID (Process ID)

The expiry is when the lease will be renewed. Normally not something you need to worry about, unless Maya crashes. This is then the time it'll take the server to realise the lease has been freed.

```xml
<?xml version="1.0" encoding="utf-8"?>
<config>
    ...
    <log file="tfs-log.txt" level="notification"/>
    ...
</config>
```

```bash
2021-05-12, 11:58:47 <notification>: New connection from IP: ::ffff:127.0.0.1
2021-05-12, 11:58:47 <notification>: New lease assigned (marcus, 1, IP=::ffff:127.0.0.1, PID=14328). Expires: 2021-05-12 11:28:47 (in UTC). Used / Total leases: 1 / 1
2021-05-12, 11:58:51 <notification>: New connection from IP: ::ffff:127.0.0.1
2021-05-12, 11:58:51 <notification>: Lease was released by client (marcus, 1, IP=::ffff:127.0.0.1, PID=14328). Used / Total leases: 0 / 1
```

A Python and web interface to this will be part of a future release, but the formatting can be relied upon for building your own monitoring mechanism.

<br>

### What does the server say when a lease request is rejected?

With `level="notification"` it'll say this.

```bash
2021-05-16, 14:52:50 <notification>: License lease request rejected because no more free slots, numTotalLics=9, pkey=YOUR-SERIAL-NUMBER
```
