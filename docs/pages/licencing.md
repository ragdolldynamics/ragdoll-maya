<img class="boxshadow no-max-height" src=https://user-images.githubusercontent.com/47274066/103476508-7d7e2780-4dae-11eb-86c9-c099a08f1314.png>

Ragdoll requires a licence per seat in order to run.

Activation requires a `Product Key` which you get by either [purchasing a licence](https://ragdolldynamics.com/pricing) or by being really awesome.

<br>

### FAQ

Let's dive into specifics.

<br>

#### How does it work?

On first launch, Ragdoll will try and connect to the Ragdoll Licence Server and register your trial version. This version is node-locked to the particular machine you are on.

Once you've acquired a product key, you can either:

1. Click the `Ragdoll` menu item (bottom)
2. Enter your product key
3. Click `Activate`

Or if you prefer:

```py
from ragdoll import licence
licence.activate(key)
```

If internet is unavailable, Ragdoll enters "offline mode" and expires at a fixed date. Each new release is given an updated expiry date.

<br>

#### What happens when my trial expires?

Any `rdScene.enabled` attribute will be set to `False`.

Scenes will still load just fine and nothing else in your scene is affected. Once activated, the `.enabled` attribute will return to normal.

<br>

#### Can I renew my trial licence?

Possibly.

Reach out to us if this is relevant to you. We're contemplating a permanently active "Personal Learning Edition" with limitations on what you can do commercially, similar to SideFX Houdini.

<br>

#### Can I use my licence on more than one machine?

Yes.

You can activate and use each Ragdoll licence on up to 3 machines. You just can't run a simulation on more than 1 at a time, that could lead to suspension of the licence.

<br>

#### Can I move a licence between two machines?

Yes.

If you've activated 3 licences, you can hit the `Deactivate` button (which is same as the `Activate` button once you've activated) and the activation will be released.

<br>

#### Do I need an internet connection to use Ragdoll?

No.

Activation can happen either offline or online, online happening from within Maya at the click of a button and offline being a 4-step process, [see below](#can-i-activate-offline).

<br>

#### What if someone steals my licence key?

That key is all that is required to run Ragdoll on any machine. If someone takes your key and activates 3 of their own machines, you won't be able to activate it yourself. If this happens, email us with proof of ownership (e.g. via the email used when purchasing) and you'll get a new one.

<br>

#### Can I have a floating licence?

Yep, get in touch with licencing@ragdolldynamics.com.

Later on, these will be as trivial as node-locked licences. All we need is you.

<br>

#### Can I activate offline?

Not yet.

As soon as someone needs it, I'll add it. Get in touch with licencing@ragdolldynamics.com

Offline will be a 4-step process.

1. Running e.g. `activation_request_to_file()` from you local machine
2. Emailing generated file 
3. Receiving a licence file back 
4. Running e.g. `activate_from_file(fname)` on the same local machine.

Floating offline is also be possible, again get in touch.

<br>

#### When exactly is internet required?

A connection is made in one of two separate occasions.

1. Calling `ragdoll.licence.install()`
2. On simulating any frame

`install()` is typically called on Maya startup when the plug-in is loaded and menu is installed. You can disable this.

That is, Maya can open a scene with Ragdoll in it without making a connection to the internet if neither of these things happen. This means you can simulate on one machine, bake or otherwise disable the solver and send it off to a farm (e.g. local or cloud) without worrying about licences.

The alternative would be having to erase any trace of Ragdoll from a scene which would be such a pain.

<br>

#### Can I manage my licence via Python?

Sure can, see below.

<br>

### Licence API

As a user, you'll generally use the UI. But the UI is ultimately making calls to Python (which is making calls to C++) and you can bypass the UI using these same calls.

```py
from ragdoll import licence

# Called once before calling any other licencing function
# This is automatically called on Ragdoll Python initialisation
# and simulation start, but needs calling manually if simulation
# hasn't yet started.
licence.install()

# Retrieve the currently activated product key
licence.current_key()

# Activate using your product ket
licence.activate(key)

# Deactivate whatever key is currently activated
licence.deactivate()

# Dictionary of useful information
data = licence.data()

{
	# Same as current_key
    "key": "Your-Key",

    # Is the current licence activated?
    "isActivated": True,

    # Is the current licence a trial licence?
    "isTrial": False,

    # Has the licence not been tampered with?
    "isGenuine": True,

    # Has the licence been verified with the server
    # (requires a connection to the internet)?
    "isVerified": True,

    # How many days until this trial expires?
    "trialDays": 23
}
```