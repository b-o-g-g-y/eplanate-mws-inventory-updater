import os
import logging
from wmsAPI import WMSAPI
from eplanetaAPI import EplanetaAPI
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def main():
    """
    get orders from eplaneta
    get order items from WMS for the last 3 days
    for each order on eplaneta that is not already on the WMS
        for each item on the order, upload it to the wms
    """

    eplanetaApi = EplanetaAPI()
    eplanetaApi.get_token()

    wmsApi = WMSAPI()


    fromDate = datetime.now() - timedelta(days=1)
    toDate = datetime.now()

    orders = eplanetaApi.getDeliveries("PENDING", fromDate, toDate)
    if not orders:
        logger.error("Unexpected order structure from Eplaneta API")
        return
    
    relevantData = []
    for order in orders:
        relevantOrderData = {}
        deliveryNumber = order["deliveryNumber"]
        orderItems = []
        for item in order["deliveryItem"]:
            sku = item["product"]["sku"]
            quantity = item["quantityOrder"]
            orderItems.append({
                "sku": sku,
                "quantity": quantity,
                "price_single": 1
            })
        relevantOrderData = {
            "deliveryNumber": deliveryNumber,
            "orderItems": orderItems
        }
        
        relevantData.append(relevantOrderData)

    for order in relevantData:
        dataForWMS = {
            "project_id": 55,
            "courier_code": "NO_COURIER",
            "order_reference": order["deliveryNumber"],
            "shipping_full_name": "Test Only",   
            "shipping_address_1": "Main street 22",
            "shipping_address_2": "Quarter 6",
            "shipping_address_3": "",
            "shipping_city": "Tokio",
            "shipping_zip": "12345",
            "shipping_country_code": "RS",
            "price_total": 1,
            "cn22_type": "Kozmetika",
            "currency": "RSD",
            "articles": order["orderItems"]
        }

        wmsApi.createOrder(dataForWMS)

if __name__ == "__main__":
    main()