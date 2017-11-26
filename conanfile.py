from conans import ConanFile
import os
from conans.tools import download
from conans.tools import unzip
from conans import CMake

class GTestConan(ConanFile):
    name = "gtest"
    version = "1.8.0"
    sources_folder = "sources"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "cygwin_msvc": [True, False],
               "no_gmock": [True, False], "no_main": [True, False], "fpic": [True, False]}
    default_options = ("shared=True", "cygwin_msvc=False", "no_gmock=False",
                       "no_main=False", "fpic=True")
    exports = "CMakeLists.txt"
    url="http://github.com/bincrafters/conan-gtest"
    license="https://github.com/google/googletest/blob/master/googletest/LICENSE"
    description = "Google's C++ test framework"

    def configure(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")
    
    def source(self):
        zip_name = "release-%s.zip" % self.version
        url = "https://github.com/google/googletest/archive/%s" % zip_name
        download(url, zip_name)
        unzip(zip_name)
        os.unlink(zip_name)
        
        os.rename("googletest-release-%s" % self.version, self.sources_folder)

    def build(self):
        cmake = CMake(self)
        if self.settings.compiler == "Visual Studio" and "MD" in str(self.settings.compiler.runtime):
            cmake.definitions["gtest_force_shared_crt"] = True
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fpic
        cmake.definitions["BUILD_GTEST"] = self.options.no_gmock
        cmake.definitions["BUILD_GMOCK"] = not self.options.no_gmock
        cmake.configure()
        cmake.build()

    def package(self):

        # Copy the license files
        self.copy("license*", src="%s/googletest" % self.sources_folder, dst=".", ignore_case=True, keep_path=False)
        # Copying headers
        self.copy(pattern="*.h", dst="include", src="%s/googletest/include" % self.sources_folder, keep_path=True)
        if not self.options.no_gmock:
            self.copy(pattern="*.h", dst="include", src="%s/googlemock/include" % self.sources_folder, keep_path=True)

        # Copying static and dynamic libs
        self.copy(pattern="*.a", dst="lib", src=".", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src=".", keep_path=False)
        self.copy(pattern="*.dll", dst="bin", src=".", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", src=".", keep_path=False)
        self.copy(pattern="*.dylib*", dst="lib", src=".", keep_path=False)
        self.copy(pattern="*.pdb", dst="lib", src=".", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ['gtest', 'gtest_main']
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
        
        if self.options.shared:
            self.cpp_info.defines.append("GTEST_LINKED_AS_SHARED_LIBRARY=1")
            if self.settings.compiler == "Visual Studio" and self.settings.compiler.version == "11":
                self.cpp_info.defines.append('_VARIADIC_MAX=10')
