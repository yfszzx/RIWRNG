from django.shortcuts import render
from django.http import HttpResponse
import requests as rq
import json

def main(request):
    code  = request.GET['code']
    r = rq.get(f"https://api.weixin.qq.com/sns/oauth2/access_token?appid=wx6742e22952f55f43&secret=7dc332250bc57fa4c8a46f980d112956&code={code}&grant_type=authorization_code")
    openid = json.loads(r.text)["openid"]
    return HttpResponse(openid)


