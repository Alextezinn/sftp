from pathlib import Path
from typing import List, Optional, Tuple, Iterator

from paramiko import SFTPClient
from paramiko.sftp_attr import SFTPAttributes


class SFTP(SFTPClient):
    def chdir(self, path: Optional[Path]=None) -> None:
        super().chdir(str(path))

    def chmod(self, path: Path, mode: int) -> None:
        super().chmod(str(path), mode)

    def chown(self, path: Path, uid: int, gid: int) -> None:
        super().chown(str(path), uid, gid)

    def get(self, remotepath: Path, localpath: Path, callback: Optional[Tuple[int, int]]=None) -> None:
        super(SFTP, self).get(str(remotepath), str(localpath))

    def put(self, localpath: Path, remotepath: Path, callback: Optional[Tuple[int, int]]=None,
            confirm: bool=True) -> SFTPAttributes:
        super().put(str(localpath), str(remotepath))

    def readlink(self, path: Path) -> Optional[str]:
        return super().readlink(str(path))

    def remove(self, path: Path) -> None:
        super().remove(str(path))

    def rmdir(self, path: Path) -> None:
        super().rmdir(str(path))

    def truncate(self, path: Path, size: int) -> None:
        super().truncate(str(path), size)

    def utime(self, path: Path, times: Optional[Tuple[float, float]]) -> None:
        super().utime(str(path), times)

    def lstat(self, path: Path) -> SFTPAttributes:
        return super().lstat(str(path))

    def mkdir(self, path: Path, mode: int=511) -> None:
        super().mkdir(str(path))

    def normalize(self, path: Path) -> str:
        return super().normalize(str(path))

    def listdir(self, path: Path=".", flag: bool=None) -> List[str]:
        return [file.filename for file in self.listdir_attr(path, flag)]

    def listdir_attr(self, path: Path=".", flag: bool=None) -> List[SFTPAttributes]:
        filelist = super().listdir_attr(str(path))

        if flag:
            files = {file: self.stat(path / file.filename).st_mtime
                     for file in filelist}
            return sorted(files, key=files.get)

        return filelist

    def last_modified_file(self, path: Path) -> str:
        return self.listdir_attr(path, True)[-1].filename

    def stat(self, path: Path) -> List[SFTPAttributes]:
        return super().stat(str(path))

    def unlink(self, path: Path) -> None:
        super().unlink(str(path))

    def listdir_iter(self, path: Path) -> Iterator[SFTPAttributes]:
        return super().listdir_iter(str(path))