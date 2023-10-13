import requests
import json
import csv
import datetime
import tkinter as tk
from collections import OrderedDict
import webbrowser


class Tracker:
    """
        Tracker adds event information to the given file, which should be a .csv
    """

    def __init__(self, file, api):
        # hold file and api info
        self.file = file
        self.api = api

        # gui variables
        self.window = tk.Tk()
        self.canvas = tk.Canvas(self.window)
        self.current_search_frame = tk.Frame(self.window)
        self.previous_search_frame = tk.Frame(self.window, borderwidth=2)

        # widgets
        self.btn_search = None
        self.search_results = tk.Text(self.current_search_frame, font="Helvetica 14", height=10)
        self.prev_searches_label = tk.Label(self.previous_search_frame)

        # set up gui
        self.gui_setup()

    def gui_setup(self):
        self.window.geometry("750x500")

        # scroll bar
        scrollbar = tk.Scrollbar(self.window, orient="vertical", command=self.canvas.yview)

        # connect scrollbar to canvas
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # display canvas and scroll bar, pack
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4, 4), window=self.current_search_frame, anchor="nw")
        self.canvas.create_window((4, 350), window=self.previous_search_frame, anchor="nw")

        # when frame is reconfigured, so is scroll bar
        self.current_search_frame.bind("<Configure>", lambda event: self.on_frame_configure())
        self.previous_search_frame.bind("<Configure>", lambda event: self.on_frame_configure())

        # display items on current search frame, grid
        artist_label = tk.Label(self.current_search_frame, text="What artist would you like to search for?")
        artist_entry = tk.Entry(self.current_search_frame)
        artist_label.grid(column=0, row=0, columnspan=5)
        artist_entry.grid(column=0, row=1, columnspan=5)
        city_label = tk.Label(self.current_search_frame, text="What city do you want to search in?")
        city_entry = tk.Entry(self.current_search_frame)
        city_label.grid(column=0, row=2, columnspan=5)
        city_entry.grid(column=0, row=3, columnspan=5)
        self.btn_search = tk.Button(self.current_search_frame, text="search", command=lambda: self.search_event(artist_entry, city_entry))
        self.btn_search.grid(column=0, row=4, columnspan=5)

        # configure tags for displaying text
        self.search_results.tag_configure("bold", font="Helvetica 14 bold")
        self.search_results.tag_configure("link", foreground="blue", font="Helvetica 14 underline")

        self.window.mainloop()

    def on_frame_configure(self):
        """
        Resets the scroll region to encompass the inner frame
        """
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def get_event_info(self, response_dict):
        """
        Get relevant info from event,
        Error handling to ensure that there are values for min and max price
        :param response_dict: dictionary of the api call from ticketmaster
        :return: list of elements, which will become the next row in the .csv file
        """

        # information to get from api call
        min_price = ''
        max_price = ''

        # error handling for if there is no min or max price
        try:
            if response_dict['priceRanges'][0]['min'] is not None:
                min_price = response_dict['priceRanges'][0]['min']
        except KeyError:
            min_price = 'No Min Price Available'

        try:
            if response_dict['priceRanges'][0]['max'] is not None:
                max_price = response_dict['priceRanges'][0]['max']
        except KeyError:
            max_price = 'No Max Price Available'

        # get venue and city name
        venue_name = response_dict["_embedded"]['venues'][0]['name']
        city = response_dict["_embedded"]['venues'][0]['city']['name']

        # row_dict contains all of the info we want to return to the user
        row_dict = OrderedDict([("ID", response_dict['id']),
                                ("Event", response_dict['name']),
                                ("Min Price", min_price),
                                ("Max Price", max_price),
                                ("Venue", venue_name),
                                ("City", city),
                                ("URL", response_dict['url']),
                                ("Search Timestamp", datetime.datetime.now())])

        return row_dict

    def add_event(self, response_dict):
        """
        Update the .csv file with the event
        :param response_dict: dictionary of the api call from ticketmaster
        :return:
        """

        row_list = []
        row_dict = self.get_event_info(response_dict)

        # search through the dictionary and place info in the determined order
        for key, value in row_dict.items():
            if key in ["ID", "Event", "Min Price", "Max Price", "Search Timestamp"]:
                row_list.append(value)

        # update the csv file with the event info
        with open(self.file, 'a') as f_object:
            writer_object = csv.writer(f_object, delimiter=",")
            writer_object.writerow(row_list)
            f_object.close()

        # print event to gui
        self.print_event(row_dict)

    def get_event_from_id(self, event_id, row_count):
        """
        Prints out all the events in the tracker that matches the given id
        :param event_id: event id
        :param row_count: keeps track of the number of rows for proper placement on the grid
        :return:
        """

        # clear out all info in previous_search_frame except for the column headers
        for widget in self.previous_search_frame.winfo_children()[6:]:
            widget.destroy()

        # read csv file to get all previous searches with the same event id
        with open(self.file, 'r') as f_object:
            csv_reader = csv.reader(f_object, delimiter=',')

            for row in csv_reader:
                # if there's a match, meaning that the event was previously searched
                if row[0] == event_id:
                    row_count += 1
                    # new rows should start grid at column 0
                    column_count = 0

                    # add info to the row, one column at a time
                    for r in row:
                        new_text = tk.Label(self.previous_search_frame, text=r)
                        new_text.grid(column=column_count, row=row_count, sticky="nesw")
                        column_count += 1

    @staticmethod
    def callback(url):
        """
        Opens url in web browser
        :param url: URL to open
        """
        webbrowser.open_new(url)

    def print_event(self, row):
        """
        Prints event information to the gui
        :param row: dictionary containing event info
        :return:
        """

        # clear out previos search results
        self.search_results.delete("1.0", "end")

        # start printing on row 5 in the grid
        row_count = 5

        for key, value in row.items():
            # add key labels in bold
            self.search_results.insert("end", key + ": ", "bold")

            # if the key is URL, make value clickable; otherwise display value
            if key == "URL":
                self.search_results.insert("insert", str(value) + "\n", "link")
                self.search_results.grid(column=0, row=row_count, columnspan=5)
                url = value
                self.search_results.bind("<Button-1>", lambda e: Tracker.callback(url))
            else:
                self.search_results.insert("insert", str(value) + "\n")
                self.search_results.grid(column=0, row=row_count, columnspan=5)
            row_count += 1

        # disable search results so users can't type in the text widget
        self.search_results.config(state="disabled")

        # display the header for the previous searches column
        self.prev_searches_label.config(text="Your Previous Searches of " + row["Event"] + " in " + row["City"])
        self.prev_searches_label.grid(column=0, row=row_count, columnspan=5)
        prev_searches_header = ["EVENT ID", "EVENT NAME", "MIN PRICE", "MAX PRICE", "SEARCH TIMESTAMP"]

        for i in range(len(prev_searches_header)):
            label = tk.Label(self.previous_search_frame, text=prev_searches_header[i], font="Helvetica 14 bold")
            label.grid(column=i, row=row_count+1, sticky="nesw")

        # get all events from csv that have the same id
        self.get_event_from_id(row["ID"], row_count + 2)

    def search_event(self, artist_entry, city_entry):
        """
        Uses ticketmaster API to search for an event with the given keyword and city
        :param artist_entry: name of the artist (this is the keyword to search on)
        :param city_entry: name of the city that user wants to search in
        """

        # change the search_results widget to normal so new text can be displayed
        self.search_results.config(state="normal")

        # re-format artist and entry for request
        artist = artist_entry.get().replace(" ", "%20")
        city = city_entry.get().replace(" ", "%20")

        # get response from api
        response = requests.get(
                                f"https://app.ticketmaster.com/discovery/v2/events?apikey={self.api}&keyword={artist}&locale=*&city={city}")
        response_dict = json.loads(response.text)

        # check if event is valid
        try:
            self.add_event(response_dict["_embedded"]['events'][0])
        except KeyError:
            # if invalid, end
            self.search_results.delete("1.0", "end")
            self.search_results.insert("insert", "Could not find event " + artist_entry.get() + " in " + city_entry.get())
            self.search_results.grid(columnspan=5)
            self.search_results.config(state="disabled")
