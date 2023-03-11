{
  inputs = {
    nixpkgs.url = "github:abbradar/nixpkgs/ugractf";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
    let
       pkgs = import nixpkgs {
         inherit system;
        };
    in {
      packages.default = pkgs.python3.pkgs.callPackage ./. { };
      apps.default = flake-utils.lib.mkApp {
        drv = self.packages.${system}.default;

      };
    });
}
