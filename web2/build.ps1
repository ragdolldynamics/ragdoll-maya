# Usage: .\build.ps1 c:\path\to\site
Write-Host "Building docs.."
rez env -e "PYTHONPATH=$(pwd)/plugins;$(pwd)/../" `
    git `
    nltk `
    python-3.9 `
    mkdocs_material-6.1.6 -- `
    mkdocs build --site-dir $args[0]

Write-Host "Success!"
