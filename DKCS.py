import hashlib
import requests
import json
import urllib
import hashlib
import configparser
from datetime import datetime,timedelta  
import sys
config = configparser.ConfigParser()
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0'
}

# 检查参数.ini文件是否存在
def check_config_file():
    config_file_path = '参数.ini'
    try:
        with open(config_file_path, 'r', encoding='utf-8') as file:
            config.read_file(file)  # 从文件对象中读取配置
            # 这里可以添加额外的检查来验证配置的正确性
            # 例如：验证是否所有必需的键都存在且不为空
            if 'Parameters' not in config or not all(key in config['Parameters'] for key in ['ipone', 'password', 'address', 'lngLat', 'device', '上班时间', '下班时间']):
                raise ValueError("配置文件缺少必需的键或节。")
        print("配置文件存在且格式正确。")
        return True
    except FileNotFoundError:
        print(f"配置文件 {config_file_path} 不存在。")
        return False
    except ValueError as e:
        print(f"配置文件格式错误：{e}")
        return False
    except Exception as e:
        print(f"读取配置文件时发生错误：{e}")
        return False
def 创建():
    # 配置文件的路径
    config_file_path = '参数.ini'
    
    # 创建配置解析器
    config = configparser.ConfigParser()
    
    # 定义要写入配置文件的键值对
    params = {
        'ipone': '账号',        # 请替换为实际的账号
        'password': '密码',     # 请替换为实际的密码
        'address': '地点名全称', # 请替换为实际的地点名
        'lnglat': '119.123456,29.123456', # 请替换为实际的经纬度
        'device': '手机设备名例如：iPhone 16 Pro Max', # 请替换为实际的设备名
        '上班时间': '8:00',            # 上班为1，下班为2，这里设置为1作为默认
        '下班时间': '18:00'              # 上班为1，下班为2，这里设置为1作为默认
    }
    
    # 将键值对写入[Parameters]部分
    config['Parameters'] = params
    
    # 将配置写入文件
    with open(config_file_path, 'w', encoding='utf-8') as configfile:
        config.write(configfile)
# 加密参数函数
def encrypt_params(all_params):
    sorted_keys = sorted(all_params.keys())
    paramString = ''.join([f'[{key}={all_params[key]}]' for key in sorted_keys])
    paramString = paramString + '[Ou3xsbXu8_yir2ekEP]'
    md5_hash = hashlib.md5(paramString.encode()).hexdigest()
    return md5_hash
 
# 生成msign的函数（需要uid和deptId作为参数）
def generate_msign(uid, deptId):
    random_str = f"{uid}{deptId}"  # 生成随机字符串（这里简单拼接了uid和deptId）
    md5_hash = hashlib.md5(random_str.encode()).hexdigest()
    return md5_hash
 
# 登录函数
def login_post(username, password, schoolid=None):
    session = requests.Session()
    password = urllib.parse.quote(password)
    url = f'http://passport2.chaoxing.com/api/login?name={username}&pwd={password}&schoolid={schoolid or ""}&verify=0'
    r = session.post(url, headers=header, verify=True, allow_redirects=False)
    if r.status_code == 200:
        user_info = json.loads(r.text)
        return session, user_info['realname'], user_info.get('schoolid'), user_info['uid']
    else:
        print(f"登录失败。状态码: {r.status_code}")
        return None, None, None, None
def login(username, password):
    # 创建会话对象
    session = requests.Session()
    # 登录API URL
    url = 'https://passport2-api.chaoxing.com/v11/loginregister'
    # 构造登录请求数据
    data = {
        "cx_xxt_passport": "json",
        "roleSelect": "true",
        "uname": username,
        "code": password,
        "loginType": "1",
    }
    password=urllib.parse.quote(password)
    # 发送登录请求
    response = session.get(url, params=data,headers=header,verify=True,allow_redirects=False)
    # 解析响应结果
    account = response.json()
    mes = account.get('mes')
    return mes
# 获取deptId的函数
def login_get(session):
    url = 'https://sso.chaoxing.com/apis/login/userLogin4Uname.do?ft=true'
    r = session.get(url, headers=header, verify=True)
    if r.status_code == 200:
        user = json.loads(r.text)
        try:
            ppfid = user['msg'].get('ppfid')  # 注意：这里可能是错误的键名，应根据实际API响应调整
            return ppfid  # 但通常我们可能需要的是deptId或其他信息
        except KeyError as e:
            print(f"键错误: {e}")
            return None
    else:
        print(f"获取登录信息失败。状态码: {r.status_code}")
        return None
def yanzheng(deptId,lngLat,datetime,enc):
    url='https://supportoffice.chaoxing.com/api/apps/punch/user/validate'
    YZ={'deptId':deptId,
    'wifiMac':'',
    'latLng':lngLat,
    'datetime':datetime,
    'sign':'officeApp',
    'enc':enc
    }
    req=session.post(url,data=YZ,headers=header)
    print(req.text)


def kaoqin_post(deptId,uid,device,msign,duty,seq,address,lngLat,datetime,enc2):
    url='https://supportoffice.chaoxing.com/api/apps/punch/user/add'
    data={
        "deptId": deptId,
        "uid": uid,
        "device": device,
        "msign": msign,
        "duty": duty,
        "seq": seq,
        "address": address,
        "automatic": "0",
        "code": "0",
        "remark": "",
        "objectId": "",
        "lngLat":lngLat,
        "wifiName": "",
        "wifiMac": "",
        "datetime": datetime,
        "sign": "officeApp",
        'enc':enc2
    }
    req=session.post(url,data=data,headers=header)
    print(req.text)
def enc(deptId,lngLat,datetime):
    YZ={'deptId':deptId,
    'wifiMac':'',
    'latLng':lngLat,
    'datetime':datetime,
    'sign':'officeApp',
    }
    return encrypt_params(YZ)
def SXB(shangban, xiaban):
    now = datetime.now()
    # 提取当前时间的时和分
    current_time = now.time()
    
    # 将上班和下班时间转换为time对象
    shangban_time = datetime.strptime(shangban, '%H:%M').time()
    xiaban_time = datetime.strptime(xiaban, '%H:%M').time()
    
    # 将当前时间、上班时间和下班时间转换为datetime对象以便进行时间比较
    current_datetime = now
    shangban_datetime = datetime.combine(now.date(), datetime.strptime(shangban, '%H:%M').time())
    xiaban_datetime = datetime.combine(now.date(), datetime.strptime(xiaban, '%H:%M').time())
    # 设置时间范围（前后一小时）
    time_range_start = timedelta(hours=-1)
    time_range_end = timedelta(hours=1)
    # 比较当前时间与上班和下班时间（考虑时间范围）
    if (shangban_datetime + time_range_start <= current_datetime <= shangban_datetime + time_range_end):
        return 1, 1  # 在上班时间范围内
    elif (xiaban_datetime + time_range_start <= current_datetime <= xiaban_datetime + time_range_end):
        return 2, 2  # 在下班时间范围内
    else:
        print('不在设置的打卡时间内。')
        sys.exit(0)  # 直接退出程序，不返回任何值
def enc2(deptId,uid,device,msign,address,lngLat,datetime):
    DK={
            "deptId":deptId,
            "uid": uid,
            "device": device,
            "msign": msign,
            "duty": duty,
            "seq": seq,
            "address": address,
            "automatic": "0",
            "code": "0",
            "remark": "",
            "objectId": "",
            "lngLat":lngLat,
            "wifiName": "",
            "wifiMac": "",
            "datetime":datetime_str,
            "sign": "officeApp"
            }
    return encrypt_params(DK)
def lngLat():
    lngLat = config['Parameters']['lngLat']
    lngLat = lngLat.replace('，', ',')
    parts = lngLat.split(',')
    flipped = ','.join([parts[1], parts[0]])
    return flipped
if __name__ == "__main__":
    if not check_config_file():
        print("配置文件不存在，正在创建...")
        创建()
        input("请配置好参数.ini文件后重新启动程序")
        # 可以选择在这里再次检查配置文件，或者让用户手动触发脚本运行
    else:
        # 从配置文件中读取参数
        config.read('参数.ini', encoding='utf-8')
        username = config['Parameters']['ipone']
        password = config['Parameters']['password']
        address = config['Parameters']['address']
        lngLat = lngLat()
        device = config['Parameters']['device']
        shangban = config['Parameters']['上班时间']
        xiaban = config['Parameters']['下班时间']
        # duty,seq=SXB(shangban,xiaban)
        duty,seq=2,2
        # print(duty,seq)
        print(username,password,address,lngLat,device,shangban,xiaban)
        mes = login(username, password)
        if mes == "验证通过":
            print("登录成功")
            # 登录并获取session及用户信息
            session, realname, schoolid, uid = login_post(username, password)
            # 获取deptId（这里假设login_get返回的是我们需要的deptId）
            deptId = login_get(session)
            if not deptId:
                print("无法获取deptId，无法继续。")
                exit(1)
            # 生成当前时间字符串
            now = datetime.now()
            datetime_str = now.strftime("%Y%m%d%H")
            # 生成msign
            msign = generate_msign(uid, deptId)
            # 加密参数（用于后续请求）
            enc=enc(deptId,lngLat,datetime_str)
            enc2=enc2(deptId,uid,device,msign,address,lngLat,datetime_str)
            yanzheng(deptId, lngLat, datetime_str, enc)
            kaoqin_post(deptId,uid,device,msign,duty,seq,address,lngLat,datetime_str,enc2)
            input("按任意键退出")
        else:
            print(mes)
            input("按任意键退出")
            sys.exit(1)
