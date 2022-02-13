## Developer Setup
### Pre-requisites

* Python 3.7
   > Install via [pyenv](https://github.com/pyenv/pyenv).  Make sure to first all system [dependencies](https://github.com/pyenv/pyenv/wiki#suggested-build-environment)


### Install dependencies
Run `pip install octoprint`
> This installs octoprint and it's dependencies

Then run `pip install -e '.[dev]'` to install the plugin in developer mode,
> You can change source-code and then see your changes automatically apply without re-running installation

### Common Errors

**User permission error when installing `pip install octoprint`**

Likely because you're not installing it in virtual env, and instead are trying to install it in the nix installation, which is read-only

**AttributeError: module '_distutils_hack' has no attribute 'ensure_shim'**

It's some issue with setuptools install.  I've found running `pip install --upgrade pip setuptools wheel` resolves this.
