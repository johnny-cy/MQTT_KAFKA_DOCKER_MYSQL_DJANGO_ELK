# -*- coding: utf-8 -*-


class Area(object):
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float


class Taichung(Area):
    name: str = "台中"
    min_lat: float = 24.132 # 24.075452 
    max_lat: float = 24.4214 # 24.42158
    min_lon: float = 120.5024 # 120.49468
    max_lon: float = 120.7889 # 120.742974
    # Circle
    radius: float = 0.3  # KM


class TaichungPort(Area):
    name: str = "台中港"
    area_id: str = "B56"
    min_lat: float = 24.1748
    max_lat: float = 24.2863
    min_lon: float = 120.5024
    max_lon: float = 120.5432
    # Event Table
    combine_minutes: int = 3


class TaichungIndustry(Area):
    name: str = "台中工業區"
    area_id: str = "B55"
    min_lat: float = 24.1320
    max_lat: float = 24.1940
    min_lon: float = 120.5730
    max_lon: float = 120.6310
    # Event Table
    combine_minutes: int = 3


class Guanyin(Area):
    name: str = "觀音"
    area_id: str = "H59"
    min_lat: float = 25.04
    max_lat: float = 25.07
    min_lon: float = 121.1
    max_lon: float = 121.145
    # Event Table
    combine_minutes: int = 3
    # Circle
    radius: float = 0.3


class Houli(Area):
    name: str = "后里豐原"
    area_id: str = "B54"
    min_lat: float = 24.2432
    max_lat: float = 24.3498
    min_lon: float = 120.6517
    max_lon: float = 120.7889
    # Event Table
    combine_minutes: int = 3


class Dajia(Area):
    name: str = "大甲幼獅工業區"
    area_id: str = "B58"
    min_lat: float = 24.3663
    max_lat: float = 24.4214
    min_lon: float = 120.6124
    max_lon: float = 120.7052
    # Event Table
    combine_minutes: int = 3


class NewTaipei(Area):
    name: str = "新北市"
    min_lat: float = 24.9344 # 24.9344
    max_lat: float = 25.085138 # 25.1550
    min_lon: float = 121.3699 # 121.3699
    max_lon: float = 121.465267 # 121.5263
    # Circle
    radius: float = 0.3  # KM


class Tucheng(Area):
    name: str = "土城三峽"
    area_id: str = "F51"
    min_lat: float = 24.9344
    max_lat: float = 24.9785
    min_lon: float = 121.3699
    max_lon: float = 121.4502
    # Event Table
    combine_minutes: int = 3


class Yilan(Area):
    name: str = "宜蘭"
    min_lat: float = 24.6188
    max_lat: float = 24.66814
    min_lon: float = 121.8070
    max_lon: float = 121.8374
    # Circle
    radius: float = 0.3  # KM

class YilanCounty(Area):
    name: str = "宜蘭"
    area_id: str = "G53"
    min_lat: float = 24.6188
    max_lat: float = 24.6422
    min_lon: float = 121.8070
    max_lon: float = 121.8355
    # Event Table
    combine_minutes: int = 3




class Taoyuan(Area):
    name: str = "桃園"
    min_lat: float = 24.921524 # 24.8276
    max_lat: float = 25.12041759 # 25.0968
    min_lon: float = 121.02565585 # 121.0815
    max_lon: float = 121.3862 # 121.3961
    # Circle
    radius: float = 0.3  # KM


class Dayuan(Area):
    name: str = "大園工業區"
    area_id: str = "H53"
    min_lat: float = 25.0541
    max_lat: float = 25.0976
    min_lon: float = 121.1700
    max_lon: float = 121.2106
    # Event Table
    combine_minutes: int = 3


class Guishan(Area):
    name: str = "龜山工業區"
    area_id: str = "H55"
    min_lat: float = 24.945
    max_lat: float = 24.9961
    min_lon: float = 121.3068
    max_lon: float = 121.362
    # Event Table
    combine_minutes: int = 3


class Hwaya(Area):
    name: str = "華亞科技園區"
    area_id: str = "H54"
    min_lat: float = 25.0274
    max_lat: float = 25.0644
    min_lon: float = 121.3650
    max_lon: float = 121.3862
    # Event Table
    combine_minutes: int = 3


class Longtan(Area):
    name: str = "龍潭平鎮"
    area_id: str = "H57"
    min_lat: float = 24.8360
    max_lat: float = 24.9188
    min_lon: float = 121.1655
    max_lon: float = 121.2202
    # Event Table
    combine_minutes: int = 3


class Hsinchu(Area):
    name: str = "新竹"
    min_lat: float = 24.7465
    max_lat: float = 24.9093
    min_lon: float = 120.8888
    max_lon: float = 121.1645
    # Circle
    radius: float = 0.3  # KM


class HsinchuIndustry(Area):
    name: str = "新竹工業區"
    area_id: str = "J52"
    min_lat: float = 24.8546
    max_lat: float = 24.8766
    min_lon: float = 120.9919
    max_lon: float = 121.0447
    # Event Table
    combine_minutes: int = 3


class HsinchuSciencePark(Area):
    name: str = "新竹科學園區"
    area_id: str = "O51"
    min_lat: float = 24.7705
    max_lat: float = 24.7826
    min_lon: float = 120.9779
    max_lon: float = 121.0342
    # Event Table
    combine_minutes: int = 3


class HsinchuCity(Area):
    name: str = "新竹市"
    area_id: str = "O00"
    min_lat: float = 24.7786
    max_lat: float = 24.8349
    min_lon: float = 120.9181
    max_lon: float = 120.9986
    # Event Table
    combine_minutes: int = 3


class Miaoli(Area):
    name: str = "苗栗"
    min_lat: float = 24.5760
    max_lat: float = 24.7401
    min_lon: float = 120.7107
    max_lon: float = 120.9529
    # Circle
    radius: float = 0.3


class Toufen(Area):
    name: str = "竹南頭份"
    area_id: str = "K52"
    min_lat: float = 24.6365
    max_lat: float = 24.7401
    min_lon: float = 120.8226
    max_lon: float = 120.9529
    # Event Table
    combine_minutes: int = 3


class MiaoliCity(Area):
    name: str = "苗栗市"
    area_id: str = "K01"
    min_lat: float = 24.5760
    max_lat: float = 24.6171
    min_lon: float = 120.7107
    max_lon: float = 120.8509
    # Event Table
    combine_minutes: int = 3


class Yunlin(Area):
    name: str = "雲林"
    min_lat: float = 23.609037  # 23.7112
    max_lat: float = 23.813108  # 23.7408
    min_lon: float = 120.165726  # 120.4947
    max_lon: float = 120.6005  # 120.5729
    # Circle
    radius: float = 0.3


class YunlinIndustryPark(Area):
    name: str = "雲林科技工業區"
    area_id: str = "P55"
    min_lat: float = 23.7112
    max_lat: float = 23.7306
    min_lon: float = 120.4947
    max_lon: float = 120.5236
    # Event Table
    combine_minutes: int = 3


class YunlinIndustryJhuweizih(Area):
    name: str = "雲林科技工業區竹圍子區"
    area_id: str = "P56"
    min_lat: float = 23.7259
    max_lat: float = 23.7408
    min_lon: float = 120.5238
    max_lon: float = 120.5729
    # Event Table
    combine_minutes: int = 3


class Chiayi(Area):
    name: str = "嘉義"
    min_lat: float = 23.4386
    max_lat: float = 23.5347
    min_lon: float = 120.3970
    max_lon: float = 120.5106
    # Circle
    radius: float = 0.3


class ChiayiCity(Area):
    name: str = "嘉義市"
    area_id: str = "I00"
    min_lat: float = 23.4386
    max_lat: float = 23.5141
    min_lon: float = 120.3970
    max_lon: float = 120.5088
    # Event Table
    combine_minutes: int = 3


class Minxiong(Area):
    name: str = "民雄工業區"
    area_id: str = "Q55"
    min_lat: float = 23.5117
    max_lat: float = 23.5349
    min_lon: float = 120.4214
    max_lon: float = 120.4617
    # Event Table
    combine_minutes: int = 3


class Tainan(Area):
    name: str = "台南"
    min_lat: float = 22.9106 # 22.9036
    max_lat: float = 23.31065776 # 23.2027
    min_lon: float = 120.12635808 # 120.0584
    max_lon: float = 120.36784094 # 120.2666
    # Circle
    radius: float = 0.3


class Jiali(Area):
    name: str = "佳里工業區"
    area_id: str = "D20"
    min_lat: float = 23.1703
    max_lat: float = 23.2057
    min_lon: float = 120.1626
    max_lon: float = 120.1972
    # Event Table
    combine_minutes: int = 3


class Rende(Area):
    name: str = "仁德工業區"
    area_id: str = "D32"
    min_lat: float = 22.9679
    max_lat: float = 23.0013
    min_lon: float = 120.2352
    max_lon: float = 120.2643
    # Event Table
    combine_minutes: int = 3


class Baoan(Area):
    name: str = "保安工業區"
    area_id: str = "D58"
    min_lat: float = 22.9106
    max_lat: float = 22.9421
    min_lon: float = 120.2146
    max_lon: float = 120.2497
    # Event Table
    combine_minutes: int = 3


class Kaohsiung(Area):
    name: str = "高雄"
    min_lat: float = 22.4836 # 22.4342
    max_lat: float = 22.86692764 # 22.8900
    min_lon: float = 120.19992595 # 120.1393
    max_lon: float = 120.4395 # 120.4398
    # Circle
    radius: float = 0.3


class Linyuan(Area):
    name: str = "林園工業區"
    area_id: str = "E58"
    min_lat: float = 22.4836
    max_lat: float = 22.5198
    min_lon: float = 120.3953
    max_lon: float = 120.4250
    # Event Table
    combine_minutes: int = 3


class Dafa(Area):
    name: str = "大發工業區"
    area_id: str = "E62"
    min_lat: float = 22.5670
    max_lat: float = 22.5980
    min_lon: float = 120.4180
    max_lon: float = 120.4395
    # Event Table
    combine_minutes: int = 3


class Linhai(Area):
    name: str = "臨海工業區"
    area_id: str = "E63"
    min_lat: float = 22.5053
    max_lat: float = 22.5752
    min_lon: float = 120.3206
    max_lon: float = 120.3908
    # Event Table
    combine_minutes: int = 3


class KaohsiungCity(Area):
    name: str = "高雄市區"
    area_id: str = "E00"
    min_lat: float = 22.5739
    max_lat: float = 22.6953
    min_lon: float = 120.2555
    max_lon: float = 120.3777
    # Event Table
    combine_minutes: int = 3


class Jenwu(Area):
    name: str = "仁武工業區"
    area_id: str = "E61"
    min_lat: float = 22.6925
    max_lat: float = 22.7317
    min_lon: float = 120.3275
    max_lon: float = 120.3489
    # Event Table
    combine_minutes: int = 3


class Pingtung(Area):
    name: str = "屏東"
    min_lat: float = 22.3987 # 21.8727
    max_lat: float = 22.7198  # 22.8734
    min_lon: float = 120.4429  # 120.4398
    max_lon: float = 120.595 # 120.9212
    # Circle
    radius: float = 0.3


class PingnanIndustry(Area):
    name: str = "屏南工業區"
    area_id: str = "T55"
    min_lat: float = 22.3987
    max_lat: float = 22.4193
    min_lon: float = 120.5602
    max_lon: float = 120.5950
    # Event Table
    combine_minutes: int = 3


class PingnanExportProcessingZone(Area):
    name: str = "屏東加工出口區"
    area_id: str = "T51"
    min_lat: float = 22.6271
    max_lat: float = 22.6547
    min_lon: float = 120.4429
    max_lon: float = 120.4639
    # Event Table
    combine_minutes: int = 3


class Neipu(Area):
    name: str = "內埔工業區"
    area_id: str = "T53"
    min_lat: float = 22.6338
    max_lat: float = 22.6516
    min_lon: float = 120.5335
    max_lon: float = 120.5593
    # Event Table
    combine_minutes: int = 3


class PingtungCity(Area):
    name: str = "屏東市區"
    area_id: str = "T01"
    min_lat: float = 22.6510
    max_lat: float = 22.7037
    min_lon: float = 120.4642
    max_lon: float = 120.5159
    # Event Table
    combine_minutes: int = 3


class AgriculturalBiotechnologyPark(Area):
    name: str = "農業生物科技園區"
    area_id: str = "T54"
    min_lat: float = 22.6923
    max_lat: float = 22.7198
    min_lon: float = 120.5279
    max_lon: float = 120.5601
    # Event Table
    combine_minutes: int = 3


# Add new area by Henry 2019.10.29 below

# for potential area(潛勢網格):
class Changhua(Area):
    name: str = "彰化"
    min_lat: float = 23.842333 # 23.8270
    max_lat: float = 24.1768 # 24.1880
    min_lon: float = 120.3383 # 120.3120
    max_lon: float = 120.575455 # 120.5270
    # Circle
    radius: float = 0.3

class Keelung(Area):
    name: str = "基隆"
    min_lat: float = 25.08057 # 25.0627
    max_lat: float = 25.1554 # 25.1562
    min_lon: float = 121.6918 # 121.6878
    max_lon: float = 121.7092 # 121.8008
    # Circle
    radius: float = 0.3

# for 告警事件area
class ChuansingIndustrialPark(Area):
    name: str = "全興工業區"
    area_id: str = "N07"
    min_lat: float = 24.1425
    max_lat: float = 24.1768
    min_lon: float = 120.4998
    max_lon: float = 120.5227
    # Event Table
    combine_minutes: int = 3

class ChanghuaCoastalIndustrialPark(Area):
    name: str = "彰化濱海工業區"
    area_id: str = "N06"
    min_lat: float = 24.0548
    max_lat: float = 24.1634
    min_lon: float = 120.3680
    max_lon: float = 120.4511
    # Event Table
    combine_minutes: int = 3

class FangyuanIndustrialPark(Area):
    name: str = "芳苑工業區"
    area_id: str = "N05"
    min_lat: float = 23.9000
    max_lat: float = 23.9324
    min_lon: float = 120.3383
    max_lon: float = 120.3629
    # Event Table
    combine_minutes: int = 3

class TapurunIndustrialPark(Area):
    name: str = "大武崙工業區"
    area_id: str = "C02"
    min_lat: float = 25.1368
    max_lat: float = 25.1554
    min_lon: float = 121.6918
    max_lon: float = 121.7092
    # Event Table
    combine_minutes: int = 3

### Doulio has added by Johnny-cy 2019-11-27
class Doulio(Area):
    name: str = "斗六工業區"
    area_id: str = "P57"
    min_lat: float = 23.7097
    max_lat: float = 23.7248
    min_lon: float = 120.5898
    max_lon: float = 120.6005
    # Event Table
    combine_minutes: int = 3

### ShiluoVegMarket added by Johnny-cy 2019-11-29
class ShiluoVegMarket(Area):
    name: str = "西螺果菜市場"
    area_id: str = "P58"
    min_lat: float = 23.781778
    max_lat: float = 23.789591
    min_lon: float = 120.437977
    max_lon: float = 120.458034
    # Event Table
    combine_minutes: int = 3

### YuanchangIndustry added by Johnny-cy 2019-11-29
class YuanchangIndustry(Area):
    name: str = "元長工業區"
    area_id: str = "P59"
    min_lat: float = 23.609037
    max_lat: float = 23.614708
    min_lon: float = 120.330129
    max_lon: float = 120.333800
    # Event Table
    combine_minutes: int = 3

### FengtianIndustry added by Johnny-cy 2019-11-29
class FengtianIndustry(Area):
    name: str = "豐田工業區"
    area_id: str = "P60"
    min_lat: float = 23.633757
    max_lat: float = 23.642969
    min_lon: float = 120.464130
    max_lon: float = 120.470248
    # Event Table
    combine_minutes: int = 3

### JungkehuweiPark added by Johnny-cy 2019-11-29
class JungkehuweiPark(Area):
    name: str = "中科虎尾園區"
    area_id: str = "P61"
    min_lat: float = 23.731800
    max_lat: float = 23.739956
    min_lon: float = 120.394213
    max_lon: float = 120.409158
    # Event Table
    combine_minutes: int = 3

### DoulioConnectingRoad added by Johnny-cy 2019-11-29
class DoulioConnectingRoad(Area):
    name: str = "斗六聯絡道路"
    area_id: str = "P62"
    min_lat: float = 23.735156
    max_lat: float = 23.736758
    min_lon: float = 120.428586
    max_lon: float = 120.469165
    # Event Table
    combine_minutes: int = 3


### WuguIndustry added by Johnny-cy 2019-11-29
class WuguIndustry(Area):
    name: str = "五股工業區"
    area_id: str = "F52"
    min_lat: float = 25.061175
    max_lat: float = 25.075487
    min_lon: float = 121.446398
    max_lon: float = 121.465267
    # Event Table
    combine_minutes: int = 3

### LiouchingIndustry added by Johnny-cy 2019-12-02
class LiouchingIndustry(Area):
    name: str = "六輕工業區"
    area_id: str = "P63"
    min_lat: float = 23.761971
    max_lat: float = 23.813108
    min_lon: float = 120.165726
    max_lon: float = 120.283109
    # Event Table
    combine_minutes: int = 3

class LitzeIndustry(Area):
    name: str = "利澤工業區"
    area_id: str = "G54"
    min_lat: float = 24.633952
    max_lat: float = 24.668137
    min_lon: float = 121.832334
    max_lon: float = 121.837367
    # Event Table
    combine_minutes: int = 3

class LoiuduTechPark(Area):
    name: str = "六堵科技園區"
    area_id: str = "C03"
    min_lat: float = 25.080570
    max_lat: float = 25.103105
    min_lon: float = 121.694617
    max_lon: float = 121.708647
    # Event Table
    combine_minutes: int = 3

class LinkouIndustry(Area):
    name: str = "林口工業區"
    area_id: str = "F02"
    min_lat: float = 25.076141
    max_lat: float = 25.085138
    min_lon: float = 121.396909
    max_lon: float = 121.403985
    # Event Table
    combine_minutes: int = 3

class TaoyuanyushihIndustry(Area):
    name: str = "桃園幼獅工業區"
    area_id: str = "H02"
    min_lat: float = 24.921524
    max_lat: float = 24.938477
    min_lon: float = 121.147418
    max_lon: float = 121.178812
    # Event Table
    combine_minutes: int = 3

class TianjungIndustry(Area):
    name: str = "田中工業區"
    area_id: str = "N02"
    min_lat: float = 23.842333
    max_lat: float = 23.853944
    min_lon: float = 120.569026
    max_lon: float = 120.575455
    # Event Table
    combine_minutes: int = 3

class PitouIndustry(Area):
    name: str = "埤頭工業區"
    area_id: str = "N03"
    min_lat: float = 23.87594
    max_lat: float = 23.87941
    min_lon: float = 120.4593
    max_lon: float = 120.4648
    # Event Table
    combine_minutes: int = 3

class NantzuIndustry(Area):
    name: str = "楠梓加工區"
    area_id: str = "S02"
    min_lat: float = 22.711836
    max_lat: float = 22.726572
    min_lon: float = 120.298536
    max_lon: float = 120.310834
    # Event Table
    combine_minutes: int = 3

### the following added by Johnny-cy 2019-12-9
class ShulinIndustry(Area):
    name: str = "樹林工業區"
    area_id: str = "F03"
    min_lat: float = 24.99979865
    max_lat: float = 25.00479232
    min_lon: float = 121.41642826
    max_lon: float = 121.42237019
    # Event Table
    combine_minutes: int = 3

class HaihuIndustry(Area):
    name: str = "海湖工業區"
    area_id: str = "H03"
    min_lat: float = 25.08203646
    max_lat: float = 25.12041759
    min_lon: float = 121.25336641
    max_lon: float = 121.28150747
    # Event Table
    combine_minutes: int = 3

class ZhongliIndustry(Area):
    name: str = "中壢工業區"
    area_id: str = "H04"
    min_lat: float = 24.96053644
    max_lat: float = 25.00440812
    min_lon: float = 121.2265544
    max_lon: float = 121.2613169
    # Event Table
    combine_minutes: int = 3

class TaoyuanyonganIndustry(Area):
    name: str = "桃園永安工業區"
    area_id: str = "H05"
    min_lat: float = 24.97748073
    max_lat: float = 24.98814686
    min_lon: float = 121.02565585
    max_lon: float = 121.04690205
    # Event Table
    combine_minutes: int = 3

class TaoyuanTechIndustry(Area):
    name: str = "桃園科技工業區"
    area_id: str = "H06"
    min_lat: float = 25.04269047
    max_lat: float = 25.05868082
    min_lon: float = 121.0814096
    max_lon: float = 121.0814096
    # Event Table
    combine_minutes: int = 3

class ZhongketaizhongExt(Area):
    name: str = "中科台中園區擴建區"
    area_id: str = "B59"
    min_lat: float = 24.1954252
    max_lat: float = 24.22932466
    min_lon: float = 120.59922342
    max_lon: float = 120.63104451
    # Event Table
    combine_minutes: int = 3

class ShuinanEcoTradePark(Area):
    name: str = "水湳經貿園區"
    area_id: str = "B60"
    min_lat: float = 24.13574223
    max_lat: float = 24.20850422
    min_lon: float = 120.63192999
    max_lon: float = 120.69244662
    # Event Table
    combine_minutes: int = 3

class TaizhongjiagongExpo(Area):
    name: str = "台中加工出口區"
    area_id: str = "B61"
    min_lat: float = 24.19571047
    max_lat: float = 24.23838807
    min_lon: float = 120.66083953
    max_lon: float = 120.73170161
    # Event Table
    combine_minutes: int = 3

class XiyingIndustry(Area):
    name: str = "新營工業區"
    area_id: str = "D59"
    min_lat: float = 23.298607
    max_lat: float = 23.31065776
    min_lon: float = 120.2704353
    max_lon: float = 120.28827277
    # Event Table
    combine_minutes: int = 3

class LiuyingTechIndustry(Area):
    name: str = "柳營科技工業區"
    area_id: str = "D60"
    min_lat: float = 23.26708114
    max_lat: float = 23.28861389
    min_lon: float = 120.35037703
    max_lon: float = 120.36784094
    # Event Table
    combine_minutes: int = 3

class GuantianIndustry(Area):
    name: str = "官田工業區"
    area_id: str = "D61"
    min_lat: float = 23.20074527
    max_lat: float = 23.22323279
    min_lon: float = 120.31722363
    max_lon: float = 120.3349677
    # Event Table
    combine_minutes: int = 3

class TainanScientificPark(Area):
    name: str = "台南科學園區"
    area_id: str = "D62"
    min_lat: float = 23.08313925
    max_lat: float = 23.13278767
    min_lon: float = 120.23504054
    max_lon: float = 120.31143346
    # Event Table
    combine_minutes: int = 3

class YongkangIndustry(Area):
    name: str = "永康工業區"
    area_id: str = "D63"
    min_lat: float = 23.031109
    max_lat: float = 23.0539687
    min_lon: float = 120.26338437
    max_lon: float = 120.28673184
    # Event Table
    combine_minutes: int = 3

class HeshunIndustry(Area):
    name: str = "和順工業區"
    area_id: str = "D64"
    min_lat: float = 23.02870249
    max_lat: float = 23.0550858
    min_lon: float = 120.2068835
    max_lon: float = 120.22854995
    # Event Table
    combine_minutes: int = 3

class ZongtouliaoIndustry(Area):
    name: str = "總頭寮工業區"
    area_id: str = "D65"
    min_lat: float = 23.05745962
    max_lat: float = 23.0619923
    min_lon: float = 120.2029261
    max_lon: float = 120.21163471
    # Event Table
    combine_minutes: int = 3

class TainanTechIndustry(Area):
    name: str = "台南科技工業區"
    area_id: str = "D66"
    min_lat: float = 23.02806863
    max_lat: float = 23.0501984
    min_lon: float = 120.12635808
    max_lon: float = 120.1612392
    # Event Table
    combine_minutes: int = 3

class AnpingIndustry(Area):
    name: str = "安平工業區"
    area_id: str = "D67"
    min_lat: float = 22.95856182
    max_lat: float = 22.98452897
    min_lon: float = 120.1703914
    max_lon: float = 120.18850904
    # Event Table
    combine_minutes: int = 3

class BeishizhouIndustry(Area):
    name: str = "北勢洲工業區"
    area_id: str = "D68"
    min_lat: float = 23.10031266
    max_lat: float = 23.11981096
    min_lon: float = 120.33088773
    max_lon: float = 120.35862453
    # Event Table
    combine_minutes: int = 3

class XinshiIndustry(Area):
    name: str = "新市工業區"
    area_id: str = "D69"
    min_lat: float = 23.07316495
    max_lat: float = 23.08295937
    min_lon: float = 120.29306484
    max_lon: float = 120.30553238
    # Event Table
    combine_minutes: int = 3

class BenzhouIndustry(Area):
    name: str = "本洲產業園區"
    area_id: str = "S03"
    min_lat: float = 22.8028911
    max_lat: float = 22.82413
    min_lon: float = 120.25670699
    max_lon: float = 120.28598
    # Event Table
    combine_minutes: int = 3

class GaoxiongyonganIndustry(Area):
    name: str = "高雄永安工業區"
    area_id: str = "S04"
    min_lat: float = 22.80719558 
    max_lat: float = 22.81799921
    min_lon: float = 120.24498656
    max_lon: float = 120.25633343
    # Event Table
    combine_minutes: int = 3

class SouthScientificIndustrygaoxiong(Area):
    name: str = "南部科學工業園區高雄園區"
    area_id: str = "S05"
    min_lat: float = 22.8246 
    max_lat: float = 22.8576
    min_lon: float = 120.2334
    max_lon: float = 120.2839
    # Event Table
    combine_minutes: int = 3

class Taipei(Area):
    name: str = "台北"
    min_lat: float = 25.0366
    max_lat: float = 25.1395
    min_lon: float = 121.4678
    max_lon: float = 121.6216
    # Circle
    radius: float = 0.3  # KM

class TaipeiCity(Area):
    name: str = "台北市區"
    area_id: str = "A01"
    min_lat: float = 25.0366
    max_lat: float = 25.0473
    min_lon: float = 121.5473
    max_lon: float = 121.5739
    # Event Table
    combine_minutes: int = 3

class NeihusongshanDist(Area):
    name: str = "內湖松山區"
    area_id: str = "A02"
    min_lat: float = 25.0509
    max_lat: float = 25.0759
    min_lon: float = 121.5538
    max_lon: float = 121.6216
    # Event Table
    combine_minutes: int = 3

class BeitoushilinDist(Area):
    name: str = "北投士林區"
    area_id: str = "A03"
    min_lat: float = 25.0894
    max_lat: float = 25.1395
    min_lon: float = 121.4678
    max_lon: float = 121.5151
    # Event Table
    combine_minutes: int = 3



all_areas = (
    TaichungPort, TaichungIndustry, Houli, Dajia,
    Tucheng,
    YilanCounty,
    Dayuan, Guishan, Hwaya, Longtan, Guanyin,
    HsinchuIndustry, HsinchuSciencePark, HsinchuCity,
    Toufen, MiaoliCity,
    YunlinIndustryPark, YunlinIndustryJhuweizih,
    ChiayiCity, Minxiong,
    Jiali, Rende, Baoan,
    Linyuan, Dafa, Linhai, KaohsiungCity, Jenwu,
    PingnanIndustry, PingnanExportProcessingZone, Neipu, PingtungCity,
    AgriculturalBiotechnologyPark,
    ChuansingIndustrialPark,
    ChanghuaCoastalIndustrialPark,
    FangyuanIndustrialPark,
    TapurunIndustrialPark,
    Doulio, ShiluoVegMarket, YuanchangIndustry, FengtianIndustry, JungkehuweiPark, DoulioConnectingRoad, WuguIndustry,
    LiouchingIndustry, LitzeIndustry, LoiuduTechPark, LinkouIndustry, TaoyuanyushihIndustry,
    TianjungIndustry, PitouIndustry, NantzuIndustry,
    ShulinIndustry, HaihuIndustry, ZhongliIndustry, TaoyuanyonganIndustry, TaoyuanTechIndustry,
    ZhongketaizhongExt, ShuinanEcoTradePark, TaizhongjiagongExpo,
    XiyingIndustry, LiuyingTechIndustry,
    GuantianIndustry, TainanScientificPark, YongkangIndustry, HeshunIndustry, ZongtouliaoIndustry,
    TainanTechIndustry, AnpingIndustry, BeishizhouIndustry, XinshiIndustry, 
    BenzhouIndustry, GaoxiongyonganIndustry, SouthScientificIndustrygaoxiong, 
    TaipeiCity, NeihusongshanDist, BeitoushilinDist
    )

