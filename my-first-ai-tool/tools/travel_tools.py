"""
旅游工具插件
定义了 Agent 可以使用的工具函数
"""

from typing import Annotated
from semantic_kernel.functions import kernel_function


class TravelToolsPlugin:
    """旅游工具插件 - 提供目的地查询和推荐功能"""
    
    @kernel_function(description="获取可用的旅游目的地列表")
    def get_destinations(self) -> Annotated[str, "返回目的地列表"]:
        """获取旅游目的地"""
        destinations = {
            "Barcelona": {"country": "Spain", "available": False, "price": "$$$"},
            "Paris": {"country": "France", "available": True, "price": "$$$$"},
            "Tokyo": {"country": "Japan", "available": False, "price": "$$$"},
            "Bali": {"country": "Indonesia", "available": True, "price": "$$"},
            "New York": {"country": "USA", "available": True, "price": "$$$$$"}
        }
        
        result = "🌍 可用目的地:\n\n"
        for city, info in destinations.items():
            status = "✅ 可预订" if info["available"] else "❌ 已满"
            result += f"📍 {city}, {info['country']} - {info['price']} - {status}\n"
        return result
    
    @kernel_function(description="检查特定目的地的详细信息和可用性")
    def check_destination_availability(
        self, 
        destination: Annotated[str, "要查询的目的地名称"]
    ) -> Annotated[str, "返回目的地的详细信息"]:
        """检查目的地可用性"""
        destinations_db = {
            "barcelona": {
                "available": False,
                "next_available": "2025-12-15",
                "features": ["海滩", "建筑", "美食"],
                "weather": "温暖宜人"
            },
            "paris": {
                "available": True,
                "next_available": "即刻",
                "features": ["艺术", "历史", "浪漫"],
                "weather": "温和"
            },
            "tokyo": {
                "available": False,
                "next_available": "2025-12-01",
                "features": ["科技", "文化", "美食"],
                "weather": "四季分明"
            },
            "bali": {
                "available": True,
                "next_available": "即刻",
                "features": ["海滩", "文化", "瑜伽"],
                "weather": "热带气候"
            },
            "new york": {
                "available": True,
                "next_available": "即刻",
                "features": ["都市", "艺术", "购物"],
                "weather": "四季分明"
            }
        }
        
        dest_lower = destination.lower()
        if dest_lower in destinations_db:
            info = destinations_db[dest_lower]
            status = "✅ 现在可预订" if info["available"] else f"❌ 已满,下次可预订: {info['next_available']}"
            return f"""
📍 {destination} 详细信息:
━━━━━━━━━━━━━━━━━
• 状态: {status}
• 特色: {', '.join(info['features'])}
• 天气: {info['weather']}
━━━━━━━━━━━━━━━━━
"""
        return f"❌ 抱歉,未找到 {destination} 的信息。"
    
    @kernel_function(description="根据用户预算和偏好推荐目的地")
    def recommend_destination(
        self,
        budget: Annotated[str, "预算等级: low, medium, high"],
        preferences: Annotated[str, "偏好类型,如: 海滩, 文化, 美食"]
    ) -> Annotated[str, "返回推荐的目的地"]:
        """智能推荐目的地"""
        recommendations = {
            "low": {
                "beach": "Bali - 性价比高的海滩度假胜地 🏖️",
                "culture": "Prague - 历史悠久且经济实惠 🏛️",
                "food": "Bangkok - 街头美食天堂 🍜"
            },
            "medium": {
                "beach": "Barcelona - 海滩与城市完美结合 🌊",
                "culture": "Kyoto - 传统日本文化体验 ⛩️",
                "food": "Barcelona - 地中海美食 🍤"
            },
            "high": {
                "beach": "Maldives - 奢华海岛度假 🏝️",
                "culture": "Paris - 世界艺术之都 🎨",
                "food": "Tokyo - 米其林餐厅最多的城市 🍱"
            }
        }
        
        pref_lower = preferences.lower()
        pref_key = "beach" if "海滩" in pref_lower or "beach" in pref_lower else \
                   "culture" if "文化" in pref_lower or "culture" in pref_lower else \
                   "food"
        
        budget_lower = budget.lower()
        if budget_lower in recommendations:
            return f"""
💡 根据您的需求推荐:
━━━━━━━━━━━━━━━━━
• 预算: {budget}
• 偏好: {preferences}
• 推荐: {recommendations[budget_lower][pref_key]}
━━━━━━━━━━━━━━━━━
"""
        return "❌ 请提供有效的预算等级: low, medium, high"
