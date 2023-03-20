{ buildPythonPackage, python-ipmi, pyserial }:

buildPythonPackage rec {
  pname = "mmctester";
  version = "0.1";
  src = ./.;
  propagatedBuildInputs = [ python-ipmi pyserial ];
}
