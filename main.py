# import json
# import os
# from typing import List
# import config
# import datetime
# from Google import createService
# from googleapiclient.http import MediaFileUpload
# import datetime

# request_body = {
#     'snippet': {
#         'categoryI': 20,
#         'title': 'Title is here',
#         'description': 'description is here',
#         'tags': []
#     },
#     'status': {
#         'privacyStatus': 'public',
#         'selfDeclaredMadeForKids': False,
#     },
#     'notifySubscribers': False
#     }


# class Account():
#     def __init__(self, name: str, client_secrets: dict):
#         self.name = name
#         self.client_secrets = client_secrets
#         self.service = createService(self.name + '.json')
        

#     def uploadVideo(self, path: str, title: str, description: str, category_id: int, tags: List[str] = []):
#         media = MediaFileUpload(path)
#         request_body['snippet']['categoryI'] = category_id
#         request_body['snippet']['title'] = title
#         request_body['snippet']['description'] = description
#         request_body['snippet']['tags'] = tags
#         response_upload = self.service.videos().insert(
#             part = 'snippet,status',
#             body = request_body,
#             media_body = media
#         ).execute()
#         print(response_upload)


# def parseAccounts() -> List[Account]:
#     '''
#     Parsing client_secrets from folder with accounts

#     Returns
#     -------
#         accounts (List[Account]): List of accounts
#     '''
#     files_raw = os.listdir(config.ACCOUNTS_FOLDER)
#     accounts = []
#     for acc in files_raw:
#         with open(os.path.join(config.ACCOUNTS_FOLDER, acc)) as file:
#             data = json.load(file)
#         accounts.append(Account(acc[:-5], data))
        
#     return accounts


# if __name__ == '__main__':
#     accounts = parseAccounts()
#     accounts[0].uploadVideo('fine.mp4', 'Песня #shorts', 'Великий Новгород', 22)

from youtube_video_uploader_bot import *

youtube.login(username="dobrydnevna@fms2007.ru",password="Cremniy0207")