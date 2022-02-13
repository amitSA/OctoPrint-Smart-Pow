{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {

  buildInputs = [
    pkgs.python37
    # pkgs.python37Packages.poetry
    pkgs.python37Packages.pip
    pkgs.python37Packages.setuptools
    pkgs.python37Packages.virtualenv
    # TODO move tools like this to a local user deriviation (outside of source-control), since it's more me specific than Octoprint-Smart-Pow
    # I think in work I've seen it's possible to merge the checked in work profile with a local user one
    pkgs.gh
  ];

}
