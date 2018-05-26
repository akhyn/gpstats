GP Stats is a light and clean data visualization site for motorcycle racing data with automated parsing of new results
and generation of snazzy charts.
![Chart 1](/docs/screen1.png)
![Chart 2](/docs/screen2.png)
### Setup
GP Stats requires a Jango 2.0 capable host

After installation, run _python manage.py updatescrapeddata_ to begin scraping the motogp.com website to fill the database.  
To force update the charts after customization, run _python manage.py updatecharts_  
To force a new scrape of the data, run _python manage.py updatescrapeddata -season XXXX_  
In order to keep the database up to date, set up new update at regular intervals.  
