from pathlib import Path

import paramiko

from sftp.sftp import SFTP
from constants import HOST, PORT, USERNAME, PASSWORD


transport = paramiko.Transport((HOST, PORT))
transport.connect(None, USERNAME, PASSWORD)

channel = transport.open_session(window_size=10000, max_packet_size=10000)
channel.invoke_subsystem("sftp")
test = SFTP(channel)
print(test.listdir(Path("/root"), True))
print(test.last_modified_file(Path("/root")))
channel.close()


# with transport.open_session(window_size=10000, max_packet_size=10000) as channel:
#     channel.invoke_subsystem("sftp")
#     test = SFTP(channel)
#     print(test.listdir(Path("/root")))
#     print(test.listdir(Path("/root"), True))
#     print(test.listdir_attr(Path("/root")))
#     print(test.listdir_attr(Path("/root"), True))