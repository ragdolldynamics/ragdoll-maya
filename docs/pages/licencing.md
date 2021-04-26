<img class="boxshadow no-max-height" src=https://user-images.githubusercontent.com/47274066/103476508-7d7e2780-4dae-11eb-86c9-c099a08f1314.png>

Each instance of Ragdoll requires an individual licence.

Activation requires a `Product Key` which you get by either [purchasing a licence](https://ragdolldynamics.com/pricing) or by being really awesome.

<br>

## FAQ

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

#### Can I open scenes made with the trial version in the commercial version?

No.

Files made with the trial version will appear scrambled with a commercial version. The trial version is however able to use files saved with a commercial version.

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

Yes.

See [Offline Activation](#offline-activation) below.

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

## Licence API

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

# Activation for those without access to Internet
licence.activation_request_to_file(key, fname)
licence.activate_from_file(fname)

# Deactivate whatever key is currently activated
licence.deactivate()

# Deactivate offline, to e.g. move a licence from one machine to another
licence.deactivation_request_to_file(fname)

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

<br>

## Offline Activation

Haven't got no internet?

No problem, here's what you need to do.

1. Generate an "activation request", a file
2. Send us this file, via [email](mailto:licencing@ragdolldynamics.com)
3. Receive a "activation response", another file
4. Activate using this file

It requires pasting some *Python* commands into the **Maya Script Editor**.

**Generate Request**

```py
from ragdoll import licence
key = "YOUR-VERY-LONG-KEY-HERE"
fname = r"c:\ragdoll_activation_request.xml"
licence.activation_request_to_file(key, fname)
```

**Email Us**

Send this file to licencing@ragdolldynamics.com. We'll abrakadabra this file before you can say [Taumatawhakatangi­hangakoauauotamatea­turipukakapikimaunga­horonukupokaiwhen­uakitanatahu](https://en.wikipedia.org/wiki/Taumatawhakatangi%C2%ADhangakoauauotamatea%C2%ADturipukakapikimaunga%C2%ADhoronukupokaiwhen%C2%ADuakitanatahu).

**Activate**

Once you've got a response, activate your licence like this.

```py
from ragdoll import licence
fname = r"c:\ragdoll_activation_response.xml"
licence.activate_from_file(fname)
```

<br>

## Offline Deactivation

Licences are node-locked (floating licences coming soon), which means that if you need to move a licence from one machine to another you can do so by *deactivating* an activated licence, and then activating it elsewhere.

The process is similar to activation.

**Generate Request**

```py
from ragdoll import licence
fname = r"c:\ragdoll_deactivation_request.xml"
licence.deactivation_request_to_file(fname)
```

**Email Us**

Send this file to licencing@ragdolldynamics.com. Once we have confirmed receipt of this file, you will be able to re-activate Ragdoll on another machine.

<br>

## Offline Licence Roadmap

Apologies for the tedious nature of offline licence management at the moment! Not long from now, you will be able to manage your licences *online* without sending any emails.
