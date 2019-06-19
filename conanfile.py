# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil


class LibevConan(ConanFile):
    name = "libev"
    version = "4.25"
    description = "A full-featured and high-performance event loop that is loosely modelled after libevent"
    topics = ("conan", "event")
    url = "https://github.com/bincrafters/conan-libev"
    homepage = "http://software.schmorp.de/pkg/libev.html"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "http://cvs.schmorp.de/libev/LICENSE"
    exports = ["LICENSE.md"]

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True}

    _source_subfolder = "source_subfolder"

    def configure(self):
        if self.settings.compiler == 'Visual Studio':
            raise ConanInvalidConfiguration("MSVC is not supported")

    def source(self):
        checksum = "78757e1c27778d2f3795251d9fe09715d51ce0422416da4abb34af3929c02589"
        tools.get("http://dist.schmorp.de/libev/libev-{}.tar.gz".format(self.version), sha256=checksum)
        extracted_folder = "libev-{0}".format(self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def build(self):
        prefix = os.path.abspath(self.package_folder)
        with tools.chdir(self._source_subfolder):
            env_build = AutoToolsBuildEnvironment(self)
            if self.settings.os == 'Windows':
                prefix = tools.unix_path(prefix)
            args = ['--prefix=%s' % prefix]
            if self.options.shared:
                args.extend(['--disable-static', '--enable-shared'])
            else:
                args.extend(['--disable-shared', '--enable-static'])
            env_build.configure(args=args)
            env_build.make()
            env_build.make(args=['install'])

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        # remove unneeded directories
        shutil.rmtree(os.path.join(self.package_folder, 'share', 'man'), ignore_errors=True)
        la_file = os.path.join(self.package_folder, "lib", "libev.la")
        if os.path.isfile(la_file):
            os.unlink(la_file)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
