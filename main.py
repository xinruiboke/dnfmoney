from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import aiohttp

@register("dnfmoney", "YourName", "DNF查询今日金币价格", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def initialize(self):
        """插件初始化方法"""
    


    # 当收到"今日价格"关键词时触发
    @filter.contains("今日价格")
    async def get_today_price(self, event: AstrMessageEvent):
        """获取今日价格信息"""
        try:
            # 准备请求数据
            data = {
                "marketRequestSource": "search",
                "sellerType": "C",
                "gameId": "G10",
                "gtid": "100001",
                "groupId": "G10P002",
                "serverId": "G10P002001",
                "tradePlace": "0",
                "goodsSortType": "1",
                "extendAttrList": [],
                "pageNum": 1,
                "pageSize": 30
            }
            
            # 准备请求头
            headers = {
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "application/json",
                "Host": "gw.7881.com",
                "Origin": "https://search.7881.com",
                "Pragma": "no-cache",
                "Referer": "https://search.7881.com/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36 Core/1.116.569.400 QQBrowser/19.7.6765.400",
                "lb-sign": "9e96cd2e1398aa7779fcf0fd64cfb498",
                "lb-timestamp": "1760890645277",
                "sec-ch-ua": "\"Not)A;Brand\";v=\"24\", \"Chromium\";v=\"116\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\""
            }
            
            # 发送POST请求
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://gw.7881.com/goods-service-api/api/goods/list",
                    json=data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        # 提取unitOfPrice值
                        unit_of_price = result.get("body", {}).get("results", {}).get("unitOfPrice", "未知")
                        yield event.plain_result(f"今日价格：{unit_of_price}")
                    else:
                        yield event.plain_result(f"请求失败，状态码：{response.status}")
                        
        except Exception as e:
            logger.error(f"获取价格信息时出错：{str(e)}")
            yield event.plain_result("获取价格信息时出现错误，请稍后重试")

    async def terminate(self):
        """插件销毁方法"""
