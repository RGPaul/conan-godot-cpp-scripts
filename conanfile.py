from conans import ConanFile, CMake, tools
import os

class GodotCppConan(ConanFile):
    name = "godot-cpp"
    version = "20190805"
    author = "Ralph-Gordon Paul (gordon@rgpaul.com)"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "android_ndk": "ANY", 
        "android_stl_type":["c++_static", "c++_shared"]}
    default_options = "shared=False", "android_ndk=None", "android_stl_type=c++_static"
    description = "C++ bindings for the Godot script API"
    url = "https://github.com/Manromen/conan-godot-cpp-scripts"
    license = "MIT"
    exports_sources = "cmake-modules/*"

    # download sources
    def source(self):
        self.run("git clone https://github.com/GodotNativeTools/godot-cpp.git")
        self.run("cd godot-cpp && git checkout c2ec46f64a24de9a46b06c3e987c306f549ccadb && cd ..")
        self.run("git clone https://github.com/GodotNativeTools/godot_headers.git godot-cpp/godot_headers")
        self.run("cd godot-cpp/godot_headers && git checkout efea911ad578abc25890f38a6c81bf8f1229aa30 && cd ../..")

    # compile using cmake
    def build(self):
        cmake = CMake(self)
        library_folder = "%s/godot-cpp" % self.source_folder
        cmake.verbose = True
        variants = []

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

        # execute ranlib for all static universal libraries (required for fat libraries on iOS)
        if self.settings.os == "iOS" and len(variants) > 0 and not self.options.shared:
            self.runRanlibForiOS(os.path.join(self.build_folder, "godot-cpp", "bin"))

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

        # define all architectures for ios fat library
        if "arm" in self.settings.arch:
            variants = ["armv7", "armv7s", "armv8"]

        # apply build config for all defined architectures
        if len(variants) > 0:
            archs = ""
            for i in range(0, len(variants)):
                if i == 0:
                    archs = tools.to_apple_arch(variants[i])
                else:
                    archs += ";" + tools.to_apple_arch(variants[i])
            cmake.definitions["CMAKE_OSX_ARCHITECTURES"] = archs

        if self.settings.arch == "x86" or self.settings.arch == "x86_64":
            cmake.definitions["IOS_PLATFORM"] = "SIMULATOR"
        else:
            cmake.definitions["IOS_PLATFORM"] = "OS"
    
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

    def runRanlibForiOS(self, lib_dir):
        for f in os.listdir(lib_dir):
            if f.endswith(".a") and os.path.isfile(os.path.join(lib_dir,f)) and not os.path.islink(os.path.join(lib_dir,f)):
                self.run("xcrun ranlib %s" % os.path.join(lib_dir,f))

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
