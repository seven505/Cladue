import os
import json
import requests
import base64
import hashlib

def fetch_subscription(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        content = response.text.strip()
        try:
            decoded = base64.b64decode(content).decode('utf-8')
            content = decoded
        except:
            pass

        links = [line.strip() for line in content.split('\n')
                 if line.strip() and any(line.startswith(p) for p in ['vmess://', 'vless://', 'trojan://', 'ss://'])]

        print(f"从 {url[:50]}... 获取到 {len(links)} 个节点")
        return links
    except Exception as e:
        print(f"获取订阅失败 {url}: {e}")
        return []

def parse_vmess(url):
    import json
    try:
        data = json.loads(base64.b64decode(url[8:]).decode('utf-8'))
        return {
            'protocol': 'vmess',
            'name': data.get('ps', ''),
            'server': data.get('add', ''),
            'port': int(data.get('port', 443)),
            'uuid': data.get('id', ''),
            'method': data.get('scy', 'auto'),
            'network': data.get('net', 'tcp'),
            'path': data.get('path', ''),
            'host': data.get('host', ''),
            'tls': data.get('tls', ''),
            'raw_url': url
        }
    except:
        return None

def parse_node(url):
    if url.startswith('vmess://'):
        return parse_vmess(url)
    # TODO: 其他协议解析，可继续补充
    return None

def detect_country(server, name):
    text = (server + ' ' + name).lower()
    countries = {
        'HK': ['hk', 'hong-kong', 'hongkong', '香港'],
        'TW': ['tw', 'taiwan', 'taipei', '台湾'],
        'US': ['us', 'usa', 'america', 'united-states'],
        'JP': ['jp', 'japan', 'tokyo', '日本'],
        'SG': ['sg', 'singapore', '新加坡'],
        'KR': ['kr', 'korea', 'seoul', '韩国']
    }
    for code, keywords in countries.items():
        if any(k in text for k in keywords):
            return code
    return 'UN'

def main():
    env_subs = os.environ.get('SUBSCRIPTION_URLS', '')
    if not env_subs:
        print("❌ 未配置订阅链接")
        exit(1)

    subscription_urls = [url.strip() for url in env_subs.split(',') if url.strip()]
    print(f"📋 配置了 {len(subscription_urls)} 个订阅源")

    all_links = []
    for url in subscription_urls:
        links = fetch_subscription(url)
        all_links.extend(links)

    print(f"📊 总共获取 {len(all_links)} 个原始节点")

    nodes = []
    for url in all_links:
        node = parse_node(url)
        if node and node['server'] and node['port']:
            node['country'] = detect_country(node['server'], node['name'])
            hash_str = f"{node['server']}:{node['port']}:{node['uuid']}"
            node['hash'] = hashlib.md5(hash_str.encode()).hexdigest()
            nodes.append(node)

    seen_hashes = set()
    unique_nodes = []
    for node in nodes:
        if node['hash'] not in seen_hashes:
            seen_hashes.add(node['hash'])
            unique_nodes.append(node)

    print(f"✅ 解析并去重后得到 {len(unique_nodes)} 个有效节点")

    max_test = int(os.environ.get('INPUT_MAX_NODES', '50'))
    if len(unique_nodes) > max_test:
        priority = {'HK': 1, 'TW': 2, 'SG': 3, 'JP': 4, 'KR': 5, 'US': 6}
        unique_nodes.sort(key=lambda x: priority.get(x['country'], 99))
        unique_nodes = unique_nodes[:max_test]
        print(f"📊 限制测试节点数量为 {max_test}")

    with open('raw_nodes.json', 'w', encoding='utf-8') as f:
        json.dump(unique_nodes, f, ensure_ascii=False, indent=2)

    print("✅ 节点获取完成，准备进行测试")

if __name__ == "__main__":
    main()
