{
  description = "MMC tester on arduino";

  inputs = { flake-utils.url = "github:numtide/flake-utils"; };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let pkgs = nixpkgs.legacyPackages.${system};
      in {
        packages = rec {
          python-ipmi = pkgs.python3Packages.python-ipmi.overridePythonAttrs
            (old: {
              postPatch = ''
                sed -i 's/version=version/version="${old.version}"/' setup.py
              '';
            });
          mmctester = pkgs.python3Packages.callPackage ./default.nix {
            inherit python-ipmi;
          };
          default = mmctester;
        };
      });
}
