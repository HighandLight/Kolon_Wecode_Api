from cgitb import reset
import json
from re import A
from unittest import result
import requests
from haversine import haversine


# from kolon_wecode.settings import API_KEY
from dealers.models import Branch

API_KEY='ecf899e71cb8d76d0534c9ec7b3f1c32'

def address(addr):
    url = 'https://dapi.kakao.com/v2/local/search/address.json?query={address}'.format(address=addr)
    headers = {'Authorization': 'KakaoAK ' + API_KEY}
    result = json.loads(str(requests.get(url, headers=headers).text))
    match_first = result['documents'][0]['address']
    return [float(match_first['x']), float(match_first['y'])]

def lode_map(origin_x,origin_y):
    url = 'https://apis-navi.kakaomobility.com/v1/destinations/directions'
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'KakaoAK ' + API_KEY
    }
    
    data = {
        'origin': {
            'x': origin_x,
            'y': origin_y
        },
        'destinations': [
            {
                'x': '127.034110839609',
                'y': '37.52202559254',
                'key': 'BMW 강남 전시장'
            },
            {
                'x': '127.066667411329',
                'y': '37.5013458204344',
                'key': 'BMW 삼성 전시장'
            },
            {
                'x': '126.765992384872',
                'y': '37.483698134572',
                'key': 'BMW 부천 전시장'
            },
            {
                'x': '127.144554682494',
                'y': '37.3743698649541',
                'key': 'BMW 분당 전시장'
            },
            {
                'x': '127.148404124838',
                'y': '37.4801356884837',
                'key': 'BMW 위례 스마트 쇼룸'
            },
            {
                'x': '127.05791988224',
                'y': '37.706414341252',
                'key': 'BMW 의정부 전시장'
            },
            {
                'x': '127.353120213396',
                'y': '36.35932586697',
                'key': 'BMW 대전 전시장'
            },
            {
                'x': '127.3820651968',
                'y': '36.3751016880633',
                'key': 'BMW 대전 아트앤사이언스 전시장'
            },
            {
                'x': '128.36330362234',
                'y': '36.104275355764',
                'key': 'BMW 구미 전시장'
            },
            {
                'x': '128.878796243924',
                'y': '35.2255515708606',
                'key': 'BMW 김해 전시장'
            },
            {
                'x': '128.62488570310',
                'y': '35.8420799010038',
                'key': 'BMW 대구 전시장'
            },
            {
                'x': '129.103165101124',
                'y': '35.1385706176281',
                'key': 'BMW 부산(남구) 전시장'
            },
            {
                'x': '127.513969390348',
                'y': '34.9845671514485',
                'key': 'BMW 순천 전시장'
            },
            {
                'x': '126.883795049984',
                'y': '35.1597608535698',
                'key': 'BMW 광주 전시장'
            }
        ],
        'radius': 10000
    }
    
    total = json.loads(str(requests.post(url, headers=headers,data=json.dumps(data)).text))
    
    success_lode_map = [total for total in total['routes'] if total['result_code'] == 0]
    
    if success_lode_map == []:
        return 'RECONFIRM'
    
    i = [ i['summary'] for i in success_lode_map ]
    j = [ j['distance'] for j in [ i['summary'] for i in success_lode_map]]
    
    branch_name = success_lode_map[j.index(min(j))]['key']
    branch = Branch.objects.get(name = branch_name)
    result = branch.id
    
    return result

def straight_distance(origin_x,origin_y):
    origin = (origin_x, origin_y)
    destinations = [(127.034110839609,37.52202559254),(127.066667411329,37.5013458204344),(126.765992384872,37.483698134572),(127.144554682494,37.3743698649541),(127.148404124838,37.4801356884837),(127.05791988224,37.706414341252),(127.353120213396,36.35932586697),(127.3820651968,36.3751016880633),(128.36330362234,36.104275355764),(128.878796243924,35.2255515708606),(128.62488570310,35.8420799010038),(129.103165101124,35.1385706176281),(127.513969390348,34.9845671514485),(126.883795049984,35.1597608535698)]
    destinations_branch = ['BMW 강남 전시장','BMW 삼성 전시장','BMW 부천 전시장','BMW 분당 전시장','BMW 위례 스마트 쇼룸','BMW 의정부 전시장','BMW 대전 전시장','BMW 대전 아트앤사이언스 전시장','BMW 구미 전시장','BMW 김해 전시장','BMW 대구 전시장','BMW 부산(남구) 전시장','BMW 순천 전시장','BMW 광주 전시장']
    
    total_distance = []
    for destination in destinations:
        i = destination
        j = haversine(origin, i, unit = 'km')
        total_distance.append(int(j))
    
    branch_name = destinations_branch[total_distance.index(min(total_distance))]
    branch = Branch.objects.get(name = branch_name)
    result = branch.id
    
    return result