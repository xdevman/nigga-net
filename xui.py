from random import randrange
import requests as req
from uuid import uuid4
import json
from config import *
import os
from dotenv import load_dotenv
load_dotenv()

# target = "https://127.0.0.1:54321"
# url = "http://159.69.37.238:54321"

url = PANEL_URL

def unsuccess(m):
    return ({"success": False, 'msg': str(m)})


def to_bytes(i: float):
    res = float(i) * 1024 * 1024 * 1024
    # return float("%.2f" % res)
    return int(res)

def to_gigabytes(i: float):
    res = float(i) / 1024 / 1024 / 1024
    return float("%.2f" % res)


def gen_config(_id, _uuid, traffic, expire_time, _uuid_splited, enable=True):
    return ({
        "id": f"{_id}",
        "settings": "{\"clients\": [{\n  \"id\": \"%s\",\n  \"flow\": \"%s\",\n  \"email\": \"%s\",\n  \"totalGB\": %s,\n  \"expiryTime\": %s,\n  \"enable\": %s,\n  \"tgId\": \"\",\n  \"subId\": \"%s\"\n}]}" % (_uuid, flow, _uuid, str(to_bytes(traffic)), str(expire_time*1000), json.dumps(enable), _uuid_splited)
    })


class Panel:
    def __init__(self, _id, url, usrname, passwd) -> None:
        self.session = req.Session()
        self.content_urlencoded = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        self.content_json = {'Content-Type': 'application/json'}
        self.session.headers.update = self.content_urlencoded
        self.url = url
        self.usrname = usrname
        self.passwd = passwd
        self._id = _id

    def islogin(self) -> bool:
        return (True if "login" not in self.session.get(self.url, verify=False).text.lower() else False)

    def login(self):
        self.session.post(f"{self.url}/login", data={
            "username": self.usrname, "password": self.passwd
        })

    def check_login(self):
        if (not self.islogin()):
            self.login()

    def create(self, traffic, expire_time):
        # traffic --> GB
        # expire_time --> unix time

        self.check_login()
        self.session.headers.update = self.content_json
        _uuid = str(uuid4())
        _uuid_splited = _uuid.replace("-", "")
        data = gen_config(self._id, _uuid, traffic, expire_time, _uuid_splited)
        try:
            src = self.session.post(
                f"{self.url}/xui/inbound/addClient", data=data, verify=False)
            res = src.json()
            res.update({'uuid':_uuid})
        except Exception as e:
            res = unsuccess(e)
            print("error while creating user: ", e)
        # print("#"*30, "\n", res)
        self.session.headers.update = self.content_urlencoded
        return res

    def all_users(self):
        self.check_login()
        try:
            src = self.session.get(
                f"{self.url}/panel/api/inbounds/list", verify=False
            )
            res = src.json()
            # print("x",res)
        except Exception as e:
            res = unsuccess(e)
            print("error while getting users: ", e)
        return res

    def update(self, uuid, traffic, expire, enable):
        self.check_login()

        self.session.headers.update = self.content_json
        try:
            src = self.session.post(
                f"{self.url}/xui/inbound/updateClient/{uuid}", data=gen_config(self._id, uuid, traffic, expire, uuid.replace("-", ""), enable), verify=False)
            res = src.json()

        except Exception as e:
            res = unsuccess(e)
            print("error while updaing user: ", e)
        # print("#"*30, "\n", res)
        self.session.headers.update = self.content_urlencoded
        return res

    def get_user(self, uuid):
        reqobj = self.all_users()
        if (reqobj['success']):
            cfgs = reqobj['obj'] 
            for cfg in cfgs:
                if cfg['id']==self._id:
                    for client in cfg['clientStats']:
                        print(cfg)
                        if (client['email'] == uuid):
                            client.update({"success": True})
                            return client
                    return unsuccess('user not found!')
            return unsuccess('users empty!')
        else:
            return unsuccess(reqobj['msg'])

    def delete(self, uuid):
        self.check_login()
        try:
            src = self.session.post(
                f"{self.url}/xui/inbound/{self._id}/delClient/{uuid}", verify=False)
            res = src.json()
        except Exception as e:
            res = unsuccess(e)
            print("error while deleting user: ", e)
        # print("#"*30, "\n", res)
        return res


myobj = Panel(4, url, PANEL_USER, PANEL_PASSWORD)


# myobj.all_users()
# myobj.update(10, 1700220032572)
# myobj.update("a56c406c-a156-4a4c-81af-4cb0020951df", 100, 1700220032, True)
# myobj.delete("a56c406c-a156-4a4c-81af-4cb0020951df")
print(myobj.get_user('xp4avysv'))
# myobj.all_users()