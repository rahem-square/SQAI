import numpy
from square.client import Client
import os
import json
import datetime
import uuid

#assuming we just use one location
locationId = 'LDH0RFQRQH4GB'
#code assumes there is only 1 variation per item
#assuming we know the two categories are Menu Item and Table
menuItemCatId = 'AZ5PUQGMUX5MKTMPC6BLJ7WA'
tableCatId = 'MS7DUCIL3YINNXVZHNWUELQD'

variationIdDict = {'Caesar Salad': 'PKTMJLSRFHOAT24YII7ZZAX3',
                       'Grilled Salmon': 'FDD7E5EDLY7PNJ2NBR3HB5JB',
                       'Lobster Tail': 'XKFCJ63QMXOEWPK5TVMYI4KJ',
                       'Grilled Steak': 'DRXQQEE3AXX3B4HTTC47UHXB',
                       'Chicken Wings': 'VLHE4ZVN3K7F3APJJES5TRSR',
                       'Cheesecake': 'GPEC7YGGTNYX2GLTP76SWMO3',
                       'Table #1': 'ZB2Q6W7M6QISEBHDH7QR7XZR',
                       'Table #2': '75QEVJSRFR6V5GPAZ5EBWRQW',
                       'Table #3': 'AIGQXD4V4PEOPO3XP7RDCOG6'
                       }

def timeNow():
    n = datetime.datetime.now(datetime.timezone.utc)
    return n.isoformat()

def clientSetup():    
    client = Client(
        access_token=os.environ['SQUARE_ACCESS_TOKEN'],
        environment='sandbox')
    return client

def getRestaurantInfo():
# Restaurant Data
    client = clientSetup()
    data = {}

    # Retrieve Location Information
    result = client.locations.retrieve_location(
    location_id = locationId
    )

    if result.is_success():
        location = result.body['location']
        data['address'] = f"{location['address']['address_line_1']}, {location['address']['locality']}, {location['address']['administrative_district_level_1']}"
        hours = []
        for period in location['business_hours']['periods']:
            hours.append(f"{period['day_of_week']} Hours: {period['start_local_time']} to {period['end_local_time']}")
        data['business_hours'] = ' '.join(x for x in hours)

    elif result.is_error():
        for error in result.errors:
            print(error['category'])
            print(error['code'])
            print(error['detail'])

    #Menu with item Prices - Catalog API
    
    result = client.catalog.list_catalog(
    types = "ITEM"
    )
    if result.is_success():
        items = result.body['objects']

        #dataMenuItems stores the menu items as a list of organized jsons inside of the business json
        dataMenuItems = []
        #dataTableItems stores tables as a list of jsons inside the business json
        dataTableItems = []
        for item in items:
            dataItem = {}
            itemCatId = item['item_data']['category_id']
            if itemCatId == tableCatId:
                #I am going to assume inventory is how you track a tables availability, which is likely not how it works, but Tables API is coming out anyways to replace the existing solution
                dataItem['name'] = item['item_data']['name']
                dataItem['description'] = item['item_data']['description_plaintext']
                dataItem['version'] = item['version']
                dataItem['variation_version'] = item['item_data']['variations'][0]['version']
                dataItem['id'] = item['id']
                dataItem['variation_id'] = item['item_data']['variations'][0]['id']
                #Inventory to see if table is available - Inventory API
                dataItem['table_availability'] = "UNKNOWN"
                result = client.inventory.retrieve_inventory_count(
                catalog_object_id = dataItem['variation_id'],
                location_ids = locationId
                )
                if result.is_success():
                    tableAvailability = int(result.body['counts'][0]['quantity'])
                    if(tableAvailability == 0):
                        dataItem['table_availability'] = "UNAVAILABLE"
                    if(tableAvailability == 1):
                        dataItem['table_availability'] = "AVAILABLE"
                dataTableItems.append(dataItem)

            elif itemCatId == menuItemCatId:
                dataItem['name'] = item['item_data']['name']
                itemPriceData = item['item_data']['variations'][0]['item_variation_data']['price_money']
                dataItem['price'] = f"{itemPriceData['amount']/100} {itemPriceData['currency']}"
                dataItem['description'] = item['item_data']['description_plaintext']
                dataItem['version'] = item['version']
                dataItem['variation_version'] = item['item_data']['variations'][0]['version']
                dataItem['id'] = item['id']
                dataItem['variation_id'] = item['item_data']['variations'][0]['id']
                #Inventory to see if item is available - Inventory API
                result = client.inventory.retrieve_inventory_count(
                catalog_object_id = dataItem['variation_id'],
                location_ids = locationId
                )
                if result.is_success():
                    dataItem['inventory_count'] = result.body['counts'][0]['quantity']
                dataMenuItems.append(dataItem)
    
        data['tables'] = dataTableItems
        data['menu'] = dataMenuItems

    #Reservations don't seem doable per table unless we just edit the catalog api info


    # ~ Smoke and Mirrors ~
    # we can also just make up info too, this can be presented as extra information that companies can add seperately via frontend component, 
    # maybe they can add their own "custom FAQ" answers
    data['parking_availaibility'] = "Our restaurant has a parking lot."
    data['delivery'] = "Our restaurant can deliver food to your location."


    json_object = json.dumps(data)
    
    print(json_object)    

    return json_object

# We can use this function behind the scenes as though it's the Restaurant POS KDS, which we can interact with to change table availaibilty and menu item stock
# refer to the variationIdDict for itemVariationIds (I should fix this if we have time)
def setItemStock(itemVariationId,quantity):
    #eg.
    #set table 1 to unavailiable:
    #setItemStock('ZB2Q6W7M6QISEBHDH7QR7XZR',0)
    #set grilled steak to 300 in stock:
    #setItemStock("Grilled Steak", 300)

    if itemVariationId in variationIdDict.keys():
        itemVariationId = variationIdDict[itemVariationId]
    
    client = clientSetup()
    #Note that the catalog object id here is for the item variaton's id, not the item itself.

    quantity = str(quantity)

    result = client.inventory.batch_change_inventory(
    body = {
        "idempotency_key": str(uuid.uuid4()),
        "changes": [
        {
            "type": "PHYSICAL_COUNT",
            "physical_count": {
            "catalog_object_id": itemVariationId,
            "state": "IN_STOCK",
            "location_id": locationId,
            "quantity": quantity,
            "occurred_at": timeNow()
            }
        }
        ]
    }
    )
    if result.is_success():
        print(result.body)
    elif result.is_error():
        print(result.errors)