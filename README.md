![gumtree_cover](https://user-images.githubusercontent.com/2152766/104089559-f6c2c200-5267-11eb-8297-67552c8f6aeb.png)

Character animation tools for Autodesk Maya 2018-2020 that enable automatic overlapping animation through high-performance rigid-body simulation techniques. 

<br>

### Usage

This repository contains the Python package associated with the commercial *compiled* plug-in for Maya.

**Read more**

-  https://ragdolldynamics.com

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

1. Install Python (3.9)
2. Install git (latest)
3. Run the below

```bash
$ pip install mkdocs_git_revision_date_plugin
$ pip install git+https://github.com/mottosso/mkdocs-material-design.git
$ git clone https://github.com/mottosso/ragdoll.git
$ cd ragdoll/docs
$ .\serve.bat  # ./serve.sh on Linux
```
