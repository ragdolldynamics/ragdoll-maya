![gumtree_cover](https://user-images.githubusercontent.com/2152766/104089559-f6c2c200-5267-11eb-8297-67552c8f6aeb.png)

Character animation tools for Autodesk Maya 2018-2022 that enable automatic overlapping animation through high-performance rigid-body simulation techniques. 

<br>

### Usage

This repository contains the Python package associated with the commercial *compiled* plug-in for Maya.

**Read more**

- https://ragdolldynamics.com
- https://learn.ragdolldynamics.com/releases/2021.03.25

<br>

### Open Source

Some of the work in Ragdoll has been separated out into its own smaller projects.

- [cmdx](https://github.com/mottosso/cmdx)
- [qargparse](https://github.com/mottosso/qargparse.py)
- [qjsonmodel](https://github.com/dridk/QJsonmodel)

<br>

### Repository

All Maya integration and user-facing tooling is stored in this repository. It's here to better help you *integrate* and *extend* the project to fit your specific pipeline, and similar to my other [open-source projects](https://mottosso.com) facilitate PRs and the opportunity to take matters into your own hands. You've also got access to the commercial website and learning material to facilitate contributions and fixes.

| Path    | Description
|:--------|:------------
| ragdoll | The Ragdoll Python package
| web     | Source for https://ragdolldynamics.com
| docs    | Source for https://learn.ragdolldynamics.com

<br>

### Contributing to Documentation

Alongside the Python package, this repository also contains the documentation for Ragdoll, which you can build and preview locally prior to making a contribution.

From PowerShell on Windows, call each line below.

```pwsh
iwr -useb get.scoop.sh | iex
scoop install python git
python -m pip install mkdocs_git_revision_date_plugin
python -m pip install git+https://github.com/mottosso/mkdocs-material-design.git
git clone https://github.com/mottosso/ragdoll.git
cd ragdoll/docs
.\serve.bat
```

> On Linux, use `serve.sh` instead of `serve.bat`

Documentation should now be accessible at http://localhost:8000. Whenever you edit any Markdown document under `ragdoll/docs/pages`, the website will automatically be rebuilt and your browser refreshed. It might take a few seconds.
