import io
import re
import os
import sys
import json
import markdown as md

from mkdocs.plugins import BasePlugin

import ragdoll

# Reloadable modules
import importlib
from . import parse_api

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

        if value.get("hidden"):
            continue

        if value.get("deprecated", False):
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


def releases(markdown, page):
    """Convert {{ releases }}"""

    rows = []
    for version, fname in get_releases():
        meta = get_metadata(fname)
        rows.append(
            "- [{version} - {title}](/releases/{version})".format(
                version=version, title=meta.get("title", ["Untitled"])[0]
            )
        )

    replace = os.linesep.join(rows)

    markdown = re.sub(
        r"\{\{(\s)*releases(\s)*\}\}", replace, markdown,
        flags=re.IGNORECASE
    )

    return markdown


def documentation(markdown, page):
    """Convert {{ documentation }}"""

    rows = []

    for root, dirs, fnames in os.walk(_page("documentation")):
        for fname in fnames:
            if not fname.endswith(".md"):
                continue

            name = fname.rsplit(".", 1)[0]
            path = os.path.join(root, fname)
            meta = get_metadata(path)

            if "hidden" in meta:
                continue

            if "title" not in meta:
                continue

            rows.append(
                "- [{title}](/documentation/{name})".format(
                    title=meta.get("title", ["Untitled"])[0], name=name
                )
            )

    replace = os.linesep.join(rows)

    markdown = re.sub(
        r"\{\{(\s)*documentation(\s)*\}\}", replace, markdown,
        flags=re.IGNORECASE
    )

    return markdown


def tutorials(markdown, page):
    """Convert {{ tutorials }}"""

    rows = []
    tutorials = []

    for root, dirs, fnames in os.walk(_page("tutorials")):
        for fname in fnames:
            if not fname.endswith(".md"):
                continue

            name = fname.rsplit(".", 1)[0]
            path = os.path.join(root, fname)
            meta = get_metadata(path)

            if "hidden" in meta:
                continue

            if "title" not in meta:
                print("%s had no title, skipping" % fname)
                continue

            try:
                order = meta["order"]

            except KeyError:
                raise ValueError("%s was missing the `order` attribute" % path)
            tutorials.append((order, name, meta))
        break

    for order, name, meta in sorted(tutorials, key=lambda i: i[0]):
        rows.append(
            "1. [{title}](/tutorials/{name})".format(
                title=meta.get("title", ["Untitled"])[0], name=name
            )
        )

    replace = os.linesep.join(rows)

    markdown = re.sub(
        r"\{\{(\s)*tutorials(\s)*\}\}", replace, markdown,
        flags=re.IGNORECASE
    )

    return markdown


def mp4(markdown, page):
    """Convert any .mp4 links into video players"""

    regex = r"\n\s+?(https\:\/\/[a-zA-Z0-9\.\/-]*.\.(mp4|mov))\s+([a-z ]*)?\n"

    def replace(match):
        # Get rid of surrounding newlines
        prefix = match.group(0).strip("\n").split("https://", 1)[0]
        url = match.group(1).strip().rstrip()
        extras = match.group(3).strip().rstrip()

        return (
            '\n{prefix}<p><video autoplay class="poster"'
            ' muted loop width=100% {extras}>'
            '<source src="{url}" type="video/mp4">'
            '</video></p>\n'
        ).format(prefix=prefix, url=url, extras=extras)

    markdown = re.sub(
        regex, replace, markdown,
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


def get_metadata(path):
    markdown = md.Markdown(extensions=["meta"])

    with io.open(path, "r", encoding="utf8") as f:
        markdown.convert(f.read())

    meta = markdown.Meta
    return meta


def get_releases():
    releases_dir = _page("releases")

    for root, dirs, fnames in os.walk(releases_dir):
        for fname in reversed(fnames):
            if not fname.endswith(".md"):
                continue

            abspath = os.path.join(root, fname)
            meta = get_metadata(abspath)

            if "hidden" in meta:
                continue

            version = fname.rsplit(".md", 1)[0]
            yield version, abspath


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
        markdown = mp4(markdown, page)

        if "api_reference" in page.url.lower():
            importlib.reload(parse_api)
            markdown = parse_api.parse(markdown, page)

        if page.title == "News":
            markdown = releases(markdown, page)

        if page.title == "Documentation":
            markdown = documentation(markdown, page)

        if page.title == "Tutorials":
            markdown = tutorials(markdown, page)

        return markdown

    def on_config(self, config):
        section = next(
            entry for entry in config["nav"]
            if "News" in entry
        )["News"]

        # Start from scratch
        section[:] = []

        for version, _ in get_releases():
            section.append(
                {version: "releases/%s.md" % version}
            )

        return config

    def on_page_content(self, html, page, config, files):
        print(page)
        return html
