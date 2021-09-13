import os
from pathlib import Path
from tempfile import mkstemp
from time import time
from paramiko.common import o777, o600, o666, o644
import sys

import pytest
import paramiko
from loguru import logger

from sftp.sftp import SFTP
from sftp.utils.configuration_logger import config
from constants import HOST, PORT, USERNAME, PASSWORD


class TestSFTP(object):
    logger.configure(**config)

    def setup(self):
        transport = paramiko.Transport((HOST, PORT))
        transport.connect(None, USERNAME, PASSWORD)
        self.channel = transport.open_session(window_size=10000, max_packet_size=10000)
        self.channel.invoke_subsystem("sftp")
        self.sftp = SFTP(self.channel)

    def teardown(self):
        self.channel.close()

    def test_listdir_success(self):
        filenames = self.sftp.listdir(Path("/root"))
        logger.info(filenames)
        assert filenames != []

        filenames = self.sftp.listdir(Path("/root"), True)
        logger.info(filenames)
        assert filenames != []

    @pytest.mark.xfail
    def test_listdir_fail(self):
        assert self.sftp.listdir(Path("/r")) != []
        assert self.sftp.listdir(Path("/r"), True) != []

    def test_listdir_attr_success(self):
        listdir_attr = self.sftp.listdir_attr(Path("/root"))
        logger.info(listdir_attr)
        assert listdir_attr != []

        listdir_attr = self.sftp.listdir_attr(Path("/root"), True)
        logger.info(listdir_attr)
        assert listdir_attr != []

    @pytest.mark.xfail
    def test_listdir_attr_fail(self):
        assert self.sftp.listdir_attr(Path("/r")) != []

    def test_stat_success(self):
        listdir_attr = self.sftp.stat(Path("/root"))
        logger.info(listdir_attr)
        assert listdir_attr != []

    @pytest.mark.xfail
    def test_stat_fail(self):
        listdir_attr = self.sftp.stat(Path("/r"))
        assert listdir_attr != []

    def test_last_modified_file_success(self):
        last_file_modified = self.sftp.last_modified_file(Path("/root"))
        logger.info(last_file_modified)
        assert last_file_modified != ""

    @pytest.mark.xfail
    def test_last_modified_file_fail(self):
        last_file_modified = self.sftp.last_modified_file(Path("/r"))
        assert last_file_modified != ""

    def test_chdir_success(self):
        self.sftp.chdir(Path("/root"))
        assert self.sftp.getcwd() == "/root"

    @pytest.mark.xfail
    def test_chdir_fail(self):
        self.sftp.chdir(Path("/r"))
        assert self.sftp.getcwd() == "/r"

    def test_readlink_success(self):
        if not hasattr(os, "symlink"):
            # skip symlink tests on windows
            return

        with self.sftp.open("/root/original.txt", "w") as f:
            f.write("original\n")
        self.sftp.symlink("original.txt", "/root/link.txt")
        assert self.sftp.readlink(Path("/root/link.txt")) == "original.txt"
        self.sftp.remove(Path("/root/link.txt"))

    @pytest.mark.xfail
    def test_readlink_fail(self):
        if not hasattr(os, "symlink"):
            # skip symlink tests on windows
            return

        with self.sftp.open("/root/original.txt", "w") as f:
            f.write("original\n")
        assert self.sftp.readlink(Path("/root/link.txt")) == "original.txt"
        self.sftp.remove(Path("/root/link.txt"))

    def test_lstat_success(self):
        dir_attr = self.sftp.lstat(Path("/root"))
        logger.info(dir_attr)
        assert dir_attr != []

    @pytest.mark.xfail
    def test_lstat_fail(self):
        dir_attr = self.sftp.lstat(Path("/r"))
        logger.info(dir_attr)
        assert dir_attr != []

    def test_mkdir_success(self):
        now_secods = str(int(time()))
        dir_name = "".join(["dir", now_secods])
        self.sftp.mkdir(Path(dir_name))
        assert self.sftp.listdir(Path("/root"), True)[-1] == dir_name

    @pytest.mark.xfail
    def test_mkdir_fail(self):
        dir_name = "resize.log"
        self.sftp.mkdir(Path(dir_name))
        assert self.sftp.listdir(Path("/root"), True)[-1] == dir_name

    def test_remove_success(self):
        self.sftp.open("/root/test", "w").close()
        self.sftp.remove(Path("/root/test"))

    @pytest.mark.xfail
    def test_remove_fail(self):
        self.sftp.remove(Path("/root/test1"))

    def test_rmdir_success(self):
        now_secods = str(int(time()))
        dir_name = "".join(["dir", now_secods])
        self.sftp.mkdir(Path(dir_name))
        self.sftp.rmdir(Path(dir_name))

    @pytest.mark.xfail
    def test_rmdir_fail(self):
        now_secods = str(int(time()))
        dir_name = "".join(["dir", now_secods])
        self.sftp.rmdir(Path(dir_name))

    def test_utime_success(self):
        with self.sftp.open("/root/special", "w") as f:
            f.write("x" * 1024)

        stat = self.sftp.stat(Path("/root/special"))
        mtime = stat.st_mtime - 3600
        atime = stat.st_atime - 1800
        self.sftp.utime(Path("/root/special"), (atime, mtime))
        stat = self.sftp.stat(Path("/root/special"))
        assert stat.st_mtime == mtime
        self.sftp.remove(Path("/root/special"))

    @pytest.mark.xfail
    def test_utime_fail(self):
        self.sftp.utime(Path("/root/s"))

    def test_truncate_success(self):
        with self.sftp.open("/root/special", "w") as f:
            f.write("x" * 1024)

        self.sftp.truncate(Path("/root/special"), 512)
        stat = self.sftp.stat(Path("/root/special"))
        assert stat.st_size == 512
        self.sftp.remove(Path("/root/special"))

    @pytest.mark.xfail
    def test_truncate_fail(self):
        self.sftp.truncate(Path("/root/s"), 512)

    def test_chmod_success(self):
        with self.sftp.open("/root/special", "w") as f:
            f.write("x" * 1024)

        stat = self.sftp.stat(Path("/root/special"))
        self.sftp.chmod(Path("/root/special"), (stat.st_mode & ~o777) | o600)
        stat = self.sftp.stat(Path("/root/special"))
        expected_mode = o600

        if sys.platform == "win32":
            # chmod not really functional on windows
            expected_mode = o666
        if sys.platform == "cygwin":
            # even worse.
            expected_mode = o644
        assert stat.st_mode & o777 == expected_mode
        self.sftp.remove(Path("/root/special"))

    @pytest.mark.xfail
    def test_chmod_fail(self):
        self.sftp.chmod(Path("/root/s"), (self.sftp.stat(Path("/root/s")).st_mode & ~o777) | o600)

    def test_chown_success(self):
        listdir_attr = self.sftp.stat(Path("/root"))
        uid = listdir_attr.st_uid
        gid = listdir_attr.st_gid
        self.sftp.chown(Path("/root"), uid, gid)

    @pytest.mark.xfail
    def test_chown_fail(self):
        self.sftp.chown(Path("/root"))

    def test_unlink_success(self):
        self.sftp.open("/root/unusual.txt", "wx").close()
        self.sftp.unlink(Path("/root/unusual.txt"))

    @pytest.mark.xfail
    def test_unlink_fail(self):
        self.sftp.open("/root/unusual1.txt").close()
        self.sftp.unlink(Path("/root/unusual1.txt"))

    def test_listdir_iter_success(self):
        files = [file.filename for file in self.sftp.listdir_iter(Path("/root"))]
        logger.info(files)
        assert files != []

    @pytest.mark.xfail
    def test_listdir_iter_fail(self):
        files = [file.filename for file in self.sftp.listdir_iter(Path("/r"))]
        assert files != []

    def test_get_success(self):
        with self.sftp.open("/root/g.txt", "w") as f:
            f.write("x" * 1024)

        self.sftp.get(Path("/root/g.txt"), Path("/home/alexander/Загрузки/doklad.txt"))
        self.sftp.remove(Path("/root/g.txt"))

    @pytest.mark.xfail
    def test_get_fail(self):
        with self.sftp.open("/root/g.txt", "w") as f:
            f.write("x" * 1024)

        self.sftp.get(Path("/root/g.txt"), Path("/home"))
        self.sftp.remove(Path("/root/g.txt"))

    def test_put_success(self):
        with self.sftp.open("/root/p.txt", "w") as f:
            f.write("o" * 10)

        self.sftp.put(Path("/home/alexander/Загрузки/doklad.txt"), Path("/root/p.txt"))
        self.sftp.remove(Path("/root/p.txt"))

    @pytest.mark.xfail
    def test_put_fail(self):
        with self.sftp.open("/root/p.txt", "w") as f:
            f.write("o" * 10)

        self.sftp.put(Path("/home"), Path("/root/p.txt"))
        self.sftp.remove(Path("/root/p.txt"))

