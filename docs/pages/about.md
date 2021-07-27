Here's a brief overview of how Ragdoll came to be.

**In 2008** Marcus graduated from Blekinge Tekniska Högskola and ventured into the world as character animator at Meindbender; to work on [The Duplicators](https://www.youtube.com/watch?v=mAhSwlFW5r8) and [The Pirate](https://vimeo.com/22342702) amongst others.

**In 2012** He joined Framestore and familiarised himself with the world of physics simulation, developing the technology behind the [*tethers*](https://youtu.be/FZfOvvGV5Q4?t=64) for Alfonso Cuaron's feature film Gravity, and later completed work on the Cloak of Leviation in Doctor Strange.

**In 2015** He started a company called Abstract Factory developing tools in Python for use in production pipelines, including [Avalon](getavalon.github.io/), [Pyblish](https://pyblish.com/), [Qt.py](https://github.com/mottosso/Qt.py), [cmdx](https://github.com/mottosso/cmdx) and [Allzpark](allzpark.com/); later recieving the ["Best Tool" award](https://forums.pyblish.com/t/pyblish-award-2020-the-pipeline-conference/618) for Pyblish at the 2020 DigiPro/The Pipeline Conference.

**In 2017** He started a company called [WeightShift](https://www.youtube.com/watch?v=YR3hvaY-0hQ) with co-founders Danny Chapman and Tim Daust. They had just wrapped up the [Endorphin](https://www.youtube.com/watch?v=xbDd8PH9jio) and [Euphoria](https://www.youtube.com/watch?v=ATr38G2hR5Y) projects at Natural Motion.

Like Euphoria, WeightShift developed a physically based animation tool, except this one was tailed to Autodesk Maya and got adopted by major feature film studios including Framestore (Harry Potter, Gravity et. al.) and Weta Digital (Avatar, Lord of the Rings et. al.)

**In 2020** WeightShift is purchased by Epic Games

**In 2020** `Ragdoll enters chat`

Ragdoll carries on where WeightShift left off, but turns things on its head. Rather than targeting riggers and technical animators, Ragdoll adopts a "no-rigging required" approach.

**July 28th 2021** Ragdoll is launched.

<br>

### London on Craigslist

In 2012, Marcus travelled to London after 5 years of character animation experience in Sweden and £15,000 of life savings in order to secure a job at Framestore, the studio he'd been looking up to since before venturing out into the real-world. He booked a crummy hotel around Hyde Park for 2 weeks during which time he expected to find a permanent residence somewhere in town, but it wasn't so easy! After days of viewing flats and hours *after* finally checking out - in desperation - he transferred a majority of his life savings for 6 months of rent up-front to a listing he found on *Craigslist*. That luckily *wasn't* a scam.

With his foot firmly on the ground, Marcus applied to work for Framestore; only to find that they weren't looking for animators! Instead, they needed "Creature FX" artists, to begin work right away on a project taking place in space. Creatures? In space? Done deal! That's when he learned that "creature" actually meant "tether" and FX means "simulation" and that the project was Gravity.

<img class="poster" src=https://user-images.githubusercontent.com/2152766/97847281-4c6a7380-1ce7-11eb-8b37-f1909121d0c4.png>

It was during that time when the character animator was introduced to *physics simulation* and with it an idea to bring this marvel of technology to the otherwise non-physically simulated world of character animation.

<br>

### Early Prototypes

With Maya and nCloth under his belt, he had all the tools necessary to begin working on an adaptation for animators. Or so he thought!

!!! information "First Prototype"
    Utilising the `Bend Resistance` and `Attract to Matching Mesh` features of nCloth. The challenge was tailoring the edges such that they carried the weight of the character and the motion he was to perform. More rigidity meant less performance, thus he always ended up too squishy.

<video controls loop width="100%">
   <source src="https://user-images.githubusercontent.com/2152766/127107247-0c134529-3958-46b2-8100-958e12cee4d7.mov" type="video/mp4">
</video>

<br>

!!! information "nCloth to IK"
    This time using follicles on the simulated geometry to derive positions for a skeleton to be attached and used to skin the final character geometry. Don't let the fps counter fool you, this version was point-cached. The interactive performance was less than 5 fps.

<video controls loop width="100%">
   <source src="https://user-images.githubusercontent.com/2152766/127107237-88ffac31-3e4e-468e-b1ec-98d5ac1eeac7.mov" type="video/mp4">
</video>

<br>

!!! information "Alternative Setup"
    Same idea, now interacting with another nCloth object in the scene.

<video controls loop width="100%">
   <source src="https://user-images.githubusercontent.com/2152766/127107228-65754bf9-1257-4fc6-b0f5-65cff47fb3d7.mp4" type="video/mp4">
</video>

<br>

A few prototypes later, he realised this wasn't going to fly. To tackle this, one would need a firm grasp on software development, but that would take time.

As they say; two steps forward, one step back.

<br>

### "Let's start small"

Inspired by the manner and amount of automation taking place at Framestore, he set out to bring automation to the masses, using skills less reliant on maths and algorithms and more reliant on workflow.

[![logo_macaw_extrasmall](https://user-images.githubusercontent.com/2152766/97844201-84bb8300-1ce2-11eb-840c-4a7734ca1bfe.png)](https://pyblish.com)

3 years later, [Pyblish](https://pyblish.com) is a technically and practically successful product, another 3 years it would go on to win the DigiPro 2020 award for [**Best Pipeline Tool**](https://forums.pyblish.com/t/pyblish-award-2020-the-pipeline-conference/618), even though it would yield very little money; lessons learnt in running a business on open-source software. (Namely *don't*)

He was now somewhat technically savvy with a greater understanding of the challenge that lies ahead, what he needed now was a team.

<br>

### Team Avalon

Building on his prior connections in Sweden, he reached out to the founders of a former workplace for aid. They were interested in branching out into software development and was a suitable customer to the technology I had in mind; they offered to invest. By happenstance, he found a character rigger with multiple feature film projects behind her, interested in trying something new. Finally, the technology was to be based heavily on machine learning for which he found a lecturer at Oxford University interested in dedicating time and resources to our cause.

Months of pitching at events in search for a team ([Startup Weekend](https://www.techstars.com/communities/startup-weekend) ftw!), everything was now in place. But there was a hitch; in order to offer investment, they wanted something in return. A pipeline. Marcus spent the next 3 months developing [Avalon](https://getavalon.github.io), which was later open sourced and is now a moderately successful pipeline framework powering dozens of studios around the globe, including [Colorbleed](https://colorbleed.nl), [Moonshine](https://www.moonshine.tw/) and [Kredenc](http://kredenc.studio/).

![27349489-58285f06-55ef-11e7-9229-b89320eae405](https://user-images.githubusercontent.com/2152766/97844330-baf90280-1ce2-11eb-9d05-c45ffffe8a2d.png)

Ready, set, go; the team was set, a customer waiting and investment ready to go. But there was a problem. After signing for a shared office space and days before moving in to start working, the investor couldn't live up to his end of the bargain and the deal blew up.

Two steps forward, one step back.

<br>

### Team Weightshift

After having to let everyone go, Marcus remembered one of the prospects he interviewed for this team; a senior figure at Natural Motion - developers of physics simulation software Endorphin and Euphoria - which was *just* about to be absorbed by the mobile-games goliath Zynga, scrapping their work on character animation technology.

They spent two weeks putting together a prototype of their aspirations and went on to form a company to develop [WeightShift Dynamics](https://www.youtube.com/playlist?list=PLpGVBr-jvPFtVfb4zbXH3kHuPUelZR6Vw)

<img class="poster" src=https://user-images.githubusercontent.com/2152766/97844530-1c20d600-1ce3-11eb-9a13-2e0caa7b1ba4.png>

2 years later and WeightShift had been adopted by **Weta Digital** in New Zealand and **Framestore** in London. But there was a hitch; visions no longer aligned, conflict arose and the team disbanded.

The silver lining was that Epic Games was interested purchasing the technology, providing enough of a runway to restart development and try again.

Two steps forward, one step back.

<br>

### Team Ragdoll

After a brief stint developing [Allzpark](https://allzpark.com) for the Japanese [Studio Anima](studioanima.co.jp/) and then animating for Redfall and Horizon Zero Dawn II at [Goodbye Kansas](goodbyekansasstudios.com) it was now 2020. With funding and experience spanning animation, programming, business and now physics all the pieces were in place. What he could not do in 2012 was now made possible.

<img class="poster" src=https://user-images.githubusercontent.com/2152766/127115947-18054044-e8f3-44b5-b23a-46650d02e64d.png>
