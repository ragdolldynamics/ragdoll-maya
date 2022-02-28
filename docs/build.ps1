# Usage: .\build.ps1 c:\path\to\site
Write-Host "Building docs.."
rez env `
    -e "PYTHONPATH=$(pwd)/plugins;$(pwd)/../" `
    git `
    nltk `
    maya-2022 `
    importlib_metadata-4.10.0 `
    typing_extensions-4.0.1 `
    mkdocs_material-6.1.6 `
    mkdocs_git_revision_date_plugin==0.3.1 -- `
    mayapy -m mkdocs build --site-dir $args[0]

copy-item .\CNAME $args[0]
copy-item .\.nojekyll $args[0]

Write-Host "Uploading docs.."
pushd $args[0]
git add --all
git commit -m "Update docs"
git push
popd

Write-Host "Success!"
