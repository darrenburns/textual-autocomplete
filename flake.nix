{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
  };

  outputs = inputs @ {flake-parts, ...}:
    flake-parts.lib.mkFlake {inherit inputs;} {
      systems = ["x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin"];
      perSystem = {
        pkgs,
        lib,
        ...
      }: let
        package = builtins.fromTOML (builtins.readFile ./pyproject.toml);
        project = package.tool.poetry;
      in {
        packages.default = pkgs.python312Packages.buildPythonPackage {
          pname = project.name;
          version = project.version;
          pyproject = true;
          src = ./.;
          build-system = [pkgs.python312Packages.poetry-core];
          dependencies = with pkgs.python312Packages; [
            python
            textual
            typing-extensions
          ];
          meta = {
            description = project.description;
            homepage = "https://github.com/darrenburns/textual-autocomplete";
            license = lib.licenses.mit;
          };
        };
      };
    };
}
