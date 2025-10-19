from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.core.config.astrbot_config import AstrBotConfig
import aiohttp
import json

@register(
    "astrbot_plugin_redstone",
    "LumineStory",
    "查询今日金币价格",
    "1.0.0",
    "https://github.com/oyxning/astrbot_plugin_redstone"
)
class JinBiChaXun(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

        # 群聊白名单
        self.enable_white_list_groups: bool = config.get(
            "enable_white_list_groups", False
        )
        self.white_list_groups: list[str] = config.get("white_list_groups", [])

    async def _get_today_gold_price(self) -> str:
        """
        获取今日金币价格的核心逻辑
        """
        url = "https://gw.7881.com/goods-service-api/api/goods/list"
        
        # 请求数据 - 查询金币价格
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
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers, timeout=10) as response:
                    if response.status != 200:
                        text = await response.text()
                        raise RuntimeError(f"API 返回码 {response.status}, 内容：{text}")
                    
                    result = await response.json()
                    
                    # 从返回的JSON数据中提取金币价格信息
                    if "body" in result and "results" in result["body"]:
                        results = result["body"]["results"]
                        if results and len(results) > 0:
                            # 获取第一个商品的价格信息
                            first_item = results[0]
                            unit_of_price = first_item.get("unitOfPrice", "未知")
                            goods_name = first_item.get("goodsName", "金币")
                            price = first_item.get("price", "未知")
                            
                            return f"💰 今日{goods_name}价格：\n📊 单价：{unit_of_price}\n💵 价格：{price}"
                        else:
                            return "未找到金币价格信息"
                    else:
                        return "返回数据格式错误"
                        
        except aiohttp.ClientError as e:
            return f"请求失败：{str(e)}"
        except json.JSONDecodeError:
            return "返回数据解析失败"
        except Exception as e:
            return f"获取金币价格时发生错误：{str(e)}"

    @filter.regex(r"^今日金币.*")
    @filter.command("金币价格")
    async def get_today_gold_price(self, event: AstrMessageEvent):
        """获取今日金币价格"""
        logger.info(f"[金币查询] 收到金币价格查询，用户：{event.get_sender_id()}")
        
        # 检查群组id是否在白名单中, 若没填写白名单则不检查
        if self.enable_white_list_groups:
            if event.get_group_id() not in self.white_list_groups:
                return
                
        result = await self._get_today_gold_price()
        yield event.plain_result(result)

    async def terminate(self):
        logger.info("金币查询插件已终止。")
