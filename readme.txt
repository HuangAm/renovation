参数含义：
    open_id  # 微信openID
    name   # 客户真实姓名
    nick_name   # 客户微信昵称
    wx_avatar   # 客户微信头像
    reservation_type   # 客户预约类型:风格,设计,报价
    json_info   # 客户预约是提交的信息,手机号在这里面
    reservation_time   # 预约发起时间
    note   # 与客户通话后的备注


项目启动：
    需要进入reversion目录下

数据库表：
    每日播报：json编码后再传，不然会有引号的问题
        [
            {"date":"2019.02.18", "photos":["0.jpg","1.jpg"], "content":"安装地板,地脚线,和瓷砖", 'principal':"杨德明"},
            {"date":"2019.02.20", "photos":["2.jpg","3.jpg"], "content":"装修厨房", 'principal':"杨德明"},
            {"date":"2019.02.20", "photos":["2.jpg","3.jpg"], "content":"装修厨房", 'principal':"杨德明"},
        ]

1. 图片上传
2. 工地增删该查

测试数据：

    预约信息接口测试
        # open_id = "asdfasfdasfdsda"
        # params = dict(
        #     open_id=open_id,
        #     name="wuyongqiang",
        #     nick_name="wuyongqinag",
        #     wx_avatar="https://weixin.com/xx.jpg",
        #     reservation_type="推荐装修风格",
        #     json_info='{"name":"武勇强","address":"通州","phone":"17602112290"}',
        #     reservation_time=datetime.datetime.now(),
        #     status=0,
        # )  # test

通过formid发送模板信息
接口(全部为post请求)：
(r"/openid", OpenidHandler),
(r"/is_admin", IsAdminHandler),
(r"/reversion", ReservationHandler),
(r"/construct_site_list", ConstructSiteListHandler),  # 工地分页查看
(r"/construct_site", ConstructSiteHandler),  # 工地查看
(r"/add_construct_site", AddConstructSiteHandler),  # 工地增加
(r"/edit_construct_site", EditConstructSiteHandler),  # 工地修改
(r"/delete_construct_site", DeleteConstructSiteHandler),  # 工地删除
(r"/add_daily_report", AddDailyReport),  # 每日播报增加
(r"/upload", UploadFileHandler),  # 上传文件
(r"/login", BaseHandler),  # 登录
(r"/create_user", AuthCreateHandler),  # 创建用户
/construct_site_list    工地分页查看
/construct_site         工地查看
/add_construct_site     工地增加
/edit_construct_site    工地修改
/delete_construct_site  工地删除
/add_daily_report       每日播报增加
/upload                 上传文件
/login                  登录
/create_user            创建用户

删除工地详情的时候，要把对应的每日播报也删除掉
增加每日播报表，连表查询语句 每日播报增加 删除 编辑 查看(混用)
工地详情查看，查看列表  代码 OK

查看员工详情  OK
详情页员工头像