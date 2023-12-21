from oci.config import from_file
from oci.signer import Signer
from PushMsg import wechat
from time import sleep
import requests, os, json

config = from_file(file_location='~/.oci/config.prod', profile_name='ADMIN')
auth = Signer(
    tenancy=config['tenancy'],
    user=config['user'],
    fingerprint=config['fingerprint'],
    private_key_file_location=config['key_file'],
    pass_phrase=config['pass_phrase']
)

def launch_compute_instance(infile):
    url = 'https://iaas.ap-singapore-1.oraclecloud.com/20160918/instances/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    with open(file=infile, mode='r', encoding='utf-8') as f:
        fo = f.read()
    response = requests.post(url=url, headers=headers, data=fo, auth=auth).status_code
    return response

def access_token(cache_dir, cfg):
    ldcfg = wechat.LoadConfig()
    wxcfg = ldcfg.loadcfg(cfg_path=cfg)
    wx_get_token = wechat.GetAccessToken(corpid=wxcfg['corpid'], secret=wxcfg['corpsecret'])
    wx_file_io = wechat.AccessTokenRd()
    wx_file_validtor = wechat.FileValidtor()
    wx_time_validtor = wechat.TimeValidtor()
    token_file = os.path.join(cache_dir, 'token.db')
    def token_validtor():
        if not os.path.exists(cache_dir):
            os.mkdir(cache_dir)
        if not os.path.exists(token_file):
            wx_file_io.writting(token_file, json.dumps(wx_get_token.access_token))
        if wx_time_validtor.is_valid(token_file):
            wx_file_io.writting(token_file, json.dumps(wx_get_token.access_token))
        if not wx_file_validtor.is_valid(token_file):
            raise Exception(f'Token file reading error, please check or delete the token file and obtain it again')
        with open(file=token_file, mode='r', encoding='utf-8') as f:
            origin = f.read()
        result = json.loads(origin)
        return result['access_token']
    return token_validtor()
    

if __name__ == '__main__':
    fileValid = wechat.FileValidtor()
    timeValid = wechat.TimeValidtor()
    ldcfg = wechat.LoadConfig()
    cfg = ldcfg.loadcfg(cfg_path='/Users/alex/.oci/MSG/wxcfg.json')
    send_msg = wechat.TextMessage()
    rqst_token = access_token(cache_dir='/Users/alex/.oci/MSG/cache', cfg='/Users/alex/.oci/MSG/wxcfg.json')
    rqst_instance_result = launch_compute_instance(infile='/Users/alex/.oci/CONFIG/instance.cfg')
    msg_text = f'\t\t抢占成功\n\n返回结果: {rqst_instance_result}\n请求令牌: {rqst_token}\n文件校验: {fileValid.is_valid(infile="/Users/alex/.oci/MSG/cache/token.db")}\n时间校验: {timeValid.is_valid(in_file="/Users/alex/.oci/MSG/cache")}'
    while True:
        if rqst_instance_result == 200:
            print(send_msg.push_message(access_token=rqst_token,
                                        agent_id=cfg['agentid'],
                                        to_who=cfg['users'],
                                        message_content=msg_text))
            break
        print(rqst_instance_result)
        sleep(15)