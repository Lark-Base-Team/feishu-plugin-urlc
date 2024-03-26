import mmh3
import base62

def generate_short_url(long_url):
    m = mmh3.hash(long_url.encode('utf-8'), signed=False)
    res = base62.encode(m)
    return res

if __name__ == '__main__':
    r = generate_short_url('https://juejin.cn/post/7057083730686377997')
    print(r)
