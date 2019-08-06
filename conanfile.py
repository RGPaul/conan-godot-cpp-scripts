from conans import ConanFile, CMake, tools
import os

class GodotCppConan(ConanFile):
    name = "godot-cpp"
    version = "20190605"
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
        self.run("cd godot-cpp && git checkout 5bdcecfc20675ad3bec8ab63df94cf445f0fe54d && cd ..")
        self.run("git clone https://github.com/GodotNativeTools/godot_headers.git godot-cpp/godot_headers")
        self.run("cd godot-cpp/godot_headers && git checkout fb3010491be433f4e44119c743f682bb4710ec72 && cd ../..")

    # compile using cmake
    def build(self):
        cmake = CMake(self)
        library_folder = "%s/godot-cpp" % self.source_folder
        cmake.verbose = True
        variants = []

        if self.settings.os == "Windows":
            cmake.definitions["CMAKE_BUILD_TYPE"] = self.settings.build_type

        if self.settings.os == "Android":
            cmake.definitions["CMAKE_SYSTEM_VERSION"] = self.settings.os.api_level
            cmake.definitions["CMAKE_ANDROID_NDK"] = os.environ["ANDROID_NDK_PATH"]
            cmake.definitions["CMAKE_ANDROID_NDK_TOOLCHAIN_VERSION"] = self.settings.compiler
            cmake.definitions["CMAKE_ANDROID_STL_TYPE"] = self.options.android_stl_type

        if self.settings.os == "iOS":
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

        if self.settings.os == "Macos":
            cmake.definitions["CMAKE_OSX_ARCHITECTURES"] = tools.to_apple_arch(self.settings.arch)

        cmake.configure(source_folder=library_folder)
        cmake.build()

        lib_dir = os.path.join(self.build_folder, "godot-cpp", "bin")

        # execute ranlib for all static universal libraries (required for fat libraries)
        if self.settings.os == "iOS" and len(variants) > 0:
            if self.options.shared == False:
                for f in os.listdir(lib_dir):
                    if f.endswith(".a") and os.path.isfile(os.path.join(lib_dir,f)) and not os.path.islink(os.path.join(lib_dir,f)):
                        self.run("xcrun ranlib %s" % os.path.join(lib_dir,f))

    def package(self):
        self.copy("*", dst="include", src='godot-cpp/include')
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
