import json

secrets = {
    "web": {
    "client_id": None,
    "client_secret": None,
    "redirect_uris": [],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://accounts.google.com/o/oauth2/token"
}}

if __name__ == "__main__":
    name = input("Enter name of the account: ")
    client_id = input("Enter client id from google console API: ")
    client_secret = input("Enter client secret from google console API: ")
    secrets['web']['client_id'] = client_id
    secrets['web']['client_secret'] = client_secret

    with open(f'client_secrets_{name}.json', 'w') as file: 
        json.dump(secrets, file, ensure_ascii=True, indent=4)
    print(f"Succesfully save secrets to client_secrets_{name}.json file")