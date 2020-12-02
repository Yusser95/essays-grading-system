import requests
from bs4 import BeautifulSoup
import re
import json
from os import abort, listdir
import time
from random import randint
import argparse

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dir", type=str, default=".",
    help = """path to where to save results ex:"./results.csv" """)
ap.add_argument("-n", "--essaysNum", type=int, default=1000,
    help=""" number of result to show """)


args = vars(ap.parse_args())
output_dir = args["dir"]
num_of_essays = args["essaysNum"]


def log_in():
    login_data = {
        'username': 'xxxx@xxxxx.com',
        'password': '*******',
    }

    s = requests.Session()
    r = s.post('https://www.markedbyteachers.com/customer/account/', data=login_data)
    if r.status_code == 200:
        return s
    else:
        raise Exception
        
def get_essay_description(s,essay_id):
    r = s.get("http://www.markedbyteachers.com/catalogsearch/ajax/description/?isAjax=1&sku={}".format(str(essay_id)))
    if r.status_code == 200:
        data = json.loads(r.content)
        if data['success']:
            return data['description']

    raise Exception


def main(s ,num_of_essays ,output_dir):
    
    start_time = time.time()
    
    print("**** STARTED ****")
    
    if not output_dir.endswith("/"):
        output_dir+="/"
        
        
    url1 = 'http://www.markedbyteachers.com/catalogsearch/result/index/?dir=desc&order=marked_by_teacher&p=1'
    res1 = s.get(url1)

    soup1 = BeautifulSoup(res1.text,"lxml")

    pages_div = soup1.find('div',{'class':'pages'})

    pages_num = re.findall('\d+',pages_div.find('label').getText())
    pages_num = int(pages_num[0])
    cnt = 0



    base_url = 'http://www.markedbyteachers.com/catalogsearch/result/index/?dir=desc&order=marked_by_teacher&p={}'
    for p in range(1,pages_num+1):
        try:
            res = s.get(base_url.format(str(p)))
            soup = BeautifulSoup(res.text,"lxml")

            essays_div = soup.find('div',{'class':'category-products'})
            essays = essays_div.findAll('li',{'class':'product'})

            for essay in essays:
                try:
                    if cnt>0 and cnt % 25 == 0:
                        print("update  , scrapped_essays_num : {} , from : {}".format(str(cnt) ,str(num_of_essays)))

                    if cnt >= num_of_essays:
                        print("finished !!!")
                        end_time = time.time() - start_time
                        print("finished in ( {} ) seconds .".format(str(int(end_time))))
                        abort()
                    
                    essay_id = str(essay['id'])
                    
                    files = listdir(output_dir) 
                    if essay_id+".json" not in files:

                        essay_title = essay.find("h2",{'class':'product-name'}).getText(strip=True)
                        rate = essay.find('div',{'class':'review-stars'}).getText(strip=True)

                        info_lis = essay.find('ul',{'class':'product-info'}).findAll('li')

                        level = info_lis[0].getText(strip=True).replace('Level:\r\n                        ','')
                        subject = info_lis[1].getText(strip=True).replace('Subject:\r\n                        ','')
                        word_count = int(info_lis[2].getText(strip=True).replace('Word count:\r\n                        ',''))
                        submitted = info_lis[3].getText(strip=True).replace('Submitted:\r\n                        ','')
                        marked_by_teacher = {'teacher_name':info_lis[4].findAll('a')[1].getText(strip=True),'date':info_lis[4].findAll('a')[1].nextSibling.strip()}

                        essay_url = essay.find('ul',{'class':'product-actions'}).find('li').find('a')['href']

                        description = get_essay_description(s,essay_id)

                        record = {
                            'essay_id':essay_id,
                            'essay_title':essay_title,
                            'rate':rate,
                            'level':level,
                            'subject':subject,
                            'word_count':word_count,
                            'submitted':submitted,
                            'marked_by_teacher':marked_by_teacher,
                            'essay_url':essay_url,
                            'description':description
                        }

                        with open('{}{}.json'.format(output_dir,essay_id) ,'w') as f:
                            json.dump(record ,f)

                        cnt += 1

                        ttime = randint(180,420)
                        print("will sleep for ( {} ) seconds !".format(str(ttime)))
                        time.sleep(ttime)
                        

                except Exception as e:
                    s = log_in()
#                     print('record error {} '.format(  e))
                    pass
#             print('finished page : {}  ,  records : {}'.format(str(p) ,str(cnt)))

        except Exception as e:
            s = log_in()
            print("page error",e)
            
    print("finished !!!")
    end_time = time.time() - start_time
    print("finished in ( {} ) seconds .".format(str(int(end_time))))

        
        
s = log_in()
main(s ,num_of_essays ,output_dir)
    

