import execjs,requests,time,json,random,os
from PIL import Image
# 验证码图片处理
def restore_picture():
    image = Image.open('bg.png')
    s = Image.new('RGBA',(260,160))
    ut = [39,38,48,49,41,40,46,47,35,34,50,51,33,32,28,29,27,26,36,37,31,30,44,45,43,42,12,13,23,22,14,15,21,20,8,9,25,24,6,7,3,2,0,1,11,10,4,5,19,18,16,17]
    height_half = 80
    for inx in range(52):
        c = ut[inx] % 26 * 12 + 1
        u = height_half if ut[inx] > 25 else 0
        l_ = image.crop(box=(c,u,c + 10,u + 80))
        s.paste(l_,box=(inx % 26 * 10,80 if inx > 25 else 0))
    s.save('bg.png')

# 获取长度
def get_distance():
    with open('gap.js') as f:
        js = execjs.compile(f.read())
    image = Image.open('bg.png').convert('RGBA')
    w,h = image.size
    pixels = []
    for pixel in image.getdata():
        pixels.extend(pixel)
    return js.call('solve',pixels,w,h)

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
    res = requests.get('https://api.geetest.com/ajax.php?gt='+gt+'&challenge='+challenge+'&lang=zh-cn&pt=0&w=&callback=geetest_'+str(round(time.time() * 1000)))
    url = 'https://api.geetest.com/get.php?is_next=true&type=slide3&gt='+gt+'&challenge='+challenge+'&lang=zh-cn&https=true&protocol=https%3A%2F%2F&product=embed&api_server=api.geevisit.com&isPC=true&autoReset=true&width=100%25&callback=geetest_'+str(round(time.time() * 1000))
    res = requests.get(url).text
    res = json.loads(res[res.index('(')+1:res.rindex(')')])
    challenge = res['challenge']
    s = res['s']
    response = requests.get('https://static.geetest.com/'+res['bg'])
    with open('bg.png','wb') as file:
        file.write(response.content)
    restore_picture()
    distance = get_distance()
    track = get_trace(distance-5)
    os.remove('bg.png')
    return gt,challenge,s,distance,track

# 获取验证码
def get_validate(gt=None,challenge=None):
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