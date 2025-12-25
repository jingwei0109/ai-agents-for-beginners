"""
缓存管理器
支持多种缓存策略和存储后端
"""

import hashlib
import json
import time
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
import asyncio


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    timestamp: float
    ttl: int  # seconds
    hit_count: int = 0
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.ttl <= 0:
            return False
        return time.time() - self.timestamp > self.ttl
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)


class CacheBackend(ABC):
    """缓存后端抽象类"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[CacheEntry]:
        """获取缓存"""
        pass
    
    @abstractmethod
    async def set(self, entry: CacheEntry) -> bool:
        """设置缓存"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """清空缓存"""
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        pass


class MemoryCacheBackend(CacheBackend):
    """内存缓存后端"""
    
    def __init__(self, max_size: int = 1000):
        self._cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self._hits = 0
        self._misses = 0
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[CacheEntry]:
        """获取缓存"""
        async with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._misses += 1
                return None
            
            if entry.is_expired():
                del self._cache[key]
                self._misses += 1
                return None
            
            entry.hit_count += 1
            self._hits += 1
            return entry
    
    async def set(self, entry: CacheEntry) -> bool:
        """设置缓存"""
        async with self._lock:
            # 如果缓存已满，删除最旧的条目
            if len(self._cache) >= self.max_size:
                oldest_key = min(
                    self._cache.keys(),
                    key=lambda k: self._cache[k].timestamp
                )
                del self._cache[oldest_key]
            
            self._cache[entry.key] = entry
            return True
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    async def clear(self) -> bool:
        """清空缓存"""
        async with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            return True
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        async with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0
            
            return {
                "backend": "memory",
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": hit_rate,
                "total_requests": total_requests
            }


class CacheManager:
    """缓存管理器"""
    
    def __init__(
        self,
        backend: Optional[CacheBackend] = None,
        default_ttl: int = 3600,  # 1 hour
        enabled: bool = True
    ):
        self.backend = backend or MemoryCacheBackend()
        self.default_ttl = default_ttl
        self.enabled = enabled
    
    def _generate_cache_key(
        self,
        messages: list,
        model: str,
        temperature: float
    ) -> str:
        """
        生成缓存键
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            
        Returns:
            缓存键
        """
        # 创建一个包含所有相关参数的字符串
        cache_input = json.dumps({
            "messages": messages,
            "model": model,
            "temperature": temperature
        }, sort_keys=True)
        
        # 生成哈希
        return hashlib.sha256(cache_input.encode()).hexdigest()
    
    async def get(
        self,
        messages: list,
        model: str,
        temperature: float = 0.7
    ) -> Optional[Any]:
        """
        获取缓存的响应
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            
        Returns:
            缓存的响应，如果不存在则返回None
        """
        if not self.enabled:
            return None
        
        cache_key = self._generate_cache_key(messages, model, temperature)
        entry = await self.backend.get(cache_key)
        
        if entry:
            return entry.value
        
        return None
    
    async def set(
        self,
        messages: list,
        model: str,
        response: Any,
        temperature: float = 0.7,
        ttl: Optional[int] = None
    ) -> bool:
        """
        设置缓存
        
        Args:
            messages: 消息列表
            model: 模型名称
            response: 响应内容
            temperature: 温度参数
            ttl: 过期时间（秒）
            
        Returns:
            是否成功
        """
        if not self.enabled:
            return False
        
        cache_key = self._generate_cache_key(messages, model, temperature)
        
        entry = CacheEntry(
            key=cache_key,
            value=response,
            timestamp=time.time(),
            ttl=ttl or self.default_ttl
        )
        
        return await self.backend.set(entry)
    
    async def clear(self) -> bool:
        """清空所有缓存"""
        return await self.backend.clear()
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        stats = await self.backend.get_stats()
        stats["enabled"] = self.enabled
        stats["default_ttl"] = self.default_ttl
        return stats
    
    def enable(self):
        """启用缓存"""
        self.enabled = True
    
    def disable(self):
        """禁用缓存"""
        self.enabled = False
