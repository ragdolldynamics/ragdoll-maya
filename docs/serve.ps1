# Usage: ./serve.ps1
rez env -e "PYTHONPATH=$(pwd)/plugins;$(pwd)/../" `
    git `
    nltk `
    maya-2022 `
    importlib_metadata-4.10.0 `
    typing_extensions-4.0.1 `
    mkdocs_material-6.1.6 `
    mkdocs_git_revision_date_plugin==0.3.1 -- `
    mayapy -m mkdocs serve --dirtyreload -a localhost:8001 $args
