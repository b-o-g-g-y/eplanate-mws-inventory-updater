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
    get orders from WMS

    """

    eplanetaApi = EplanetaAPI()
    eplanetaApi.get_token()
    wmsApi = WMSAPI()

    fromDate = datetime.now() - timedelta(days=1)
    toDate = datetime.now()

    eplanetaOrders = eplanetaApi.getDeliveries("PENDING", fromDate, toDate)
    if not eplanetaOrders:
        logger.error("Unexpected order structure from Eplaneta API")
        return
    
    wmsOrders = wmsApi.getOrders(date_from=fromDate.strftime("%Y-%m-%d"), date_to=toDate.strftime("%Y-%m-%d"))
    if not wmsOrders:
        logger.error("Unexpected order structure from WMS API")
        return

    for order in wmsOrders:
        # Make sure all wmsOrders that are marked Processed are Confirmed on Eplaneta
        orderReference = order['attributes']["reference"]
        if order['attributes']["status"] == "Processed":
            # find the matching order in eplaneta using the order reference
            matchingOrder = next((order for order in eplanetaOrders if order["deliveryNumber"] == orderReference), None)

            if matchingOrder:
                print("Updating order status to Confirmed for order", orderReference)
                # eplanetaApi.updateStatus(matchingOrder["id"], "Confirmed")
      

        # Make sure all wmsOrders that are marked Packed are "Waiting for receipt" on Eplaneta
        if order['attributes']["status"] == "Packed":
            # find the matching order in eplaneta using the order reference
            matchingOrder = next((order for order in eplanetaOrders if order["deliveryNumber"] == orderReference), None)

            if matchingOrder:
                print("Updating order status to Waiting for receipt for order", orderReference)
                # eplanetaApi.updateStatus(matchingOrder["id"], "Waiting for receipt")

        # Make sure all wmsOrders that are marked Returned are "Returned to warehouse" on Eplaneta
        if order['attributes']["status"] == "Returned":
            # find the matching order in eplaneta using the order reference
            matchingOrder = next((order for order in eplanetaOrders if order["deliveryNumber"] == orderReference), None)

            if matchingOrder:
                print("Updating order status to Returned to warehouse for order", orderReference)
                # eplanetaApi.updateStatus(matchingOrder["id"], "Returned to warehouse")

        # Make sure all wmsOrders that are marked Missing are "Not confirmed or Partially_confirmed" on Eplaneta
        if order['attributes']["status"] == "Missing":
            # find the matching order in eplaneta using the order reference
            matchingOrder = next((order for order in eplanetaOrders if order["deliveryNumber"] == orderReference), None)

            if matchingOrder:
                print("Updating order status to Not confirmed or Partially_confirmed for order", orderReference)
                # eplanetaApi.updateStatus(matchingOrder["id"], "Not confirmed or Partially_confirmed")





if __name__ == "__main__":
    main()