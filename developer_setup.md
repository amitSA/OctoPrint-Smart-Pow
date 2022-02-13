An ocotprint plugin to auto switch off the power to a 3d-printer when a print has finished.

### Developer Setup
The preprequisites are just a system nix installation

Run `direnv allow .`

This will install python3.7 in your user nix profile.  But this python is just used to "bootstrap" by creating the virtualenv

Run `virtualenv .venv`
> Since virtualenv is a python package itself, we need python to run it! Hence the usage of nix.

The reason we don't use nix further (they're are a number of nix/python integrations out there)
is because I couldn't think of any good way to install octoprint's dependencies encoded in it's setup.py (I think) from nix.

My nix knowledge + setup.py knowledge limits here.  But that's okay! I have a number of other tools at my desposal plus tutorials to folow :)

This sets the python environment to the virtualenv.
> Which means we can run `pip install` no matter where what the cwd is, and it will install them into this "environment"

<!-- Clone octoprint into the `3rd_party` directory via this \
XXX \
Then run  Run `cd third_party/octoprint/ && pip install -e .`
> Octoprint Plugins depend on the octoprint CLI program for it's "dev" commands (see below). But this project also depends on source modules in Octoprint like the EventManager which is another reason why we need to clone octoprint -->
**XXX where is the "-e ." mentioned here ? I think these docs need to be changed**
Run `pip install octoprint`
> But don't include octoprint as a setup.py dependency, that will automatically be added by Octoprint's helper install command (mentioned below)

This installs octoprint and it's deps
> I think the `-e .` incantation tells it to find octoprint's deps through it's setup.py.  But not sure

Then cd back into project root, and then cd into the plugin directory `Octoprint_Smart_Pow`

Then run `octoprint dev plugin:install` to install the plugin in developer mode, which means that the source-code of the install
is the actual checked-in sourcecode, not some copied location
> This means you can change source-code and then see your changes automatically apply without running any installation command


### Common Errors

**User permission error when installing `pip install octoprint`**
Likely because you're not installing it in virtual env, and instead are trying to install it in the nix installation, which is read-only
