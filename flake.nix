{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
  };

  outputs = inputs @ {flake-parts, ...}:
    flake-parts.lib.mkFlake {inherit inputs;} {
      flake.overlays.default = final: prev: {
        python312PackagesExtensions =
          prev.python312PackagesExtensions
          ++ [
            (python-final: python-prev: {textual-autocomplete = final.callPackagee ./package.nix {};})
          ];
      };
      systems = ["x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin"];
      perSystem = {pkgs, ...}: {
        packages.default = pkgs.callPackage ./package.nix {};
      };
    };
}
