# qwerty123
import yagmail

# 连接邮箱服务器
yag = yagmail.SMTP(user="wuyongqiang2012@163.com", password="qwerty123", host="smtp.163.com")

# 邮箱正文
NAME = '武勇强'
PHONE = 11111111111
ADDR = '金地格林格林小区'
contents = f"<table><tr><td>姓名：{NAME}</td></tr><tr><td>电话：{PHONE}</td></tr><tr><td>小区：{ADDR}</td></tr></table>"

# 给多个人发送邮件,并发送附件
yag.send(['454381958@qq.com'], '新的预约消息', contents)