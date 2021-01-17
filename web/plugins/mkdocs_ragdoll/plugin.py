import os
import sys
import tempfile
import subprocess

from mkdocs import plugins, structure


class CompileSCSSPlugin(plugins.BasePlugin):
    def on_files(self, files, config):
        """Build our precious SCSS"""

        assets = os.path.join(os.getcwd(), "theme", "assets")
        scss = os.path.join(assets, "scss")

        # We can't modify anything in our source directory,
        # as it would cause an infinite loop of building,
        # generating, building, generating, etc.
        tempdir = tempfile.gettempdir()
        theme = os.path.join(scss, "theme.scss")
        out = os.path.join(tempdir, "theme.css")

        sys.stdout.write("Compiling %s -> %s.." % (theme, out))
        if subprocess.check_call(["pysassc", theme, out]) != 0:
            sys.stdout.write(" failed\n")
            return files
        else:
            sys.stdout.write("\n")

        file = structure.files.File(
            "theme.css",
            src_dir=tempdir,
            dest_dir=os.path.join(config["site_dir"], "assets", "css"),
            use_directory_urls=False
        )

        files.append(file)

        return files
