import requests
from bs4 import BeautifulSoup
import re
import json
from os import abort, listdir
import time
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


def get_autherize_headers():
    data = {"email":"moktar@progressay.com","password":"Teacher1!"}
    headers = {
        "Authorization": "Basic bW9rdGFyQHByb2dyZXNzYXkuY29tOlRlYWNoZXIxIQ==",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15"
    }
    url = "https://api.bartleby.com/auth/authorize"
    r = requests.post(url=url,data=data,headers=headers)
    
    response = json.loads(r.content)
    access_token = response['data']['access_token']
    token_type = response['data']['token_type']

    headers = {
            "Authorization": "{} {}".format(token_type,access_token),
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15"
        }
    return headers


def get_full_doc(doc_id):
    
    headers = get_autherize_headers()
    
    r= requests.get(url="https://api.bartleby.com/documents/{}/full".format(doc_id),headers=headers)
    
    response = json.loads(r.content)
    return response

def scrape_page_info(url ,essay_category):

    res = requests.get(url)

    soup = BeautifulSoup(res.text,"lxml")
    
    info = soup.find('div',{'id':'h1-and-details'})
    
    essay_title = info.find('h1').getText(strip=True)
    
    other_info = info.find('div').findAll('span')
    
    word_count = int(other_info[0].getText(strip=True).replace(" Words",""))
    submitted = other_info[1].getText(strip=True)
    page_count = other_info[2].getText(strip=True)
    
    doc_id = url.split("/")[-1].split("-")[-1]
    document = get_full_doc(doc_id)
    
    record = {
        "essay_id": doc_id,
        "essay_category": essay_category,
        "essay_title": essay_title,
        "word_count": word_count,
        "submitted": submitted,
        "page_count": page_count,
        "essay_url": url,
        "document":document
    }
    
    return record


def main(num_of_essays , output_dir):
    
    start_time = time.time()
    
    if not output_dir.endswith("/"):
        output_dir+="/"
    
    
    print("**** STARTED ****")
    base = 'https://www.bartleby.com'
    cnt = 0

    url1 = 'https://www.bartleby.com/writing/'
    res1 = requests.get(url1)

    soup1 = BeautifulSoup(res1.text,"lxml")

    page_sections1 = soup1.findAll('section')
    categories = page_sections1[4].findAll('li')
    for c in categories:
        try:
            category_name = c.find('a').getText(strip=True)
            category_url = c.find('a')['href']

            print(category_name,category_url)

            url2 = category_url
            res2 = requests.get(url2)

            soup2 = BeautifulSoup(res2.text,"lxml")

            page_sections2 = soup2.findAll('section')




            temp=0



            # section 0
            essays = page_sections2[0].findAll('a',{'class':'card__title'})

            temp += len(essays)

            for essay in essays:
                try:

                    if cnt>0 and cnt % 25 == 0:
                        print("UPDATE : current_category : {}  , scrapped_essays_num : {} , from : {}".format(category_name ,str(cnt) ,str(num_of_essays)))

                    if cnt >= num_of_essays:
                        print("finished !!!")
                        end_time = time.time() - start_time
                        print("finished in ( {} ) seconds .".format(str(int(end_time))))
                        abort()

                    essay_name = essay.getText(strip=True)
                    essay_url = base + essay['href']
                    essay_id = essay_url.split('/')[-1]



    #                 print(essay_id,essay_name,essay_url)
                    files = listdir(output_dir) 
                    if essay_id+".json" not in files:
                        record = scrape_page_info(essay_url,category_name)
    #                     print(record)

                        with open('{}{}.json'.format(output_dir,essay_id) ,'w') as f:
                            json.dump(record ,f)

                        cnt += 1

                except Exception as e:
                    pass
#                     print('record error {} '.format(  e))


            # section 1
            essays = page_sections2[1].findAll('li')

            temp += len(essays)

            for essay in essays:
                try:

                    if cnt>0 and cnt % 25 == 0:
                        print("UPDATE : current_category : {}  , scrapped_essays_num : {} , from : {}".format(category_name ,str(cnt) ,str(num_of_essays)))


                    if cnt >= num_of_essays:
                        print("finished !!!")
                        end_time = time.time() - start_time
                        print("finished in ( {} ) seconds .".format(str(int(end_time))))
                        abort()

                    essay_name = essay.find('a').getText(strip=True)
                    essay_url = base + essay.find('a')['href']
                    essay_id = essay_url.split('/')[-1]

    #                 print(essay_id,essay_name,essay_url)

                    files = listdir(output_dir) 
                    if essay_id+".json" not in files:
                        record = scrape_page_info(essay_url,category_name)
    #                     print(record)

                        with open('{}{}.json'.format(output_dir,essay_id) ,'w') as f:
                            json.dump(record ,f)

                        cnt += 1


                except Exception as e:
                    pass
    #                 print('record error {} '.format(  e))

            print("finished , category : {}  , essays_num : {} , from : {}".format(category_name ,str(cnt) ,str(temp)))
        
            end_time = time.time() - start_time
            print("finished in ( {} ) seconds .".format(str(int(end_time))))

        except Exception as e:
            pass
            print("page error",e)
    

main(num_of_essays , output_dir)