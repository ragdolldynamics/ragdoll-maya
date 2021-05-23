## UI and Resolution Scaling

Read about how Ragdoll implements resolution scaling, to support scalable UIs on modern high-resolution displays.

<br>

### TL;DR

Here's a standalone version of the function I'll be walking you through, requires Maya 2017 (Qt 5) and above (due to `QScreen`).

```py
def px(value):
    if not hasattr(px, "dpi"):
        any_widget = QtWidgets.QWidget()
        any_widget.setWindowFlags(QtCore.Qt.ToolTip)
        any_widget.show()
        window = any_widget.windowHandle()
        scale = window.screen().logicalDotsPerInch() / 96.0
        px.dpi = scale

    return value * px.dpi
```

<br>

### What is Resolution Scaling?

Most displays have resolutions beyond the traditional 1080p, which makes text and graphics overly small. To account for this, operating systems have implemented "resolution scaling"; which is some factor to scale text and graphics by when drawing it on screen.

Maya added (early and crude) support for resolution scaling in Maya 2016 with a usable and mostly transparent version landing in 2018 and beyond.

Building UIs with Maya's native MEL-based UI tools account for scaling automatically, so you generally don't have to think about it. Unfortunately, for any non-trivial Qt project however you'll need to actively implement and maintain support for it.

Ragdoll does this, and here's how.

<br>

### Implementation

In short, any mention pixels run through a conversion function like this.

```py
# setFixedWidth(50)    # Before
setFixedWidth(px(50))  # After
```

Where `px()` looks something like this.

```py
def px(value):
	return value * 1.5
```

That goes for stylesheets as well.

```py
style = """
	QPushButton {
		width: 50px;
	}
"""
style = convert_px(style)
setStyleSheet(style)
```

Where `convert_px()` looks something like..

```py
def convert_px(style):
	lines = []
	for line in style.splitlines();
		if "px" in line:
			# Find them and destroy them
	return "\n".join(lines)
```

But where does this magical `1.5` value come from? The value depends on your display scale factor, or more precisely whichever scale factor Maya is currently working with.

On Windows, the scale factor is set under your Display settings and Linux's various display managers have something like it.

<img width=300 src=https://user-images.githubusercontent.com/2152766/102087648-c6773780-3e11-11eb-8c38-4131267576f1.png>

You can read this straight from the operating system, but the more cross-platform method would be to lean on Qt. Unfortunately, the Qt documentation for resolution scaling is a good representation of how *confusing* resolution scaling is amongst UI developers at large.

- https://doc.qt.io/qt-5/highdpi.html

Because you have (1) an application scale, (2) an operating system scale and (3) a physical monitor scale; each of which combine in non-obvious ways to produce the final pixel coordinate on screen.

What is the difference between "Physical DPI" and "Logical DPI"? Where does "Device Pixel Ratio" come into the picture?

Here's what you need to know.

```py
scale = logicalDpi / 96.0
```

The value you'll end up with is `1.0` for a non-scaled display, such as your everyday 1080p monitor, and `1.5` or `2.0` for greater resolutions. If your OS allows, you could get values inbetween or greater, and although text scales somewhat well to any value, graphics shipped with Ragdoll is scaled at `2.0` which means it'll look best at `1.0`, `1.5` and `2.0`. Anything else will likely introduce blur.

But wait, where does `logicalDpi` come from, and what's this magical `96.0`?

Qt can provide that for you, but not without a fight.

```py
window.
```
