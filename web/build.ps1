rez env -e "PYTHONPATH=$(pwd)/plugins" `
    nltk `
    mkdocs `
    libsass `
    -- mkdocs build

copy-item ./CNAME site/