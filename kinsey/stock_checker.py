import requests
from bs4 import BeautifulSoup
import pandas as pd
import sys
from .jsonwriter import JW
import csv
import json
import os
import threading
import time


class Scraper(object):

    def __init__(self, sourcefile=""):
        self.session = requests.Session()
        self.input_folder = "media/from_chino"
        self.output_folder = "media/to_chino"
        self.filename = sourcefile
        thread = threading.Thread(target=self.main, args=())
        thread.daemon = True
        thread.start()

    def get_result(self, row, c, record_len):
        part_no = str(row['Kinsey #']).strip()
        title = row['Title'].strip()
        try:
            base_url = "https://webstore.kinseysinc.com/search?q="
            res3 = self.session.get(base_url + part_no)
            s3 = BeautifulSoup(res3.text, 'html.parser')

            try:
                # results = s3.find('ul', {'id': 'list-of-products'}).select('li')  # OLD VERSION
                results = s3.find('div', {'id': 'list-of-products'}).findAll('div', recursive=False)
            except Exception as e:
                print("Error....", e)
                results = []

            match_found = False
            jdata = {}
            for result in results:
                p_name = result.select('a.product-title')[0].text.strip()
                p_no = result.select('span.product-id')[0].text.strip()  # OLD VERSION
                p_no = result.select('span.product-id-value')[0].text.strip()
                try:
                    stock = result.select('span.stock-indication')[0].text.strip()
                except:
                    try:
                        stock = result.select('span.msg-not-available')[0].text.strip()
                    except:
                        stock = "undefined"
                print(p_name)
                print(p_no)
                print(stock)
                if p_no == part_no:
                    # add to json file
                    jdata = {"Kinsey #": part_no, "Title": title, 'active?': 'active', 'stock': stock}
                    jwriter = JW()
                    jwriter.append_json(jdata, self.output_folder, "{}.json".format(self.filename))
                    match_found = True
                    with open('{}/{}.csv'.format(self.output_folder, self.filename), 'a', newline='', encoding='utf-8')\
                            as csvw:
                        csv.writer(csvw).writerow([part_no, p_no, title, p_name, 'active', stock])

                    break
            if not match_found:
                jdata = {"Kinsey #": part_no, "Title": title, 'active?': '', 'stock': ''}
                jwriter = JW()
                jwriter.append_json(jdata, self.output_folder, "{}.json".format(self.filename))
                with open('{}/{}.csv'.format(self.output_folder, self.filename), 'a', newline='', encoding='utf-8')\
                        as csvw:
                    csv.writer(csvw).writerow([part_no, '', title, '', '', ''])

            # RECORDING PROGRESS FOR FRONT-END USE
            jprog = {"completed": c, "total": record_len, "current_record": part_no + " - " + title}
            jwriter = open(os.path.join(self.output_folder, "progress-{}.json".format(self.filename)), 'w',
                           encoding='utf-8')
            json.dump(jprog, jwriter)
            jwriter.close()

            print(c, "  of ", record_len, match_found, "  ", part_no, jdata['stock'])

        except Exception as e:
            print(e)

    def main(self):
        # Delete log file
        try:
            os.remove("media/mylogs.txt")
            print("Log file deleted")
        except Exception as e:
            print('Nothing to remove')

        # JSON FILE IS USE TO CHECK THE STATE OF SCRAPER
        js = open('media/status.json', 'w')
        json.dump([{'running': True, 'excel_saved': False}], js, indent=3)
        js.close()

        print('Info: Converting source excel file to dataframe')
        parts = pd.read_excel("{}/{}.xlsx".format(self.input_folder, self.filename))
        print('Column names: ', parts.columns.to_list())

        record_rows = parts.to_dict('records')
        record_len = len(record_rows)

        try:
            jfile = open(self.output_folder + "/" + self.filename + ".json")
            completed = json.load(jfile)
            completed = [str(x['Kinsey #']).strip() + str(x['Title']).strip() for x in completed]
            print(len(completed))
            jfile.close()

        except Exception as e:
            print(e)
            print('error loading source file')
            completed = []

        print("Trying to login")

        res1 = self.session.get('https://webstore.kinseysinc.com/profile/login')
        s1 = BeautifulSoup(res1.text, 'html.parser')
        token = s1.find('input', {'name': '__RequestVerificationToken'})['value']
        username = 'F114137'
        password = 'l#cCEY&D14Ai'
        rememberme = 'False'

        payload = {'__RequestVerificationToken': token, 'Username': username, 'Password': password,
                   'RememberMe': rememberme}
        login_url = 'https://webstore.kinseysinc.com/profile/login'
        post = self.session.post(login_url, data=payload)
        print(payload)

        # strt = int(sys.argv[2])

        res2 = self.session.get('https://webstore.kinseysinc.com/')
        s2 = BeautifulSoup(res2.text, 'html.parser')

        if s2.select('a#logoutLink')[0].text == 'Logout':

            print('Logged in !')

            print('completed = {}'.format(len(completed)))
            c = len(completed)
            c = c
            for row in record_rows:
                if str(row['Kinsey #']).strip() + str(row['Title']).strip() not in completed:
                    print(row['Kinsey #'])
                    c += 1
                    self.get_result(row, c, record_len)

                    # time.sleep()
                js = open('media/status.json', encoding='utf-8')
                status = json.load(js)[0]['running']
                js.close()
                if not status:
                    break

            print("Preparing files for chino.")
            for_df = pd.read_json("{}/{}.json".format(self.output_folder, self.filename))
            for_df.to_excel("{}/{}.xlsx".format(self.output_folder, self.filename), encoding='utf-8', index=False)
            js = open('media/status.json', 'w', encoding='utf-8')
            json.dump([{'running': False, 'excel_saved': True}], js, indent=3)
            js.close()
            print('Excel saved.')

            dl_link = f"http://stock-chk.herokuapp.com/{self.output_folder}/{self.filename}.xlsx"
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            data = 'payload={"username": "Kinseys Stock Check", "color":"#D00000", "pretext": "Download Complete", "text": "' + dl_link + '"}'
            slack = requests.post('https://hooks.slack.com/services/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', headers=headers, data=data)
            print(slack)
            
            time.sleep(2)
        else:
            sys.exit(0)
