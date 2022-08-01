import os
import config

if __name__ == '__main__':
    if not os.path.exists(config.ACCOUNTS_FOLDER):
        os.mkdir(config.ACCOUNTS_FOLDER)
    if not os.path.exists(config.VIDEOS_FOLDER):
        os.mkdir(config.VIDEOS_FOLDER)