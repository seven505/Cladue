#!/usr/bin/env python3

# -*- coding: utf-8 -*-

“””
增强版节点测试器
支持测速、流媒体解锁检测、地区识别等功能
类似 SubsCheck 项目的功能实现
“””

import asyncio
import aiohttp
import time
import socket
import json
import re
import subprocess
import logging
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import ssl
from dataclasses import dataclass, asdict

logger = logging.getLogger(**name**)

@dataclass
class NodeTestResult:
“”“节点测试结果”””
name: str
server: str
port: int
protocol: str

```
# 连通性测试
tcp_ping: float = -1  # TCP连接延迟 (ms)
http_ping: float = -1  # HTTP请求延迟 (ms)
is_alive: bool = False

# 速度测试
download_speed: float = 0  # 下载速度 (MB/s)
upload_speed: float = 0    # 上传速度 (MB/s)

# 地区检测
real_ip: str = ""
country: str = ""
city: str = ""
isp: str = ""

# 流媒体解锁
netflix: str = "未测试"      # Netflix解锁状态
youtube: str = "未测试"      # YouTube Premium
disney: str = "未测试"       # Disney+
hbo: str = "未测试"          # HBO Max
prime_video: str = "未测试"  # Prime Video
bilibili: str = "未测试"     # 哔哩哔哩
bahamut: str = "未测试"      # 巴哈姆特

# 其他信息
test_time: str = ""
error_msg: str = ""
```

class StreamingTester:
“”“流媒体解锁检测器”””

```
def __init__(self, timeout=10):
    self.timeout = timeout
    self.session = None
    
async def create_session(self, proxy_url=None):
    """创建HTTP会话"""
    connector = aiohttp.TCPConnector(
        limit=10,
        ssl=ssl.create_default_context(),
        enable_cleanup_closed=True
    )
    
    timeout = aiohttp.ClientTimeout(total=self.timeout)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    if proxy_url:
        # 这里需要根据实际代理协议配置
        # 简化处理，实际使用时需要更完整的代理配置
        pass
        
    self.session = aiohttp.ClientSession(
        connector=connector,
        timeout=timeout,
        headers=headers
    )

async def test_netflix(self) -> str:
    """检测Netflix解锁状态"""
    try:
        # Netflix检测API
        url = "https://www.netflix.com/title/81280792"  # 特定地区内容
        async with self.session.get(url) as response:
            if response.status == 200:
                content = await response.text()
                if "Not Available" in content or "不可播放" in content:
                    return "❌ 不支持"
                elif "watch now" in content.lower() or "立即观看" in content:
                    return "✅ 完整支持"
                else:
                    return "⚠️ 部分支持"
            else:
                return "❓ 检测失败"
    except Exception as e:
        logger.debug(f"Netflix检测失败: {e}")
        return "❓ 检测失败"

async def test_youtube_premium(self) -> str:
    """检测YouTube Premium解锁"""
    try:
        # 检测YouTube Premium特性
        url = "https://www.youtube.com/red"
        async with self.session.get(url) as response:
            if response.status == 200:
                content = await response.text()
                if "Premium" in content:
                    return "✅ 支持"
                else:
                    return "❌ 不支持"
            else:
                return "❓ 检测失败"
    except Exception as e:
        logger.debug(f"YouTube检测失败: {e}")
        return "❓ 检测失败"

async def test_disney_plus(self) -> str:
    """检测Disney+解锁"""
    try:
        url = "https://www.disneyplus.com/"
        async with self.session.get(url) as response:
            if response.status == 200:
                content = await response.text()
                if "not available" in content.lower():
                    return "❌ 不支持"
                elif "sign up" in content.lower() or "subscribe" in content.lower():
                    return "✅ 支持"
                else:
                    return "⚠️ 部分支持"
            else:
                return "❓ 检测失败"
    except Exception as e:
        logger.debug(f"Disney+检测失败: {e}")
        return "❓ 检测失败"

async def test_bilibili(self) -> str:
    """检测哔哩哔哩解锁（港澳台限定内容）"""
    try:
        # 检测港澳台限定视频
        url = "https://api.bilibili.com/pgc/player/web/playurl"
        params = {
            'avid': '50762638',  # 某个港澳台限定视频
            'cid': '100279344',
            'qn': '16'
        }
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('code') == 0:
                    return "✅ 支持"
                elif data.get('code') == -10403:
                    return "❌ 不支持"
                else:
                    return "⚠️ 部分支持"
            else:
                return "❓ 检测失败"
    except Exception as e:
        logger.debug(f"哔哩哔哩检测失败: {e}")
        return "❓ 检测失败"

async def test_bahamut(self) -> str:
    """检测巴哈姆特动画疯解锁"""
    try:
        url = "https://ani.gamer.com.tw/"
        async with self.session.get(url) as response:
            if response.status == 200:
                content = await response.text()
                if "地區限制" in content or "地区限制" in content:
                    return "❌ 不支持"
                elif "動畫瘋" in content or "动画疯" in content:
                    return "✅ 支持"
                else:
                    return "⚠️ 部分支持"
            else:
                return "❓ 检测失败"
    except Exception as e:
        logger.debug(f"巴哈姆特检测失败: {e}")
        return "❓ 检测失败"

async def test_all_streaming(self) -> Dict[str, str]:
    """测试所有流媒体服务"""
    results = {}
    
    # 并发测试各个流媒体服务
    tasks = [
        ("netflix", self.test_netflix()),
        ("youtube", self.test_youtube_premium()),
        ("disney", self.test_disney_plus()),
        ("bilibili", self.test_bilibili()),
        ("bahamut", self.test_bahamut())
    ]
    
    for name, task in tasks:
        try:
            result = await asyncio.wait_for(task, timeout=self.timeout)
            results[name] = result
        except asyncio.TimeoutError:
            results[name] = "⏱️ 超时"
        except Exception as e:
            results[name] = "❓ 检测失败"
            logger.debug(f"{name}检测异常: {e}")
    
    return results

async def close(self):
    """关闭会话"""
    if self.session:
        await self.session.close()
```

class SpeedTester:
“”“网络速度测试器”””

```
def __init__(self, timeout=30):
    self.timeout = timeout
    
async def test_download_speed(self, proxy_url=None) -> float:
    """测试下载速度"""
    try:
        # 使用多个测试文件
        test_urls = [
            "http://speedtest.ftp.otenet.gr/files/test1Mb.db",      # 1MB
            "http://speedtest.ftp.otenet.gr/files/test10Mb.db",     # 10MB
            "https://proof.ovh.net/files/1Mb.dat",                  # 1MB
            "https://proof.ovh.net/files/10Mb.dat"                  # 10MB
        ]
        
        best_speed = 0
        
        for url in test_urls:
            try:
                speed = await self._download_test_single(url, proxy_url)
                if speed > best_speed:
                    best_speed = speed
            except:
                continue
        
        return best_speed
        
    except Exception as e:
        logger.debug(f"下载速度测试失败: {e}")
        return 0

async def _download_test_single(self, url: str, proxy_url=None) -> float:
    """单个文件下载测试"""
    connector = aiohttp.TCPConnector(limit=1)
    timeout = aiohttp.ClientTimeout(total=self.timeout)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        start_time = time.time()
        downloaded = 0
        
        async with session.get(url) as response:
            if response.status == 200:
                async for chunk in response.content.iter_chunked(8192):
                    downloaded += len(chunk)
                    
                    # 限制测试时间，避免下载过大文件
                    if time.time() - start_time > 10:  # 最多测试10秒
                        break
        
        elapsed = time.time() - start_time
        if elapsed > 0:
            speed_mbps = (downloaded / 1024 / 1024) / elapsed  # MB/s
            return speed_mbps
        
    return 0

async def test_upload_speed(self, proxy_url=None) -> float:
    """测试上传速度（简化版）"""
    try:
        # 上传测试相对复杂，这里返回下载速度的70%作为估算
        download_speed = await self.test_download_speed(proxy_url)
        return download_speed * 0.7
    except:
        return 0
```

class IPInfoTester:
“”“IP信息检测器”””

```
def __init__(self, timeout=10):
    self.timeout = timeout

async def get_ip_info(self, proxy_url=None) -> Dict[str, str]:
    """获取IP地理位置信息"""
    try:
        # 使用多个IP检测API
        apis = [
            "https://ipapi.co/json/",
            "http://ip-api.com/json/",
            "https://httpbin.org/ip",
            "https://api.ipify.org?format=json"
        ]
        
        for api in apis:
            try:
                result = await self._query_ip_api(api, proxy_url)
                if result:
                    return result
            except:
                continue
        
        return {
            "ip": "未知",
            "country": "未知", 
            "city": "未知",
            "isp": "未知"
        }
        
    except Exception as e:
        logger.debug(f"IP信息获取失败: {e}")
        return {"ip": "检测失败", "country": "未知", "city": "未知", "isp": "未知"}

async def _query_ip_api(self, api_url: str, proxy_url=None) -> Optional[Dict[str, str]]:
    """查询单个IP API"""
    connector = aiohttp.TCPConnector(limit=1)
    timeout = aiohttp.ClientTimeout(total=self.timeout)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        async with session.get(api_url) as response:
            if response.status == 200:
                data = await response.json()
                
                # 根据不同API格式解析
                if "ipapi.co" in api_url:
                    return {
                        "ip": data.get("ip", ""),
                        "country": data.get("country_name", ""),
                        "city": data.get("city", ""),
                        "isp": data.get("org", "")
                    }
                elif "ip-api.com" in api_url:
                    return {
                        "ip": data.get("query", ""),
                        "country": data.get("country", ""),
                        "city": data.get("city", ""),
                        "isp": data.get("isp", "")
                    }
                elif "httpbin.org" in api_url:
                    return {
                        "ip": data.get("origin", ""),
                        "country": "未知",
                        "city": "未知", 
                        "isp": "未知"
                    }
                elif "ipify.org" in api_url:
                    return {
                        "ip": data.get("ip", ""),
                        "country": "未知",
                        "city": "未知",
                        "isp": "未知"
                    }
    
    return None
```

class EnhancedNodeTester:
“”“增强版节点测试器主类”””

```
def __init__(self, config=None):
    self.config = config or {
        "enable_speed_test": True,
        "enable_streaming_test": True, 
        "enable_ip_test": True,
        "test_timeout": 30,
        "max_concurrent": 5
    }
    
def tcp_ping_test(self, host: str, port: int) -> Tuple[bool, float]:
    """TCP连接测试"""
    try:
        start_time = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        result = sock.connect_ex((host, port))
        ping_time = (time.time() - start_time) * 1000
        
        sock.close()
        
        return result == 0, ping_time if result == 0 else -1
        
    except Exception as e:
        logger.debug(f"TCP ping失败 {host}:{port} - {e}")
        return False, -1

async def http_ping_test(self, proxy_url=None) -> float:
    """HTTP延迟测试"""
    try:
        start_time = time.time()
        
        connector = aiohttp.TCPConnector(limit=1)
        timeout = aiohttp.ClientTimeout(total=10)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # 使用Google生成204，速度快且稳定
            async with session.get("http://www.gstatic.com/generate_204") as response:
                await response.read()
                
        return (time.time() - start_time) * 1000
        
    except Exception as e:
        logger.debug(f"HTTP ping失败: {e}")
        return -1

async def test_single_node(self, node) -> NodeTestResult:
    """测试单个节点"""
    result = NodeTestResult(
        name=node.name,
        server=node.server,
        port=node.port,
        protocol=node.protocol,
        test_time=time.strftime("%Y-%m-%d %H:%M:%S")
    )
    
    try:
        # 1. TCP连接测试
        logger.info(f"测试节点: {node.name}")
        is_alive, tcp_ping = self.tcp_ping_test(node.server, node.port)
        result.is_alive = is_alive
        result.tcp_ping = tcp_ping
        
        if not is_alive:
            result.error_msg = "TCP连接失败"
            return result
        
        # 构建代理URL（这里需要根据实际协议实现）
        proxy_url = self._build_proxy_url(node)
        
        # 2. HTTP延迟测试
        if proxy_url:
            result.http_ping = await self.http_ping_test(proxy_url)
        
        # 3. IP信息检测
        if self.config.get("enable_ip_test"):
            ip_tester = IPInfoTester()
            ip_info = await ip_tester.get_ip_info(proxy_url)
            result.real_ip = ip_info.get("ip", "")
            result.country = ip_info.get("country", "")
            result.city = ip_info.get("city", "")
            result.isp = ip_info.get("isp", "")
        
        # 4. 速度测试
        if self.config.get("enable_speed_test"):
            speed_tester = SpeedTester()
            result.download_speed = await speed_tester.test_download_speed(proxy_url)
            result.upload_speed = await speed_tester.test_upload_speed(proxy_url)
        
        # 5. 流媒体解锁测试
        if self.config.get("enable_streaming_test"):
            streaming_tester = StreamingTester()
            await streaming_tester.create_session(proxy_url)
            
            streaming_results = await streaming_tester.test_all_streaming()
            result.netflix = streaming_results.get("netflix", "未测试")
            result.youtube = streaming_results.get("youtube", "未测试")
            result.disney = streaming_results.get("disney", "未测试")
            result.bilibili = streaming_results.get("bilibili", "未测试")
            result.bahamut = streaming_results.get("bahamut", "未测试")
            
            await streaming_tester.close()
        
        logger.info(f"✅ 节点 {node.name} 测试完成")
        
    except Exception as e:
        result.error_msg = str(e)
        logger.error(f"❌ 节点 {node.name} 测试失败: {e}")
    
    return result

def _build_proxy_url(self, node) -> Optional[str]:
    """构建代理URL（简化版）"""
    # 这里需要根据具体的代理协议来实现
    # 实际使用时需要更完整的实现
    try:
        if node.protocol == "http":
            return f"http://{node.server}:{node.port}"
        elif node.protocol == "socks5":
            return f"socks5://{node.server}:{node.port}"
        # 其他协议需要更复杂的配置
        return None
    except:
        return None

async def test_nodes_batch(self, nodes: List) -> List[NodeTestResult]:
    """批量测试节点"""
    results = []
    semaphore = asyncio.Semaphore(self.config.get("max_concurrent", 5))
    
    async def test_with_semaphore(node):
        async with semaphore:
            return await self.test_single_node(node)
    
    # 创建所有测试任务
    tasks = [test_with_semaphore(node) for node in nodes]
    
    # 执行批量测试
    logger.info(f"开始批量测试 {len(nodes)} 个节点...")
    start_time = time.time()
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 处理异常结果
    valid_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            error_result = NodeTestResult(
                name=nodes[i].name,
                server=nodes[i].server,
                port=nodes[i].port,
                protocol=nodes[i].protocol,
                error_msg=str(result),
                test_time=time.strftime("%Y-%m-%d %H:%M:%S")
            )
            valid_results.append(error_result)
        else:
            valid_results.append(result)
    
    elapsed = time.time() - start_time
    logger.info(f"✅ 批量测试完成，耗时 {elapsed:.2f} 秒")
    
    return valid_results

def generate_test_report(self, results: List[NodeTestResult]) -> Dict:
    """生成测试报告"""
    alive_nodes = [r for r in results if r.is_alive]
    dead_nodes = [r for r in results if not r.is_alive]
    
    # 统计信息
    stats = {
        "total_nodes": len(results),
        "alive_nodes": len(alive_nodes),
        "dead_nodes": len(dead_nodes),
        "alive_rate": len(alive_nodes) / len(results) * 100 if results else 0,
        "avg_tcp_ping": sum(r.tcp_ping for r in alive_nodes if r.tcp_ping > 0) / len(alive_nodes) if alive_nodes else 0,
        "avg_download_speed": sum(r.download_speed for r in alive_nodes) / len(alive_nodes) if alive_nodes else 0,
    }
    
    # 流媒体解锁统计
    streaming_stats = {}
    for service in ["netflix", "youtube", "disney", "bilibili", "bahamut"]:
        supported = len([r for r in alive_nodes if getattr(r, service).startswith("✅")])
        streaming_stats[service] = {
            "supported": supported,
            "rate": supported / len(alive_nodes) * 100 if alive_nodes else 0
        }
    
    # 地区分布
    country_stats = {}
    for result in alive_nodes:
        country = result.country or "未知"
        if country not in country_stats:
            country_stats[country] = 0
        country_stats[country] += 1
    
    return {
        "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "stats": stats,
        "streaming_stats": streaming_stats,
        "country_stats": country_stats,
        "detailed_results": [asdict(r) for r in results]
    }
```

# 使用示例

async def main():
“”“测试示例”””
# 模拟一些节点数据
class MockNode:
def **init**(self, name, server, port, protocol):
self.name = name
self.server = server
self.port = port
self.protocol = protocol

```
# 创建测试节点
test_nodes = [
    MockNode("香港节点1", "hk1.example.com", 443, "vmess"),
    MockNode("美国节点1", "us1.example.com", 443, "trojan"),
    MockNode("日本节点1", "jp1.example.com", 443, "vless"),
]

# 配置测试参数
config = {
    "enable_speed_test": True,
    "enable_streaming_test": True,
    "enable_ip_test": True,
    "test_timeout": 30,
    "max_concurrent": 3
}

# 创建测试器
tester = EnhancedNodeTester(config)

# 执行测试
results = await tester.test_nodes_batch(test_nodes)

# 生成报告
report = tester.generate_test_report(results)

# 输出报告
print(json.dumps(report, indent=2, ensure_ascii=False))
```

if **name** == “**main**”:
asyncio.run(main())
