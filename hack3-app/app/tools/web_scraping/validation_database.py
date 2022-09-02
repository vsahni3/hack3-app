from re import I
import requests
import bs4
from time import time, sleep
from concurrent.futures import as_completed
from requests_futures import sessions
import json
import sqlite3
import mysql.connector
import getpass

letter_map = {224: 97, 225: 97, 226: 97, 227: 97, 228: 97, 229: 97, 231: 99, 232: 101, 233: 101, 234: 101, 235: 101, 236: 105, 237: 105, 238: 105, 239: 105, 240: 111, 241: 110, 242: 111, 243: 111, 244: 111, 245: 111, 246: 111, 248: 111, 249: 117, 250: 117, 251: 117, 252: 117, 253: 121, 255: 121}

def scrape_imdb(type, start, stop):

    url = 'https://www.imdb.com/search/title/?title_type=tv_series'
    index = 55
    indicator = '<h3 class="lister-item-header">'

    num = start
    add_on = 10 * ' '
    if type == 'movie':
        indicator = '<span class="lister-item-header">'
        url = 'https://www.imdb.com/search/title/?title_type=feature,tv_movie,documentary,short&view=simple&ref_=adv_prv'
        index = 92

    def generate_add_on(num):
        if num == 1:
            return ''
        return '&start=' + str(num)
        
    while add_on != f'&start={stop}':
        
        add_on = generate_add_on(num)
        url = url[:index] + add_on
        

        headers = requests.utils.default_headers()

        headers.update(
            {
                'User-Agent': 'My User Agent 1.0',
            }
        )
        try:
            result = requests.get(url, headers=headers)
        except:
            num += 50
            continue

        soup = bs4.BeautifulSoup(result.text, 'lxml')

        terms = str(soup.select('body')[0])
        
        # code
        
        for i in range(len(terms)):
            length = len(indicator)
            if len(terms) - i > length and terms[i:i+length] == indicator:
    
                index = i
                while index < len(terms) and terms[index:index+3] != '</a':
                    index += 1
                name = ''
                index -= 1
                while terms[index] != '>':
                    name += terms[index]
                    index -= 1
                name = name[::-1].replace(u'\xa0', u' ').replace(u'&amp;', u'and').lower()
                name = name.translate(letter_map)
               
                
                
                with open(f'app/tools/web_scraping/{type}.txt', 'a') as f:
                
                    f.write(f'{name}, ')
                    f.close()
        
        
        num += 50
        
def scrape_anime(letters, start=0, stop=2500):
    
    for letter in letters:
        num = start
        while num < stop:
            url = f'https://myanimelist.net/anime.php?letter={letter}&show={num}'
            headers = requests.utils.default_headers()

            headers.update(
                {
                    'User-Agent': 'My User Agent 1.0',
                }
            )
            try:
                result = requests.get(url, headers=headers)
            except:
                continue

            soup = bs4.BeautifulSoup(result.text, 'lxml')

            terms = soup.select('strong')
            if terms == []:
                break
            for term in terms:
                term = str(term)
                
                name = term[8:-9]
                if '(' in name:
                    name = name[:name.index('(') - 1]
                name = name.replace(u'\xa0', u' ').replace(u'&amp;', u'and').lower()
               
                with open(f'app/tools/web_scraping/final_animes.txt', 'a') as f:
                    try:
                        f.write(f'{name}|!? ')
                    except:
                        pass
                    f.close()

            
            
            num += 50

# movies_db = set(open('app/tools/web_scraping/movie.txt').read().split(', '))


# tvshows_db = set(open('app/tools/web_scraping/tvshow.txt').read().split(', '))

# anime_db = set(open('app/tools/web_scraping/animes.txt').read().split('|!? '))
# print(anime_db)

list1 = []
list2 = []

def scrape_english_anime(start, stop):

    urls = [f'https://myanimelist.net/anime/{i}' for i in range(start, stop+1)]
    headers = requests.utils.default_headers()

    headers.update(
        {
            'User-Agent': 'My User Agent 1.0',
        }
    )
    first = True
    first_name = ''
    with sessions.FuturesSession() as session:
        
        futures = [session.get(url, headers=headers) for url in urls]
        
        for future in as_completed(futures):
            try:

                resp = future.result()
            except:
                
                continue
           
            soup = bs4.BeautifulSoup(resp.text, 'lxml')
            terms = str(soup.select('head')[0])
            if "{action: 'submit'}" in terms:
                print('TRY AGAIN')
                print(first_name)
                break
            
            for i in range(len(terms)):
                
                if terms[i:i+22] == '<meta content="Looking':
                    
                    name = ''
                    index = i
                    
                    while terms[index] != '(':
                        index += 1
                    index += 1
                    
                    while terms[index] != ')':
                        name += terms[index]
                        index += 1
                    
                    if terms[index+3:index+11] == 'Find out':
                  
                        name = name.replace(u'\xa0', u' ').replace(u'&amp;', u'and').replace('&#039;', "'").lower()
                        name = name.translate(letter_map)
                        list1.append(name)
                        if first:
                            first_name = name
                            first = False

                    # with open(f'app/tools/web_scraping/anime.txt', 'a') as f:
                    #     try:
                    #         f.write(f'{name}, ')
                    #     except:
                    #         pass
                    #     f.close()

# 3000 - 7000ish might be missing stuff

# anime_db = set(open('app/tools/web_scraping/anime.txt').read().split(', '))
# for anime in anime_db:
#     if ':' in anime:
#         colon_index = anime.index(':')
#         anime_db.add(anime[:colon_index])
def scrape_english_animes(start, stop, seen=[]):
    seen_new = []
    urls = [f'https://myanimelist.net/anime/{i}' for i in range(start, stop+1) if i not in seen]
    headers = requests.utils.default_headers()

    headers.update(
        {
            'User-Agent': 'My User Agent 1.0',
        }
    )
    
    
    with sessions.FuturesSession() as session:
        
        futures = [session.get(url, headers=headers) for url in urls]
        
        for future in as_completed(futures):
            
            try:
                resp = future.result()
            except:
                continue
            

           
            soup = bs4.BeautifulSoup(resp.text, 'lxml')
            terms = str(soup.select('head')[0])
            if "{action: 'submit'}" in terms:
                print('TRY AGAIN')
                print(seen_new)
                break

            seen_new.append(int(resp.url[-5:]))

            for i in range(len(terms)):
                
                if terms[i:i+32] == '? Find out more with MyAnimeList' and terms[i-1] == ')':
                    
                    name = ''
                    index = i - 2
                  
                    while terms[index] != '(':
                        name += terms[index]
                        index -= 1
                    
                    
                    name = name[::-1].replace(u'\xa0', u' ').replace(u'&amp;', u'and').replace('&#039;', "'").replace('&quot;', '"').lower()
                    name = name.translate(letter_map)
                    

                    list2.append(name)
                    

                    with open(f'app/tools/web_scraping/animes.txt', 'a') as f:
                        try:
                            f.write(f'{name}|!? ')
                        except:
                            pass
                        f.close()
                    break
                   

# scrape_english_animes(37000, 37999)
# first 25000 done for other one
# 0 - 50k done
# scrape_english_animes(38000, 39999)

def scrape_english_animesv2(start, stop, seen=[]):

    urls = [f'https://myanimelist.net/anime/{i}' for i in range(start, stop+1) if i not in seen]
    for i in range(len(urls)):
        
        url = urls[i]
        print(url)
        headers = requests.utils.default_headers()

        headers.update(
            {
                'User-Agent': 'My User Agent 1.0',
            }
        )
        try:
            result = requests.get(url, headers=headers)
        except:
            continue

        soup = bs4.BeautifulSoup(result.text, 'lxml')

        
        terms = str(soup.select('head')[0])
        if "{action: 'submit'}" in terms:
            print('TRY AGAIN')
            break

        
        
        for i in range(len(terms)):
            
            if terms[i:i+32] == '? Find out more with MyAnimeList' and terms[i-1] == ')':
                
                name = ''
                index = i - 2
                
                while terms[index] != '(':
                    name += terms[index]
                    index -= 1
                
                
                name = name[::-1].replace("'", '"').replace(u'\xa0', u' ').replace(u'&amp;', u'and').replace('&#039;', "'").replace('&quot;', '"').lower()
                name = name.translate(letter_map)
             

                list2.append(name)
                

                with open(f'app/tools/web_scraping/animes.txt', 'a') as f:
                    try:
                        f.write(f'{name}|!? ')
                    except:
                        pass
                    f.close()
                break
    
    num = ''
    index = -1
    while url[index].isdigit():
        num += url[index]
        index -= 1
    
    return int(num[::-1])


# temp_db = set(open('app/tools/web_scraping/temp.txt').read().split('|!? '))
# final = set()
# for i in temp_db:
 
#     if ':' in i:
#         index = i.index(':')
#         final.add(i[:index])
#     new_name = ""
#     for letter in i:
#         if letter not in ['!', '?', '.', '']:
#             new_name += letter
#     if new_name != i:
#         final.add(new_name)

# for name in final:
#     with open(f'app/tools/web_scraping/final_animes.txt', 'a') as f:
#         try:
#             f.write(f'{name}|!? ')
#         except:
#             print(name)

#         f.close()



movies_db = set(open('app/tools/web_scraping/movie.txt').read().split(', '))


tvshows_db = set(open('app/tools/web_scraping/tvshow.txt').read().split(', '))

anime_db = set(open('app/tools/web_scraping/final_animes.txt').read().split('|!? ')) 
# id, image, genres, age rating, release year, rating, length

def full_scrape_imdb(start:str, stop:str):
    def give_technical_dict():
        cur = ''
        add_letters = False
        for j in range(i, len(terms)):
            if terms[j-51:j] == '<script id="__NEXT_DATA__" type="application/json">': 
                add_letters = True
            if add_letters:
                cur += terms[j]
            if terms[j:j+24] == ',"contributionQuestions"':
                break
        cur = cur[:-1] + (cur.count('{') - cur.count('}')) * '}'
        
        technical_dict = json.loads(cur)
        return technical_dict
    def give_reg_dict():
        for i in range(len(terms)):
            if terms[i:i+35] == '<script type="application/ld+json">':
                index = i + 35
                cur = ''
                while terms[index:index+9] != '</script>':
                    cur += terms[index]
                    index += 1
                my_dict = json.loads(cur)
                return my_dict
    num = start
    url = f'https://www.imdb.com/title/tt{num}/'
    headers = requests.utils.default_headers()
    info = tuple()
    headers.update(
        {
            'User-Agent': 'My User Agent 1.0',
        }
    )
    while num != stop:
        try:
            result = requests.get(url, headers=headers)
        except:
            continue

        terms = result.text
        
        
        for i in range(len(terms)):
            if terms[i:i+35] == '<script type="application/ld+json">':
                index = i + 35
                cur = ''
                while terms[index:index+9] != '</script>':
                    cur += terms[index]
                    index += 1
                my_dict = json.loads(cur)
                info = [''] * 7
                if "url" in my_dict:
                    info[0] = my_dict["url"][6:-1]
                if "name" in reg_dict:
                    info[1] = reg_dict["name"].replace(u'\xa0', u' ').replace(u'&amp;', u'and').replace('&#039;', "'").replace('&quot;', '"').replace('&apos;', "'").translate(letter_map).lower()
                if "image" in reg_dict:
                    info[2] = reg_dict["image"]
                try:
                    info[3] = my_dict["aggregateRating"]["ratingValue"]
                except:
                    pass
                if "genre" in my_dict:
                    info[4] = my_dict["genre"]
                if "duration" in my_dict:
                    info[5] = my_dict["duration"]
                else:
                    
                    technical_dict = give_technical_dict()
                    try:
                        info[5] = technical_dict["series"]["series"]["runtime"]["seconds"]
                    except:
                        pass
                            
                if "datePublished" in my_dict:
                    info[6] = my_dict["datePublished"][:4]
                else:
                    try:
                        technical_dict
                    except:
                        technical_dict = give_technical_dict()
                    try:
                        info[6] = technical_dict["releaseYear"]["year"]
                    except:
                        pass

        # with open(f'app/tools/web_scraping/final_animes.txt', 'a') as f:
        #     try:
        #         f.write(f'{name}|!? ')
        #     except:
        #         print(name)

        #     f.close()

        num = list(num)
        for i in range(-1, -1 * len(num) - 1, -1):
            if num[i] != '9':
                num[i] = str(int(num[i]) + 1)
                for j in range(i+1, 0):
                    num[j] = '0'
                break
        num = ''.join(num)
        url = f'https://www.imdb.com/title/tt{num}/'
        print(info)


def full_scrape_imdbv2(start:str, stop:str):
    
    def give_technical_dict():
        cur = ''
        add_letters = False
        for j in range(len(terms)):
            if terms[j-51:j] == '<script id="__NEXT_DATA__" type="application/json">': 
                add_letters = True
            if add_letters:
                cur += terms[j]
            if terms[j:j+24] == ',"contributionQuestions"':
                break
        cur = cur[:-1] + (cur.count('{') - cur.count('}')) * '}'
        try:
            technical_dict = json.loads(cur)
        except:
            technical_dict = None
        return technical_dict


    def give_reg_dict():
        for i in range(len(terms)):
            if terms[i:i+35] == '<script type="application/ld+json">':
                index = i + 35
                cur = ''
                while terms[index:index+9] != '</script>':
                    cur += terms[index]
                    index += 1
                try:
                    my_dict = json.loads(cur)
                except:
                    my_dict = None
                return my_dict

    num = start
    url = f'https://www.imdb.com/title/tt{num}/'
    headers = requests.utils.default_headers()
    
    headers.update(
        {
            'User-Agent': 'My User Agent 1.0',
        }
    )
    while num != stop:
        try:
            result = requests.get(url, headers=headers)
        except:
            continue

        num = list(num)
        for i in range(-1, -1 * len(num) - 1, -1):
            if num[i] != '9':
                num[i] = str(int(num[i]) + 1)
                for j in range(i+1, 0):
                    num[j] = '0'
                break
        num = ''.join(num)
        url = f'https://www.imdb.com/title/tt{num}/'

        terms = result.text
      
        

        technical_dict = give_technical_dict()
        
        reg_dict = give_reg_dict()
        if reg_dict == technical_dict == None:
            continue
        info = [''] * 6 + [[]]
        
        try:
            ifo[0] = technical_dict["props"]["pageProps"]["tconst"]
        except:
        
            if "url" in reg_dict:
                info[0] = reg_dict["url"][7:-1]

        try:
            name = echnical_dict["props"]["pageProps"]["aboveTheFoldData"]["series"]["series"]["titleText"]["text"]
            
        except:
            try:
                name = echnical_dict["props"]["pageProps"]["aboveTheFoldData"]["titleText"]["text"]

            except:
               
                name = ''
                index = terms.index('<title>') + 7
                while terms[index] != '(' and terms[index:index+7] != '&quot; ':
                    name += terms[index]
                    index += 1
                if '&quot;' in name:
                    name = name[6:]

        info[1] = name.replace(u'\xa0', u' ').replace(u'&amp;', u'and').replace('&#039;', "'").replace('&quot;', '"').replace('&apos;', "'").translate(letter_map).lower()

            

        try:
            ino[2] = technical_dict["props"]["pageProps"]["aboveTheFoldData"]["primaryImage"]["url"]
        except:
            
            if "image" in reg_dict:
                info[2] = reg_dict["image"]
        try:
            ino[3] = technical_dict["props"]["pageProps"]["aboveTheFoldData"]["ratingsSummary"]["aggregateRating"]
        except:
            
            if "aggregateRating" in reg_dict and "ratingValue" in reg_dict["aggregateRating"]:
                info[3] = reg_dict["aggregateRating"]["ratingValue"]
       
        try:
            ino[4] = technical_dict["props"]["pageProps"]["mainColumnData"]["series"]["series"]["runtime"]["seconds"] // 60
        
        except:
            try:
                ifo[4] = technical_dict["props"]["pageProps"]["mainColumnData"]["runtime"]["seconds"] // 60

            except:
             
                if "duration" in reg_dict and reg_dict["duration"] != '':
                   
                    total = 0
                    full = reg_dict["duration"]
                    for i in range(len(full)):
                        if full[i].isdigit():
                            if 'H' in full and i < full.index('H'):
                                total += int(full[i]) * 60
                            else:
                                total += int(full[i]) * 10 ** (full.index('M') - i - 1)
                    info[4] = total

                    
       
        try:
            ino[5] = technical_dict["props"]["pageProps"]["aboveTheFoldData"]["series"]["series"]["releaseYear"]["year"] 
        except:
            try:
                ino[5] = technical_dict["props"]["pageProps"]["aboveTheFoldData"]["releaseYear"]["year"] 
   
            except:
                
                if "datePublished" in reg_dict:
                    info[5] = reg_dict["datePublished"][:4]

        try:
            genres = echnical_dict["props"]["pageProps"]["aboveTheFoldData"]["genres"]["genres"]
        except:
            
            if "genre" in reg_dict:
                info[6] = reg_dict["genre"]
        else:
            for genre in genres:
                if "text" in genre:
                    info[6].append(genre["text"])
        info = [str(i) for i in info]
        print(info)

        
def full_scrape_imdbv3(start:str, stop:str):
    # better for genres + gives og year for tv series
    def give_technical_dict():
        cur = ''
        add_letters = False
        for j in range(len(terms)):
            if terms[j-51:j] == '<script id="__NEXT_DATA__" type="application/json">': 
                add_letters = True
            if add_letters:
                cur += terms[j]
            if terms[j:j+24] == ',"contributionQuestions"':
                break
        cur = cur[:-1] + (cur.count('{') - cur.count('}')) * '}'
        try:
            technical_dict = json.loads(cur)
        except:
            technical_dict = None
        return technical_dict


    def give_reg_dict():
        for i in range(len(terms)):
            if terms[i:i+35] == '<script type="application/ld+json">':
                index = i + 35
                cur = ''
                while terms[index:index+9] != '</script>':
                    cur += terms[index]
                    index += 1
                try:
                    my_dict = json.loads(cur)
                except:
                    my_dict = None
                return my_dict

    num = start
    url = f'https://www.imdb.com/title/tt{num}/'
    headers = requests.utils.default_headers()
    
    headers.update(
        {
            'User-Agent': 'My User Agent 1.0',
        }
    )
    while num != stop:
        try:
            result = requests.get(url, headers=headers)
        except:
            continue

        num = list(num)
        for i in range(-1, -1 * len(num) - 1, -1):
            if num[i] != '9':
                num[i] = str(int(num[i]) + 1)
                for j in range(i+1, 0):
                    num[j] = '0'
                break
        num = ''.join(num)
        url = f'https://www.imdb.com/title/tt{num}/'

        terms = result.text
      
        

        technical_dict = give_technical_dict()
        
        reg_dict = give_reg_dict()
        if reg_dict == technical_dict == None:
            continue
        info = [''] * 6 + [[]]
        
        try:
            info[0] = technical_dict["props"]["pageProps"]["tconst"]
        except:
            print(0)
            if "url" in reg_dict:
                info[0] = reg_dict["url"][7:-1]

        try:
            name = technical_dict["props"]["pageProps"]["aboveTheFoldData"]["series"]["series"]["titleText"]["text"]
            
        except:
            try:
                name = technical_dict["props"]["pageProps"]["aboveTheFoldData"]["titleText"]["text"]

            except:
                print(1)
                name = ''
                index = terms.index('<title>') + 7
                while terms[index] != '(' and terms[index:index+7] != '&quot; ':
                    name += terms[index]
                    index += 1
                if '&quot;' in name:
                    name = name[6:]

        info[1] = name.replace(u'\xa0', u' ').replace(u'&amp;', u'and').replace('&#039;', "'").replace('&quot;', '"').replace('&apos;', "'").translate(letter_map).lower()

            

        try:
            info[2] = technical_dict["props"]["pageProps"]["aboveTheFoldData"]["primaryImage"]["url"]
        except:
            print(2)
            if "image" in reg_dict:
                info[2] = reg_dict["image"]
        try:
            info[3] = technical_dict["props"]["pageProps"]["aboveTheFoldData"]["ratingsSummary"]["aggregateRating"]
        except:
            print(3)
            if "aggregateRating" in reg_dict and "ratingValue" in reg_dict["aggregateRating"]:
                info[3] = reg_dict["aggregateRating"]["ratingValue"]
       
        try:
            info[4] = technical_dict["props"]["pageProps"]["mainColumnData"]["series"]["series"]["runtime"]["seconds"] // 60
        
        except:
            try:
                info[4] = technical_dict["props"]["pageProps"]["mainColumnData"]["runtime"]["seconds"] // 60

            except:
                print(4)
                if "duration" in reg_dict and reg_dict["duration"] != '':
                   
                    total = 0
                    full = reg_dict["duration"]
                    for i in range(len(full)):
                        if full[i].isdigit():
                            if 'H' in full and i < full.index('H'):
                                total += int(full[i]) * 60
                            else:
                                total += int(full[i])
                    info[4] = total

                    
       
        try:
            info[5] = technical_dict["props"]["pageProps"]["aboveTheFoldData"]["series"]["series"]["releaseYear"]["year"] 
        except:
            try:
                info[5] = technical_dict["props"]["pageProps"]["aboveTheFoldData"]["releaseYear"]["year"] 
   
            except:
                print(5)
                if "datePublished" in reg_dict:
                    info[5] = reg_dict["datePublished"][:4]

        try:
            genres = technical_dict["props"]["pageProps"]["aboveTheFoldData"]["genres"]["genres"]
        except:
            print(6)
            if "genre" in reg_dict:
                info[6] = reg_dict["genre"]
        else:
            for genre in genres:
                if "text" in genre:
                    info[6].append(genre["text"])
        info = [str(i) for i in info]
        print(info)

# full_scrape_imdbv2('13320622', '13320628')
# print('\n')
# full_scrape_imdbv3('13320622', '13320628')
# # with open(f'app/tools/web_scraping/final_animes.txt', 'a') as f:
# #     try:
# #         f.write(f'{name}|!? ')
# #     except:
# #         print(name)

# #     f.close()


    
# mine = full_scrape_imdbv2('0800370', '0800371')
# a = b = 0
# brackets_stack = ['']
# for i in range(1, len(mine)):
#     if mine[i] == '{':
#         a += 1
#         brackets_stack.append(mine[i-20:i])
#         print(brackets_stack)
     
      
#     elif mine[i] == '}':
#         b += 1
#         brackets_stack.pop()
    
#     if mine[i:i+len('"primaryImage":{"url":')] == '"primaryImage":{"url":':
#         print(a, b)
#         break


# a = [print(i) for i in brackets_stack]

# full_scrape_imdbv2('1850009', '1850010')
# db = list(open('app/tools/web_scraping/full_anime.txt').read().split('|!? ')) 
# print(db[0])

# id, image, genres, age rating, release year, rating, length
def remove_trailing_brackets(name):
    open_count = closed_count = 0
    for idx in range(len(name) - 1, -1, -1):
        if name[idx] == ')':
            closed_count += 1
        elif name[idx] == '(':
            open_count += 1
        elif open_count == closed_count:
            if name[idx] != ' ':
                break
            
    else:
        return
    
    return name[:idx+1]

def full_scrape_mal(num:str):
    url = f'https://myanimelist.net/anime/{num}'

    headers = requests.utils.default_headers()

    headers.update(
        {
            'User-Agent': 'My User Agent 1.0',
        }
    )
    
    info = {
    'japanese name' : '',
    'english name' : '',
    'image url' : '',
    'duration' : '',
    'year' : '',
    'genres' : '',
    'age rating' : '',
    'rating' : '',
    'url' : num
    }
    try:
        result = requests.get(url, headers=headers)
    except:
        return

    
    terms = result.text
    if "{action: 'submit'}" in terms:
        print('TRY AGAIN')
        return 'bad'
    # print(terms)
    for i in range(len(terms)):
        if terms[i:i+37] == 'Looking for information on the anime ':
            info['english name'] = ''
            info['image url'] = ''
            index = i + 37
            name = ''
            while terms[index:index+6] != '? Find' and index < len(terms):
                name += terms[index]
                index += 1
            
            
            if name[-1] == ')':
                closed_count = 1
                open_count = 0
                for i in range(len(name) - 2, -1, -1):
                    if name[i] == ')':
                        closed_count += 1
                       

                    elif name[i] == '(':
                        open_count += 1
                        if closed_count == open_count:
                            break
                    info['english name'] += name[i]
                name = name[:i-1]
                info['english name'] = remove_trailing_brackets(info['english name'])
                info['english name'] = info['english name'][::-1].replace(u'\xa0', u' ').replace(u'&amp;', u'and').replace('&#039;', "'").replace('&quot;', '"').translate(letter_map).lower().strip()
        
                    
                    
               
                
                
        
            # while ' (' != terms[index:index+2] and terms[index:index+6] != '? Find':
            #     info['japanese name'] += terms[index]
            #     index += 1
            info['japanese name'] = remove_trailing_brackets(name).replace(u'\xa0', u' ').replace(u'&amp;', u'and').replace('&#039;', "'").replace('&quot;', '"').translate(letter_map).lower().strip()
            new_name = ''
            for letter in name:
                if letter not in ['(', ')']:
                    new_name += letter
            new_name = new_name.replace(' ', '_').replace(':', '_')
            pic_url = f"{url}/{new_name}/pics"
            
            try:
                result_img = requests.get(pic_url, headers=headers)
            except:
                continue
            soup_img = bs4.BeautifulSoup(result_img.text, 'lxml')
        
            terms_img = str(soup_img.select('head')[0])
        
            for j in range(len(terms_img)):
                if terms_img[j:j+23] == '" property="og:image"/>':
                    
                    index = j - 1
                    while terms_img[index] != '"':
                        info['image url'] += terms_img[index]
                        index -= 1
                    
                    info['image url'] = info['image url'][::-1]


            
        
        # if terms[i:i+32] == '? Find out more with MyAnimeList' and terms[i-1] == ')':
        #     index = i - 2
            
        #     while terms[index] != '(':
        #         info['english name'] += terms[index]
        #         index -= 1
            
        if terms[i:i+37] == '<span class="dark_text">Aired:</span>':
            info['year'] = ''
            
            
            index = i + 37
            
            while terms[index] != '<' and index < len(terms):
                
                info['year'] += terms[index]
                index += 1
      
            if ',' in info['year']:
                comma_index = info['year'].index(',')
                info['year'] = info['year'][comma_index+2:comma_index+6]
            else:
                info['year'] = ''.join(char for char in info['year'] if char not in [' ', '\n'])
            


        if terms[i:i+38] == '<span class="dark_text">Genres:</span>' or terms[i:i+37] == '<span class="dark_text">Genre:</span>': # Genre
            info['genres'] = ''
            index = i + 37
            div_count = 0
            while div_count < 2 and index < len(terms):
                if terms[index:index+7] == '</span>' and terms[index-1] != ':':
                    cur = index - 1
                    genre = ''
                    while terms[cur] != '>':
                        genre += terms[cur]
                        cur -= 1
                    info['genres'] += f'{genre[::-1]}!?|'
                index += 1
                if terms[index:index+6] == '</div>':
                    div_count += 1
                

        if terms[i:i+40] == '<span class="dark_text">Duration:</span>':
            info['duration'] = ''
            index = i + 40
            while terms[index:index+4] != ' min' and index < len(terms):
                if terms[index].isdigit():
                    info['duration'] += terms[index]
                if len(info['duration']) > 2:
                    info['duration'] = str(int(info['duration'][0]) * 60 + int(info['duration'][1:]))
                    break
                index += 1
        
        if terms[i:i+38] == '<span class="dark_text">Rating:</span>':
            info['age rating'] = ''
            index = i + 38
            while index < len(terms) and terms[index] != '<':
                if terms[index] != '\n':
                    info['age rating'] += terms[index]
                index += 1
            info['age rating'] = info['age rating'].strip()

        if terms[i:i+47] == '<span itemprop="ratingValue" class="score-label':
            info['rating'] = ''
            index = i + 47
            while index < len(terms) and terms[index] != '<':
                if (terms[index].isdigit() or terms[index] == '.') and terms[index-1] != '-':
                    info['rating'] += terms[index]
                index += 1
    if info != {
    'japanese name' : '',
    'english name' : '',
    'image url' : '',
    'duration' : '',
    'year' : '',
    'genres' : '',
    'age rating' : '',
    'rating' : '',
    'url' : num
    }:
        return info
        

# print(full_scrape_mal('44167'))
conn = sqlite3.connect('titles.db')

cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS ANIME(name TEXT PRIMARY KEY, image TEXT, duration TEXT, year TEXT, genres TEXT, age_rating TEXT, rating TEXT, id TEXT)''')
conn.commit()
conn.close()

def sqlite_mal(start:str, stop:str):
    conn = sqlite3.connect('titles.db')
    cursor = conn.cursor()
    num = start
    while num != stop:
        info = full_scrape_mal(num)
        if info == 'bad':
            return num
        if info:
            
            try:
                cursor.execute(f'''INSERT INTO ANIME VALUES ("{info['japanese name']}", "{info['image url']}", "{info['duration']}", "{info['year']}", "{info['genres']}", "{info['age rating']}", "{info['rating']}", "{info['url']}")''')
                with open(f'app/tools/web_scraping/full_animev2.txt', 'a') as f:
        
                    f.write(f"{info['japanese name']}|!? ")
                    f.close()

            except sqlite3.IntegrityError:
                
                cursor.execute(f'''SELECT * FROM ANIME WHERE name = "{info['japanese name']}"''')
                data = cursor.fetchall()
                print(data)
            except:
                print(info['japanese name'])

                
            try:
                if len(info['english name']) > 0:
                    cursor.execute(f'''INSERT INTO ANIME VALUES ("{info['english name']}", "{info['image url']}", "{info['duration']}", "{info['year']}", "{info['genres']}", "{info['age rating']}", "{info['rating']}", "{info['url']}")''')
                    with open(f'app/tools/web_scraping/full_animev2.txt', 'a') as f:
                       
                        f.write(f"{info['english name']}|!? ")
                        f.close()

            except sqlite3.IntegrityError:
                cursor.execute(f'''SELECT * FROM ANIME WHERE name = "{info['english name']}"''')
                data = cursor.fetchall()
                print(data)
            except:
                print(info['english name'])
            
            
            conn.commit()
            
       
        num = str(int(num) + 1)
# print(full_scrape_mal('44167'))  

# CHANGED NAME ALGO FROM 44168 ONWARDS
# num = '47940'

# from time import sleep
# for i in range(50):

#     num = sqlite_mal(num, '51000')
#     print(num)
#     sleep(300)

conn = sqlite3.connect('titles.db')
cursor = conn.cursor()
name = input().lower()
cursor.execute(f'''SELECT * FROM ANIME WHERE name = "{name}"''')
data = cursor.fetchall()
print(data)
# for i in range(len(data)):
#     entry = data[i]
#     # print(entry)
#     image = entry[1]
#     name = entry[0]

#     if image[:len(image) // 2] == image[len(image) // 2:][::-1]:
#         print(image)
#         print(name)
#         # new_name = name[:len(name) // 2]
#         # new_image = image[:len(image) // 2]
#         # # cursor.execute(f'''SELECT * FROM ANIME WHERE NAME = "{name}"''')
#         # # print(cursor.fetchall())
     
#         #     # cursor.execute(f'''UPDATE ANIME SET NAME = "{new_name}" WHERE NAME = "{name}"''')
#         # cursor.execute(f'''UPDATE ANIME SET IMAGE = "{new_image}" WHERE IMAGE = "{image}"''')
#         # # except:
#         # #     cursor.execute(f'''SELECT * FROM ANIME WHERE name = "{name}"''')
#         # #     new = cursor.fetchall()
#         # #     print(new)
        
#         # conn.commit()
        
      
# for i in data:
#     try:
#         int(i[3])
#     except:
#         print(i)
# data = cursor.fetchall()
# print(data)
# print(len(data))



# for i in anime_db:
#     cursor.execute(f'''SELECT * FROM ANIME WHERE name = "1{i}"''')
#     data = cursor.fetchall()
#     if len(data) == 0:
#         print(i)
#         print('bad')


    
# cursor.execute('''CREATE TABLE IF NOT EXISTS COMPANY(id REAL PRIMARY KEY, name TEXT, rating TEXT, duration TEXT, url TEXT, age_rating TEXT, genre1 TEXT, genre2 TEXT, genre3 TEXT, genre4 TEXT)''')
# for i in range(50000):
#     cursor.execute(f"INSERT INTO COMPANY VALUES ({i}, 'Paul{i}{i}{i}', '5{i}{i}{i}', '{i}{i}1h33{i}', '{i}{i}12123{i}', '{i}{i}PG-13{i}', '{i}{i}cool{i}', '{i}scary{i}{i}', '{i}nice{i}{i}', '{i}sad{i}{i}')")
# cursor.execute(f"INSERT INTO COMPANY VALUES (1, 'Paul{i}{i}{i}', '5{i}{i}{i}', '{i}{i}1h33{i}', '{i}{i}12123{i}', '{i}{i}PG-13{i}', '{i}{i}cool{i}', '{i}scary{i}{i}', '{i}nice{i}{i}', '{i}sad{i}{i}')")

# cursor.execute("SELECT * FROM COMPANY WHERE id IN (1, 49999)")
# data = cursor.fetchall()
# print(data)

    
  
    
# # print(total)
# # conn.close()

# # mydb = mysql.connector.connect(
# #   host = "localhost",
# #   user = "varun",
# #   passwd = getpass.getpass('Password:'),
# #   database = "titles"
# # )
# # mycursor = mydb.cursor()
# # mycursor.execute("SHOW TABLES")

# # for x in mycursor:
# #   print(x)

# # # total = 0
# # # for i in range(20):
    
# # #     # mycursor.execute("CREATE TABLE customers (id REAL, name VARCHAR(255), rating VARCHAR(255), url VARCHAR(255), age VARCHAR(255), duration VARCHAR(255), genre1 VARCHAR(255), genre2 VARCHAR(255), genre3 VARCHAR(255), genre4 VARCHAR(255))")
# # #     # for i in range(1000000):
# # #     #     mycursor.execute(f"INSERT INTO customers VALUES ({i}, 'Paul{i}{i}{i}', '5{i}{i}{i}', '{i}{i}1h33{i}', '{i}{i}12123{i}', '{i}{i}PG-13{i}', '{i}{i}cool{i}', '{i}scary{i}{i}', '{i}nice{i}{i}', '{i}sad{i}{i}')")
# # #     start = time()
# # #     mycursor.execute("SELECT name, rating, duration, url, age, genre1, genre2, genre3, genre4 FROM customers where id in (1, 500000, 13010, 999999, 345346, 123123, 987124, 1234, 4, 787878, 555555, 44444, 666666, 989898, 167167, 876123, 45612, 18, 191919, 222222)")
# # #     myresult = mycursor.fetchall()
# # #     total += (time() - start)
# # #     # mydb.commit()
# # # print(total / 20)