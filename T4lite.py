from selenium import webdriver
import pandas as pd
from selenium.common.exceptions import NoSuchElementException
import datetime
from assets.database import db_session
from assets.models import Data
from time import sleep

header=['vessel','carrier','voyage No.','service','POD', 'ETA','Berthing','Updatetime']
df_original = pd.DataFrame(columns=header)

driver_path = '/app/.chromedriver/bin/chromedriver'
options = webdriver.ChromeOptions()
options.add_argument('--headless')
browser = webdriver.Chrome(options=options,executable_path=driver_path)

portname = {3:"SED",13:"TYO",11:"YOK",30:"SHI",35:"NGO",40:"OSA",41:"OBE",70:"MOJ"}

#port = [13,11,40,41] #東京,横浜,大阪,神戸 OOCL
#week = [3,4]
port = [11] #東京,横浜,大阪,神戸 OOCL
week = [3]
carrier = 'OOC'
target = ['KTX1','KTX2','KTX3']

for k in range(len(port)):
    pod = portname[port[k]]
    for s in range(len(week)):
        url = 'https://www.toyoshingo.com/oocl/index.php?port={0}&week={1}'.format(port[k],week[s])
        browser.get(url)

        
        count = len(browser.find_elements_by_class_name('vesselname'))

        for i in range(count):
            elems_vessel = browser.find_elements_by_class_name('vesselname')
            elems_vessel[i].click()

            try:
                elem_content_body = browser.find_element_by_tag_name('tbody')
            except NoSuchElementException:
                continue
            elems_content=elem_content_body.find_elements_by_tag_name('tr')
            
            vessel = [elem_content.text.replace("船名(Vessel Name)","") for elem_content in elems_content if "船名" in elem_content.text]
            if len(vessel)==0:
                vessel=["NA"]
                
            voyage = [elem_content.text.replace("Voyage[Import/Export]","") for elem_content in elems_content if "Voyage" in elem_content.text]
            if len(voyage)==0:
                voyage=["NA"]

            service = [elem_content.text.replace("航路(Route)","").replace(" ","").replace("　","") for elem_content in elems_content if "航路" in elem_content.text]
            if len(service)==0:
                service=["NA"]

            arrival = [elem_content.text.replace("入港時間(Arrival)","") for elem_content in elems_content if "Arrival" in elem_content.text]
            if len(arrival)==0:
                arrival=["NA"] 

            berthing = [elem_content.text.replace("着岸日(Berthing)","") for elem_content in elems_content if "着岸日" in elem_content.text]
            if len(berthing)==0:
                berthing=["NA"]

            updatedate= datetime.datetime.now().strftime("%Y/%m/%d %H:%M")
            
      
            if service[0] in target:

                row =Data(Vessel=vessel[0],Carrier=carrier,Voyage=voyage[0],Service=service[0],Pod=pod,ETA=arrival[0],Berthing=berthing[0])

                db_session.add(row)
                db_session.commit()
            
            sleep(1)
            browser.back()


#port = [13,11,40,41] #東京,横浜,大阪,神戸 EVG
#week = [3,4,5]
port = [11] #東京,横浜,大阪,神戸 EVG
week = [3]
carrier = 'EVG'
target = ['NSA','NSD','NSC']

for k in range(len(port)):
    pod = portname[port[k]]
    for s in range(len(week)):
        url = 'https://www.toyoshingo.com/evergreen/index.php?port={0}&week={1}'.format(port[k],week[s])
        browser.get(url)

        
        count = len(browser.find_elements_by_class_name('vesselname'))

        for i in range(count):
            elems_vessel = browser.find_elements_by_class_name('vesselname')
            elems_vessel[i].click()
            try:
                elem_content_body = browser.find_element_by_tag_name('tbody')
            except NoSuchElementException:
                continue
            
            elems_content=elem_content_body.find_elements_by_tag_name('tr')
            
            vessel = [elem_content.text.replace("本船 Vessel","") for elem_content in elems_content if "本船" in elem_content.text]
            if len(vessel)==0:
                vessel=["NA"]
                
            voyage = [elem_content.text.replace("Voyage","") for elem_content in elems_content if "Voyage" in elem_content.text]
            if len(voyage)==0:
                voyage=["NA"]

            service = [elem_content.text.replace("サービス Service","").replace(" ","").replace("　","") for elem_content in elems_content if "Service" in elem_content.text]
            if len(service)==0:
                service=["NA"]

            arrival = [elem_content.text.replace("入港時間 Arrival","") for elem_content in elems_content if "Arrival" in elem_content.text]
            if len(arrival)==0:
                arrival=["NA"] 

            berthing = [elem_content.text.replace("着岸時間 Berthing","") for elem_content in elems_content if "Berthing" in elem_content.text]
            if len(berthing)==0:
                berthing=["NA"]

            updatedate= datetime.datetime.now().strftime("%Y/%m/%d %H:%M")
      
            if service[0] in target:
                row =Data(Vessel=vessel[0],Carrier=carrier,Voyage=voyage[0],Service=service[0],Pod=pod,ETA=arrival[0],Berthing=berthing[0])

                db_session.add(row)
                db_session.commit()
            
            sleep(1)
            browser.back()
           

browser.quit()


