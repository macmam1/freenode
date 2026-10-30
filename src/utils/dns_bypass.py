"""
DNS Bypass Utilities برای محیط CoCalc

این ماژول توابعی برای حل DNS با استفاده از DNS‑over‑HTTPS (DoH) فراهم می‌کند.
"""

import urllib.request
import json
import socket
import sys

# کش ساده برای نتایج DNS
DNS_CACHE = {}

# سرورهای DoH عمومی (IP مستقیم برای دور زدن DNS داخلی)
DOH_SERVERS = [
    ("104.16.132.229", "1.1.1.1"),  # Cloudflare DoH
    ("8.8.8.8", "dns.google"),       # Google DNS (در صورت دسترس)
]
def resolve_via_doh(domain, timeout=5):
    """حل DNS با DoH fallback.
    
    Args:
        domain (str): اسم دامنه برای حل.
        timeout (int): زمان انتظار برای پاسخ.
    
    Returns:
        str|None: آدرس IPv4 یا None در صورت شکست.
    """
    if domain in DNS_CACHE:
        return DNS_CACHE[domain]
    
    for doh_ip, doh_host in DOH_SERVERS:
        try:
            # ساخت URL DoH با IP مستقیم
            url = f"https://{doh_ip}/dns-query?name={domain}&type=A"
            req = urllib.request.Request(
                url,
                headers={
                    "Host": doh_host,
                    "Accept": "application/dns-json"
                }
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read())
                if 'Answer' in data and len(data['Answer']) > 0:
                    ip = data['Answer'][0]['data']
                    DNS_CACHE[domain] = ip
                    return ip
        except Exception as e:
            # ثبت خطا برای دیباگ (به stderr)
            print(f"[DoH] Failed for {domain} via {doh_ip}: {e}", file=sys.stderr)
            continue
    
    return None


def patch_socket_getaddrinfo():
    """Monkey‑patch socket.getaddrinfo برای استفاده از DoH fallback"""
    original = socket.getaddrinfo
    
    def patched(host, port, family=0, type=0, proto=0, flags=0):
        try:
            return original(host, port, family, type, proto, flags)
        except socket.gaierror:
            ip = resolve_via_doh(host)
            if ip:
                # بازگشت یک tuple مشابه خروجی getaddrinfo
                return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (ip, port))]
            raise
    
    socket.getaddrinfo = patched
    print("[DNS Bypass] socket.getaddrinfo patched", file=sys.stderr)


def patch_urllib():
    """Monkey‑patch urllib.request.urlopen برای استفاده از DoH fallback"""
    original = urllib.request.urlopen
    
    def patched(url, data=None, timeout=None, **kwargs):
        from urllib.parse import urlparse
        parsed = urlparse(url)
        if parsed.scheme in ('http', 'https') and parsed.netloc:
            domain = parsed.netloc.split(':')[0]
            ip = resolve_via_doh(domain)
            if ip:
                # جایگزینی دامنه با IP
                url = url.replace(parsed.netloc, ip)
                # اضافه کردن Host header
                headers = kwargs.get('headers', {})
                if not isinstance(headers, dict):
                    headers = {}
                headers['Host'] = domain
                kwargs['headers'] = headers
        return original(url, data=data, timeout=timeout, **kwargs)
    
    urllib.request.urlopen = patched
    print("[DNS Bypass] urllib.request.urlopen patched", file=sys.stderr)


def enable_all():
    """فعال‌سازی تمام پچ‌ها"""
    patch_socket_getaddrinfo()
    patch_urllib()

if __name__ == '__main__':
    # برای تست سریع
    print(resolve_via_doh('github.com'))
