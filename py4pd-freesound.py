import os
import pickle
import webbrowser

import pd
import requests_oauthlib

import freesound

auth_url = "https://freesound.org/apiv2/oauth2/authorize/"
redirect_url = "https://freesound.org/home/app_permissions/permission_granted/"
token_url = "https://freesound.org/apiv2/oauth2/access_token/"
scope = ["read", "write"]


# ╭──────────────────────────────────────╮
# │             Oauth Login              │
# ╰──────────────────────────────────────╯
def pickle_object(token, name):
    path = pd.get_patch_dir()
    with open(path + "/" + name + ".pkl", "wb") as f:
        pickle.dump(token, f)


def unpickle_object(name):
    path = pd.get_patch_dir()
    fp = path + "/" + name + ".pkl"
    if os.path.exists(fp):
        with open(fp, "rb") as f:
            token = pickle.load(f)
        return token
    else:
        raise FileNotFoundError("Token not found! Send [oauth] for freesound object.")


# ╭──────────────────────────────────────╮
# │            LOGIN METHODS             │
# ╰──────────────────────────────────────╯

"""
We use global variables to store the client_id, api_key, and oauth_key. 
"""

FREESOUND_CLIENT = None
OAUTH = None
TOKEN = None
CLIENT_ID = None
API_KEY = None
OAUTH_KEY = None
LOGGED_IN = False


def set_login_var(listKey):
    global OAUTH
    global TOKEN
    global CLIENT_ID
    global API_KEY
    global OAUTH_KEY

    key = listKey[0]
    value = listKey[1]

    if key == "client":
        CLIENT_ID = value
    elif key == "api-key":
        API_KEY = value
    elif key == "oauth":
        OAUTH_KEY = value
    else:
        raise AttributeError("Invalid key")


def initialize_oauth():
    global OAUTH
    global LOGGED_IN
    global CLIENT_ID
    if CLIENT_ID is None:
        pd.error("Please set client_id first")

    path = pd.get_patch_dir()
    fp = path + "/_token.pkl"
    if os.path.exists(fp):
        token = unpickle_object("_token")
        OAUTH = requests_oauthlib.OAuth2Session(
            CLIENT_ID, redirect_uri=redirect_url, scope=scope, token=token
        )
        LOGGED_IN = True

    else:
        OAUTH = requests_oauthlib.OAuth2Session(
            CLIENT_ID, redirect_uri=redirect_url, scope=scope
        )
        authorization_url, _ = OAUTH.authorization_url(auth_url)
        webbrowser.open(authorization_url)
        pd.print("Check your default browser")


def login():
    global OAUTH
    global TOKEN
    global CLIENT_ID
    global LOGGED_IN
    global API_KEY
    global OAUTH_KEY
    global FREESOUND_CLIENT

    if OAUTH is None:
        raise AttributeError("Please initialize oauth first")
    if API_KEY is None:
        raise AttributeError("Please set api_key first")

    if OAUTH_KEY is None:
        raise AttributeError("Please auth first")

    if LOGGED_IN:
        token = unpickle_object("_token")
        FREESOUND_CLIENT = freesound.FreesoundClient()
        FREESOUND_CLIENT.set_token(token["access_token"], auth_type="oauth")
        pd.print("Logged successfully")
    else:
        token = OAUTH.fetch_token(
            token_url,
            authorization_response=OAUTH_KEY,
            code=OAUTH_KEY,
            client_secret=API_KEY,
        )
        pickle_object(token, "_token")
        pd.print("Logged successfully")
        token = unpickle_object("_token")
        FREESOUND_CLIENT = freesound.FreesoundClient()
        FREESOUND_CLIENT.set_token(token["access_token"], auth_type="oauth")


# ╭──────────────────────────────────────╮
# │            Search Methods            │
# ╰──────────────────────────────────────╯
def get(something):
    results = pd.get_obj_var("search")
    if results is None:
        raise AttributeError("Please search first")
    if hasattr(results[0], something):
        pd.print("", show_prefix=False)
        for result in results:
            pd.print(getattr(result, something))
    else:
        error = f"Attribute '{something}' does not exist"
        raise AttributeError(error)


def download(id):
    global FREESOUND_CLIENT
    results = pd.get_obj_var("search")
    for result in results:
        if result.id == id:
            path = pd.get_patch_dir() + "/freesound"
            if not os.path.exists(path):
                os.makedirs(path)

            filename = path + f"/{result.id}.{result.type}"
            if os.path.exists(filename):
                pd.print("File already downloaded")
                return ["sound", filename]

            result.retrieve(path, name=f"{result.id}.{result.type}")
            pd.print("Downloaded successfully")
            return ["sound", path + f"/{result.id}.{result.type}"]


def target(params):
    if not FREESOUND_CLIENT:
        pd.error("Please login first")
        return

    # Ensure params has the correct length and types
    if len(params) < 2:
        pd.error("Insufficient parameters provided")
        return

    results = pd.get_obj_var("target", initial_value=[])
    for i in range(len(results)):
        if results[i][0] == params[0]:
            results[i] = params
            pd.set_obj_var("target", results)
            return
    results.append(params)
    pd.set_obj_var("target", results)


def filter(params):
    if not FREESOUND_CLIENT:
        pd.error("Please login first")
        return

    # Ensure params has the correct length and types
    if len(params) < 2:
        pd.error("Insufficient parameters provided")
        return

    results = pd.get_obj_var("filter", initial_value=[])
    for i in range(len(results)):
        if results[i][0] == params[0]:
            results[i] = params
            pd.set_obj_var("filter", results)
            return
    results.append(params)
    pd.set_obj_var("filter", results)


def query(params):
    if not FREESOUND_CLIENT:
        pd.error("Please login first")
        return

    # Ensure params has the correct length and types
    if len(params) < 1:
        pd.error("To use [query], type at least 1 word")
        return

    if type(params) != list:
        params = [params]

    pd.set_obj_var("query", [])
    query = pd.get_obj_var("query", initial_value=[])
    for i in range(len(params)):
        query.append(params[i])
    pd.set_obj_var("query", query)


def search():
    global FREESOUND_CLIENT

    if FREESOUND_CLIENT is None:
        pd.error("Please login first")
        return None

    # target
    target = pd.get_obj_var("target", initial_value=[])
    filter = pd.get_obj_var("filter", initial_value=[])

    # TODO: Precisa rever isso aqui para ser mais completo
    target_string = ""
    for i in range(len(target)):
        target_string += f"{target[i][0]}:{target[i][1]} "

    filter_string = ""
    for i in range(len(filter)):
        if len(filter[i]) == 2:
            filter_string += f"{filter[i][0]}:{filter[i][1]} AND "
        elif len(filter[i]) == 3:
            filter_string += f"{filter[i][0]}:[{filter[i][1]} TO {filter[i][2]}] AND "
        else:
            raise AttributeError(
                "Filter with more than 3 parameters are not implemented yet"
            )

    if filter_string == "":
        filter_string = None

    # query
    query = pd.get_obj_var("query", initial_value=[])
    query = " ".join(query)

    # finally search
    results = FREESOUND_CLIENT.text_search(
        query=query,
        target=target_string,
        filter=filter_string,
        fields="id,name,duration,type",
    )

    if len(results.results) == 0:
        pd.print("No results found")
        return

    if hasattr(results[0], "name"):
        pd.print("", show_prefix=False)
        for result in results:
            pd.print(getattr(result, "id"), getattr(result, "name"))

    pd.set_obj_var("search", results)
    pd.print("Search completed!")


def clear():
    pd.set_obj_var("target", [])
    pd.set_obj_var("filter", [])
    pd.set_obj_var("query", [])
    pd.print("Parameters cleared")


# ╭──────────────────────────────────────╮
# │           Freesound Object           │
# ╰──────────────────────────────────────╯
def py4pdLoadObjects():
    # freesound
    pd_freesound = pd.new_object("freesound")
    pd_freesound.py_out = True
    pd_freesound.ignore_none = True

    # login
    pd_freesound.addmethod("set", set_login_var)
    pd_freesound.addmethod("oauth", initialize_oauth)
    pd_freesound.addmethod("login", login)

    # search
    pd_freesound.addmethod("target", target)
    pd_freesound.addmethod("filter", filter)
    pd_freesound.addmethod("query", query)

    pd_freesound.addmethod("search", search)

    pd_freesound.addmethod("clear", clear)  # clear all configs

    # get info
    pd_freesound.addmethod("get", get)

    # download
    pd_freesound.addmethod("download", download)

    pd_freesound.add_object()
