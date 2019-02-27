#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from conans import ConanFile, CMake, tools
from conans.model.version import Version
from conans.errors import ConanInvalidConfiguration


class GTestConan(ConanFile):
    name = "gtest"
    version = "1.8.1"
    description = "Google's C++ test framework"
    url = "http://github.com/bincrafters/conan-gtest"
    homepage = "https://github.com/google/googletest"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "BSD-3-Clause"
    topics = ("conan", "gtest", "testing", "google-testing", "unit-test")
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt", "FindGTest.cmake.in", "FindGMock.cmake.in", "gtest.patch"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "build_gmock": [True, False], "fPIC": [True, False], "no_main": [True, False], "debug_postfix": "ANY"}
    default_options = {"shared": False, "build_gmock": True, "fPIC": True, "no_main": False, "debug_postfix": 'd'}
    _source_subfolder = "source_subfolder"

    @property
    def _postfix(self):
        return self.options.debug_postfix if self.settings.build_type == "Debug" else ""

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.build_type != "Debug":
            del self.options.debug_postfix

    def configure(self):
        if self.settings.os == "Windows":
            if self.settings.compiler == "Visual Studio" and Version(self.settings.compiler.version.value) <= "12":
                raise ConanInvalidConfiguration("Google Test {} does not support Visual Studio <= 12".format(self.version))

    def source(self):
        sha256 = "9bf1fe5182a604b4135edc1a425ae356c9ad15e9b23f9f12a02e80184c3a249c"
        tools.get("{0}/archive/release-{1}.tar.gz".format(self.homepage, self.version), sha256=sha256)
        extracted_dir = "googletest-release-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        if self.settings.build_type == "Debug":
            cmake.definitions["CUSTOM_DEBUG_POSTFIX"] = self.options.debug_postfix
        if self.settings.compiler == "Visual Studio" and "MD" in str(self.settings.compiler.runtime):
            cmake.definitions["gtest_force_shared_crt"] = True
        cmake.definitions["BUILD_GMOCK"] = self.options.build_gmock
        cmake.definitions["GTEST_NO_MAIN"] = self.options.no_main
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            cmake.definitions["gtest_disable_pthreads"] = True
        cmake.configure()
        return cmake

    def build(self):
        tools.patch(base_path=self._source_subfolder, patch_file="gtest.patch")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.pdb", dst="bin", src=".", keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")

        if self.options.shared:
            self.cpp_info.defines.append("GTEST_LINKED_AS_SHARED_LIBRARY=1")

        if self.settings.compiler == "Visual Studio":
            if Version(self.settings.compiler.version.value) >= "15":
                self.cpp_info.defines.append("GTEST_LANG_CXX11=1")
                self.cpp_info.defines.append("GTEST_HAS_TR1_TUPLE=0")
