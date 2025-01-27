import os
from conan import ConanFile
from conan.tools.files import copy, get


class HightecTricore(ConanFile):
    name = "hightec_tricore"
    package_type = "application"
    settings = "os", "arch"

    # Define dependencies on external packages (python requires)
    python_requires = "hightec_tricore_cfg/[>=0.1.0]"
    # Specify which classes/methods to extend from the specified packages
    python_requires_extend = "hightec_tricore_cfg.HightecTricoreCfg"

    def source(self):
        username = os.getenv("HUB_ARTIFACTORY_USER", "user")
        password = os.getenv("HUB_ARTIFACTORY_API_KEY", None)
        get(self, **self.conan_data["sources"][self.version], auth=(username, password))

    def package(self):        
        self.output.info(f"Tool folder: {self.build_folder}")
        self.output.info(f"Package folder: {self.package_folder}")
        # Copy the binaries in tool folder in the conan cache, keep the same directory structure
        copy(self, "*", self.build_folder, os.path.join(self.package_folder, self.name), keep_path=True)

    def package_info(self):
        super().package_info()
        self.cpp_info.libs = [self.name]
        package_path = os.path.join(self.package_folder, self.name)
        # Define Env. Var. for the tool
        tool_home = "TOOLS_" + self.name.upper() + "_PATH"
        self.runenv_info.define(tool_home, package_path)
        bin_folder = None
        # Read all conandata information
        try:
            conan_data_values = self.conan_data["binaries"]
            # Quote the version to create conan_data version dictionary
            pkg_version = "{}".format(self.version)
            # Create a separate dictionary based on the self.version
            version_data = {pkg_version: conan_data_values[pkg_version]}
            bin_folder = version_data[pkg_version].get('bin_folder')
        except KeyError:
            self.output.info("=> No bin folder")
        # Add the binaries location to the PATH to access the binaries
        if bin_folder:
            bin_path = os.path.join(package_path, bin_folder)
            self.runenv_info.prepend_path("PATH", bin_path)
        else:
            self.runenv_info.prepend_path("PATH", package_path)