import requests
import json
import csv
import datetime


class Tracker:
    """
        Tracker adds event information to the given file, which should be a .csv
    """
    #api = "KbtTMD50liCy9mA6Aeh0eG3EIoGD75xu"

    def __init__(self, file, api):
        self.file = file
        self.api = api

    def check_entries(self, response_dict):
        """
        error handling to ensure that there are values for min and max price
        :param response_dict: dictionary of the api call from ticketmaster
        :return: list of elements, which will become the next row in the .csv file
        """

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
        """
        Update the .csv file with the event
        :param event_id: event id, used in the get request
        :return:
        """
        response = requests.get(f"https://app.ticketmaster.com/discovery/v2/events/{event_id}?apikey={self.api}")
        response_dict = json.loads(response.text)
        row_list = self.check_entries(response_dict)

        with open(self.file, 'a') as f_object:
            writer_object = csv.writer(f_object, delimiter=",")
            writer_object.writerow(row_list)
            f_object.close()

    def get_event(self, event_id):
        """
        Prints out all the events in the tracker that matches the given id
        :param event_id: event id
        :return:
        """
        with open(self.file, 'r') as f_object:
            csv_reader = csv.reader(f_object, delimiter=',')
            for row in csv_reader:
                if row[0] == event_id:
                    print(row)


tracker = Tracker("TicketMasterTracker.csv", "KbtTMD50liCy9mA6Aeh0eG3EIoGD75xu")
tracker.add_event("Z7r9jZ1AdO673")
tracker.get_event("Z7r9jZ1AdO673")

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



