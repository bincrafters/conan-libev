# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os


class LibevConan(ConanFile):
    name = "libev"
    version = "4.25"
    description = "A full-featured and high-performance event loop that is loosely modelled after libevent"
    topics = ("conan", "event", "libev", "event-loop", "periodic-timer", "notify")
    url = "https://github.com/bincrafters/conan-libev"
    homepage = "http://software.schmorp.de/pkg/libev.html"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = ["BSD-2-Clause", "GPL-2.0-or-later"]
    exports = ["LICENSE.md"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("libev is not supported by Visual Studio")
        if self.settings.os == "Windows" and self.options.shared:
            # libtool:   error: can't build i686-pc-mingw32 shared library unless -no-undefined is specified
            raise ConanInvalidConfiguration("libev can't be built as shared on Windows")

    def source(self):
        checksum = "78757e1c27778d2f3795251d9fe09715d51ce0422416da4abb34af3929c02589"
        tools.get("http://dist.schmorp.de/libev/libev-{}.tar.gz".format(self.version), sha256=checksum)
        extracted_folder = "libev-{0}".format(self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            args = []
            if self.options.shared:
                args.extend(['--disable-static', '--enable-shared'])
            else:
                args.extend(['--disable-shared', '--enable-static'])
            self._autotools.configure(configure_dir=self._source_subfolder, args=args)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(self.package_folder, 'share'))
        la_file = os.path.join(self.package_folder, "lib", "libev.la")
        if os.path.isfile(la_file):
            os.unlink(la_file)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("m")
        elif self.settings.os == "Windows":
            self.cpp_info.libs.append("Ws2_32")
