from conans import ConanFile
import os
from conans.tools import download
from conans.tools import unzip
from conans import CMake

class GTestConan(ConanFile):
    name = "gtest"
    version = "1.7.0"
    sources_folder = "sources"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    exports = ["CMakeLists.txt", "LICENSE"]
    url="http://github.com/lasote/conan-gtest"
    license="https://github.com/google/googletest/blob/master/googletest/LICENSE"
    
    def source(self):
        zip_name = "release-%s.zip" % self.version
        url = "https://github.com/google/googletest/archive/%s" % zip_name
        download(url, zip_name)
        unzip(zip_name)
        os.unlink(zip_name)
        os.rename("googletest-release-%s" % self.version, self.sources_folder)

    def build(self):
        cmake = CMake(self)
        cmake.definitions['BUILD_SHARED_LIBS'] = self.options.shared
        cmake.definitions['gtest_force_shared_crt'] = True
        cmake.configure()
        cmake.build()

    def package(self):
        # Copying headers
        self.copy(pattern="*.h", dst="include", src="%s/include" % self.sources_folder, keep_path=True)

        # Copying static and dynamic libs
        self.copy(pattern="*.a", dst="lib", src=".", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src=".", keep_path=False)
        self.copy(pattern="*.dll", dst="bin", src=".", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", src=".", keep_path=False)
        self.copy(pattern="*.dylib*", dst="lib", src=".", keep_path=False)      
        self.copy(pattern="*.pdb", dst="lib", src=".", keep_path=False)

        # Copying the license
        self.copy("LICENSE*", dst="licenses",  ignore_case=True, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ['gtest', 'gtest_main']
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
        
        if self.options.shared:
            self.cpp_info.defines.append("GTEST_LINKED_AS_SHARED_LIBRARY=1")
            if self.settings.compiler == "Visual Studio" and self.settings.compiler.version == "11":
                self.cpp_info.defines.append('_VARIADIC_MAX=10')
