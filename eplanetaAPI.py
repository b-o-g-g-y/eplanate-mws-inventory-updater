import requests
from dotenv import load_dotenv
import os


class EplanetaAPI:
    def __init__(self):
        load_dotenv()
        self.username = os.getenv("EPLANETA_USERNAME")
        self.password = os.getenv("EPLANETA_PASSWORD")
        self.url = os.getenv("EPLANETA_URL")
        self.token = None

    def get_token(self):
        data = {"username": self.username, "password": self.password}
        headers = {"Content-Type": "application/json"}
        requestUrl = f"{self.url}/login_check"

        response = requests.post(requestUrl, headers=headers, json=data)

        if response.status_code == 200:
            data = response.json()
            self.token = data["token"]
        else:
            raise Exception("Failed to get token")

    def getItem(self, sku, siteID):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        url = f"{self.url}/integration/product-info/1/6511"

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            raise Exception("Failed to get item")

    def getInventoryListing(self):
        headers = {"Authorization": f"Bearer {self.token}"}

        url = f"{self.url}/delivery-requests/warehouses"

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            raise Exception("Failed to get inventory listing")

    def getDeliveries(self):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        page = 1
        numPages = 9999
        deliveries = []

        while page <= numPages:
            url = f"{self.url}/delivery/list/{page}"
            response = requests.post(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                deliveries += data["data"]

                numPages = data["totalPage"]
                page += 1

        return deliveries

    def getDocument(self, deliveryId):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

        url = f"{self.url}/delivery-document/list"

        data = {"DeliveryId": deliveryId}

        response = requests.post(url, headers=headers)

        if response.status_code == 200:
            data = response.json()["documents"]

            for document in data:
                if (
                    document["documentType"] == "INVOICE"
                    and document["deliveryId"] == deliveryId
                ):
                    return document
        else:
            raise Exception("Failed to get document")

    # TODO: Test this function
    def updateStatus(self, id, status):
        """Updates delivery status in ePlaneta system.

        Args:
            id (int): Delivery ID
            status (str): New status - WAITING_FOR_RECEIPT or RETURNED_TO_WAREHOUSE

        Returns:
            dict: Response with updated status

        Raises:
            ValueError: If invalid status provided
            Exception: If API request fails
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

        # Different endpoints based on status
        if status == "WAITING_FOR_RECEIPT":
            url = f"{self.url}/delivery/submit-packed"
            data = {
                "deliveryID": id,
                "packagesAmount": 1,  # Required parameter, defaults to 1
            }
        elif status == "RETURNED_TO_WAREHOUSE":
            url = f"{self.url}/delivery/return-delivery-to-warehouse"
            data = {"deliveryID": id}
        else:
            raise ValueError(
                "Invalid status. Supported statuses: WAITING_FOR_RECEIPT, RETURNED_TO_WAREHOUSE"
            )

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to update status: {response.text}")


# Usage
api = EplanetaAPI()
api.get_token()

orders = api.getDeliveries()

# go through each order
# get the deliveryNumber
# get the Buyer name: invoice->dropship->buyer->name
# go through each deliveryItem in the order
# get the sku: product->sku
# get the quantity: quantityOrder

relevantData = []
for order in orders:
    relevantOrderData = {}
    deliveryNumber = order["deliveryNumber"]
    buyerName = order["invoice"]["dropship"]["buyer"]["name"]
    for item in order["deliveryItem"]:
        sku = item["product"]["sku"]
        quantity = item["quantityOrder"]
        relevantOrderData = {
            "deliveryNumber": deliveryNumber,
            "buyerName": buyerName,
            "sku": sku,
            "quantity": quantity,
        }

    # retrieve document
    document = api.getDocument(order["id"])
    documentUrl = f"https://pp-dev.planeta.services/api/rest/delivery-document/file-preview/{document['documentHash']}"

    # download document
    # get its content bytes

    relevantOrderData["document"] = document

    relevantData.append(relevantOrderData)

    # api.updateStatus(id, status)


"""
Update order status
    on a scheduled basis check the status of each order on the WMS
    update the order on eplaneta with the status from the WMS


    Write a function that will take a orderId and status as an input and update the oder/delivery status on eplaneta
"""
