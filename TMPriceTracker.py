import requests
import json
from csv import writer
import datetime


class Tracker:
    """
        Tracker adds event information to the given file, which should be a .csv
    """
    #api = "KbtTMD50liCy9mA6Aeh0eG3EIoGD75xu"

    def __init__(self, file, api):
        self.file = file
        self.api = api

    def check_entries(self, response):
        response_dict = json.loads(response.text)
        min_price = ''
        max_price = ''
        try:
            if response_dict['priceRanges'][0]['min'] is not None:
                min_price = response_dict['priceRanges']['min']
            if response_dict['priceRanges'][0]['max'] is not None:
                max_price = response_dict['priceRanges']['max']
        except KeyError:
            min_price = ''
            max_price = ''

        row_list = [response_dict['id'],
                    response_dict['name'],
                    min_price,
                    max_price,
                    datetime.datetime.now()]

        return row_list

    def add_event(self, event_id):
        response2 = requests.get(f"https://app.ticketmaster.com/discovery/v2/events/{event_id}?apikey={self.api}")
        #response_dict2 = json.loads(response2.text)
        #query2 = response_dict2['priceRanges']

        row_list = self.check_entries(response2)

        # row_list = [response_dict2['id'],
        #             response_dict2['name'],
        #             query2[0]['min'],
        #             query2[0]['max'],
        #             datetime.datetime.now()]

        with open(self.file, 'a') as f_object:
            writer_object = writer(f_object, delimiter=",")
            writer_object.writerow(row_list)
            f_object.close()


tracker = Tracker("TicketMasterTracker.csv", "KbtTMD50liCy9mA6Aeh0eG3EIoGD75xu")
tracker.add_event("Z7r9jZ1AdO673")

# Ed Sheeran vvG1HZ9KD5yVsh
# Tegan & Sara Z7r9jZ1AdO673
# Paramore vvG1HZ9pk8jo1v

# response = requests.get(f"https://app.ticketmaster.com/discovery/v2/events.json?apikey={api}&city=seattle&classificationName=music")
# response_dict = json.loads(response.text)
# print(len(response_dict))
#
# for i in range(len(response_dict)):
#
#     query = response_dict['_embedded']['events'][i]
#     if 'priceRanges' in query:
#         print(query['priceRanges'])
#         print(query['name'], query['id'], query['url'])
#
# # print(type(response_dict['_embedded']['events']))
# print(query)



