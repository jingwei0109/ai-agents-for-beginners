"""
缓存管理器实现
支持内存缓存和Redis缓存
"""
import hashlib
import json
import time
from typing import Optional, Dict, Any
from dataclasses import asdict


class CacheManager:
    """缓存管理器"""
    
    def __init__(
        self,
        enabled: bool = True,
        ttl_seconds: int = 3600,
        max_size: int = 1000,
        use_redis: bool = False,
        redis_url: Optional[str] = None
    ):
        self.enabled = enabled
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self.use_redis = use_redis
        
        # 内存缓存
        self._cache: Dict[str, tuple[Any, float]] = {}
        self._access_order = []
        
        # Redis缓存（如果启用）
        self._redis_client = None
        if use_redis and redis_url:
            try:
                import redis
                self._redis_client = redis.from_url(redis_url)
            except ImportError:
                print("警告: redis包未安装，将使用内存缓存")
                self.use_redis = False
    
    def _generate_cache_key(
        self,
        messages: list,
        model: str,
        temperature: float,
        **kwargs
    ) -> str:
        """生成缓存键"""
        cache_data = {
            "messages": [m.to_dict() if hasattr(m, 'to_dict') else m for m in messages],
            "model": model,
            "temperature": temperature,
            **kwargs
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_str.encode()).hexdigest()
    
    def get(self, cache_key: str) -> Optional[Any]:
        """从缓存获取"""
        if not self.enabled:
            return None
        
        # 尝试Redis
        if self.use_redis and self._redis_client:
            try:
                cached_data = self._redis_client.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)
            except Exception as e:
                print(f"Redis获取失败: {e}")
        
        # 尝试内存缓存
        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self.ttl_seconds:
                # 更新访问顺序
                if cache_key in self._access_order:
                    self._access_order.remove(cache_key)
                self._access_order.append(cache_key)
                return data
            else:
                # 过期删除
                del self._cache[cache_key]
                if cache_key in self._access_order:
                    self._access_order.remove(cache_key)
        
        return None
    
    def set(self, cache_key: str, data: Any) -> None:
        """设置缓存"""
        if not self.enabled:
            return
        
        # 设置Redis
        if self.use_redis and self._redis_client:
            try:
                self._redis_client.setex(
                    cache_key,
                    self.ttl_seconds,
                    json.dumps(data)
                )
            except Exception as e:
                print(f"Redis设置失败: {e}")
        
        # 设置内存缓存
        # LRU淘汰
        if len(self._cache) >= self.max_size and self._access_order:
            oldest_key = self._access_order.pop(0)
            if oldest_key in self._cache:
                del self._cache[oldest_key]
        
        self._cache[cache_key] = (data, time.time())
        if cache_key not in self._access_order:
            self._access_order.append(cache_key)
    
    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self._access_order.clear()
        
        if self.use_redis and self._redis_client:
            try:
                # 注意: 这会清空整个Redis数据库
                # 在生产环境中可能需要更精细的控制
                pass  # 不自动清空Redis
            except Exception as e:
                print(f"Redis清空失败: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        return {
            "enabled": self.enabled,
            "size": len(self._cache),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds,
            "use_redis": self.use_redis
        }


class PrefetchManager:
    """预取管理器"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self._prefetch_queue = []
    
    async def prefetch(
        self,
        client,
        messages_list: list,
        model: str,
        **kwargs
    ) -> None:
        """预取多个请求"""
        import asyncio
        
        tasks = []
        for messages in messages_list:
            task = client.complete(
                messages=messages,
                model=model,
                _skip_cache_write=False,
                **kwargs
            )
            tasks.append(task)
        
        # 并发执行预取
        await asyncio.gather(*tasks, return_exceptions=True)
    
    def add_to_queue(self, messages: list, model: str, **kwargs) -> None:
        """添加到预取队列"""
        self._prefetch_queue.append({
            "messages": messages,
            "model": model,
            **kwargs
        })
    
    async def process_queue(self, client) -> None:
        """处理预取队列"""
        if not self._prefetch_queue:
            return
        
        messages_list = [item["messages"] for item in self._prefetch_queue]
        model = self._prefetch_queue[0]["model"]  # 假设同一模型
        
        await self.prefetch(client, messages_list, model)
        self._prefetch_queue.clear()
