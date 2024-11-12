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

        response = requests.get(
            f"{self.url}/api/articles",
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            raise Exception("Failed to get inventory")

    def createOrder(self, data):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

        url = f"{self.url}/api/orders"  

        response = requests.post(
            url,
            headers=headers,
            json=data
        )

        if response.status_code == 201:
            data = response.json()
            return data
        
        else:
            raise Exception("Failed to create order")
        
    def getOrders(self, date_from=None, date_to=None):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

        query_parameters = {}
        if date_from:
            query_parameters["date_from"] = date_from
        if date_to:
            query_parameters["date_to"] = date_to

        response = requests.get(
            f"{self.url}/api/orders",
            headers=headers,
            params=query_parameters
        )

        if response.status_code == 200:
            data = response.json()['data']
            return data
        else:
            raise Exception("Failed to get orders")



# # USAGE
# from datetime import datetime, timedelta
# wms = WMSAPI()
# # format date y-m-d
# date_from = datetime.now() - timedelta(days=5)
# date_to = datetime.now()
# print(wms.getOrders(date_from=date_from.strftime("%Y-%m-%d"), date_to=date_to.strftime("%Y-%m-%d")))

# '{"message":"The given data was invalid.","errors":{"shipping_country_code":["The shipping country code field is required."]}}'
# dataForWMS = {
#         "project_id": 55,
#         "courier_code": "NO_COURIER",
#         "order_reference": "123-TESTING-1",
#         "shipping_full_name": "Test Only",   
#         "shipping_address_1": "Main street 22",
#         "shipping_address_2": "Quarter 6",
#         "shipping_address_3": "",
#         "shipping_city": "Tokio",
#         "shipping_zip": "12345",
#         "shipping_country_code": "RS",
#         "price_total": 1,
#         "cn22_type": "Kozmetika",
#         "currency": "RSD",
#         "articles": [
#             {
#                 "sku": "parfem_1",
#                 "quantity": 2,
#                 "price_single": 1
#             }
#         ]
#     }

# print(wms.createOrder(dataForWMS))



        



