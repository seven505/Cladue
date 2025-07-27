import json
import base64
import time
import os

def generate_clash_config(nodes):
    proxies = []
    proxy_names = []

    for node in nodes:
        name = node['enhanced_name']
        proxy_names.append(name)

        if node['protocol'] == 'vmess':
            proxy = {
                'name': name,
                'type': 'vmess',
                'server': node['server'],
                'port': node['port'],
                'uuid': node['uuid'],
                'alterId': 0,
                'cipher': node.get('method', 'auto'),
                'network': node.get('network', 'tcp'),
                'udp': True
            }
            if node.get('tls'):
                proxy['tls'] = True
            if node.get('host'):
                proxy['servername'] = node['host']
            if node.get('path') and node.get('network') == 'ws':
                proxy['ws-opts'] = {'path': node['path']}
                if node.get('host'):
                    proxy['ws-opts']['headers'] = {'Host': node['host']}
            proxies.append(proxy)

    country_groups = {}
    for node in nodes:
        country = node['country']
        if country not in country_groups:
            country_groups[country] = []
        country_groups[country].append(node['enhanced_name'])

    proxy_groups = [
        {
            'name': '🚀 节点选择',
            'type': 'select',
            'proxies': ['♻️ 自动选择', '🔯 故障转移'] + proxy_names[:10]
        },
        {
            'name': '♻️ 自动选择',
            'type': 'url-test',
            'proxies': proxy_names,
            'url': 'http://www.gstatic.com/generate_204',
            'interval': 300,
            'tolerance': 150
        },
        {
            'name': '🔯 故障转移',
            'type': 'fallback',
            'proxies': proxy_names
        }
    ]

    for country, names in country_groups.items():
        proxy_groups.append({
            'name': f'🌐 {country}',
            'type': 'select',
            'proxies': names
        })

    config = {
        'port': 7890,
        'socks-port': 7891,
        'redir-port': 7892,
        'allow-lan': True,
        'mode': 'Rule',
        'log-level': 'info',
        'proxies': proxies,
        'proxy-groups': proxy_groups,
        'rules': [
            'DOMAIN-SUFFIX,google.com,🚀 节点选择',
            'DOMAIN-KEYWORD,youtube,🚀 节点选择',
            'FINAL,🔯 故障转移'
        ]
    }
    return config

def main():
    with open('test_results.json', 'r', encoding='utf-8') as f:
        test_report = json.load(f)

    alive_nodes = [n for n in test_report['results'] if n['is_alive']]
    for node in alive_nodes:
        # 给节点名字加上延迟和速度标记
        node['enhanced_name'] = f"{node['name']} | {int(node['tcp_ping'])}ms | {node['download_speed']:.2f}MB/s"

    config = generate_clash_config(alive_nodes)

    with open('clash_generated.yaml', 'w', encoding='utf-8') as f:
        import yaml
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)

    print("✅ Clash 配置文件生成成功: clash_generated.yaml")

if __name__ == "__main__":
    main()
