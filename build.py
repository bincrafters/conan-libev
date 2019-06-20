#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import tools
from bincrafters import build_template_default

if __name__ == "__main__":
    builder = build_template_default.get_builder(pure_c=True)
    builder.remove_build_if(lambda build: build.options["libev:shared"] == True and tools.os_info.is_windows)
    builder.run()
