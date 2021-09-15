from pathlib import Path
from typing import List, Optional, Tuple, Iterator

from paramiko import SFTPClient
from paramiko.sftp_attr import SFTPAttributes
from paramiko.sftp_client import b_slash
from paramiko.py3compat import b


class SFTP(SFTPClient):
    def chdir(self, path: Optional[Path]=None) -> None:
        super().chdir(path)

    def chmod(self, path: Path, mode: int) -> None:
        super().chmod(path, mode)

    def chown(self, path: Path, uid: int, gid: int) -> None:
        super().chown(path, uid, gid)

    def get(self, remotepath: Path, localpath: Path, callback: Optional[Tuple[int, int]]=None) -> None:
        super(SFTP, self).get(remotepath, localpath)

    def put(self, localpath: Path, remotepath: Path, callback: Optional[Tuple[int, int]]=None,
            confirm: bool=True) -> None:
        super().put(localpath, remotepath)

    def readlink(self, path: Path) -> Optional[str]:
        return super().readlink(path)

    def remove(self, path: Path) -> None:
        super().remove(path)

    def rmdir(self, path: Path) -> None:
        super().rmdir(path)

    def truncate(self, path: Path, size: int) -> None:
        super().truncate(path, size)

    def utime(self, path: Path, times: Optional[Tuple[float, float]]) -> None:
        super().utime(path, times)

    def lstat(self, path: Path) -> SFTPAttributes:
        return super().lstat(path)

    def mkdir(self, path: Path, mode: int=511) -> None:
        super().mkdir(path)

    def normalize(self, path: Path) -> str:
        return super().normalize(path)

    def listdir(self, path: Path, flag: bool=None) -> List[str]:
        return [file.filename for file in self.listdir_attr(path, flag)]

    def listdir_attr(self, path: Path, flag: bool=None) -> List[SFTPAttributes]:
        filelist = super().listdir_attr(path)

        if flag:
            files = {file: self.stat(path / file.filename).st_mtime
                     for file in filelist}
            return sorted(files, key=files.get)

        return filelist

    def last_modified_file(self, path: Path) -> str:
        return self.listdir_attr(path, True)[-1].filename

    def stat(self, path: Path) -> List[SFTPAttributes]:
        return super().stat(path)

    def unlink(self, path: Path) -> None:
        super().unlink(path)

    def listdir_iter(self, path: Path) -> Iterator[SFTPAttributes]:
        return super().listdir_iter(path)

    def _adjust_cwd(self, path: Path):
        """
        Return an adjusted path if we're emulating a "current working
        directory" for the server.
        """
        path = b(str(path))
        string_path = str(path)
        if self._cwd is None:
            return path
        if len(string_path) and string_path[0:1] == b_slash:
            # absolute path
            return path
        if self._cwd == b_slash:
            return "".join([self._cwd, string_path])
        return "".join([self._cwd, b_slash, string_path])
