# Usage: .\deploy.ps1 c:\path\to\site
Write-Host "Building website.."
rez env -e "PYTHONPATH=$(pwd)/plugins" `
    python-3.9 `
    git `
    nltk `
    mkdocs `
    libsass `
    mkdocs -- `
    mkdocs build --site-dir $args[0]

copy-item .\CNAME $args[0]
copy-item .\.nojekyll $args[0]

Write-Host "Uploading website.."
pushd $args[0]
git add --all
git commit -m "Update website"
git push
popd

Write-Host "Success!"
