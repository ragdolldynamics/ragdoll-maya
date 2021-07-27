import io
import re
import os
import sys
import json
import markdown as md

from mkdocs.plugins import BasePlugin

import ragdoll


MENU_HEADER = """\
|Item | Description
|:----|:---------\
"""

MENU_TEMPLATE = """\
| <nobr>{icon} {label}</nobr> | {summary}\
"""

DETAILS_TEMPLATE = """\
{description}
{videos}
{options}
"""

VIDEO_TEMPLATE = """
<img src=/{video}>
"""

OPTIONS_HEADER = """\
| Option             | Description | Default
|:-------------------|:------------|:-------\
"""

OPTION_TEMPLATE = """\
| {label}            | {help} | <nobr>{default}</nobr>\
"""

ATTRIBUTES_HEADER = """\
| Attribute          | Description | Type
|:-------------------|:------------|:------\
"""

ATTRIBUTE_TEMPLATE = """\
| `.{longName}`     | {help}      | <nobr>`{type}`</nobr>\
"""

DETAILED_ATTRIBUTES_HEADER = """\
| Attribute          | Description | Keyable | Type | Default
|:-------------------|:------------|:--------|:-----|:--------\
"""

DETAILED_ATTRIBUTE_TEMPLATE = """\
| `.{longName}` | {help} | {keyable} | <nobr>`{type}`</nobr> | {default}\
"""

MEDIA_TEMPLATE = """\
??? example "{label}"
    <div class="overlaid-media">
        <img src=/{fname}>
        <div class="overlaid-background"></div>
        <div class="overlaid-container">
            <h3>{label}</h3>
            <p>{description}</p>
        </div>
    </div>
"""


def _resource(*fname):
    dirname = os.path.dirname(ragdoll.__file__)
    resdir = os.path.join(dirname, "resources")
    return os.path.normpath(os.path.join(resdir, *fname))


def _page(*path):
    dirname = os.getcwd()  # Assume root of docs/
    return os.path.normpath(os.path.join(dirname, "pages", *path))


def camel_to_title(text):
    """Convert camelCase `text` to Title Case

    Example:
        >>> camel_to_title("mixedCase")
        "Mixed Case"
        >>> camel_to_title("myName")
        "My Name"
        >>> camel_to_title("you")
        "You"
        >>> camel_to_title("You")
        "You"
        >>> camel_to_title("This is That")
        "This Is That"

    """

    return re.sub(
        r"((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))",
        r" \1", text
    ).title()


def menu_all(markdown):
    """Convert the {{ menu:all }} instances"""

    with open(_resource("menu.json")) as f:
        menu = json.load(f)
        menu.pop("#", None)  # Exclude comments

    def icon(item):
        return (
            "<img class=\"invertme icon\" width=20 src=/icons/{icon}>"
            if "icon" in value else "<p class=\"filler icon\"></p>"
        ).format(**value)

    rows = []
    for key, value in menu.items():

        # Don't bother documenting what can't be used
        if not value.get("enable", True):
            continue

        row = MENU_TEMPLATE.format(**{
            "label": value.get("label", camel_to_title(key)),
            "icon": icon(value),
            "summary": value.get("summary", ""),
        })

        rows += [row]

    replace = os.linesep.join([
        MENU_HEADER,
        "\n".join(rows)
    ])

    markdown = re.sub(
        r"\{\{(\s)*menu:all(\s)*\}\}", replace, markdown,
        flags=re.IGNORECASE
    )

    return markdown


def menu(markdown):
    """Convert the {{ menu.<any> }} instances"""

    def options(item):
        lines = []

        for option in item.get("options", ["noOptions"]):
            option = Options.get(option, None)

            if not option:
                continue

            if option["type"] == "Separator":
                continue

            default = option.get("default", "")
            default = ("`%s`" % default) if default else ""
            option = OPTION_TEMPLATE.format(
                label=option.get("label", camel_to_title(option["name"])),
                help=option.get("help", ""),
                default=default
            )

            lines += [option]

        lines = os.linesep.join(lines)
        return os.linesep.join([OPTIONS_HEADER, lines])

    def description(item):
        desc = item.get(
            "description", item.get(
                "summary", ""
            )
        )

        return desc + "\n\n"

    def media(item):
        videos = []
        for media in item.get("media", []):
            videos += [MEDIA_TEMPLATE.format(**media)]
        return os.linesep.join(videos)

    with open(_resource("menu.json")) as f:
        Menu = json.load(f)
        Menu.pop("#", None)  # Exclude comments

    with open(_resource("options.json")) as f:
        Options = json.load(f)
        Options.pop("#", None)  # Exclude comments
        Options["noOptions"] = {
            "name": "noOptions",
            "type": "Boolean"
        }

    lines = markdown.splitlines()

    for index, line in enumerate(lines.copy()):
        if not line.startswith("{{ menu."):
            continue

        key = line.rstrip()
        key = key.strip("{").strip(" ").rstrip("}").rstrip(" ")
        key = key.split(".", 1)[-1]  # E.g. activeRigid.options
        key, element = key.split(".")

        if key not in Menu:
            # Docs and code are out of date, not good
            sys.stderr.write(
                "WARNING: '%s' was referenced in the documentation, "
                "but wasn't found in menu.json, this is a problem.\n"
                % key
            )
            continue

        item = Menu[key]

        if element == "description":
            lines[index] = description(item)

        if element == "options":
            lines[index] = options(item)

        if element == "media":
            lines[index] = media(item)

    return os.linesep.join(lines)


def attributes(markdown):
    def attributes(node, detailed=True):
        with open(_resource("%s.json" % node)) as f:
            Node = json.load(f)

        lines = []
        for _, attr in sorted(Node["attributes"].items()):
            animated = (
                attr.get("keyable", False) or
                attr.get("animated", False)
            )

            if not detailed and not animated:
                continue

            description = ""
            if "summary" in attr:
                description = (
                    "<p class=\"summary\">%s</p>"
                    % attr["summary"]
                )

                description = attr["summary"]

                if "description" in attr:
                    description += " " + attr["description"]

            description = md.markdown(description)
            description = description[3:-4]  # Remove the surrounding `<p>`

            if "default" in attr:
                default = attr["default"]
                if isinstance(default, (tuple, list)):
                    default = "<br>".join(map(str, default))
                else:
                    default = "%s" % attr["default"]
            else:
                default = ""

            kwargs = {
                "shortName": attr["shortName"],
                "longName": attr["longName"],
                "help": description,
                "type": attr["type"],
                "keyable": "✔️" if attr.get("animated", False) else "",
                "default": default,
            }

            if detailed:
                line = DETAILED_ATTRIBUTE_TEMPLATE.format(**kwargs)
            else:
                line = ATTRIBUTE_TEMPLATE.format(**kwargs)

            lines += [line]

        lines = os.linesep.join(lines)

        if detailed:
            return os.linesep.join([DETAILED_ATTRIBUTES_HEADER, lines])
        else:
            return os.linesep.join([ATTRIBUTES_HEADER, lines])

    lines = markdown.splitlines()

    for index, line in enumerate(lines.copy()):
        if not line.startswith("{{ node."):
            continue

        key = line.rstrip()
        key = key.strip("{").strip(" ").rstrip("}").rstrip(" ")
        key = key.split(".", 1)[-1]  # E.g. activeRigid.options
        key, element = key.split(".")

        if element == "attributes":
            lines[index] = attributes(key, detailed=True)

        if element == "keyableAttributes":
            lines[index] = attributes(key, detailed=False)

    return os.linesep.join(lines)


def releases(markdown):
    """Convert {{ releases }}"""

    def find_title(fname):
        with io.open(fname, "r", encoding="utf8") as f:
            max_lines = 5
            for index, line in enumerate(f):

                if not line.startswith("title:"):
                    continue

                title = line.split("title:", 1)[-1].strip(" ").rstrip()
                return title

                if index > max_lines:
                    break

        raise ValueError("Couldn't find title of %s" % fname)

    rows = []
    for version, fname in get_releases():

        # Find title
        title = find_title(fname)

        rows.append(
            "- [{version} - {title}](/releases/{version})".format(
                version=version, title=title
            )
        )

    replace = os.linesep.join(rows)

    markdown = re.sub(
        r"\{\{(\s)*releases(\s)*\}\}", replace, markdown,
        flags=re.IGNORECASE
    )

    return markdown


def meta(markdown, page, config):
    for key, value in page.meta.items():
        if "page.meta.%s" % key not in markdown:
            continue

        markdown = re.sub(
            r"\{\{(\s)*page.meta.%s(\s)*\}\}" % key, value, markdown,
            flags=re.IGNORECASE
        )

    for key, value in config.data.items():
        if "config.%s" % key not in markdown:
            continue

        markdown = re.sub(
            r"\{\{(\s)*config.%s(\s)*\}\}" % key, value, markdown,
            flags=re.IGNORECASE
        )

    return markdown


def get_releases():
    releases_dir = _page("releases")

    for root, dirs, fnames in os.walk(releases_dir):
        for fname in reversed(fnames):
            if not fname.endswith(".md"):
                continue

            version = fname.rsplit(".md", 1)[0]
            yield version, os.path.join(root, fname)


class MenuGeneratorPlugin(BasePlugin):
    def __init__(self):
        self.enabled = True
        self.latest_version = list(get_releases())[0][0]

    def on_page_markdown(self, markdown, page, config, files):
        if not self.enabled:
            return markdown

        config.data.update({
            "latest_version": self.latest_version,
        })

        if page.title == "Menu Reference":
            markdown = menu_all(markdown)
            markdown = menu(markdown)

        if "nodes" in page.url.lower():
            markdown = attributes(markdown)

        markdown = meta(markdown, page, config)

        if page.title == "Releases":
            markdown = releases(markdown)

        return markdown

    def on_config(self, config):
        section = next(
            entry for entry in config["nav"]
            if "Release History" in entry
        )["Release History"]

        # Start from scratch
        section[:] = []

        for version, _ in get_releases():
            section.append(
                {version: "releases/%s.md" % version}
            )

        return config
