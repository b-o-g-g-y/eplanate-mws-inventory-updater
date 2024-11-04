import requests
from dotenv import load_dotenv
import os

class WMSAPI:
    def __init__(self):
        load_dotenv()
        self.url = os.getenv("WMS_URL")
        self.client_id = os.getenv("WMS_CLIENT_ID")
        self.client_secret = os.getenv("WMS_CLIENT_SECRET")
        self.username = os.getenv("WMS_USERNAME")
        self.password = os.getenv("WMS_PASSWORD")
        self.token = os.getenv("WMS_TOKEN", None)

        if not self.token or self.token == "None":
            self.get_token()

    def get_token(self):

        data = {
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": self.username,
            "password": self.password
        }
        headers = {
            "Accept": "application/json", 
            "Content-Type": "application/json"
        }

        response = requests.post(
            f"{self.url}/oauth/token",
            headers=headers,
            json=data
        )   

        if response.status_code == 200:
            self.token = response.json()["access_token"]
            os.environ["WMS_TOKEN"] = self.token
        else:
            raise Exception("Failed to get token")
    
    def getInventory(self):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

        startdate = "2024-09-01"
        enddate = "2024-10-01"

        response = requests.get(
            f"{self.url}/api/articles?date_from={startdate}&date_to={enddate}",
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            raise Exception("Failed to get inventory")
# USAGE
wms = WMSAPI()
print(wms.getInventory())

        



