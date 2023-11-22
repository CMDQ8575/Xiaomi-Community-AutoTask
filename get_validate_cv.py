import execjs,cv2,requests,time,json,random,os
from PIL import Image
# 下载图片
def download(url,save_path):
    response = requests.get(url)
    with open(save_path,'wb') as file:
        file.write(response.content)

# 清除验证码空白
def clear_white(img_path):
    img = cv2.imread(img_path)
    rows,cols,channel = img.shape
    min_x = 255
    min_y = 255
    max_x = 0
    max_y = 0
    for x in range(1,rows):
        for y in range(1,cols):
            t = set(img[x,y])
            if len(t) >= 2:
                if x <= min_x:
                    min_x = x
                elif x >= max_x:
                    max_x = x
                if y <= min_y:
                    min_y = y
                elif y >= max_y:
                    max_y = y
    return img[min_x:max_x,min_y: max_y]

# 缺口匹配
def template_match(tpl=None,target=None,out=None):
    th,tw = tpl.shape[:2]
    result = cv2.matchTemplate(target,tpl,cv2.TM_CCOEFF_NORMED)
    min_val,max_val,min_loc,max_loc = cv2.minMaxLoc(result)
    tl = max_loc
    br = (tl[0] + tw,tl[1] + th)
    cv2.rectangle(target,tl,br,(0,0,255),2)
    cv2.imwrite(out,target)
    return tl[0]

# 验证码图片处理
def restore_picture():
    img_list = ['./img/oldbg.png','./img/oldallbg.png']
    for index,img in enumerate(img_list):
        image = Image.open(img)
        s = Image.new('RGBA',(260,160))
        ut = [39,38,48,49,41,40,46,47,35,34,50,51,33,32,28,29,27,26,36,37,31,30,44,45,43,42,12,13,23,22,14,15,21,20,8,9,25,24,6,7,3,2,0,1,11,10,4,5,19,18,16,17]
        height_half = 80
        for inx in range(52):
            c = ut[inx] % 26 * 12 + 1
            u = height_half if ut[inx] > 25 else 0
            l_ = image.crop(box=(c,u,c + 10,u + 80))
            s.paste(l_,box=(inx % 26 * 10,80 if inx > 25 else 0))
        if index == 0:
            s.save('./img/bg.png')
        else:
            s.save('./img/newallbg.png')

# 获取长度
def get_distance():
    restore_picture()
    img1 = clear_white('./img/slide.png')
    img1 = cv2.cvtColor(img1,cv2.COLOR_RGB2GRAY)
    slide = cv2.Canny(img1,100,200)
    back = cv2.imread('./img/bg.png',0)
    back = cv2.Canny(back,100,200)
    slide_pic = cv2.cvtColor(slide,cv2.COLOR_GRAY2RGB)
    back_pic = cv2.cvtColor(back,cv2.COLOR_GRAY2RGB)
    return template_match(slide_pic,back_pic,'./img/show_image.png')

# 路径生成
def get_trace(distance):
    slide_trace = [[random.randint(-50, -10), random.randint(-50, -10), 0],[0, 0, 0]]
    count = 30 + int(distance / 2)
    t = random.randint(50, 100)
    for i in range(count):
        sep = i/count
        if i/count == 1:
            j = i/count
        else:
            j = 1- pow(2,-10*i/count)
        x = round(j*distance)
        t += random.randint(10, 20)
        if x == 0:
            continue
        slide_trace.append([x, 0, t])
    slide_trace.append(slide_trace[-1])
    return slide_trace

# 获取验证图片
def get_image(gt,challenge):
    os.makedirs('img',exist_ok=True)
    res = requests.get('https://api.geetest.com/ajax.php?gt='+gt+'&challenge='+challenge+'&lang=zh-cn&pt=0&w=&callback=geetest_'+str(round(time.time() * 1000))).text
    url = 'https://api.geetest.com/get.php?is_next=true&type=slide3&gt='+gt+'&challenge='+challenge+'&lang=zh-cn&https=true&protocol=https%3A%2F%2F&offline=false&product=embed&api_server=api.geetest.com&isPC=true&autoReset=true&width=100%25&callback=geetest_'+str(round(time.time() * 1000))
    res = requests.get(url).text
    res = json.loads(res[res.index('(')+1:res.rindex(')')])
    challenge = res['challenge']
    s = res['s']
    download('https://static.geetest.com/'+res['fullbg'],'img/oldallbg.png')
    download('https://static.geetest.com/'+res['bg'],'img/oldbg.png')
    download('https://static.geetest.com/'+res['slice'],'img/slide.png')
    distance = get_distance()
    track = get_trace(distance-5)
    return gt,challenge,s,distance,track

# 获取验证码
def get_validate(gt,challenge):
    gt,challenge,s,distance,track = get_image(gt,challenge)
    with open('geetest.js') as f:
        js = execjs.compile(f.read())
    passtime = track[-1][-1]
    track = js.call('get_encode_trace',track,s)
    o = js.call('get_o',distance - 5,track,challenge,challenge[:32],passtime,str(random.randint(100,200)),gt)
    w = js.call('get_w',json.dumps(o))
    url = 'https://api.geetest.com/ajax.php?gt='+gt+'&challenge='+challenge+'&lang=zh-cn&pt=0&w='+w+'&callback=geetest_'+str(round(time.time() * 1000))
    res = requests.get(url).text
    result = json.loads(res[res.index('(')+1:res.rindex(')')])
    if 'validate' in result.keys():
        return challenge,result['validate']
    else:
        raise Exception('Get validate failed')