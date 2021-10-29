{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {

  buildInputs = [
    pkgs.python37
    # pkgs.python37Packages.poetry
    pkgs.python37Packages.pip
    pkgs.python37Packages.setuptools
    pkgs.python37Packages.virtualenv
  ];

}