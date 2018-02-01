#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class GTestConan(ConanFile):
    name = "gtest"
    version = "1.7.0"
    description = "Google's C++ test framework"
    url = "http://github.com/bincrafters/conan-gtest"
    license = "BSD 3-Clause"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    source_subfolder = "source_subfolder"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=True"

    def configure(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")
    
    def source(self):
        source_url =  "https://github.com/google/googletest"
        tools.get("{0}/archive/release-{1}.tar.gz".format(source_url, self.version))
        extracted_dir = "googletest-release-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def build(self):
        if self.settings.compiler == "Visual Studio" and self.settings.compiler.version == "15":
            tools.replace_in_file(os.path.join(self.source_subfolder, "CMakeLists.txt"),
                            '# aggressive about warnings.',
                            '''
# aggressive about warnings.
string(REPLACE "-WX" "" cxx_strict ${cxx_strict})
''')
        cmake = CMake(self)
        cmake.definitions['BUILD_SHARED_LIBS'] = self.options.shared
        cmake.definitions['gtest_force_shared_crt'] = True
        cmake.configure()
        cmake.build()

    def package(self):
        
        # Copy the license files
        self.copy("LICENSE", dst="licenses", src=self.source_subfolder)
        # Copying headers
        gtest_include_dir = os.path.join(self.source_subfolder,"include")
        
        self.copy(pattern="*.h", dst="include", src=gtest_include_dir, keep_path=True)

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
