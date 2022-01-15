import os
import re


def parse(markdown, page):
    """Convert {{ api }}"""

    try:
        from ragdoll import api
    except ImportError:
        return markdown

    import inspect

    constants = []

    overview = []
    overview.append("| Function | Description")
    overview.append("|:---------|:------------")

    for name in api.__all__:
        func = getattr(api, name)
        summary = ""

        if not callable(func):
            constants.append((name, func))
            continue

        doc = inspect.getdoc(func)

        if doc:
            summary = doc.splitlines()[0]

        overview.append("| **{func}** | {summary}".format(
            func=name,
            summary=summary
        ))

    details = []
    for name in api.__all__:
        func = getattr(api, name)
        summary = ""

        if not callable(func):
            continue

        doc = inspect.getdoc(func)

        if doc:
            summary = doc.splitlines()[0]

        args = [
            a for a in inspect.getargspec(func)[0]
            if a not in ("self", "cls")
        ]

        details.append("#### %s" % name)
        details.append("")
        details.append(summary)
        details.append("")

        details.append("```py")
        details.append("def %s(%s):" % (name, ", ".join(args)))
        lines = doc.splitlines()
        lines[0] = '"""' + lines[0]
        lines.append("")
        lines.append('"""')
        for lines in lines:
            details.append("    %s" % lines)
        details.append("```")
        details.append("<br>")

    constants2 = []
    constants2.append("| Constant | Value")
    constants2.append("|:---------|:---:|")
    for constant, value in constants:
        constants2.append("| %s | %s" % (constant, value))

    replace = os.linesep.join(overview)
    markdown = re.sub(
        r"\{\{(\s)*api:overview(\s)*\}\}", replace, markdown,
        flags=re.IGNORECASE
    )

    replace = os.linesep.join(details)
    markdown = re.sub(
        r"\{\{(\s)*api:details(\s)*\}\}", replace, markdown,
        flags=re.IGNORECASE
    )

    replace = os.linesep.join(constants2)
    markdown = re.sub(
        r"\{\{(\s)*api:constants(\s)*\}\}", replace, markdown,
        flags=re.IGNORECASE
    )

    return markdown
