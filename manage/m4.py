import os
import logging as log

from manage.util.subproc import run
from manage import Component


class M4(Component):
    def setup(self, args, tools):
        self.path = os.path.join(args["top"], "m4")
        self.output = os.path.join(args["output_dir"], "m4")
        self.tools = tools

        if not args["no_dev"]:
            self.device = args["dev_addr"]
        else:
            self.device = None

    def build(self):
        run(["mkdir", "-p", self.output])
        run(
            [
                "cmake",
                "-DCMAKE_TOOLCHAIN_FILE={}".format(os.path.join(
                    self.tools["freertos"].path,
                    "tools/cmake_toolchain_files/armgcc.cmake",
                )),
                "-G", "Unix Makefiles",
                "-DCMAKE_BUILD_TYPE=Release",
                self.path,
            ],
            add_env={
                "FREERTOS_DIR": self.tools["freertos"].path,
                "ARMGCC_DIR": self.tools["armgcc_m4"].path,
            },
            cwd=self.output,
        )
        run(["make", "-j4"], cwd=self.output)
    
    def clean(self):
        run(["rm", "-rf", self.output])

    def test(self):
        pass

    def deploy(self):
        self.build()
        if self.device is not None:
            devcmd = "cat > m4image.bin && mount /dev/mmcblk0p1 /mnt && mv m4image.bin /mnt && umount /mnt"
            hostcmd = "out=$(cat {}/release/m4image.bin) && echo '$out' | ssh root@{} '{}'".format(
                self.output, self.device, devcmd
            )
            run(["sh", "-c", hostcmd])