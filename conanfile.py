from conans import ConanFile, CMake, tools
import os

class GodotCppConan(ConanFile):
    name = "godot-cpp"
    version = "3.2"
    author = "Ralph-Gordon Paul (gordon@rgpaul.com)"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "android_ndk": "ANY", 
        "android_stl_type":["c++_static", "c++_shared"]}
    default_options = "shared=False", "android_ndk=None", "android_stl_type=c++_static"
    description = "C++ bindings for the Godot script API"
    url = "https://github.com/RGPaul/conan-godot-cpp-scripts"
    license = "MIT"
    exports_sources = "cmake-modules/*"

    # download sources
    def source(self):
        self.run("git clone https://github.com/GodotNativeTools/godot-cpp.git")
        self.run("cd godot-cpp && git checkout aba8766618c6aa40c6f7b40b513e8e47cfa807f4 && cd ..")
        self.run("git clone https://github.com/GodotNativeTools/godot_headers.git godot-cpp/godot_headers")
        self.run("cd godot-cpp/godot_headers && git checkout ddf67cc7b8274c5fb77a71c828bab2991f1ee12a && cd ../..")

    # compile using cmake
    def build(self):
        cmake = CMake(self)
        library_folder = "%s/godot-cpp" % self.source_folder
        cmake.verbose = True

        if self.settings.os == "Windows":
            self.applyCmakeSettingsForWindows(cmake)

        if self.settings.os == "Android":
            self.applyCmakeSettingsForAndroid(cmake)

        if self.settings.os == "iOS":
            self.applyCmakeSettingsForiOS(cmake)

        if self.settings.os == "Macos":
            self.applyCmakeSettingsFormacOS(cmake)

        cmake.configure(source_folder=library_folder)
        cmake.build()

    def applyCmakeSettingsForAndroid(self, cmake):
        android_toolchain = os.environ["ANDROID_NDK_PATH"] + "/build/cmake/android.toolchain.cmake"
        cmake.definitions["CMAKE_SYSTEM_NAME"] = "Android"
        cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = android_toolchain
        cmake.definitions["ANDROID_NDK"] = os.environ["ANDROID_NDK_PATH"]
        cmake.definitions["ANDROID_ABI"] = tools.to_android_abi(self.settings.arch)
        cmake.definitions["ANDROID_STL"] = self.options.android_stl_type
        cmake.definitions["ANDROID_NATIVE_API_LEVEL"] = self.settings.os.api_level
        cmake.definitions["ANDROID_TOOLCHAIN"] = "clang"

    def applyCmakeSettingsForiOS(self, cmake):
        ios_toolchain = "cmake-modules/Toolchains/ios.toolchain.cmake"
        cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = ios_toolchain
        cmake.definitions["DEPLOYMENT_TARGET"] = "10.0"

        if self.settings.arch == "x86":
            cmake.definitions["PLATFORM"] = "SIMULATOR"
        elif self.settings.arch == "x86_64":
            cmake.definitions["PLATFORM"] = "SIMULATOR64"
        else:
            cmake.definitions["PLATFORM"] = "OS"

        # define all architectures for ios fat library
        if "arm" in self.settings.arch:
            cmake.definitions["ARCHS"] = "armv7;armv7s;arm64;arm64e"
        else:
            cmake.definitions["ARCHS"] = tools.to_apple_arch(self.settings.arch)
    
    def applyCmakeSettingsFormacOS(self, cmake):
        cmake.definitions["CMAKE_OSX_ARCHITECTURES"] = tools.to_apple_arch(self.settings.arch)

    def applyCmakeSettingsForWindows(self, cmake):
        cmake.definitions["CMAKE_BUILD_TYPE"] = self.settings.build_type
        if self.settings.compiler == "Visual Studio":
            # check that runtime flags and build_type correspond (consistency check)
            if "d" not in self.settings.compiler.runtime and self.settings.build_type == "Debug":
                raise Exception("Compiling for Debug mode but compiler runtime does not contain 'd' flag.")

            if self.settings.build_type == "Debug":
                cmake.definitions["CMAKE_CXX_FLAGS_DEBUG"] = "/%s" % self.settings.compiler.runtime
            elif self.settings.build_type == "Release":
                cmake.definitions["CMAKE_CXX_FLAGS_RELEASE"] = "/%s" % self.settings.compiler.runtime

            cmake_file = "%s/godot-cpp/CMakeLists.txt" % self.source_folder
            if self.settings.compiler.runtime == "MT" or self.settings.compiler.runtime == "MTd":
                 tools.replace_in_file(cmake_file, "/MDd", "/MTd")
                 tools.replace_in_file(cmake_file, "/MD", "/MT")

    def package(self):
        self.copy("*", dst="include", src='godot-cpp/include')
        self.copy("*", dst="include/godot_headers", src='godot-cpp/godot_headers')
        self.copy("*.lib", dst="lib", src='godot-cpp/bin', keep_path=False)
        self.copy("*.dll", dst="bin", src='godot-cpp/bin', keep_path=False)
        self.copy("*.so", dst="lib", src='godot-cpp/bin', keep_path=False)
        self.copy("*.dylib", dst="lib", src='godot-cpp/bin', keep_path=False)
        self.copy("*.a", dst="lib", src='godot-cpp/bin', keep_path=False)
        
    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = ['include']

    def package_id(self):
        if "arm" in self.settings.arch and self.settings.os == "iOS":
            self.info.settings.arch = "AnyARM"

    def config_options(self):
        # remove android specific option for all other platforms
        if self.settings.os != "Android":
            del self.options.android_ndk
            del self.options.android_stl_type
