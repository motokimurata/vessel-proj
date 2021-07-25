from selenium import webdriver
import pandas as pd
from selenium.common.exceptions import NoSuchElementException
import datetime

header=['vessel','carrier','voyage No.','service','POD', 'ETA','Berthing','Updatetime']
df_original = pd.DataFrame(columns=header)

driver_path = '/app/.chromedriver/bin/chromedriver'
options = webdriver.ChromeOptions()
options.add_argument('--headless')
browser = webdriver.Chrome(options=options,executable_path=driver_path)

portname = {3:"SED",13:"TYO",11:"YOK",30:"SHI",35:"NGO",40:"OSA",41:"OBE",70:"MOJ"}

#port = [13,11,35,40,41] #東京,横浜,名古屋,大阪,神戸 ONE
#week = [1,2,3,4,5]
port = [13] #東京,横浜,名古屋,大阪,神戸 ONE
week = [1]
carrier = 'ONE'

for k in range(len(port)):
    pod = portname[port[k]]
    for s in range(len(week)):
        url = 'https://www.toyoshingo.com/one/index.php?port={0}&week={1}'.format(port[k],week[s])
        browser.get(url)
        count = len(browser.find_elements_by_class_name('vesselname'))
        for i in range (count):
            elems_vessel = browser.find_elements_by_class_name('vesselname')
            elems_vessel[i].click()
            try:
                elem_content_body = browser.find_element_by_tag_name('tbody')
            except NoSuchElementException:
                continue
            elems_content=elem_content_body.find_elements_by_tag_name('tr')
            
            vessel = [elem_content.text.replace("本船\n","").replace("Vessel","") for elem_content in elems_content if "本船" in elem_content.text]
            if len(vessel)==0:
                vessel=["NA"]
                
            voyage = [elem_content.text.replace("Voyage","") for elem_content in elems_content if "Voyage" in elem_content.text]
            if len(voyage)==0:
                voyage=["NA"]

            service = [elem_content.text.replace("サービス\n","").replace("Service","") for elem_content in elems_content if "Service" in elem_content.text]
            if len(service)==0:
                service=["NA"]

            arrival = [elem_content.text.replace("入港時間\n","").replace("Arrival","") for elem_content in elems_content if "Arrival" in elem_content.text]
            if len(arrival)==0:
                arrival=["NA"] 

            berthing = [elem_content.text.replace("着岸時間\n","").replace("Berthing","") for elem_content in elems_content if "Berthing" in elem_content.text]
            if len(berthing)==0:
                berthing=["NA"]

            updatedate= datetime.datetime.now().strftime("%Y/%m/%d %H:%M")
            
            df_newrow =pd.DataFrame(data= [[vessel[0],carrier,voyage[0],service[0],pod,arrival[0],berthing[0],updatedate]],columns=header)

            df_original = pd.concat([df_original,df_newrow],axis=0)
            browser.back()

df_original.to_csv("vessel_schedule.csv",index= False)
browser.quit()