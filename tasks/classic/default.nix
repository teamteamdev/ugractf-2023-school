{ lib, pkgs }:
let
  poetry = pkgs.poetry2nix;
  pathExtraPkgs = deps: [ "--prefix PATH : ${lib.makeBinPath deps}" ];
  in let
  pkg = poetry.mkPoetryApplication rec {
    projectDir = ./.;
    makeWrapperArgs = pathExtraPkgs [ pkgs.imagemagick ];
    overrides = poetry.defaultPoetryOverrides.extend (final: prev: {
      macresources = prev.macresources.overridePythonAttrs (old: {
        buildInputs = (old.buildinputs or [ ]) ++ [ final.setuptools ];
      });
      machfs = prev.machfs.overridePythonAttrs (old: {
        buildInputs = (old.buildinputs or [ ]) ++ [ final.setuptools ];
      });
    });
  };
  in pkg
