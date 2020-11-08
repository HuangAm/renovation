import unittest


class TestReservation(unittest.TestCase):
    def test_wxauth(self):
        import requests
        APPID = 'wx5197a8451ac55b3a'
        SECRET = '609a14992f0c98e4dcf92622e0a2d9c3'
        JSCODE = '071TqY1a2RcRmM09MXZ92Iuo2a2TqY1T'
        url = f"https://api.weixin.qq.com/sns/jscode2session?appid={APPID}&secret={SECRET}&js_code={JSCODE}&grant_type=authorization_code"
        res = requests.get(url)
        print(res.text)

    def test_mysel_limit(self):
        from database.sqlalchemyconn import session, Reservation, Users
        # # 查询
        # obj = session.query(Reservation.id,Reservation.reservation_time).order_by(Reservation.id.desc()).first()[1]
        # a,b = session.query(Reservation.name,Reservation.garden_name).filter_by(id=1).first()
        b = session.query(Users.name).filter_by(openid='').first()
        print(b)
        # print(obj)
        # print(obj[15*0:15*1])
        # print(obj[15*1:15*2])
        # print(obj[15*1:15*2])
        # x = session.query(Reservation).filter(id=227).delete()
        # session.commit()
        # session.close()
        # # 删除
        # x = session.query(Reservation).filter_by(id=226).delete()
        # session.commit()
        # session.close()
        # print(x)
        # # 修改
        # obj = session.query(Reservation.json_info).filter_by(id=225).first()[0]
        # session.close()
        # print(obj)

    def test_json(self):
        import json
        daily_report = [
            {"date": "2019.02.18", "photos": ["0.jpg", "1.jpg"], "content": "安装地板,地脚线,和瓷砖", 'principal': "杨德明"},
            {"date": "2019.02.20", "photos": ["2.jpg", "3.jpg"], "content": "装修厨房", 'principal': "杨德明"},
        ]
        j = json.dumps(daily_report)
        print(j)
