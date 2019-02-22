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
    exports_sources = ["CMakeLists.txt", "FindGTest.cmake.in", "FindGMock.cmake.in"]
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
        tools.get("{0}/archive/release-{1}.tar.gz".format(self.homepage, self.version))
        extracted_dir = "googletest-release-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        cmake = CMake(self)
        if self.settings.compiler == "Visual Studio" and "MD" in str(self.settings.compiler.runtime):
            cmake.definitions["gtest_force_shared_crt"] = True
        if self.settings.build_type == "Debug":
            tools.replace_in_file(os.path.join(self._source_subfolder, "googletest", "cmake", "internal_utils.cmake"), '"d"', '"${CUSTOM_DEBUG_POSTFIX}"')
            cmake.definitions["CUSTOM_DEBUG_POSTFIX"] = self.options.debug_postfix
        cmake.definitions["BUILD_GMOCK"] = self.options.build_gmock
        cmake.definitions["GTEST_NO_MAIN"] = self.options.no_main
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            cmake.definitions["gtest_disable_pthreads"] = True
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

        self.copy("FindGTest.cmake", dst=".", src=".")
        gtest_include_dir = os.path.join(self._source_subfolder, "googletest", "include")
        self.copy(pattern="*.h", dst="include", src=gtest_include_dir, keep_path=True)

        if self.options.build_gmock:
            self.copy("FindGMock.cmake", dst=".", src=".")
            gmock_include_dir = os.path.join(self._source_subfolder, "googlemock", "include")
            self.copy(pattern="*.h", dst="include", src=gmock_include_dir, keep_path=True)

        if self.settings.os in ["Linux", "Android"] or tools.is_apple_os(self.settings.os):
            shared_ext = "dylib" if tools.is_apple_os(self.settings.os) else "so"
            ext = shared_ext if self.options.shared else "a"
            self.copy("libgtest%s.%s" % (self._postfix, ext), dst="lib", src="lib")
            if not self.options.no_main:
                self.copy("libgtest_main%s.%s" % (self._postfix, ext), dst="lib", src="lib")
            if self.options.build_gmock:
                self.copy("libgmock%s.%s" % (self._postfix, ext), dst="lib", src="lib")
                if not self.options.no_main:
                    self.copy("libgmock_main%s.%s" % (self._postfix, ext), dst="lib", src="lib")
        elif self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            self.copy(pattern="*.pdb", dst="bin", src=".", keep_path=False)
            for ext, folder in [('lib', 'lib'), ('dll', 'bin')]:
                self.copy("gtest%s.%s" % (self._postfix, ext), dst=folder, src=folder)
                if not self.options.no_main:
                    self.copy("gtest_main%s.%s" % (self._postfix, ext), dst=folder, src=folder)
                if self.options.build_gmock:
                    self.copy("gmock%s.%s" % (self._postfix, ext), dst=folder, src=folder)
                    if not self.options.no_main:
                        self.copy("gmock_main%s.%s" % (self._postfix, ext), dst=folder, src=folder)
        elif self.settings.os == "Windows" and self.settings.compiler == "gcc":
            static_ext = "dll.a" if self.options.shared else 'a'
            for ext, folder in [(static_ext, 'lib'), ('dll', 'bin')]:
                self.copy("libgtest%s.%s" % (self._postfix, ext), dst=folder, src=folder)
                if not self.options.no_main:
                    self.copy("libgtest_main%s.%s" % (self._postfix, ext), dst=folder, src=folder)
                if self.options.build_gmock:
                    self.copy("libgmock%s.%s" % (self._postfix, ext), dst=folder, src=folder)
                    if not self.options.no_main:
                        self.copy("libgmock_main%s.%s" % (self._postfix, ext), dst=folder, src=folder)

    def package_info(self):
        if self.options.build_gmock:
            gmock_libs = ['gmock', 'gtest'] if self.options.no_main else ['gmock_main', 'gmock', 'gtest']
            self.cpp_info.libs = ["{}{}".format(lib, self._postfix) for lib in gmock_libs]
        else:
            gtest_libs = ['gtest'] if self.options.no_main else ['gtest_main' , 'gtest']
            self.cpp_info.libs = ["{}{}".format(lib, self._postfix) for lib in gtest_libs]

        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")

        if self.options.shared:
            self.cpp_info.defines.append("GTEST_LINKED_AS_SHARED_LIBRARY=1")

        if self.settings.compiler == "Visual Studio":
            if Version(self.settings.compiler.version.value) >= "15":
                self.cpp_info.defines.append("GTEST_LANG_CXX11=1")
                self.cpp_info.defines.append("GTEST_HAS_TR1_TUPLE=0")
