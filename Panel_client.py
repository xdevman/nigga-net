import random
import string
import uuid
import requests
from config import PANEL_URL, PANEL_USER, PANEL_PASSWORD
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import os
import base64
import json
import urllib.parse
# Disable SSL warning if using self-signed certificate
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def to_bytes(gb: float) -> int:
    return int(gb * 1024 * 1024 * 1024)  # GB to bytes

def unsuccess(message):
    return {"success": False, "msg": str(message)}

def gen_random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def gen_base64_password():
    return base64.b64encode(os.urandom(32)).decode()

def build_shadowsocks_link(method, password, server, port, query='', label=''):
    # 1. Create the userinfo string: method:password
    userinfo = f"{method}:{password}"
    
    # 2. Base64 encode the userinfo bytes, then decode to str and strip trailing '='
    base64userinfo = base64.b64encode(userinfo.encode()).decode().rstrip('=')
    
    # 3. Build the basic link
    link = f"ss://{base64userinfo}@{server}:{port}"
    
    # 4. Add query string if provided (should start with '?')
    if query:
        if not query.startswith('?'):
            query = '?' + query
        link += query
    
    # 5. Add label if provided (URL-encoded, prefixed by '#')
    if label:
        encoded_label = urllib.parse.quote(label)
        link += f"#{encoded_label}"
    
    return link




class PanelClient:
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        self.session = requests.Session()

    def login(self):
        res = self.session.post(
            f"{self.url}/login",
            data={"username": self.username, "password": self.password},
            verify=False
        )
        if res.ok:
            print("[+] Logged in successfully")
        else:
            print("[-] Login failed:", res.text)

    def get_inbound_list(self):
        self.login()
        try:
            res = self.session.get(f"{self.url}/panel/api/inbounds/list", verify=False)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            print("[-] Failed to get inbound list:", e)
            return None
    
    def add_ss_client(self,userid, inbound_id=1):
        self.login()
        inbound_id = self.find_available_inbound()
        password = gen_base64_password()
        # email = gen_random_string()
        sub_id = gen_random_string(16)
        total_gb_bytes = to_bytes(10)  # 10 GB

        client_dict = {
            "method": "aes-256-gcm",
            "password": password,
            "email": userid,
            "limitIp": 0,
            "totalGB": total_gb_bytes,
            "expiryTime": 0,
            "enable": True,
            "tgId": "",
            "subId": sub_id,
            "comment": "",
            "reset": 0
        }

        payload = {
            "id": int(inbound_id),
            "settings": json.dumps({"clients": [client_dict]})
        }
        # print(payload)

        try:
            res = self.session.post(
                f"{self.url}/panel/api/inbounds/addClient",
                json=payload,
                headers={"Accept": "application/json"},
                verify=False
            )
            data = res.json()
            if not data.get("success"):
                return unsuccess(data.get("msg", "Failed to add client."))

            # Generate Shadowsocks URI
            ip = self.url.split("://")[1].split(":")[0]
            port = self.get_port_from_inbound(inbound_id)
            # encoded_pass = urllib.parse.quote(password)
            # encoded_email = urllib.parse.quote(email)
            # link = f"ss://aes-256-gcm:{encoded_pass}@{ip}:{port}#{encoded_email}"
            link = build_shadowsocks_link(
    method='aes-256-gcm',
    password=password,
    server='91.99.198.252',
    port=9094,
    query='type=tcp',
    label='@CyberNigga2'
)
            return {
                "success": True,
                "email": userid,
                "password": password,
                "subId": sub_id,
                "link": link
            }

        except Exception as e:
            return unsuccess(f"Error adding SS client: {str(e)}")



    def get_port_from_inbound(self, inbound_id):
        try:
            res = self.session.get(f"{self.url}/panel/api/inbounds/list", verify=False)
            data = res.json()
            for item in data.get("obj", []):
                if str(item.get("id")) == str(inbound_id):
                    return item.get("port")
        except Exception as e:
            print("[-] Failed to fetch inbound port:", e)
        return "0"
    
    def all_users(self):
        self.login()
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
    def get_user(self, userid):
        reqobj = self.all_users()
        if (reqobj['success']):
            cfgs = reqobj['obj'] 
            for cfg in cfgs:
                for client in cfg['clientStats']:
                    if (client['email'] == userid):
                        settings_str = cfg['settings']  # your string JSON
                        settings_dict = json.loads(settings_str)  # parse to dict
                        clients = settings_dict['clients']
                        for client in clients:
                            if client['email'] == userid:

                                link = build_shadowsocks_link(
            method='aes-256-gcm',
            password=client['password'],
            server='91.99.198.252',
            port=9094,
            query='type=tcp',
            label='@CyberNigga2'
        )
                                return link
                return unsuccess('user not found!')
            return unsuccess('users empty!')
        else:
            return unsuccess(reqobj['msg'])
    
    def get_inbounds(self):
        # call API to get all inbounds with their clients info
        res = self.session.get(f"{self.url}/panel/api/inbounds/list")
        return res.json()['obj']  # example structure

    def find_available_inbound(self,max_clients=240):

        inbounds = self.get_inbounds()
        for inbound in inbounds:
            clients = len(inbound['clientStats'])
            if clients < max_clients:
                return inbound['id']
        # None found - no inbound with free space
        return None
    def reset_users(self,users):
        self.login()
        try:
            for user in users:
                src = self.session.post(
                    f"{self.url}/panel/inbound/2/resetClientTraffic/{user}", verify=False
                )
            
            return "done"
        except Exception as e:
            res = unsuccess(e)
            print("error while getting users: ", e)
        return res

# Example usage:
# ss_link = build_shadowsocks_link(
#     method='aes-256-gcm',
#     password='RZh62D7FXBBTlsHPcZtfiMcGQ6uJBJVDJvJw0CqHtDY=',
#     server='91.99.198.252:2052',
#     port=9094,
#     query='type=tcp',
#     label='@CyberNigga2'
# )

# print(ss_link)

# Example usage
# if __name__ == "__main__":
    # client = PanelClient(PANEL_URL, PANEL_USER, PANEL_PASSWORD)
    # inbounds = client.get_inbound_list()
    # if inbounds:
    #     print("[+] Inbounds:")
    #     print(inbounds)

    # result = client.add_ss_client("132916606")
    # if result["success"]:
    #     print("[+] Link:", result["link"])
    # else:
    #     print("[-]", result["msg"])
    # res = client.get_user("132916606")
    # print(res)