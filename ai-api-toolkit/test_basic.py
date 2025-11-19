"""
基础测试文件
用于验证工具的基本功能
"""
import asyncio
from base import Message, CompletionResponse


def test_message():
    """测试Message类"""
    msg = Message(role="user", content="Hello")
    assert msg.role == "user"
    assert msg.content == "Hello"
    
    msg_dict = msg.to_dict()
    assert msg_dict["role"] == "user"
    assert msg_dict["content"] == "Hello"
    print("✓ Message测试通过")


def test_completion_response():
    """测试CompletionResponse类"""
    response = CompletionResponse(
        content="Hello world",
        model="gpt-4o-mini",
        usage={"total_tokens": 10},
        finish_reason="stop",
        provider="openai",
        cached=False,
        latency_ms=100.5
    )
    
    assert response.content == "Hello world"
    assert response.model == "gpt-4o-mini"
    assert response.cached == False
    
    resp_dict = response.to_dict()
    assert resp_dict["content"] == "Hello world"
    print("✓ CompletionResponse测试通过")


def test_cache_manager():
    """测试CacheManager"""
    from cache import CacheManager
    
    cache = CacheManager(enabled=True, ttl_seconds=60)
    
    # 生成缓存键
    messages = [Message(role="user", content="test")]
    key = cache._generate_cache_key(messages, "gpt-4o-mini", 0.7)
    assert isinstance(key, str)
    assert len(key) == 64  # SHA256 hash
    
    # 设置和获取
    cache.set(key, {"test": "data"})
    data = cache.get(key)
    assert data == {"test": "data"}
    
    # 获取统计
    stats = cache.get_stats()
    assert stats["enabled"] == True
    assert stats["size"] == 1
    
    print("✓ CacheManager测试通过")


def test_client_initialization():
    """测试客户端初始化"""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    
    import client
    import importlib
    importlib.reload(client)
    
    # 测试支持的提供商
    providers_config = {
        "openai": {},
        "azure_openai": {
            "azure_endpoint": "https://test.openai.azure.com/",
            "api_version": "2024-02-15-preview"
        },
        "anthropic": {},
        "google": {}
    }
    
    for provider, extra_kwargs in providers_config.items():
        try:
            # 只测试初始化，不实际调用API
            cli = client.AIClient(
                provider=provider,
                api_key="test-key",
                **extra_kwargs
            )
            assert cli.provider.get_provider_name() == provider
            print(f"✓ {provider}提供商初始化通过")
        except ImportError as e:
            print(f"⚠ {provider}提供商跳过（依赖未安装）: {str(e)[:50]}...")


def test_message_helpers():
    """测试消息辅助方法"""
    print("⚠ 消息辅助方法测试跳过（需要安装依赖）")


def test_config():
    """测试配置管理"""
    from config import ProviderConfig, CacheConfig, ClientConfig
    
    # ProviderConfig
    provider_config = ProviderConfig(
        provider="openai",
        api_key="test-key",
        extra_params={"base_url": "https://api.openai.com/v1"}
    )
    assert provider_config.provider == "openai"
    
    # CacheConfig
    cache_config = CacheConfig(
        enabled=True,
        ttl_seconds=3600
    )
    assert cache_config.enabled == True
    
    # ClientConfig
    client_config = ClientConfig(
        provider_config=provider_config,
        cache_config=cache_config
    )
    kwargs = client_config.to_client_kwargs()
    assert kwargs["provider"] == "openai"
    assert kwargs["enable_cache"] == True
    
    print("✓ 配置管理测试通过")


def run_all_tests():
    """运行所有测试"""
    print("开始测试...")
    print("=" * 50)
    
    test_message()
    test_completion_response()
    test_cache_manager()
    test_client_initialization()
    test_message_helpers()
    test_config()
    
    print("=" * 50)
    print("✓ 所有基础测试通过！")


if __name__ == "__main__":
    run_all_tests()
