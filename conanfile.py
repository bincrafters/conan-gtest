#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class GTestConan(ConanFile):
    name = "gtest"
    version = "1.8.0"
    description = "Google's C++ test framework"
    url = "http://github.com/bincrafters/conan-gtest"
    license = "BSD 3-Clause"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    source_subfolder = "source_subfolder"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "build_gmock": [True, False], "fpic": [True, False]}
    default_options = ("shared=False", "build_gmock=True", "fpic=True")

    def configure(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def source(self):
        source_url = "https://github.com/google/googletest"
        tools.get("{0}/archive/release-{1}.tar.gz".format(source_url, self.version))
        extracted_dir = "googletest-release-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def build(self):

        cmake = CMake(self)
        if self.settings.compiler == "Visual Studio" and "MD" in str(self.settings.compiler.runtime):
            cmake.definitions["gtest_force_shared_crt"] = True
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["GTEST_CREATE_SHARED_LIBRARY"] = self.options.shared
        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fpic
        cmake.definitions["BUILD_GTEST"] = True
        cmake.definitions["BUILD_GMOCK"] = self.options.build_gmock
        cmake.configure()
        cmake.build()

    def package(self):

        # Copy the license files
        self.copy("LICENSE", dst="licenses", src=self.source_subfolder)
        # Copying headers
        gtest_include_dir = os.path.join(self.source_subfolder, "googletest", "include")
        gmock_include_dir = os.path.join(self.source_subfolder, "googlemock", "include")

        self.copy(pattern="*.h", dst="include", src=gtest_include_dir, keep_path=True)
        if self.options.build_gmock:
            self.copy(pattern="*.h", dst="include", src=gmock_include_dir, keep_path=True)

        # Copying static and dynamic libs
        self.copy(pattern="*.a", dst="lib", src=".", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src=".", keep_path=False)
        self.copy(pattern="*.dll", dst="bin", src=".", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", src=".", keep_path=False)
        self.copy(pattern="*.dylib*", dst="lib", src=".", keep_path=False)
        self.copy(pattern="*.pdb", dst="lib", src=".", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ['gtest']
        if self.options.build_gmock:
            self.cpp_info.libs.append('gmock')
            self.cpp_info.libs.append('gmock_main')
        else:
            self.cpp_info.libs.append('gtest_main')

        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")

        if self.options.shared:
            self.cpp_info.defines.append("GTEST_LINKED_AS_SHARED_LIBRARY=1")
            if self.settings.compiler == "Visual Studio" and self.settings.compiler.version == "11":
                self.cpp_info.defines.append('_VARIADIC_MAX=10')

        if self.settings.compiler == "Visual Studio" and float(str(self.settings.compiler.version)) >= 15:
            self.cpp_info.defines.append("GTEST_LANG_CXX11=1")
            self.cpp_info.defines.append("GTEST_HAS_TR1_TUPLE=0")

