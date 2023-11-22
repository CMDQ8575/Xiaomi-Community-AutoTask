import requests,json,time,base64,binascii,hashlib,datetime,random,os,toml
from Crypto.Cipher import AES,PKCS1_v1_5
from Crypto.Util.Padding import pad
from Crypto.PublicKey import RSA
# from get_validate_cv import get_validate
from get_validate_js import get_validate

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

# 获取验证网址
def get_url(uid=None):
    if uid == None:
        uid = random_str(27)
    key = random_str(16)
    public_key = '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArxfNLkuAQ/BYHzkzVwtu\ng+0abmYRBVCEScSzGxJIOsfxVzcuqaKO87H2o2wBcacD3bRHhMjTkhSEqxPjQ/FE\nXuJ1cdbmr3+b3EQR6wf/cYcMx2468/QyVoQ7BADLSPecQhtgGOllkC+cLYN6Md34\nUii6U+VJf0p0q/saxUTZvhR2ka9fqJ4+6C6cOghIecjMYQNHIaNW+eSKunfFsXVU\n+QfMD0q2EM9wo20aLnos24yDzRjh9HJc6xfr37jRlv1/boG/EABMG9FnTm35xWrV\nR0nw3cpYF7GZg13QicS/ZwEsSd4HyboAruMxJBPvK3Jdr4ZS23bpN0cavWOJsBqZ\nVwIDAQAB\n-----END PUBLIC KEY-----'
    data = {'type':0,'startTs':str(round(time.time()*1000)),'endTs':str(round(time.time()*1000)),'env':{'p1':'','p2':'','p3':'','p4':'','p5':'','p6':'','p7':'','p8':'','p9':'','p10':'','p11':'','p12':'','p13':'','p14':'','p15':'','p16':'','p17':'','p18':'','p19':'','p20':'','p21':'','p22':'','p23':'','p24':'','p25':'','p26':'','p28':'','p29':'','p30':'','p31':'','p32':'','p33':'','p34':''},'action':{'a1':[],'a2':[],'a3':[],'a4':[],'a5':[],'a6':[],'a7':[],'a8':[],'a9':[],'a10':[],'a11':[],'a12':[],'a13':[],'a14':[]},'force':False,'talkBack':False,'uid':uid,'nonce':{'t':str(round(time.time())),'r':str(round(time.time()))[::-1]},'version':'2.0','scene':'GROW_UP_CHECKIN'}
    s = rsa_encrypt(public_key,key)
    d = aes_encrypt(key,str(data))
    url='https://verify.sec.xiaomi.com/captcha/v2/data?k=3dc42a135a8d45118034d1ab68213073&locale=zh_CN&_t='+str(round(time.time()*1000))
    data={'s':s,'d':d,'a':'GROW_UP_CHECKIN'}
    result = requests.post(url=url,data=data).json()
    return result['data']['url']

# 获取token
def get_token(uid=None):
    for i in range(10):
        try:
            url = get_url(uid)
            data = url.split('?')[1].split('&')
            result_dict = {}
            for item in data:
                key, value = item.split('=')
                result_dict[key] = value
            e = result_dict['e']
            gt = result_dict['c']
            challenge = result_dict['l']
            challenge,validate = get_validate(gt,challenge)
            url = 'https://verify.sec.xiaomi.com/captcha/v2/gt/dk/verify?k=3dc42a135a8d45118034d1ab68213073&locale=zh_CN&_t='+str(round(time.time()*1000))
            data = f'e={e}&challenge={challenge}&seccode={validate}%7Cjordan'
            headers = {'content-type':'application/x-www-form-urlencoded'}
            result = requests.post(url=url,data=data,headers=headers).json()['data']
            if 'token' in result.keys():
                return result['data']['token']
            else:
                print('获取token失败',result)
        except Exception as e:
            print('获取token失败',e)

# 用户信息
def info(cookie):
    url = 'https://api.vip.miui.com/mtop/planet/vip/homepage/mineInfo'
    result = requests.get(url=url,cookies=cookie).json()
    print('昵称：'+result['entity']['userInfo']['userName']+' 等级：'+result['entity']['userInfo']['userGrowLevelInfo']['showLevel']+' 积分：'+str(result['entity']['userInfo']['userGrowLevelInfo']['point']))

# 签到
def check_in(cookie):
    url = 'https://api.vip.miui.com/mtop/planet/vip/user/getUserCheckinInfo?miui_vip_ph='+cookie['miui_vip_ph']
    result = requests.get(url=url,cookies=cookie).json()
    if result['entity']['checkin7DaysDetail'][datetime.date.today().weekday()] == 0:
        url = f'https://api.vip.miui.com/mtop/planet/vip/user/checkinV2'
        data = {'miui_vip_ph':cookie['miui_vip_ph'],'token':get_token(cookie['cUserId'])}
        result = requests.post(url=url,cookies=cookie,data=data).json()
        if 'success' not in result['message']:
            print('签到失败：'+result['message'])

# 点赞
def like(cookie):
    url = 'https://api.vip.miui.com/mtop/planet/vip/content/announceThumbUp'
    data = {'postId':'36625780','sign':'36625780','timestamp':int(round(time.time()*1000))}
    requests.get(url=url,cookies=cookie,data=data)

# 浏览帖子
def browse(cookie):
    url = 'https://api.vip.miui.com/mtop/planet/vip/member/addCommunityGrowUpPointByActionV2?miui_vip_ph='+cookie['miui_vip_ph']
    for action in ['BROWSE_POST_10S','BROWSE_SPECIAL_PAGES_SPECIAL_PAGE','BROWSE_SPECIAL_PAGES_USER_HOME']:
        data = {'action':action,'miui_vip_ph':cookie['miui_vip_ph']}
        requests.post(url,cookies=cookie,data=data)
        time.sleep(0.5)

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
    if Auth['description'] != '登录验证失败' and 'nonce' in Auth and 'ssecurity' in Auth:
        sha1.update(('nonce=' + str(Auth['nonce']) + '&' + Auth['ssecurity']).encode('utf-8'))
        clientSign = base64.encodebytes(binascii.a2b_hex(sha1.hexdigest().encode('utf-8'))).decode(encoding='utf-8').strip()
        nurl = Auth['location'] + '&_userIdNeedEncrypt=true&clientSign=' + clientSign
        cookie = requests.utils.dict_from_cookiejar(requests.get(url=nurl).cookies)
        if cookie:
            if len(cookie) != 0:
                return cookie

# 签到情况
def check_status(cookie):
    url = 'https://api.vip.miui.com/mtop/planet/vip/member/getCheckinPageCakeList?miui_vip_ph='+cookie['miui_vip_ph']
    result = requests.get(url=url,cookies=cookie).json()
    url = 'https://api.vip.miui.com/mtop/planet/vip/member/getGrowUpPageData?miui_vip_ph='+cookie['miui_vip_ph']
    score_dict = requests.get(url,cookies=cookie).json()
    score_dict = {i['title']:i['jumpText'] for i in score_dict['entity'][-1]['data'][::-1] if i['desc'] == datetime.date.today().strftime('%Y/%m/%d')}
    for i in result['entity'][2]['data']:
        title = i['title'][:4]
        if i['jumpText'] == '已完成':
            if score_dict.get(title):
                print(title,score_dict.get(title))
            else:
                print(title,'√')
        elif i['jumpText'] == '':
            print(title,'×')

# 主程序
def main(accountt=[],password=[]):
    print('Xiaomi Community AutoTask V4')
    print('By:纯梅锭清 github@CMDQ8575') 
    for i in range(len(account)):
        cookie = login(account[i],password[i])
        if cookie:
            for action in ['info','check_in','like','browse','carrot','check_status']:
                name = {'info':'查询信息','check_in':'签到','like':'点赞','browse':'浏览','carrot':'拔萝卜','check_status':'查询状态'}
                try:
                    eval(f'{action}(cookie)')
                except Exception as e:
                    print('任务 ' + name[action] + ' 执行失败',e)
        else:
            print(f'{account[i]}：登录失败')
 
if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__)) # Pyinstaller请注释掉
    if os.path.exists('config.toml'):
        try:
            config = toml.load('config.toml')
            account = config['account']
            password = config['password']
            if account == None or password == None:
                raise Exception()
            if type(account) != list or type(password) != list:
                raise Exception()
            if len(account) != len(password):
                raise Exception()
        except:
            print('配置文件错误')
        else:
            main(account,password)
    else:
        with open('config.toml','w') as f:
            f.write('account=[\'123456789\']\npassword=[\'123456789\']')
        print('首次运行，已生成配置文件：' + os.path.join(os.getcwd(),'config.toml'))