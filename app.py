import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.options
from database.sqlalchemyconn import Reservation, ConstructSite, Users, DailyReport, session
from log.gen_logger import logger
import datetime
import traceback
import json
import os
from tornado.options import define, options
import requests
import yagmail

define("port", default=8888, help="run on the given port", type=int)


def try_except(func):
    """
    日志装饰器
    """

    def handle_problems(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception:
            session.close()
            logger.error(traceback.format_exc())

    return handle_problems


class BaseHandler(tornado.web.RequestHandler):
    """没啥用"""

    def options(self, *args, **kwargs):
        pass


class UserListHandler(BaseHandler):
    @try_except
    def post(self, *args, **kwargs):
        """查看员工列表"""
        objs = session.query(Users).filter_by(openid="openid").all()
        res_list = []
        for obj in objs:
            res = {}
            res["user_id"] = obj.id
            res["name"] = obj.name
            res["position"] = obj.position
            res["email"] = obj.email
            res["avatar"] = obj.avatar
            res["openid"] = obj.openid
            res["phone"] = obj.phone
            res_list.append(res)
        self.write({"status": 1, "data": res_list})


class UserHandler(BaseHandler):
    @try_except
    def post(self, *args, **kwargs):
        """查看员工详情"""
        user_id = self.get_argument("user_id", None)
        if user_id:
            obj = session.query(Users).filter_by(id=user_id).first()
            res = {
                "user_id": obj.id,
                "name": obj.name,
                "position": obj.position,
                "email": obj.email,
                "avatar": obj.avatar,
                "openid": obj.openid,
                "phone": obj.phone,
            }
            self.write({"status": 1, "data": res})
        else:
            self.write({"status": 2, "message": "UserHandler user_id is None!"})


class AddUserHandler(BaseHandler):
    @try_except
    def post(self, *args, **kwargs):
        """新增员工, 不能写入open_id，此时的open_id是老板的"""
        params = dict(
            name=self.get_argument("name", None),
            position=self.get_argument("position", None),
            email=self.get_argument("email", None),
            avatar=self.get_argument("avatar", None),
            openid="openid",
            phone=self.get_argument("phone", None)
        )
        obj = Users(**params)
        session.add(obj)
        session.commit()
        user_id = obj.id
        session.close()
        self.write({"status": 1, "data": {"user_id": user_id}})


class EditUserHandler(BaseHandler):
    @try_except
    def post(self, *args, **kwargs):
        """编辑员工"""
        user_id = self.get_argument("user_id", None)
        if user_id:
            params = dict(
                name=self.get_argument("name", None),
                position=self.get_argument("password", None),
                email=self.get_argument("email", None),
                avatar=self.get_argument("avatar", None),
                openid=self.get_argument("openid", None),
                phone=self.get_argument("phone", None)
            )
            session.query(Users).filter_by(id=user_id).update(params)
            session.commit()
            session.close()
            self.write({"status": 1, "data": "update user success!"})
        else:
            self.write({"status": 2, "message": "EditUserHandler user_id is None!"})


class DeleteUserHandler(BaseHandler):
    def post(self, *args, **kwargs):
        """删除员工列表"""
        user_id = self.get_argument("user_id", None)
        if user_id:
            session.query(Users).filter_by(id=user_id).delete()
            self.write({"status": 1, "data": "delete user success!"})
        else:
            self.write({"status": 2, "message": "DeleteUserHandler user_id is None!"})


class OpenidHandler(BaseHandler):
    @try_except
    def post(self, *args, **kwargs):
        """通过code去微信服务器获取openid"""
        js_code = self.get_argument("code", None)
        if js_code:
            appid = "wx5197a8451ac55b3a"
            secret = "609a14992f0c98e4dcf92622e0a2d9c3"
            js_code = js_code
            response = requests.get(
                "https://api.weixin.qq.com/sns/jscode2session?appid=%s&secret=%s&js_code=%s&grant_type=authorization_code" % (
                    appid, secret, js_code))
            # {"session_key":"mM1fWC4FrEe+1DeZccZMTg==","expires_in":7200,"openid":"obbfs0J4Brt-_a_MFLOq25lJdkr8"}
            ret = json.loads(response.text)
            errmsg = ret.get("errmsg", None)
            openid = ret.get("openid", None)
            if errmsg:
                self.write({"status": 0, "message": errmsg})
            if openid:
                self.write({"status": 1, "data": {"openid": openid}})


class IsAdminHandler(BaseHandler):
    @try_except
    def post(self, *args, **kwargs):
        """通过openid判断是不是admin"""
        openid = self.get_argument("openid", None)
        obj = session.query(Users).filter_by(openid=openid).first()
        session.close()
        if obj:
            self.write({"status": 1, "data": {"is_admin": "Y"}})
        else:
            self.write({"status": 1, "data": {"is_admin": "N"}})


class ReservationHandler(BaseHandler):
    @try_except
    def post(self):
        """
        将收到的预约信息存入数据库,并通知后台
        :return:
        """
        name = self.get_argument("name", None)
        garden_name = self.get_argument("garden_name", None)
        phone = self.get_argument("phone", None)
        params = dict(
            openid=self.get_argument("openid", None),
            name=name,
            garden_name=garden_name,
            phone=phone,
            reservation_time=datetime.datetime.now(),
            status=0,
        )
        obj = Reservation(**params)
        session.add(obj)
        session.commit()
        reservation_id = obj.id
        session.close()
        self.write({"status": 1, "data": reservation_id})
        # 发邮件
        yag = yagmail.SMTP(user="wuyongqiang2012@163.com", password="qwerty123", host="smtp.163.com")
        contents = "<table><tr><td>姓名：%s</td></tr><tr><td>电话：%s</td></tr><tr><td>小区：%s</td></tr></table>" % (
            name, phone, garden_name)
        yag.send(["djjm188@163.com"], "新的预约消息", contents)


class ConstructSiteHandler(BaseHandler):
    @try_except
    def post(self, *args, **kwargs):
        """
        查看工地详情
        :param cs_id: 工地id
        :return: 工地详情
        """
        cs_id = self.get_argument("cs_id", None)
        if cs_id:
            obj = session.query(ConstructSite).filter_by(id=cs_id).first()
            leader_name, leader_avatar = session.query(Users.name, Users.avatar).filter_by(id=obj.leader).first()
            designer_name, designer_avatar = session.query(Users.name, Users.avatar).filter_by(id=obj.designer).first()
            headman_name, headman_avatar = session.query(Users.name, Users.avatar).filter_by(id=obj.headman).first()
            supervisor_name, supervisor_avatar = session.query(Users.name, Users.avatar).filter_by(
                id=obj.supervisor).first()
            if obj:
                res = {
                    "id": obj.id,
                    "top_banner": obj.top_banner,
                    "construct_site_addr": obj.construct_site_addr,
                    "employer_name": obj.employer_name,
                    "sex": obj.sex,
                    "construct_start_time": obj.construct_start_time,
                    "area": obj.area,
                    "house_type": obj.house_type,
                    "style": obj.style,
                    "leader": {"user_id": obj.leader, "name": leader_name, "avatar": leader_avatar},
                    "designer": {"user_id": obj.designer, "name": designer_name, "avatar": designer_avatar},
                    "headman": {"user_id": obj.headman, "name": headman_name, "avatar": headman_avatar},
                    "supervisor": {"user_id": obj.supervisor, "name": supervisor_name, "avatar": supervisor_avatar},
                    "progress": obj.progress,
                    "create_time": str(obj.create_time)
                }
                report_objs = session.query(DailyReport).filter_by(cs_id=cs_id).order_by(DailyReport.id.desc()).all()
                daily_report_list = []
                for report_obj in report_objs:
                    report_dic = {}
                    report_dic["id"] = report_obj.id
                    report_dic["date"] = report_obj.date
                    report_dic["photos"] = report_obj.photos
                    report_dic["content"] = report_obj.content
                    report_dic["principal"] = report_obj.principal
                    report_dic["work_status"] = report_obj.work_status
                    report_dic["stop_reason"] = report_obj.stop_reason
                    report_dic["cs_id"] = report_obj.cs_id
                    daily_report_list.append(report_dic)
                res["daily_report_list"] = daily_report_list
                session.close()
                self.write({"status": 1, "data": res})
            else:
                self.write({"status": 1, "data": None})
        else:
            self.write({"status": 2, "message": "cs_id is must param!"})


class AddConstructSiteHandler(BaseHandler):
    @try_except
    def post(self):
        """创建工地详情"""
        params = dict(
            top_banner=self.get_argument("top_banner", None),
            construct_site_addr=self.get_argument("construct_site_addr", None),
            employer_name=self.get_argument("employer_name", None),
            sex=self.get_argument("sex", "1"),
            construct_start_time=self.get_argument("construct_start_time", None),
            area=self.get_argument("area", None),
            house_type=self.get_argument("house_type", None),
            style=self.get_argument("style", None),
            leader=self.get_argument("leader", None),
            designer=self.get_argument("designer", None),
            headman=self.get_argument("headman", None),
            supervisor=self.get_argument("supervisor", None),
            progress=self.get_argument("progress", None),
            create_time=datetime.datetime.now()
        )
        obj = ConstructSite(**params)
        session.add(obj)
        session.commit()
        cs_id = obj.id
        session.close()
        self.write({"status": 1, "data": {"cs_id": cs_id}})


class EditConstructSiteHandler(BaseHandler):
    @try_except
    def post(self, *args, **kwargs):
        """修改工地详情"""
        cs_id = self.get_argument("cs_id", None)
        if cs_id:
            params = dict(
                top_banner=self.get_argument("top_banner", None),
                construct_site_addr=self.get_argument("construct_site_addr", None),
                employer_name=self.get_argument("employer_name", None),
                construct_start_time=self.get_argument("construct_start_time", None),
                area=self.get_argument("area", None),
                house_type=self.get_argument("house_type", None),
                style=self.get_argument("style", None),
                leader=self.get_argument("leader", None),
                designer=self.get_argument("designer", None),
                headman=self.get_argument("headman", None),
                supervisor=self.get_argument("supervisor", None),
                progress=self.get_argument("progress", None),
            )
            session.query(ConstructSite).filter_by(id=cs_id).update(params)
            session.commit()
            session.close()
            self.write({"status": 1, "data": "update construct_site success!"})
        else:
            self.write({"status": 2, "message": "cs_id is must param!"})


class DeleteConstructSiteHandler(BaseHandler):
    @try_except
    def post(self, *args, **kwargs):
        """删除工地信息"""
        cs_id = self.get_argument("cs_id", None)
        if cs_id:
            res = session.query(ConstructSite).filter_by(id=cs_id).delete()
            session.query(DailyReport).filter_by(cs_id=cs_id).delete()  # 删除对应的每日播报
            session.commit()
            session.close()
            if res:
                self.write({"status": 1, "data": "delete success!"})
            else:
                self.write({"status": 2, "message": "delete fail!"})
        else:
            self.write({"status": 2, "message": "cs_id is must param!"})


class ConstructSiteListHandler(BaseHandler):
    @try_except
    def post(self, *args, **kwargs):
        """
        分页查看工地列表，每页15条，对应工地播报
        :return: 头图片地址，房间名称，房间布局(例:3室一厅)，房间面积(例:面积：104m^2)
        """
        page_num = self.get_argument("page_num", None)  # 如果传了页码就只给该页数据,否则全给
        if page_num:
            if page_num.isdigit():
                page_num = int(page_num)
                objs = session.query(ConstructSite).order_by(ConstructSite.id.desc())[
                    15 * (page_num - 1), 15 * page_num]
                res_list = []
                for obj in objs:
                    res = {}
                    res["cs_id"] = obj.id
                    res["top_banner"] = obj.top_banner.split(",")[-1]
                    res["construct_site_addr"] = obj.construct_site_addr
                    res["house_type"] = obj.house_type
                    res["area"] = obj.area
                    res_list.append(res)
                session.close()
                self.write({"status": 1, "data": res_list})
            else:
                self.write({"status": 2, "message": "page_num输入错误"})
        else:
            objs = session.query(ConstructSite).order_by(ConstructSite.id.desc()).all()
            res_list = []
            for obj in objs:
                res = {}
                res["cs_id"] = obj.id
                res["top_banner"] = obj.top_banner.split(",")[-1]
                res["construct_site_addr"] = obj.construct_site_addr
                res["house_type"] = obj.house_type
                res["area"] = obj.area
                res_list.append(res)
            session.close()
            self.write({"status": 1, "data": res_list})


class DailyReportHandler(BaseHandler):
    @try_except
    def post(self, *args, **kwargs):
        """查看每日播报详情"""
        daily_report_id = self.get_argument("daily_report_id")
        obj = session.query(DailyReport).filter_by(id=daily_report_id).first()
        session.close()
        if obj:
            res = {
                "date": obj.date,
                "photos": obj.photos,
                "content": obj.content,
                "principal": obj.principal,
                "work_status": obj.work_status,
                "stop_reason": obj.stop_reason,
                "cs_id": obj.cs_id,
            }
            self.write({"status": 1, "data": res})
        else:
            self.write({"status": 1, "data": None})


class AddDailyReportHandler(BaseHandler):
    @try_except
    def post(self, *args, **kwargs):
        """添加每日播报"""
        params = dict(
            date=self.get_argument("date", str(datetime.date.today())),
            photos=self.get_argument("photos", None),
            content=self.get_argument("content", None),
            principal=self.get_argument("principal", None),
            work_status=self.get_argument("work_status", None),
            stop_reason=self.get_argument("stop_reason", None),
            cs_id=self.get_argument("cs_id", None)
        )
        obj = DailyReport(**params)
        session.add(obj)
        session.commit()
        daily_report_id = obj.id
        session.close()
        self.write({"status": 1, "data": {"daily_report_id": daily_report_id}})


class EditDailyReportHandler(BaseHandler):
    @try_except
    def post(self, *args, **kwargs):
        """编辑每日播报"""
        daily_report_id = self.get_argument("daily_report_id", None)
        if daily_report_id:
            params = dict(
                date=self.get_argument("date", str(datetime.date.today())),
                photos=self.get_argument("photos", None),
                content=self.get_argument("content", None),
                principal=self.get_argument("principal", None),
                work_status=self.get_argument("work_status", None),
                stop_reason=self.get_argument("stop_reason", None),
                cs_id=self.get_argument("cs_id", None)
            )
            session.query(DailyReport).filter_by(id=daily_report_id).update(params)
            session.commit()
            session.close()
            self.write({"status": 1, "data": {"daily_report_id": daily_report_id}})
        else:
            self.write({"status": 2, "data": {"message": "EditDailyReportHandler daily_report_id is None!"}})


class DeleteDailyReportHandler(BaseHandler):
    @try_except
    def post(self, *args, **kwargs):
        """删除每日播报"""
        daily_report_id = self.get_argument("daily_report_id", None)
        if daily_report_id:
            session.query(DailyReport).filter_by(id=daily_report_id).delete()
            session.commit()
            session.close()
            self.write({"status": 1, "data": "delete success!"})
        else:
            self.write({"status": 2, "data": {"message": "DeleteDailyReportHandler daily_report_id is None!"}})


class UploadFileHandler(BaseHandler):
    @try_except
    def post(self, *args, **kwargs):
        """
        所有上传操作
        :return: 返回文件url
        """
        upload_path = os.path.join(os.path.dirname(__file__), "static", "imgs")
        file_metas = self.request.files["file"]
        paths = []
        for meta in file_metas:
            file_path = os.path.join(upload_path, meta["filename"])
            with open(file_path, "wb") as up:
                up.write(meta["body"])
            paths.append("/".join(["https://51djzs.cn", "static", "imgs", meta["filename"]]))
        self.write({"status": 1, "data": paths})


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/openid", OpenidHandler),
            (r"/is_admin", IsAdminHandler),
            (r"/reversion", ReservationHandler),
            (r"/construct_site_list", ConstructSiteListHandler),  # 工地分页查看
            (r"/construct_site", ConstructSiteHandler),  # 工地查看,每日播报列表查看
            (r"/add_construct_site", AddConstructSiteHandler),  # 工地增加
            (r"/edit_construct_site", EditConstructSiteHandler),  # 工地修改
            (r"/delete_construct_site", DeleteConstructSiteHandler),  # 工地删除
            (r"/daily_report", DailyReportHandler),  # 每日播报查看
            (r"/add_daily_report", AddDailyReportHandler),  # 每日播报增加
            (r"/edit_daily_report", EditDailyReportHandler),  # 每日播报修改
            (r"/delete_daily_report", DeleteDailyReportHandler),  # 每日播报删除
            (r"/user_list", UserListHandler),  # 查看员工列表
            (r"/user", UserHandler),  # 员工查看
            (r"/add_user", AddUserHandler),  # 员工增加
            (r"/edit_user", EditUserHandler),  # 员工修改
            (r"/delete_user", DeleteUserHandler),  # 员工删除
            (r"/upload", UploadFileHandler),  # 上传文件
            (r"/login", BaseHandler),  # 登录
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
        )
        super(Application, self).__init__(handlers, **settings)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    # http_server = tornado.httpserver.HTTPServer(Application())
    http_server = tornado.httpserver.HTTPServer(Application(), ssl_options={
        "certfile": os.path.join(os.path.dirname(__file__), "keys", "caimouse.crt"),
        "keyfile": os.path.join(os.path.dirname(__file__), "keys", "caimouse.key"),
    })
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
