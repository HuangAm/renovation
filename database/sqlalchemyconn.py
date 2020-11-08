from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, event
from sqlalchemy.exc import DisconnectionError
from sqlalchemy.dialects.mysql import \
    BIGINT, BINARY, BIT, BLOB, BOOLEAN, CHAR, DATE, \
    DATETIME, DECIMAL, DECIMAL, DOUBLE, ENUM, FLOAT, INTEGER, \
    LONGBLOB, LONGTEXT, MEDIUMBLOB, MEDIUMINT, MEDIUMTEXT, NCHAR, \
    NUMERIC, NVARCHAR, REAL, SET, SMALLINT, TEXT, TIME, TIMESTAMP, \
    TINYBLOB, TINYINT, TINYTEXT, VARBINARY, VARCHAR, YEAR

Base = declarative_base()  # 陈述基类,拿到Base基类


# 创建表单,类就是表单,但是在数据库中的表明是__tablename__
# class Reservation(Base):
#
#     __tablename__ = 'reservation'  # 真正的表名
#
#     id = Column(BIGINT, primary_key=True, autoincrement=True)  # 主键
#     open_id = Column(VARCHAR(32), index=True)  # 微信openID
#     name = Column(VARCHAR(32), nullable=True)  # 客户真实姓名
#     nick_name = Column(VARCHAR(32), nullable=True)  # 客户微信昵称
#     wx_avatar = Column(VARCHAR(256), nullable=True)  # 客户微信头像
#     reservation_type = Column(VARCHAR(32), index=True)  # 客户预约类型:风格,设计,报价
#     json_info = Column(VARCHAR(600),)  # 客户预约是提交的信息,手机号在这里面
#     reservation_time = Column(DateTime, nullable=True)  # 预约发起时间
#     status = Column(CHAR(1),)  # 客户预约事件的处理状态{"0":"未处理","1":"处理中","2":"处理完","3":"成单"}
#     deal_time = Column(DateTime, nullable=True)  # 预约处理时间
#     note = Column(VARCHAR(1000), nullable=True)  # 与客户通话后的备注


class Reservation(Base):
    __tablename__ = 'reservation'  # 真正的表名

    id = Column(BIGINT, primary_key=True, autoincrement=True)  # 主键
    openid = Column(VARCHAR(100), index=True)  # 微信openID
    name = Column(VARCHAR(32), )  # 客户真实姓名
    garden_name = Column(VARCHAR(600), )  # 小区名称
    phone = Column(VARCHAR(32))  # 手机号
    reservation_time = Column(DateTime, nullable=True)  # 预约发起时间
    status = Column(CHAR(1), )  # 客户预约事件的处理状态{"0":"未处理","1":"处理中","2":"处理完","3":"成单"}
    deal_time = Column(DateTime, nullable=True)  # 预约处理时间
    note = Column(VARCHAR(1000), nullable=True)  # 与客户通话后的备注


class ConstructSite(Base):
    __tablename__ = 'construct_site'  # 真正的表名

    id = Column(BIGINT, primary_key=True, autoincrement=True)  # 主键
    top_banner = Column(TEXT())  # 详情页顶头图片,例:https://weixin.com/xx.jpg,https://weixin.com/xx.jpg
    construct_site_addr = Column(VARCHAR(256), )  # 工地非详细地址
    employer_name = Column(VARCHAR(32), nullable=True)  # 雇主姓名,例:董先生/女士的家
    sex = Column(VARCHAR(1), nullable=True)  # 男1女0
    construct_start_time = Column(VARCHAR(32), nullable=True)  # 施工时间,例:2019.03.02
    area = Column(VARCHAR(32), nullable=True)  # 面积,例:92.46,默认单位m^2
    house_type = Column(VARCHAR(32), nullable=True)  # 户型,例:2室1厅1卫
    style = Column(VARCHAR(32), nullable=True)  # 风格,例:北欧混搭
    leader = Column(BIGINT, nullable=True)  # 项目负责人id
    designer = Column(BIGINT, nullable=True)  # 设计师id
    headman = Column(BIGINT, nullable=True)  # 工队长id
    supervisor = Column(BIGINT, nullable=True)  # 施工监理id
    progress = Column(CHAR(2), nullable=True)  # 施工进度,目前就只有五步,1-5
    create_time = Column(DateTime, nullable=True)  # 创建时间
    update_time = Column(DateTime, nullable=True)  # 更新时间


class DailyReport(Base):
    __tablename__ = 'daily_report'
    id = Column(BIGINT, primary_key=True, autoincrement=True)  # 主键
    date = Column(VARCHAR(32), nullable=True)  # 施工日期
    photos = Column(TEXT(), nullable=True)  # 施工照片
    content = Column(VARCHAR(600), nullable=True)  # 施工内容
    principal = Column(VARCHAR(32), nullable=True)  # 项目负责人
    work_status = Column(CHAR(1))  # 施工状态 0:停工 1:进行中 2:完工
    stop_reason = Column(VARCHAR(600))  # 停工原因
    cs_id = Column(BIGINT, nullable=True)  # 工地id


class Users(Base):
    __tablename__ = 'users'
    id = Column(BIGINT, primary_key=True, autoincrement=True)  # 主键
    name = Column(VARCHAR(100), unique=True)  # 员工姓名
    position = Column(VARCHAR(100), unique=True)  # 员工职位
    email = Column(VARCHAR(100), nullable=True)  # 员工邮箱
    avatar = Column(VARCHAR(1000), nullable=True)  # 员工头像
    openid = Column(VARCHAR(100), index=True, nullable=True)  # 微信openID
    phone = Column(VARCHAR(32), nullable=True)  # 员工手机号


def checkout_listener(dbapi_con, con_record, con_proxy):
    try:
        try:
            dbapi_con.ping(False)
        except TypeError:
            dbapi_con.ping()
    except dbapi_con.OperationalError as exc:
        if exc.args[0] in (2006, 2013, 2014, 2045, 2055):
            raise DisconnectionError()
        else:
            raise


engine = create_engine("mysql+pymysql://root:@127.0.0.1:3306/reservation?charset=utf8",
                       pool_size=100,
                       pool_recycle=3600)
event.listen(engine, 'checkout', checkout_listener)
Base.metadata.create_all(engine)  # 检测文件中所有继承了Base类的类,在mysqld中建立所有的表,类就是表
Session = sessionmaker(bind=engine)  # 根据对话制造者,绑定引擎,创建出对话类,bind=engine就是socket里面的bind
session = Session()  # 对话类实例化出对话对象  #isolation_level="READ UNCOMMITTED",
