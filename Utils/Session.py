import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Session(object):
    def __init__(self, apic_ip, apic_port, user, passwd):
        self.ip = apic_ip
        self.port = apic_port
        self.user = user
        self.passwd = passwd
        self.ACIERROR = Exception
        self.cookie = ''

    def set_cookie(self, cookie):
        self.cookie = cookie

    def get_cookie(self):
        try:
            auth_url = "https://%s:%s/api/aaaLogin.json" % (self.ip, self.port)
            auth_json = '{"aaaUser": {"attributes": {"name": "%s", "pwd": "%s"}}}' % (self.user, self.passwd)
            print("Getting cookie from %s" % self.ip)
            session = requests.post(auth_url, data=auth_json, verify=False, timeout=5)
            session_json = session.json()
            token = session_json["imdata"][0]["aaaLogin"]["attributes"]["token"]
            return {'APIC-cookie': token}
        except requests.exceptions.Timeout:
            print("APIC %s timed out " % (self.ip))
            auth_url = "https://%s:%s/api/aaaLogin.json" % (self.ip, self.port)
            auth_json = '{"aaaUser": {"attributes": {"name": "%s", "pwd": "%s"}}}' % (self.user, self.passwd)
            print("Getting cookie from %s" % self.ip)
            session = requests.post(auth_url, data=auth_json, verify=False, timeout=5)
            session_json = session.json()
            token = session_json["imdata"][0]["aaaLogin"]["attributes"]["token"]
            return {'APIC-cookie': token}
        except requests.exceptions.ConnectionError:
            print("Connection error can't logging to APIC %s with user %s" % (self.ip, self.user))

    def apic_xml_post(self, xmldata):
        xmlpost_url = "https://%s:%s/api/policymgr/mo/.xml" % (self.ip, self.port)
        xmlpost = requests.post(xmlpost_url, data=xmldata, cookies=self.cookie, verify=False)
        if xmlpost.status_code != 200:
            return xmlpost.text
        else:
            return 200

    def apic_json_get(self, url):
        get_json_url = "https://%s:%s/api/class/%s.json" % (self.ip, self.port, url)
        json_get = requests.get(get_json_url, cookies=self.cookie, verify=False)
        print(get_json_url)
        if json_get.status_code == 200:
            return json_get.text
        else:
            print(json_get.text)

    def leaf_json_get(self, url):
        get_json_url = url
        json_get = requests.get(get_json_url, cookies=self.cookie, verify=False)
        print(get_json_url)
        if json_get.status_code == 200:
            return json_get.text
        else:
            print(json_get.text)
