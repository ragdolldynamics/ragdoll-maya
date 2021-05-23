# Usage: ./serve.ps1
rez env -e "PYTHONPATH=$(pwd)/plugins;$(pwd)/../" `
    git `
    nltk `
    python-3.9 `
    mkdocs_material-6.1.6 `
    mkdocs_git_revision_date_plugin==0.3.1 -- `
    mkdocs serve -a localhost:8002 $args
