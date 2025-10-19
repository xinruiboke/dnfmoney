import json
import requests
from astrbot.api.event import filter
from astrbot.api.star import Context, Star, register
from astrbot.core.config.astrbot_config import AstrBotConfig
from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import (
    AiocqhttpMessageEvent,
)

@register(
    "astrbot_plugin_zanwo",
    "Futureppo",
    "发送 今日价格 获取当前价格",
    "1.0.8",
    "https://github.com/Futureppo/astrbot_plugin_zanwo",
)
class zanwo(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

        # 群聊白名单
        self.enable_white_list_groups: bool = config.get(
            "enable_white_list_groups", False
        )
        self.white_list_groups: list[str] = config.get("white_list_groups", [])

    async def _get_today_price(self) -> str:
        """
        获取今日价格的核心逻辑
        """
        url = "https://gw.7881.com/goods-service-api/api/goods/list"
        
        # 请求数据
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
        
        # 请求头
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Length": "207",
            "Content-Type": "application/json",
            "redirectUrl": "https://search.7881.com/",
            "Hm_lpvt_6fb35abaf76325a4316e33e23c984e73": "1760890645",
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
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            # 从返回的JSON数据中提取body.results.unitOfPrice的值
            if "body" in result and "results" in result["body"]:
                results = result["body"]["results"]
                if results and len(results) > 0:
                    unit_of_price = results[0].get("unitOfPrice", "未知")
                    return f"今日价格：{unit_of_price}"
                else:
                    return "未找到价格信息"
            else:
                return "返回数据格式错误"
                
        except requests.exceptions.RequestException as e:
            return f"请求失败：{str(e)}"
        except json.JSONDecodeError:
            return "返回数据解析失败"
        except Exception as e:
            return f"获取价格时发生错误：{str(e)}"

    @filter.regex(r"^今日价格.*")
    async def get_today_price(self, event: AiocqhttpMessageEvent):
        """获取今日价格"""
        # 检查群组id是否在白名单中, 若没填写白名单则不检查
        if self.enable_white_list_groups:
            if event.get_group_id() not in self.white_list_groups:
                return
                
        result = await self._get_today_price()
        yield event.plain_result(result)


