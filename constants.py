from environs import Env


env = Env()
env.read_env()


HOST = env.str("HOST")
PORT = env.int("PORT")
USERNAME = env.str("NAMEUSER")
PASSWORD = env.str("PASSWORD")
PATH_LOG_FILE = 'sftp/resources/log/main.json'