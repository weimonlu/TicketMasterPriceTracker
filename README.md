# TicketMasterPriceTracker

Uses Ticketmaster's Discovery API to get track event prices. Users will need an API key and the name of a file to write information to.

## Use the tracker
Download the TMPriceTracker.py file. In your terminal, run the following commands, replacing `NAME_OF_FILE` with the file that you want to write to and `API_KEY` with your Ticketmaster API Key.

```
python3
from TMPriceTracker import Tracker
Tracker(NAME_OF_FILE, API_KEY)
```

With every successful search, the event's information will be written to the file and previous searches of that event will show on screen. You can see if there have been any price changes over time.
