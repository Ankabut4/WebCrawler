"""
Definition of views.
"""

from django.shortcuts import render
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime

import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import re
from django.http import JsonResponse
import json
from .models import Record
from django.conf import settings as djangoSettings
from django.core import serializers
def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )
def json_status(request):
    json_data = open(djangoSettings.STATIC_ROOT+'/app/json/status.json')   
    data1 = json.load(json_data)
    return JsonResponse(data1)
def json_sites(request):
    json_data = open(djangoSettings.STATIC_ROOT+'/app/json/sites.json')   
    data1 = json.load(json_data)
    return JsonResponse(data1, safe=False)
def scan_sites(request):
	return render(
		request,
		'app/scan_sites.html',
		{
			'title':'Web Crawler',
			'message':'Intelligent Data Collector'
		}
	)
def ajax_scan_sites(request):
    data=[]
    count=0
    ## site 1 : brockandscott.com
    site = 'brockandscott.com'
    try:
        with open(djangoSettings.STATIC_ROOT+'/app/json/status.json', 'w') as json_file1:
            json.dump(dict(status='running', message='Started Processing', site=site, count=count), json_file1)
            json_file1.close()
        for page_id in range(1,500000):
            response = requests.get('https://www.brockandscott.com/foreclosure-sales/?_sft_foreclosure_state=nc&sf_paged='+str(page_id))
            soup = BeautifulSoup(response.text, "html.parser")
            notfound = soup.find('h1',{'class':'page-title'})
            if(notfound):
                print('Not Found at page ',page_id)
                break
            for row in soup.findAll('div', {"class": 'record'}):
                count=count + 1
                rec = Record()
                rec.id = count
                rec.site = site
                for cell in row.findAll('div',{'class':'forecol'}):
                    ptags = cell.findAll('p')
                    if(ptags[0].text.strip() == 'County:'):
                        rec.county = ptags[1].text.strip()
                    elif(ptags[0].text.strip() == 'Sale Date:'):
                        rec.sale_date = ptags[1].text.strip()
                    elif(ptags[0].text.strip() == 'Case #:'):
                        rec.case = ptags[1].text.strip()
                    elif(ptags[0].text.strip() == 'Address:'):
                        rec.address = ptags[1].text.strip()
                    elif(ptags[0].text.strip() == 'Opening Bid Amount:'):
                        rec.bid = ptags[1].text.strip()
                    elif(ptags[0].text.strip() == 'Court SP #:'):
                        rec.courtsp = ptags[1].text.strip()
                    #keytext = re.sub('[^A-Za-z]+', '', ptags[0].text)
                    #keytext =  keytext.lower()
                    #row_data.update({keytext:ptags[1].text})
				    ##print(ptags[1].text, end=', ')
			    ##print() 
                with open(djangoSettings.STATIC_ROOT+'/app/json/status.json', 'w') as json_file1:
                    json.dump(dict(status='running', message='Started Processing', site=site, count=count), json_file1)
                data.append(rec.as_json())
    except:
        print('Something Went Wrong '+site)


    ## site 2 : sales.hutchenslawfirm.com
    site = 'sales.hutchenslawfirm.com'
    try:
        #with open(djangoSettings.STATIC_ROOT+'/app/json/status.json', 'w') as json_file1:
        #    json.dump(dict(status='running', message='Started Processing', site=site, count=count), json_file1)
        #    json_file1.close()
        url = 'https://sales.hutchenslawfirm.com/NCfcSalesList.aspx'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        pager_row=soup.findAll('tr', attrs={'class':'GridPager_WebBlue'})
        pager_td=pager_row[0].findAll('td')
        vs = soup.find('input', {'id': '__VIEWSTATE'}).get('value')
        ev = soup.find('input', {'id': '__EVENTVALIDATION'}).get('value')
        vg = soup.find('input', {'id': '__VIEWSTATEGENERATOR'}).get('value')
        words = pager_td[0].text.split()
        total_pages = words[-1]
        print(total_pages)
        for page in range(1,int(total_pages)+1):
            et='SalesListGrid$ctl01$ctl03$ctl01$ctl0'+str(page)
            postdata = {'__EVENTTARGET':et,
                    '__EVENTARGUMENT':'',
                    '__VIEWSTATE':vs,
                    '__EVENTVALIDATION':ev,
                    '__VIEWSTATEGENERATOR':vg,
                    'SearchTextBox':'',
                    'SearchGroup':'AllRadio',
                    'SalesListGridPostDataValue':''}
            r =requests.post(url, data=postdata)
            newsoup = BeautifulSoup(r.text, "html.parser")
            for rows in newsoup.findAll('tr', attrs={'class':['GridRow_WebBlue','GridAltRow_WebBlue']}):
                index=0
                count=count + 1
                rec = Record()
                rec.id = count
                rec.site = site
                for cols in rows.findAll('td'):
                    if(index==0):
                        rec.case = cols.text.strip()
                    elif(index==1):
                        rec.courtsp = cols.text.strip()
                    elif(index==2):
                        rec.county = cols.text.replace(', NC', '').strip()
                    elif(index==3):
                        rec.sale_date = cols.text.strip()
                    elif(index==4):
                        rec.address = cols.text.strip()
                    elif(index==7):
                        rec.bid = cols.text.strip()
                    index = index +1
                with open(djangoSettings.STATIC_ROOT+'/app/json/status.json', 'w') as json_file1:
                    json.dump(dict(status='running', message='Started Processing', site=site, count=count), json_file1)
                data.append(rec.as_json())
    except:
        print('Something Went Wrong '+site)


    ## site 3 : sales.hutchenslawfirm.com
    site = 'shapiro-ingle.com'
    try:
        url = 'https://www.shapiro-ingle.com/sales.aspx?state=NC'
        sale_types = ['upcoming_sales','sales_held']
        for sale_type in sale_types:
            print()
            print(sale_type)
            print()
            response = requests.post(url, data={'db':sale_type,'county':'%','SubmitBtn':'Search'})
            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find('table')
            rows = table.findAll('tr')
            for row in rows:
                index=0
                count=count + 1
                rec = Record()
                rec.id = count
                rec.site = site
                for cols in row.findAll('td'):
                    if(index==0):
                        rec.county = cols.text.replace(', NC', '').strip()
                    elif(index==1):
                        rec.sale_date = cols.text.strip()
                    elif(index==2):
                        rec.case = cols.text.strip()
                    elif(index==3):
                        rec.address = cols.text.strip()
                    elif(index==4):
                        rec.bid = cols.text.strip()
                    index = index +1
                with open(djangoSettings.STATIC_ROOT+'/app/json/status.json', 'w') as json_file1:
                    json.dump(dict(status='running', message='Started Processing', site=site, count=count), json_file1)
                data.append(rec.as_json())
    except:
        print('Something Went Wrong '+site)
    if(len(data)>0):
        with open(djangoSettings.STATIC_ROOT+'/app/json/sites.json', 'w') as json_file:
            json.dump(dict(data=data), json_file)
            json_file.close()
    with open(djangoSettings.STATIC_ROOT+'/app/json/status.json', 'w') as json_file1:
        json.dump(dict(status='completed', message='Scan Completed', site='All Site', count=count), json_file1)
        json_file1.close()
    return JsonResponse({'status':'done'})

def ajax_search(request):
    countiesgis = [
        dict(name='Rutherford',url='https://rutherfordcounty.connectgis.com', ucounty='RutherfordCounty', address='Physical_Address', themeid=256, layerid=7836, agslayerid=45),
        dict(name='Scotland',url='https://laurinburg.connectgis.com', ucounty='Scotland', address='FULLADDR', themeid=236, layerid=7004, agslayerid=16),
        dict(name='Yancey',url='https://yancey.connectgis.com', ucounty='Yancey', address='PropertyL', themeid=162, layerid=4923, agslayerid=25),
        dict(name='Wilson',url='https://wilsoncounty.connectgis.com', ucounty='Wilson', address='ADDRESS', themeid=300, layerid=10490, agslayerid=0),
        dict(name='Brunswick',url='https://bladen2.connectgis.com', ucounty='Brunswick', address='ADDRESS', themeid=28, layerid=1372, agslayerid=5),
        dict(name='Stanly',url='https://stanly.connectgis.com', ucounty='Stanly', address='PhyStreetAddr', themeid=181, layerid=7836, agslayerid=24),
        dict(name='Nash',url='https://nashcounty.connectgis.com', ucounty='NashCounty', address='CONDADD1', themeid=403, layerid=12128, agslayerid=12),
        dict(name='Iredell',url='https://iredell.connectgis.com', ucounty='Iredelle', address='FullAddr', themeid=4, layerid=1023, agslayerid=25),
        dict(name='Lenoir',url='https://lenoir2.connectgis.com', ucounty='Lenoir', address='PhysStrAdd', themeid=39, layerid=9846, agslayerid=8),
        dict(name='Hoke',url='https://hoke2.connectgis.com', ucounty='HokePrivate', address='PHY_ADDRES', themeid=64, layerid=2645, agslayerid=9),
        dict(name='Sampson',url='https://sampson.connectgis.com', ucounty='Sampson2', address='PARCEL_ADD', themeid=40, layerid=1747, agslayerid=35),
        dict(name='Vance',url='https://vance.connectgis.com', ucounty='Vance', address='full_addre', themeid=41, layerid=12896, agslayerid=93),
        dict(name='Wayne',url='https://wayne.connectgis.com', ucounty='Wayn', address='FULL_ADD', themeid=226, layerid=10335, agslayerid=19),
        dict(name='Yadkin',url='https://yadkin.connectgis.com', ucounty='Yadkin', address='full_addre', themeid=189, layerid=5478, agslayerid=0)
    ]
    #countiesgis = [
    #    dict(name='Rutherford',url='https://rutherfordcounty.connectgis.com', ucounty='RutherfordCounty', address='Physical_Address',themeid=256,layerid=7836,agslayerid=45),
    #    dict(name='Scotland',url='https://laurinburg.connectgis.com', address='FULLADDR'),
    #    dict(name='Yancey',url='https://yancey.connectgis.com', address='PropertyL'),
    #    dict(name='Wilson',url='https://wilsoncounty.connectgis.com', ucounty='WilsonCounty', address='ADDRESS'),
    #    dict(name='Brunswick',url='https://bladen2.connectgis.com', address='ADDRESS'),
    #    dict(name='Stanly',url='https://stanly.connectgis.com', address='PhyStreetAddr',themeid=181,layerid=7836,agslayerid=24),
    #    dict(name='Nash',url='https://nashcounty.connectgis.com', ucounty='NashCounty', address='CONDADD1'),
    #    dict(name='Iredell',url='https://iredell.connectgis.com', address='FullAddr'),
    #    dict(name='Lenoir',url='https://lenoir2.connectgis.com', address='PhysStrAdd'),
    #    dict(name='Hoke',url='https://hoke2.connectgis.com', ucounty='HokePrivate', address='PHY_ADDRES'),
    #    dict(name='Sampson',url='https://sampson.connectgis.com', ucounty='Sampson2', address='PARCEL_ADD'),
    #    dict(name='Vance',url='https://vance.connectgis.com', address='full_addre'),
    #    dict(name='Wayne',url='https://wayne.connectgis.com', address='FULL_ADD'),
    #    dict(name='Yadkin',url='https://yadkin.connectgis.com', address='full_addre')]
    ##print(mobilemap)
    data=[]
    stats=[]
    count=0
    with open(djangoSettings.STATIC_ROOT+'/app/json/sites.json', "r") as read_file:
        sites = json.load(read_file)
        ##input_dict = json.load(djangoSettings.STATIC_ROOT+'/app/json/sites.json')
        ##print(data)
        for county in countiesgis:
            print()
            print()
            print(county['name'], county['url'])
            ucounty=county['name']
            if 'ucounty' in county:
                ucounty=county['ucounty']
            output_dict = [x for x in sites['data'] if x['county'] == county['name']]
            print(county['name'], len(output_dict))
            if(len(output_dict)>0):
                try:
                    url = county['url']+"/Disclaimer.aspx"
                    with requests.session() as ses:
                        req = ses.get(url)
                        soup = BeautifulSoup(req.text, "html.parser")
                        inputs = soup.findAll('input')
                        controls={}
                        for inp in inputs:
                            controls.update({inp.get('name'):inp.get('value')})
                        controls.update({'__EVENTTARGET':'btnAccept'})
                        controls.update({'__EVENTARGUMENT':''})
                        r = ses.post(url, data=controls)
                        ses.get(county['url']+'/Map.aspx')
                        headers = {
                            'Origin': county['url'],
                            'Accept-Encoding': 'gzip, deflate, br',
                            'Accept-Language': 'en-US,en;q=0.9,la;q=0.8,es;q=0.7',
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
                            'Content-Type': 'application/json; charset=UTF-8',
                            'Accept': '*/*',
                            'Referer': county['url']+'/Map.aspx',
                            'X-Requested-With': 'XMLHttpRequest',
                            'Connection': 'keep-alive'
                        }
                        cookies = {
                            '.ConnectGISAUTH':str(ses.cookies.get_dict()['.ConnectGISAUTH']),
                            'ASP.NET_SessionId':str(ses.cookies.get_dict()['ASP.NET_SessionId'])
                        }
                        for rec in output_dict:
                            print()
                            words_address = rec['address'].split()
                            for attempt in range(0,3):
                                whereclause = ''
                                if(attempt==0):
                                    search1 = words_address[0]+' '+ words_address[1]+' '+ words_address[2]
                                    search2 = words_address[0]+'  '+ words_address[1]+' '+ words_address[2]
                                    search3 = words_address[0]+' '+ words_address[1]+' '+ words_address[2]
                                    search3 = search3.replace('Road', 'Rd').strip()
                                    search3 = search3.replace('Street', 'St').strip()
                                    search3 = search3.replace('Highway', 'Hwy').strip()
                                    search4 = words_address[0]+'  '+ words_address[1]+' '+ words_address[2]
                                    search4 = search4.replace('Road', 'Rd').strip()
                                    search4 = search4.replace('Street', 'St').strip()
                                    search4 = search4.replace('Highway', 'Hwy').strip()
                                    whereclause = 'UPPER('+county['address']+') LIKE &#039;'+search1.strip()+'%&#039;'
                                    whereclause = whereclause + ' or UPPER('+county['address']+') LIKE &#039;'+search2.strip()+'%&#039;'
                                    whereclause = whereclause + ' or UPPER('+county['address']+') LIKE &#039;'+search3.strip()+'%&#039;'
                                    whereclause = whereclause + ' or UPPER('+county['address']+') LIKE &#039;'+search4.strip()+'%&#039;'
                                elif(attempt==1):
                                    search1 = words_address[0]+' '+ words_address[1]
                                    search2 = words_address[0]+'  '+ words_address[1]
                                    whereclause = 'UPPER('+county['address']+') LIKE &#039;'+search1.strip()+'%&#039;'
                                    whereclause = whereclause + ' or UPPER('+county['address']+') LIKE &#039;'+search2.strip()+'%&#039;'
                                elif(attempt==2):
                                    search1 = words_address[0]
                                    whereclause = 'UPPER('+county['address']+') LIKE &#039;'+search1.strip()+'%&#039;'
                                else:
                                    print(county['name'] + ' not found with all attempts')
                                    break
                                print(rec['address'], '=>', whereclause)
                                response = requests.post(county['url']+'/WebServices/WS.asmx/querylayer',
                                    headers=headers,
                                    cookies=cookies,
                                    json={'url':'https://arcgis.mobile311.com/ArcGIS/rest/services/NorthCarolina/'+ucounty+'/MapServer',
                                        'gurl':'https://arcgis.mobile311.com/ArcGIS/rest/services/Utilities/Geometry/GeometryServer',
                                        'sr':102719, 'themeid':county['themeid'], 'layerid':county['layerid'], 'agslayerid':county['agslayerid'],
                                        'whereclause':whereclause,
                                        #'whereclause':'UPPER('+county['address']+') LIKE &#039;'+search_address.strip()+'%&#039;',
                                        'maxresults':50, 'distance':0,'oid':-1,'geometrytype':None,'geometry':'null'});
                                if response.status_code == 200:
                                    print(response.text)
                                    #break
                                    #m=json.dumps(response.text)
                                    #print("*")
                                    result=json.loads(str(response.text.strip()))
                                    #print("**")
                                    #print(response.text)
                                    #result = response.text.json()
                                    if 'result' in result['d']:
                                        if 'resultsCount' in result['d']['result']:
                                            if(result['d']['result']['resultsCount']>0):
                                                print('Got '+str(attempt))
                                                break
                                            else:
                                                print('resultsCount 0 at attempt '+str(attempt))
                                        else:
                                            print('resultsCount not found at attempt '+str(attempt))
                                    else:
                                        print('not found '+str(attempt))
                                        attempt=attempt+1
                                elif response.status_code == 200:
                                    print('page not found '+county['name'])
                                    break
                                else:
                                    print('error '+str(response.status_code)+' '+county['name'])
                                    break
                except:
                    print('Something Went Wrong in County '+county['name'])
            else:
                print('No Records to Search in '+county['name'])
            break
    return JsonResponse({'status':'done'})