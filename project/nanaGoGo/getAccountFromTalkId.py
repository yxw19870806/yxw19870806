# -*- coding:UTF-8  -*-
"""
7gogo批量获取参与talk的账号
https://7gogo.jp/
@author: hikaru
email: hikaru870806@hotmail.com
如有问题或建议请联系
"""
import os
from common import *

# 存放解析出的账号文件路径
ACCOUNT_ID_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "info/account.data"))


# 根据talk id获取全部参与者
def get_member_from_talk(talk_id):
    talk_index_url = "https://7gogo.jp/%s" % talk_id
    talk_index_response = net.http_request(talk_index_url, method="GET")
    account_list = {}
    if talk_index_response.status != net.HTTP_RETURN_CODE_SUCCEED:
        raise crawler.CrawlerException(crawler.request_failre(talk_index_response.status))
    talk_data_string = tool.find_sub_string(talk_index_response.data, "window.__DEHYDRATED_STATES__ = ", "</script>")
    if not talk_data_string:
        raise crawler.CrawlerException("页面截取talk信息失败\n%s" % talk_index_response.data)
    talk_data = tool.json_decode(talk_data_string)
    if talk_data is None:
        raise crawler.CrawlerException("talk信息加载失败\n%s" % talk_data_string)
    if not crawler.check_sub_key(("page:talk:service:entity:talkMembers",), talk_data):
        raise crawler.CrawlerException("talk信息'page:talk:service:entity:talkMembers'字段不存在\n%s" % talk_data)
    if not crawler.check_sub_key(("members",), talk_data["page:talk:service:entity:talkMembers"]):
        raise crawler.CrawlerException("talk信息'members'字段不存在\n%s" % talk_data)
    for member_info in talk_data["page:talk:service:entity:talkMembers"]["members"]:
        if not crawler.check_sub_key(("userId", "name"), member_info):
            raise crawler.CrawlerException("参与者信息'userId'或'name'字段不存在\n%s" % talk_data)
        account_list[str(member_info["userId"])] = str(member_info["name"].encode("UTF-8")).replace(" ", "")
    return account_list


def main():
    # 存档位置
    save_data_path = crawler.quickly_get_save_data_path()
    save_data = crawler.read_save_data(save_data_path, 0, [])
    account_list =  crawler.read_save_data(ACCOUNT_ID_FILE_PATH, 0, []).keys()
    for talk_id in save_data:
        try:
            member_list = get_member_from_talk(talk_id)
        except crawler.CrawlerException, e:
            output.print_msg(talk_id + " 获取成员失败，原因：%s" % e.message)
            continue
        for account_id in member_list:
            if account_id not in account_list:
                output.print_msg("%s %s" % (account_id, member_list[account_id]))
                tool.write_file("%s\t%s" % (account_id, member_list[account_id]), ACCOUNT_ID_FILE_PATH)
                account_list.append(account_id)


if __name__ == "__main__":
    main()
