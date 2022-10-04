import logging
import sched
import time
import sys
import pywhatkit
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import webbrowser
import json

logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
LOGGER = logging.getLogger('bookmyshow_notify')
BASE_URL = r'https://in.bookmyshow.com'
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0'
HEADERS = {'User-Agent': USER_AGENT}

SECONDS = 120

CELEBRATE = "https://www.youtube.com/watch?v=DYWe6v2TW14"
BMS_URL = "https://in.bookmyshow.com/buytickets/ponniyin-selvan-part-1-chennai/movie-chen-ET00323897-MT/20220930"
TN_URL = "https://www.ticketnew.com/Ponniyin-Selvan---Part-One-Movie-Tickets-Online-Show-Timings/Online-Advance-Booking/21899/C/Chennai"
JAZZ_URL = ""
PVR_URL = ""

show_details_key = 'ShowDetails'

theatres = {
    'PVR: VR Chennai':False,
    'PVR: Grand Mall':False,
    'PVR: Ampa Mall':False,
    'PVR: Grand Galada':False,
    'SPI Palazzo':False,
    'Luxe Cinemas':False,
    'SPI: S2 Perambur':False,
    'SPI: Sathyam Cinemas':False,
    'SPI: Escape':False,
    'SPI: S2 Theyagaraja':False,
    'IMAX':False,
}

def get_headers():
    return {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/101.0.4951.64 Safari/537.36',
    }

def souped():
    try:
        response = requests.request('GET', BMS_URL, headers=get_headers(), data={})
        page_content = BeautifulSoup(response.content, features='lxml')
        return page_content
    except Exception as e:
        pywhatkit.sendwhatmsg("+91<mobile-no>", str(e), datetime.now().hour, datetime.now().minute+2)

def message(s):
    pywhatkit.sendwhatmsg("+91<mobile-no>", s, datetime.now().hour, datetime.now().minute+2)

def check_bms():
    soup = str(souped())
    for key in theatres:
        if theatres[key]==False:
            sf = soup.find(str(key))
            if sf!=-1:
                theatres[key] = True
                LOGGER.info('*** {} ***'.format(str(key)))
                webbrowser.open(BMS_URL)
                webbrowser.open(CELEBRATE)
                # message("{} open".format(str(key)))

def keep_checking(schdlr, url, seconds):
    LOGGER.info('Checking if open...')
    value = [i for i in theatres if theatres[i]==False]
    if len(value)>0:
        check_bms()
        LOGGER.info('Pending: {}'.format(value))
        schdlr.enter(seconds, 1, keep_checking, (schdlr, url, seconds))
    else:
        LOGGER.info('*** ALL DONE ***')
        sys.exit()

def main():
    seconds = SECONDS
    url = BMS_URL
    LOGGER.debug('BookMyShow buytickets page URL: %s', BMS_URL)
    schdlr = sched.scheduler(time.time, time.sleep)
    schdlr.enter(seconds, 1, keep_checking, (schdlr, url, seconds))
    try:
        schdlr.run()
    except KeyboardInterrupt:
        LOGGER.info("Exiting.")

if __name__ == '__main__':
    main()
