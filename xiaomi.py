import requests,json,time,base64,binascii,hashlib,datetime,random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

# 随机字符
def random_str(length):
    s = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()-=_+~`{}[]|:<>?/.'
    return ''.join(random.choice(s) for _ in range(length))

# AES加密
def aes_encrypt(key,data):
    iv = '0102030405060708'.encode('utf-8')
    cipher = AES.new(key.encode('utf-8'),AES.MODE_CBC,iv)
    padded_data = pad(data.encode('utf-8'),AES.block_size,style='pkcs7')
    ciphertext = cipher.encrypt(padded_data)
    return base64.b64encode(ciphertext).decode('utf-8')

# RSA加密
def rsa_encrypt(key,data):
    public_key = RSA.import_key(key)
    cipher = PKCS1_v1_5.new(public_key)
    ciphertext = cipher.encrypt(base64.b64encode(data.encode('utf-8')))
    return base64.b64encode(ciphertext).decode('utf-8')

# 获取Token
def get_token():
    key = random_str(16)
    public_key = """-----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArxfNLkuAQ/BYHzkzVwtu
    g+0abmYRBVCEScSzGxJIOsfxVzcuqaKO87H2o2wBcacD3bRHhMjTkhSEqxPjQ/FE
    XuJ1cdbmr3+b3EQR6wf/cYcMx2468/QyVoQ7BADLSPecQhtgGOllkC+cLYN6Md34
    Uii6U+VJf0p0q/saxUTZvhR2ka9fqJ4+6C6cOghIecjMYQNHIaNW+eSKunfFsXVU
    +QfMD0q2EM9wo20aLnos24yDzRjh9HJc6xfr37jRlv1/boG/EABMG9FnTm35xWrV
    R0nw3cpYF7GZg13QicS/ZwEsSd4HyboAruMxJBPvK3Jdr4ZS23bpN0cavWOJsBqZ
    VwIDAQAB
    -----END PUBLIC KEY-----"""
    data = '{"type":0,"startTs":'+str(round(time.time()*1000))+',"endTs":'+str(round(time.time()*1000))+',"env":{"p1":"","p2":"","p3":"","p4":"","p5":"","p6":"","p7":"","p8":"","p9":"","p10":"","p11":"","p12":"","p13":"","p14":"","p15":"","p16":"","p17":"","p18":"","p19":5,"p20":"","p21":"","p22":5,"p23":"","p24":"","p25":"","p26":"","p28":"","p29":"","p30":"","p31":"","p32":"","p33":"","p34":""},"action":{"a1":[],"a2":[],"a3":[],"a4":[],"a5":[],"a6":[],"a7":[],"a8":[],"a9":[],"a10":[],"a11":[],"a12":[],"a13":[],"a14":[]},"force":false,"talkBack":false,"uid":"'+random_str(27)+'","nonce":{"t":'+str(round(time.time()))+',"r":'+str(round(time.time()))+'},"version":"2.0","scene":"GROW_UP_CHECKIN"}'
    s = rsa_encrypt(public_key,key)
    d = aes_encrypt(key,data)
    url='https://verify.sec.xiaomi.com/captcha/v2/data?k=3dc42a135a8d45118034d1ab68213073&locale=zh_CN'
    data={'s':s,'d':d,'a':'GROW_UP_CHECKIN'}
    result = requests.post(url=url,data=data).json()
    if result['msg'] != '参数错误':
        return result['data']['token']

# 用户信息
def info(cookie):
    url = 'https://api.vip.miui.com/mtop/planet/vip/homepage/mineInfo'
    result = requests.get(url=url,cookies=cookie).json()
    print(f'昵称：{result["entity"]["userInfo"]["userName"]} 等级：{result["entity"]["userInfo"]["userGrowLevelInfo"]["showLevel"]} 积分：{result["entity"]["userInfo"]["userGrowLevelInfo"]["point"]} ')

# 签到
def check_in(cookie):
    url = f'https://api.vip.miui.com/mtop/planet/vip/user/getUserCheckinInfo?miui_vip_ph={cookie["miui_vip_ph"]}'
    result = requests.get(url=url,cookies=cookie).json()
    if result['entity']['checkin7DaysDetail'][datetime.date.today().weekday()] == 0:
        url = f'https://api.vip.miui.com/mtop/planet/vip/user/checkinV2'
        data = {'miui_vip_ph':cookie['miui_vip_ph'],'token':get_token()}
        result = requests.post(url=url,cookies=cookie,data=data).json()
        if 'success' not in result['message']:
            print(f'签到失败: {result["message"]}')

# 点赞
def like(cookie):
    url = 'https://api.vip.miui.com/mtop/planet/vip/content/announceThumbUp'
    data = {'postId':'36625780','sign':'36625780','timestamp':int(round(time.time()*1000))}
    requests.get(url=url,cookies=cookie,data=data)

# 浏览帖子
def browse(cookie):
    url = f'https://api.vip.miui.com/mtop/planet/vip/member/addCommunityGrowUpPointByActionV2?miui_vip_ph={cookie["miui_vip_ph"]}'
    for action in ['BROWSE_POST_10S','BROWSE_SPECIAL_PAGES_SPECIAL_PAGE','BROWSE_SPECIAL_PAGES_USER_HOME']:
        data = {'action':action,'miui_vip_ph':cookie['miui_vip_ph']}
        requests.post(url,cookies=cookie,data=data)

# 拔萝卜
def carrot(cookie):
    url ='https://api.vip.miui.com/api/carrot/pull'
    requests.post(url=url,cookies=cookie,params={'miui_vip_ph': cookie['miui_vip_ph']})
    
# 获取cookie
def login(account,password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    Hash = md5.hexdigest()
    sha1 = hashlib.sha1()
    url = 'https://account.xiaomi.com/pass/serviceLoginAuth2'
    headers = {'User-Agent':'Dalvik/2.1.0 (Linux; U; Android 12; Redmi K20 Pro Build/SKQ1.211006.001) APP/xiaomi.vipaccount APPV/231026 MK/UmVkbWkgSzIwIFBybw== SDKV/5.1.0.release.13 PassportSDK/5.1.0.release.15 passport-ui/5.1.0.release.15'}
    data = {'callback':'https://api.vip.miui.com/sts','_json':'true','user':account,'hash':Hash.upper(),'sid':'miui_vip','_sign':'ZJxpm3Q5cu0qDOMkKdWYRPeCwps=','_locale':'zh_CN'}
    Auth = json.loads(requests.post(url=url,headers=headers,data=data).text.replace('&&&START&&&',''))
    if Auth['description'] == '登录验证失败':
        return 'Error'
    sha1.update(('nonce=' + str(Auth['nonce']) + '&' + Auth['ssecurity']).encode('utf-8'))
    clientSign = base64.encodebytes(binascii.a2b_hex(sha1.hexdigest().encode('utf-8'))).decode(encoding='utf-8').strip()
    nurl = Auth['location'] + '&_userIdNeedEncrypt=true&clientSign=' + clientSign
    cookie = requests.utils.dict_from_cookiejar(requests.get(url=nurl).cookies)
    return cookie

# 签到情况
def check_status(cookie):
    url = f'https://api.vip.miui.com/mtop/planet/vip/member/getCheckinPageCakeList?miui_vip_ph={cookie["miui_vip_ph"]}'
    result = requests.get(url=url,cookies=cookie).json()
    for i in result['entity'][2]['data']:
        if i['jumpText'] == '已完成':
            print(i['title'],'√')
        elif i['jumpText'] == '':
            print(i['title'],'×')

# 主程序
def main(account,password):
    for i in range(5):
        cookie = login(account,password)
        if len(cookie) != 0:
            break
        else:
            time.sleep(i)
    if len(cookie) == 0 or cookie == 'Error':
        print(f'{account}：登录失败')
    else:
        for action in ['check_in','like','browse','carrot','check_status']:
            eval(f'{action}(cookie)')

if __name__ == '__main__':
    # 多账号用逗号隔开
    account = ['123456789'] # 账号
    password = ['123456789'] # 密码
    for i in range(len(account)):
        main(account[i],password[i])