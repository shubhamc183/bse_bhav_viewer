![BSE BHAV ZERODHA](https://raw.githubusercontent.com/shubhamc183/bse_bhav_viewer/master/bse_bhav/static/favicon.ico)
# Zerodha BSE Bhav Copy Viewer
# Application Link: https://bse-bhav-zerodha.herokuapp.com/


An app to visual BSE EOD bhav(indian term for Rate) on a front end by querying redis via CherryPy framework.

This app download the latest BSE Bhavcopy from the BSE website extracts it and parses the csv file to save all the stock values along with the columns. It also calculates the percentage by taking the difference of open and close.


# Tech Stack
 - Python 3.5
 - CherryPy Framework
 - Redis as database
 - JQuery, MdBootStrap, Datatables
 
# Platform
 - Heroku: PaaS


# End Points
  - **get_top_stocks**: API end point to get top stocks
  - **get_stocks_by_name**: API end point to get stocks by name
  - **save_latest_bhav_report**: Save the latest bhav report on D/B.

# Worklfow
 - Whenever the server starts from today to today - 10 days it try to get the bhav copy and save it into the d/b.
 - If it founds the data then in doesn't look any further.

# Redis Keys
 - **last_date_indexed**
   - Saves the date when the data was last indexed
   - ex. 15-11-19
 - **ticker_STOCK1**
    - Every stock is prefixed with the "ticker_" and inserted as a field and value with its attribute
    - ex. HMSET ticker_STOCK1 code CODE open OPEN high HIGH low LOW close CLOSE percentage PERCENTAGE
- **bhav_score**
    - The top 10 bhav with the max percentage are added in a Sorted Set
    - ex. ZADD bhav_score 1 ticker_YESBANK
