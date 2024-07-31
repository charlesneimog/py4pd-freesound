import os
import pickle
import webbrowser

import librosa
import pd
import requests
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
# │       freesound object methods       │
# ╰──────────────────────────────────────╯

FREESOUND_CLIENT = None

OAUTH = None
TOKEN = None
CLIENT_ID = None
API_KEY = None
OAUTH_KEY = None
LOGGED_IN = False


def setThing(listKey):
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
    else:
        token = OAUTH.fetch_token(
            token_url,
            authorization_response=OAUTH_KEY,
            code=OAUTH_KEY,
            client_secret=API_KEY,
        )
        pickle_object(token, "_token")
        pd.print("Logged in successfully")
        token = unpickle_object("_token")
        FREESOUND_CLIENT = freesound.FreesoundClient()
        FREESOUND_CLIENT.set_token(token["access_token"], auth_type="oauth")


def filter(args):
    key = args[0]
    if key == "duration":
        min_duration = args[1]
        max_duration = args[2]
        pd.set_obj_var(
            "f_duration", "duration:[{} TO {}]".format(min_duration, max_duration)
        )
        pd.print("Duration filter set")


def search(query):
    global FREESOUND_CLIENT

    if FREESOUND_CLIENT is None:
        pd.error("Please login first")
        return None

    pd.print("Searching for: " + query)
    filter = ""
    duration_filter = pd.get_obj_var("f_duration")
    if duration_filter is not None:
        filter = duration_filter

    if filter != "":
        results = FREESOUND_CLIENT.text_search(
            query=query, fields="name,id", filter=filter
        )
    else:
        results = FREESOUND_CLIENT.text_search(query=query, fields="name,id")

    pd.set_obj_var("search", results)
    pd.print("Search completed!")


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
            filename = path + f"/{result.id}.wav"
            if os.path.exists(filename):
                pd.print("File already downloaded")
                return ["sound", filename]
            result.retrieve(path, name=f"{result.id}.wav")
            pd.print("Downloaded successfully")
            return ["sound", path + f"/{result.id}.wav"]


# ╭──────────────────────────────────────╮
# │          Parameters Builder          │
# ╰──────────────────────────────────────╯
def addParamsSearch(params):
    if not FREESOUND_CLIENT:
        pd.error("Please login first")
        return

    # Ensure params has the correct length and types
    if len(params) < 2:
        pd.error("Insufficient parameters provided")
        return

    param_id = params[0]
    parameter0 = params[1]

    if len(params) == 3:
        parameter1 = params[2]
        if isinstance(parameter0, float):
            parameter0 = round(parameter0, 2)
        if isinstance(parameter1, float):
            parameter1 = round(parameter1, 2)
        string = f"{param_id}:[{parameter0} TO {parameter1}]"
    else:
        string = f"{param_id}:{parameter0}"

    results = pd.get_obj_var("params", initial_value=[])
    results.append(string)
    pd.set_obj_var("params", results)


def clear():
    pd.set_obj_var("params", [])
    pd.print("Parameters cleared")


def freesoundParamsSearch():
    global FREESOUND_CLIENT
    if FREESOUND_CLIENT is None:
        pd.error("Please login first")
        return None

    results = pd.get_obj_var("params", initial_value=[])
    if not results:
        pd.error("Please add parameters first")
        return

    string = " ".join(results)
    string = string.encode("utf-8")
    results_pager = FREESOUND_CLIENT.content_based_search(
        descriptors_filter=string,
        fields="id,name,analysis,duration",
    )
    pd.set_obj_var("search", results_pager)
    pd.print("Search completed!")


# ╭──────────────────────────────────────╮
# │           Freesound Object           │
# ╰──────────────────────────────────────╯
def py4pdLoadObjects():
    # freesound
    py4pd_parmsearch = pd.new_object("f.main")
    py4pd_parmsearch.py_out = True
    py4pd_parmsearch.ignore_none = True

    py4pd_parmsearch.addmethod("oauth", initialize_oauth)
    py4pd_parmsearch.addmethod("login", login)
    py4pd_parmsearch.addmethod("search", search)
    py4pd_parmsearch.addmethod("get", get)
    py4pd_parmsearch.addmethod("set", setThing)
    py4pd_parmsearch.addmethod("download", download)
    py4pd_parmsearch.addmethod("filter", filter)

    py4pd_parmsearch.add_object()

    # f.paramsearch
    py4pd_parmsearch = pd.new_object("f.paramsearch")
    py4pd_parmsearch.addmethod("search", freesoundParamsSearch)
    py4pd_parmsearch.addmethod("add", addParamsSearch)
    py4pd_parmsearch.addmethod("clear", clear)
    py4pd_parmsearch.addmethod("get", get)
    py4pd_parmsearch.addmethod("download", download)
    py4pd_parmsearch.add_object()
