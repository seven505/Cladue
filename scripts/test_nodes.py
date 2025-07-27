import asyncio
import aiohttp
import json
import time
import os

async def tcp_ping_test(host, port, timeout=5):
    try:
        start_time = time.time()
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout
        )
        ping_time = (time.time() - start_time) * 1000
        writer.close()
        await writer.wait_closed()
        return True, ping_time
    except:
        return False, -1

async def http_speed_test(session, test_url="http://www.gstatic.com/generate_204"):
    try:
        start_time = time.time()
        async with session.get(test_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            await response.read()
            return (time.time() - start_time) * 1000
    except:
        return -1

async def download_speed_test(session, size_mb=1):
    try:
        test_url = "https://proof.ovh.net/files/1Mb.dat"
        start_time = time.time()

        async with session.get(test_url, timeout=aiohttp.ClientTimeout(total=15)) as response:
            if response.status == 200:
                downloaded = 0
                async for chunk in response.content.iter_chunked(8192):
                    downloaded += len(chunk)
                    if time.time() - start_time > 10:
                        break
                elapsed = time.time() - start_time
                if elapsed > 0:
                    speed_mbps = (downloaded / 1024 / 1024) / elapsed
                    return speed_mbps
        return 0
    except:
        return 0

async def get_ip_info(session):
    try:
        async with session.get("https://httpbin.org/ip",
                               timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("origin", "未知")
        return "未知"
    except:
        return "检测失败"

async def test_streaming_unlock(session):
    results = {}
    try:
        async with session.get("https://www.netflix.com/",
                               timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status == 200:
                content = await response.text()
                if "Not Available" in content:
                    results['netflix'] = "❌ 不支持"
                else:
                    results['netflix'] = "✅ 可能支持"
            else:
                results['netflix'] = "❓ 检测失败"
    except:
        results['netflix'] = "❓ 超时"

    try:
        async with session.get("https://www.youtube.com/",
                               timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status == 200:
                results['youtube'] = "✅ 可访问"
            else:
                results['youtube'] = "❌ 无法访问"
    except:
        results['youtube'] = "❓ 超时"
    return results

async def test_single_node(node, test_mode):
    result = {
        'name': node['name'],
        'server': node['server'],
        'port': node['port'],
        'protocol': node['protocol'],
        'country': node['country'],
        'is_alive': False,
        'tcp_ping': -1,
        'http_ping': -1,
        'download_speed': 0,
        'ip_info': '未知',
        'streaming': {},
        'test_time': time.strftime('%Y-%m-%d %H:%M:%S'),
        'error': ''
    }

    try:
        print(f"🧪 测试节点: {node['name']}")

        is_alive, tcp_ping = await tcp_ping_test(node['server'], node['port'])
        result['is_alive'] = is_alive
        result['tcp_ping'] = tcp_ping

        if not is_alive:
            result['error'] = 'TCP连接失败'
            return result

        connector = aiohttp.TCPConnector(limit=1, ttl_dns_cache=300)
        async with aiohttp.ClientSession(connector=connector) as session:

            if test_mode in ['speed', 'full']:
                result['http_ping'] = await http_speed_test(session)
                result['download_speed'] = await download_speed_test(session)

            if test_mode == 'full':
                result['ip_info'] = await get_ip_info(session)
                result['streaming'] = await test_streaming_unlock(session)

        print(f"✅ 节点 {node['name']} 测试完成")

    except Exception as e:
        result['error'] = str(e)
        print(f"❌ 节点 {node['name']} 测试失败: {e}")

    return result

async def main():
    with open('raw_nodes.json', 'r', encoding='utf-8') as f:
        nodes = json.load(f)

    test_mode = os.environ.get('TEST_MODE', 'full')
    print(f"📊 开始测试 {len(nodes)} 个节点，模式: {test_mode}")

    semaphore = asyncio.Semaphore(3)

    async def test_with_limit(node):
        async with semaphore:
            return await test_single_node(node, test_mode)

    start_time = time.time()
    results = await asyncio.gather(*[test_with_limit(node) for node in nodes])
    elapsed = time.time() - start_time

    print(f"📊 测试完成，耗时 {elapsed:.2f} 秒")

    alive_nodes = [r for r in results if r['is_alive']]
    dead_nodes = [r for r in results if not r['is_alive']]

    stats = {
        'test_time': time.strftime('%Y-%m-%d %H:%M:%S'),
        'test_mode': test_mode,
        'total_nodes': len(results),
        'alive_nodes': len(alive_nodes),
        'dead_nodes': len(dead_nodes),
        'success_rate': len(alive_nodes) / len(results) * 100 if results else 0,
        'avg_tcp_ping': sum(r['tcp_ping'] for r in alive_nodes if r['tcp_ping'] > 0) / len(alive_nodes) if alive_nodes else 0,
        'avg_download_speed': sum(r['download_speed'] for r in alive_nodes) / len(alive_nodes) if alive_nodes else 0
    }

    country_stats = {}
    for result in alive_nodes:
        country = result['country']
        if country not in country_stats:
            country_stats[country] = {'total': 0, 'avg_ping': 0, 'avg_speed': 0}
        country_stats[country]['total'] += 1

    test_report = {
        'stats': stats,
        'country_stats': country_stats,
        'results': results
    }

    with open('test_results.json', 'w', encoding='utf-8') as f:
        json.dump(test_report, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
