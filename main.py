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
print(test._adjust_cwd("/root"))
channel.close()
