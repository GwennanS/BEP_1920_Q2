import json
import os
import time

import requests
from sciler.device import Device

"""
https://domoticproject.com/controlling-philips-hue-lights-with-raspberry-pi/
How to use Hue Lights with S.C.I.L.E.R.:
- download Hue app
- create groups and scenes to use in the escape room
- retrieve IP address of hue bridge ( apt-get install avahi-utils ; avahi-browse -rt _hue._tcp )
- retrieve valid hue username (curl -d '{"devicetype":"[whatever]"}' -H
"Content-Type: application/json" -X POST 'http://<BRIDGE_IP>/api' ; returns long hue username)
- retrieve scene id's ( curl 'http://<hue bridge IP>/api/<hue username>/scenes )
- implement config using scene ids
"""
"""
current scenes:
{"jDMyoEKOrmIFHOA":{"name":"Ontspannen","type":"GroupScene","group":"1","lights":["1","2","3","4"],"owner":"09837eab-cbfa-4e9c-b4eb-8fc8f1f97e78","recycle":false,"locked":false,"appdata":{"version":1,"data":"BfWl5_r01_d01"},"picture":"","lastupdated":"2020-01-10T10:55:23","version":2},
"fzxtSqzVzTuSc5h":{"name":"Lezen","type":"GroupScene","group":"1","lights":["1","2","3","4"],"owner":"09837eab-cbfa-4e9c-b4eb-8fc8f1f97e78","recycle":false,"locked":false,"appdata":{"version":1,"data":"4Yawq_r01_d02"},"picture":"","lastupdated":"2020-01-10T10:55:23","version":2},
"4DZP3Df6TQT1Hth":{"name":"Concentreren","type":"GroupScene","group":"1","lights":["1","2","3","4"],"owner":"09837eab-cbfa-4e9c-b4eb-8fc8f1f97e78","recycle":false,"locked":false,"appdata":{"version":1,"data":"cNmrX_r01_d03"},"picture":"","lastupdated":"2020-01-10T10:55:23","version":2},
"3UlNGpm1hvwgLGf":{"name":"Energie","type":"GroupScene","group":"1","lights":["1","2","3","4"],"owner":"09837eab-cbfa-4e9c-b4eb-8fc8f1f97e78","recycle":false,"locked":false,"appdata":{"version":1,"data":"1QZhD_r01_d04"},"picture":"","lastupdated":"2020-01-10T10:55:23","version":2},
"PnwvUwfd3BV76Ya":{"name":"Helder","type":"GroupScene","group":"1","lights":["1","2","3","4"],"owner":"09837eab-cbfa-4e9c-b4eb-8fc8f1f97e78","recycle":false,"locked":false,"appdata":{"version":1,"data":"NhEXw_r01_d05"},"picture":"","lastupdated":"2020-01-10T10:55:23","version":2},
"9ul4tcAPnFYmBAo":{"name":"Gedimd","type":"GroupScene","group":"1","lights":["1","2","3","4"],"owner":"09837eab-cbfa-4e9c-b4eb-8fc8f1f97e78","recycle":false,"locked":false,"appdata":{"version":1,"data":"5y4vQ_r01_d06"},"picture":"","lastupdated":"2020-01-10T10:55:24","version":2},
"L7PC5YY-fmmR3b9":{"name":"Nachtlampje","type":"GroupScene","group":"1","lights":["1","2","3","4"],"owner":"09837eab-cbfa-4e9c-b4eb-8fc8f1f97e78","recycle":false,"locked":false,"appdata":{"version":1,"data":"NXcUw_r01_d07"},"picture":"","lastupdated":"2020-01-10T10:55:24","version":2},
"wvz3NRzyxyPDKWy":{"name":"Savanne zonsondergang","type":"GroupScene","group":"1","lights":["1","2","3","4"],"owner":"09837eab-cbfa-4e9c-b4eb-8fc8f1f97e78","recycle":false,"locked":false,"appdata":{"version":1,"data":"yQtch_r01_d15"},"picture":"","lastupdated":"2020-01-10T10:55:24","version":2},
"5P6KFCzwXKKjdIL":{"name":"Tropische schemering","type":"GroupScene","group":"1","lights":["1","2","3","4"],"owner":"09837eab-cbfa-4e9c-b4eb-8fc8f1f97e78","recycle":false,"locked":false,"appdata":{"version":1,"data":"j2XJH_r01_d16"},"picture":"","lastupdated":"2020-01-10T10:55:24","version":2},
"VCxaJj7gH1np6-S":{"name":"Arctische dageraad","type":"GroupScene","group":"1","lights":["1","2","3","4"],"owner":"09837eab-cbfa-4e9c-b4eb-8fc8f1f97e78","recycle":false,"locked":false,"appdata":{"version":1,"data":"PUsIU_r01_d17"},"picture":"","lastupdated":"2020-01-10T10:55:24","version":2},
"xAgrIMeKpZD8Gla":{"name":"Lentebloesem","type":"GroupScene","group":"1","lights":["1","2","3","4"],"owner":"09837eab-cbfa-4e9c-b4eb-8fc8f1f97e78","recycle":false,"locked":false,"appdata":{"version":1,"data":"vmRcf_r01_d18"},"picture":"","lastupdated":"2020-01-10T10:55:24","version":2},
"0TOnN5zTfRSOTmC":{"name":"Kerst","type":"GroupScene","group":"1","lights":["1","2","3","4"],"owner":"09837eab-cbfa-4e9c-b4eb-8fc8f1f97e78","recycle":false,"locked":false,"appdata":{"version":1,"data":"UYU33_r01_d99"},"picture":"","lastupdated":"2020-01-10T12:51:57","version":2},
"MBvYmUk1U-EUaGz":{"name":"Halloween","type":"GroupScene","group":"1","lights":["1","2","3","4"],"owner":"09837eab-cbfa-4e9c-b4eb-8fc8f1f97e78","recycle":false,"locked":false,"appdata":{"version":1,"data":"phMML_r01_d99"},"picture":"","lastupdated":"2020-01-10T12:51:33","version":2},
"J5vJs20sDr9ZpGB":{"name":"Kleurrijk","type":"GroupScene","group":"1","lights":["1","2","3","4"],"owner":"09837eab-cbfa-4e9c-b4eb-8fc8f1f97e78","recycle":false,"locked":false,"appdata":{"version":1,"data":"0vFOg_r01_d99"},"picture":"","lastupdated":"2020-01-10T13:20:13","version":2},
"dyUFQw0nqbkmY3D":{"name":"Focus1","type":"GroupScene","group":"1","lights":["1","2","3","4"],"owner":"09837eab-cbfa-4e9c-b4eb-8fc8f1f97e78","recycle":false,"locked":false,"appdata":{"version":1,"data":"BAEtJ_r01_d99"},"picture":"","lastupdated":"2020-01-30T08:48:55","version":2},
"v1rapwJJ0fe3JtM":{"name":"Focus2","type":"GroupScene","group":"1","lights":["1","2","3","4"],"owner":"09837eab-cbfa-4e9c-b4eb-8fc8f1f97e78","recycle":false,"locked":false,"appdata":{"version":1,"data":"2E33y_r01_d99"},"picture":"","lastupdated":"2020-01-30T08:49:42","version":2},
"NvjJYxd3ylYMJlK":{"name":"Focus3","type":"GroupScene","group":"1","lights":["1","2","3","4"],"owner":"09837eab-cbfa-4e9c-b4eb-8fc8f1f97e78","recycle":false,"locked":false,"appdata":{"version":1,"data":"VlkoK_r01_d99"},"picture":"","lastupdated":"2020-01-30T08:50:25","version":2},
"L0MTsayuGYndnGC":{"name":"Focus4","type":"GroupScene","group":"1","lights":["1","2","3","4"],"owner":"09837eab-cbfa-4e9c-b4eb-8fc8f1f97e78","recycle":false,"locked":false,"appdata":{"version":1,"data":"Zwhwe_r01_d99"},"picture":"","lastupdated":"2020-01-30T08:51:21","version":2}}
"""


class HueLights(Device):
    def __init__(self):
        two_up = os.path.abspath(os.path.join(__file__, ".."))
        rel_path = "hue_lights_config.json"
        abs_file_path = os.path.join(two_up, rel_path)
        abs_file_path = os.path.abspath(os.path.realpath(abs_file_path))
        config = open(file=abs_file_path)
        super().__init__(config)
        self.scene = "none"
        self.bri = 0
        self.x = 0
        self.y = 0
        #self.hue_bridge = "http://192.168.178.20/"
        self.hue_bridge = "http://192.168.0.106/"
        #self.hue_user = "JQrPwJNthHtfPEG9vhW3mqwIVuFo3ESLD3gvkZOB"
        self.hue_user = "d3Vji9wgd150ttFBQM3wHl-DyXVBYWnZdO6ALHci"

        self.group = "Spotlights"
        self.header = {"Content-type": "application/json"}

    def get_status(self):
        return {"all": self.scene}

    def perform_instruction(self, action):
        instruction = action.get("instruction")

        if instruction == "scene":
            self.set_scene(action)
        elif instruction == "manual":
            self.set_manual(action.get("component_id"), action.get("value"))
        elif instruction == "bri" or instruction == "x" or instruction == "y":
            self.set_single(action)
        else:
            return False
        return True

    def test(self):
        params = json.dumps({"on": True, "bri": 200, "xy": [0.3, 0.3]})
        url = (self.hue_bridge
               + "api/"
               + self.hue_user
               + "/groups/"
               + self.group
               + "/action")
        requests.put(url,
                     data=params,
                     headers=self.header,
                     )
        time.sleep(2)
        self.pub_to_hue(url)

    def set_scene(self, data):
        self.scene = data.get("value")
        params = json.dumps({"scene": self.scene})
        resp = requests.put(
            self.hue_bridge
            + "api/"
            + self.hue_user
            + "/groups/"
            + self.group
            + "/action",
            data=params,
            headers=self.header,
        )
        if resp.status_code == 200:
            self.log("Template has been published.")
        else:
            self.log("Unable to publish template.")
        self.status_changed()

    def set_manual(self, comp, data):
        self.bri = data[1]
        self.x = data[2][0]
        self.y = data[2][1]
        if comp == "all":
            url = (
                    self.hue_bridge
                    + "api/"
                    + self.hue_user
                    + "/groups/"
                    + self.group
                    + "/action"
            )
        else:
            url = (
                    self.hue_bridge
                    + "api/"
                    + self.hue_user
                    + "/lights/"
                    + comp[-1:]
                    + "/state"
            )
        self.pub_to_hue(url)

    def set_single(self, action):
        if action.get("instruction") == "bri":
            self.bri = action.get("value") * 2.5
        elif action.get("instruction") == "x":
            self.x = 1 / 100 * action.get("value")
        elif action.get("instruction") == "y":
            self.y = 1 / 100 * action.get("value")
        if action.get("component_id") == "all":
            url = (
                    self.hue_bridge
                    + "api/"
                    + self.hue_user
                    + "/groups/"
                    + self.group
                    + "/action"
            )
        else:
            url = (
                    self.hue_bridge
                    + "api/"
                    + self.hue_user
                    + "/lights/"
                    + action.get("component_id")[-1:]
                    + "/state"
            )
        self.pub_to_hue(url)

    def pub_to_hue(self, url):
        params = json.dumps({"on": True, "bri": self.bri, "xy": [self.x, self.y]})
        print(params)
        resp = requests.put(url, data=params, headers=self.header)
        if resp.status_code == 200:
            self.log("Template has been published.")
        else:
            self.log("Unable to publish template.")
        self.status_changed()

    def reset(self):
        self.scene = "none"
        self.bri = 100
        self.x = 0.3
        self.y = 0.3
        url = (
                self.hue_bridge
                + "api/"
                + self.hue_user
                + "/groups/"
                + self.group
                + "/action"
        )
        self.pub_to_hue(url)

    def main(self):
        self.start()


if __name__ == "__main__":
    device = HueLights()
    device.main()
