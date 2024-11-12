{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
  };

  outputs = inputs @ {flake-parts, ...}:
    flake-parts.lib.mkFlake {inherit inputs;} {
      flake.overlays.default = final: prev: {
        textual-autocomplete = final.callPackage ./package.nix {};
      };
      systems = ["x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin"];
      perSystem = {pkgs, ...}: {
        packages.default = pkgs.callPackage ./package.nix {};
      };
    };
}
