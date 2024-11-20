{
  pkgs,
  lib,
  ...
}: let
  package = builtins.fromTOML (builtins.readFile ./pyproject.toml);
  project = package.tool.poetry;
in
  pkgs.python312Packages.buildPythonPackage {
    pname = project.name;
    version = project.version;
    pyproject = true;
    src = ./.;
    build-system = [pkgs.python312Packages.poetry-core];
    dependencies = with pkgs.python312Packages; [
      python
      (textual.overridePythonAttrs (old: rec {
        version = "0.86.2";
        src = pkgs.fetchFromGitHub {
          owner = "Textualize";
          repo = "textual";
          rev = "refs/tags/v${version}";
          hash = "sha256-cQYBa1vba/fuv/j0D/MNUboQNTc913UG4dp8a1EPql4=";
        };

        postPatch = ''
          sed -i "/^requires-python =.*/a version = '${version}'" pyproject.toml
        '';
      }))
      typing-extensions
    ];
    meta = {
      description = project.description;
      homepage = "https://github.com/darrenburns/textual-autocomplete";
      license = lib.licenses.mit;
    };
  }
