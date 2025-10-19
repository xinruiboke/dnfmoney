from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.core.config.astrbot_config import AstrBotConfig
import aiohttp
import json
import time  # 新增：用于动态生成时间戳

# 关键：添加__all__，明确告诉AstrBot要加载的插件类，解决类识别为空的问题
__all__ = ["JinBiChaXun"]

@register(
    "dnfmoney",          # 插件唯一标识（与文件夹名一致）
    "mowang",            # 作者名
    "查询今日金币价格",  # 插件功能描述
    "1.0.0",             # 版本号
    "https://github.com/xinruiboke/dnfmoney"  # 仓库地址
)
class JinBiChaXun(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

        # 群聊白名单配置
        self.enable_white_list_groups: bool = config.get(
            "enable_white_list_groups", False
        )
        self.white_list_groups: list[str] = config.get("white_list_groups", [])

    async def _get_today_gold_price(self) -> str:
        """获取今日金币价格的核心逻辑（优化请求头时效性）"""
        url = "https://gw.7881.com/goods-service-api/api/goods/list"
        
        # 请求数据（保持不变）
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
        
        # 优化请求头：动态生成时间戳，删除过期的固定签名（避免API拒绝）
        current_timestamp = str(int(time.time() * 1000))  # 毫秒级时间戳
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "redirectUrl": "https://search.7881.com/",
            "Host": "gw.7881.com",
            "Origin": "https://search.7881.com",
            "Pragma": "no-cache",
            "Referer": "https://search.7881.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36",
            "lb-timestamp": current_timestamp,  # 动态时间戳（关键优化）
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
                    
                    # 提取价格信息（保持不变）
                    if "body" in result and "results" in result["body"]:
                        results = result["body"]["results"]
                        if results and len(results) > 0:
                            first_item = results[0]
                            unit_of_price = first_item.get("unitOfPrice", "未知")
                            goods_name = first_item.get("goodsName", "金币")
                            price = first_item.get("price", "未知")
                            return f"💰 今日{goods_name}价格：\n📊 单价：{unit_of_price}\n💵 价格：{price}元"
                        else:
                            return "未找到金币价格信息（可能暂无数据）"
                    else:
                        return "返回数据格式错误（API可能更新）"
                        
        except aiohttp.ClientError as e:
            return f"请求失败：{str(e)}（检查网络或API地址）"
        except json.JSONDecodeError:
            return "返回数据解析失败（非JSON格式）"
        except Exception as e:
            return f"获取价格出错：{str(e)}"

    @filter.regex(r"^今日金币.*")  # 匹配"今日金币"开头的消息
    @filter.command("金币价格")    # 匹配指令"金币价格"
    async def get_today_gold_price(self, event: AstrMessageEvent):
        """触发金币查询的入口方法"""
        logger.info(f"[金币查询] 用户{event.get_sender_id()}发起查询")
        
        # 白名单校验（保持不变）
        if self.enable_white_list_groups and event.get_group_id() not in self.white_list_groups:
            return
                
        result = await self._get_today_gold_price()
        yield event.plain_result(result)

    async def terminate(self):
        """插件终止时的清理方法"""
        logger.info("✅ 金币查询插件已正常终止")