import os
import logging
from wmsAPI import WMSAPI
from eplanetaAPI import EplanetaAPI

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def sync_inventory():
    try:
        # Initialize API instances
        wms = WMSAPI()
        eplaneta = EplanetaAPI()

        # Authenticate with Eplaneta API
        if not eplaneta.get_token():
            logger.error("Failed to authenticate with Eplaneta API")
            return

        # Fetch inventory from WMS
        try:
            inventory = wms.getInventory()
            if 'data' not in inventory:
                logger.error("Unexpected inventory structure from WMS API")
                return
        except Exception as e:
            logger.error(f"Error fetching inventory from WMS: {e}")
            return

        # Fetch inventory from Eplaneta API
        try:
            eplaneta_inventory = eplaneta.getAllItems()
            eplanetaSKUS = {item['sku'] for item in eplaneta_inventory}
        except Exception as e:
            logger.error(f"Error fetching inventory from Eplaneta: {e}")
            return

        # Prepare stock data for upload
        stockDataToUpload = []
        for item in inventory['data']:
            try:
                itemAttributes = item['attributes']
                sku = itemAttributes['sku']
                stock = itemAttributes['stock'][0]['quantity']
                
                if sku in eplanetaSKUS:
                    stockDataToUpload.append({
                        "sku": sku,
                        "product_type": 'simple',
                        "stock": {"Arola Pazova magacin": stock},
                    })
            except KeyError as e:
                logger.warning(f"Missing expected data in WMS item {item}: {e}")
            except Exception as e:
                logger.error(f"Error processing WMS item {item}: {e}")

        # Upload stock data to Eplaneta
        if stockDataToUpload:
            try:
                updatedItemResponse = eplaneta.updateItems('eplaneta_srbija', stockDataToUpload)
                logger.info("Successfully updated items in Eplaneta")
                logger.debug(f"Eplaneta update response: {updatedItemResponse}")
            except Exception as e:
                logger.error(f"Error updating items in Eplaneta: {e}")
        else:
            logger.info("No items to update in Eplaneta")

    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    sync_inventory()

