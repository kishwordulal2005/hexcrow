import argparse
import glob
import hashlib
import os
import random
import re
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import banner

for stream in (sys.stdout, sys.stderr):
    if stream and hasattr(stream, 'reconfigure'):
        try:
            stream.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass


def ensure_package(name):
    try:
        __import__(name)
        return True
    except ImportError:
        print('[\033[1;33m*\033[0m] %s is not installed, installing now...' % name)
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--quiet', name])
            print('[\033[1;32m+\033[0m] %s installed successfully' % name)
            return True
        except Exception as e:
            print('[\033[1;31m!\033[0m] failed to install %s: %s' % (name, e))
            return False


if not ensure_package('requests'):
    sys.exit(1)

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

C = {
    'black': '\033[30m',
    'red': '\033[1;31m',
    'green': '\033[1;32m',
    'yellow': '\033[1;33m',
    'blue': '\033[1;34m',
    'magenta': '\033[1;35m',
    'cyan': '\033[1;36m',
    'white': '\033[1;37m',
    'gray': '\033[90m',
    'dim': '\033[2m',
    'bold': '\033[1m',
    'bg_green': '\033[42m',
    'bg_cyan': '\033[46m',
    'bg_yellow': '\033[43m',
    'bg_red': '\033[41m',
    'reset': '\033[0m',
}


def color(name, text):
    return C[name] + text + C['reset']


def badge(text, bg='bg_green'):
    return C[bg] + C['black'] + C['bold'] + ' ' + text + ' ' + C['reset']


def build_banner():
    banners = getattr(banner, 'BANNERS', None)
    if banners:
        return random.choice(banners)
    if hasattr(banner, 'get_banner'):
        return banner.get_banner()
    return ''


BANNER = build_banner()

TITLE_RE = re.compile(r'<title[^>]*>(.*?)</title>', re.I | re.S)
PASSWORD_RE = re.compile(r'type=["\']?password', re.I)
LOGIN_RE = re.compile(r'(login|sign\s*in|log\s*in|username|password|authenticate|access\s+denied)', re.I)
FORM_RE = re.compile(r'<form[^>]*action=["\']([^"\']*)["\']', re.I)
LOCATION_HINT_RE = re.compile(r'(login|admin|auth|signin|logon|panel|user|dashboard)', re.I)

PANELS = [
    (r'phpmyadmin', 'phpMyAdmin'),
    (r'wordpress|wp-content|wp-login', 'WordPress'),
    (r'joomla|com_content', 'Joomla'),
    (r'drupal|sites/default/files', 'Drupal'),
    (r'cpanel|whm', 'cPanel'),
    (r'webmin', 'Webmin'),
    (r'plesk', 'Plesk'),
    (r'jenkins', 'Jenkins'),
    (r'grafana', 'Grafana'),
    (r'kibana', 'Kibana'),
    (r'sonarqube', 'SonarQube'),
    (r'citrix', 'Citrix'),
    (r'openvpn', 'OpenVPN'),
    (r'pfsense', 'pfSense'),
    (r'fortigate|fortinet', 'FortiGate'),
    (r'sophos', 'Sophos'),
    (r'meraki', 'Cisco Meraki'),
    (r'ubiquiti|unifi', 'Ubiquiti UniFi'),
    (r'gitea', 'Gitea'),
    (r'nextcloud', 'Nextcloud'),
    (r'owncloud', 'ownCloud'),
    (r'roundcube', 'Roundcube'),
    (r'zabbix', 'Zabbix'),
    (r'nagios', 'Nagios'),
    (r'icinga', 'Icinga'),
]

TAG_COLORS = {
    'password-field': 'yellow',
    'title': 'cyan',
    'login-form': 'cyan',
    'http-auth': 'red',
    'redirect-login': 'magenta',
    'forbidden': 'yellow',
}

WORDLIST_URL = 'https://raw.githubusercontent.com/maurosoria/dirsearch/master/db/dicc.txt'
BIG_WORDLIST_FILE = 'dicc.txt'
MIN_WORDLIST = 5000
EXTENSIONS = ['php', 'asp', 'aspx', 'jsp', 'html', 'htm', 'cgi', 'pl']
UA_POOL = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Vivaldi/6.7',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Brave/1.67.123',
]


def rand_headers():
    return {
        'User-Agent': random.choice(UA_POOL),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': random.choice(['en-US,en;q=0.9', 'en-GB,en;q=0.8', 'en-US,en;q=0.5', 'en;q=0.7']),
    }

EMBEDDED = [
    '/admin/', '/admin', '/login', '/login.php', '/login.asp', '/login.html',
    '/admin/login.php', '/admin/index.php', '/administrator/', '/administrator/index.php',
    '/wp-admin/', '/wp-login.php', '/phpmyadmin/', '/adminer.php', '/dbadmin/',
    '/cpanel/', '/webmail/', '/panel/', '/dashboard/', '/user/login', '/signin',
    '/auth/', '/account/', '/adminpanel/', '/admin-panel/', '/admin_area/', '/manage/',
    '/manager/', '/controlpanel/', '/control-panel/', '/cms/', '/backend/', '/adm/',
    '/sysadmin/', '/system/', '/portal/', '/secure/', '/staff/', '/superadmin/',
    '/webadmin/', '/api/', '/console/', '/shell/', '/backup/', '/config/', '/config.php',
]

state = {
    'done': 0,
    'found': 0,
    'panels': 0,
    'errors': 0,
    'filtered': 0,
    'start': 0.0,
    'stop': False,
    'lock': threading.Lock(),
    'denied': {},
    'throttle': 0.0,
    'out': None,
    'out_lock': threading.Lock(),
    'dirs': [],
    'panel_urls': [],
}
base = ''


def clear_line():
    sys.stdout.write('\r\033[2K')
    sys.stdout.flush()


def status_badge(st):
    if st < 300:
        c = 'green'
    elif st < 400:
        c = 'yellow'
    elif st in (401, 403):
        c = 'red'
    elif st < 500:
        c = 'yellow'
    else:
        c = 'red'
    return color(c, '[%d]' % st)


def fmt_tag(t):
    if t.startswith('-> '):
        return color('magenta', t)
    return color(TAG_COLORS.get(t, 'green'), t)


def rich_row(segs, width):
    total = sum(len(t) for t, _ in segs)
    pad = max(0, width - total)
    out = ''
    for i, (t, cname) in enumerate(segs):
        if i == len(segs) - 1:
            t = t + ' ' * pad
        out += color(cname, t) if cname else t
    return out


def build_session(timeout, retries, ua, extra_headers, proxy):
    s = requests.Session()
    retry = Retry(
        total=retries,
        connect=retries,
        read=retries,
        backoff_factor=0.4,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=['GET'],
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=100, pool_maxsize=100)
    s.mount('http://', adapter)
    s.mount('https://', adapter)
    hdrs = {
        'User-Agent': ua,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    hdrs.update(extra_headers)
    s.headers.update(hdrs)
    if proxy:
        s.proxies.update({'http': proxy, 'https': proxy})
    return s


def page_text(r):
    try:
        return r.content.decode(r.encoding or 'utf-8', errors='ignore')[:300000]
    except Exception:
        return ''


def title_of(r):
    m = TITLE_RE.search(page_text(r))
    return re.sub(r'\s+', ' ', m.group(1)).strip() if m else ''


def calibrate(session, timeout, probe=None, samples=12):
    baseline = []
    if probe is not None:
        baseline.append({
            'status': probe.status_code,
            'size': len(probe.content),
            'hash': hashlib.md5(probe.content).hexdigest(),
        })
    for _ in range(samples):
        junk = base + '/' + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(6, 14))) \
            + random.choice(['', '.zzz', '.php', '.asp', '.html', '.bak', '~'])
        try:
            r = session.get(junk, timeout=timeout, allow_redirects=True, headers=rand_headers())
            baseline.append({
                'status': r.status_code,
                'size': len(r.content),
                'hash': hashlib.md5(r.content).hexdigest(),
            })
        except requests.exceptions.RequestException:
            pass
    return baseline


def analyze(path, r, baseline, follow):
    status = r.status_code
    size = len(r.content)
    text = page_text(r)
    m = TITLE_RE.search(text)
    title = re.sub(r'\s+', ' ', m.group(1)).strip() if m else ''
    body_hash = hashlib.md5(r.content).hexdigest()
    fp = False
    if status in (404, 410):
        fp = True
    elif baseline:
        for b in baseline:
            if body_hash == b['hash'] or (size == b['size'] and status == b['status']):
                fp = True
                break
    if fp:
        return {'path': path, 'status': status, 'size': size, 'title': title,
                'score': 0, 'fp': True, 'tags': [], 'history': len(r.history)}
    if status >= 400:
        sig = (status, size)
        with state['lock']:
            n = state['denied'].get(sig, 0) + 1
            state['denied'][sig] = n
            if n >= 5:
                fp = True
    if fp:
        return {'path': path, 'status': status, 'size': size, 'title': title,
                'score': 0, 'fp': True, 'tags': [], 'history': len(r.history)}
    score = 0
    tags = []
    hard = False
    if PASSWORD_RE.search(text):
        score += 3
        hard = True
        tags.append('password-field')
    if title and re.search(r'(admin|login|sign\s*in|dashboard|panel|control|auth)', title, re.I):
        score += 2
        tags.append('title')
    if LOGIN_RE.search(text):
        score += 1
    fm = FORM_RE.search(text)
    if fm and LOCATION_HINT_RE.search(fm.group(1)):
        score += 2
        hard = True
        tags.append('login-form')
    for pat, name in PANELS:
        if re.search(pat, text, re.I):
            score += 3
            hard = True
            tags.append(name)
            break
    if status == 401:
        score += 2
        hard = True
        tags.append('http-auth')
    if not follow and status in (301, 302, 303, 307, 308):
        loc = r.headers.get('Location', '')
        if LOCATION_HINT_RE.search(loc):
            score += 2
            hard = True
            tags.append('redirect-login')
        if loc:
            tags.append('-> ' + loc[:60])
    if status == 403:
        score += 1
        tags.append('forbidden')
    if status >= 400 and not hard:
        score = min(score, 1)
    return {'path': path, 'status': status, 'size': size, 'title': title,
            'score': score, 'fp': fp, 'tags': tags, 'history': len(r.history), 'hard': hard}


def progress(total):
    elapsed = max(time.time() - state['start'], 0.001)
    rps = state['done'] / elapsed
    pct = state['done'] * 100.0 / total if total else 0.0
    bar_w = 20
    filled = int(round(bar_w * pct / 100.0))
    bar = C['green'] + '\u2588' * filled + C['gray'] + '\u2591' * (bar_w - filled) + C['reset']
    sys.stdout.write(
        '\r' + bar + ' ' + color('cyan', '%5.1f%%' % pct) + color('gray', ' [%d/%d]' % (state['done'], total))
        + '  ' + color('green', 'found %d' % state['found'])
        + '  ' + color('green', 'panels %d' % state['panels'])
        + '  ' + color('red', 'err %d' % state['errors'])
        + '  ' + color('magenta', '%.1f req/s' % rps))
    sys.stdout.flush()


def report(res, args, total):
    with state['lock']:
        state['done'] += 1
        if res is None:
            state['errors'] += 1
            if args.verbose:
                clear_line()
                print(color('red', '[!]') + ' ' + color('gray', 'request failed'))
            progress(total)
            return
        st = res['status']
        if args.show and st not in args.show:
            progress(total)
            return
        if res['fp']:
            state['filtered'] += 1
        url = base + res['path']
        score = res['score']
        hard = res.get('hard', False)
        is_panel = score >= 5 and hard
        if is_panel:
            state['panels'] += 1
            state['panel_urls'].append(url)
        if not res['fp']:
            state['found'] += 1
        if res['path'].endswith('/') and st < 400:
            state['dirs'].append(res['path'])
        clear_line()
        if is_panel:
            head = badge('ADMIN PANEL') + ' ' + color('bold', url) + ' ' + status_badge(st)
        elif res['fp']:
            head = color('dim', '[~]') + ' ' + color('dim', url) + ' ' + status_badge(st) + color('dim', ' (filtered)')
        elif score >= 2 and hard:
            head = badge('POSSIBLE PANEL', 'bg_cyan') + ' ' + color('cyan', url) + ' ' + status_badge(st)
        elif st < 400:
            head = color('green', '[+]') + ' ' + color('white', url) + ' ' + status_badge(st)
        elif st in (401, 403, 405):
            head = color('red', '[!]') + ' ' + color('white', url) + ' ' + status_badge(st)
        else:
            head = color('yellow', '[!]') + ' ' + color('white', url) + ' ' + status_badge(st)
        bits = []
        if res['size']:
            bits.append(color('gray', '%d B' % res['size']))
        if res['title']:
            bits.append(color('cyan', '"%s"' % res['title'][:70]))
        if res['history'] and args.follow:
            bits.append(color('gray', 'via %d redirect%s' % (res['history'], 's' if res['history'] > 1 else '')))
        bits += [fmt_tag(t) for t in res['tags']]
        line = head
        if bits:
            line += '  ' + color('gray', '\u2502'.join(bits))
        print(line)
        if state['out']:
            with state['out_lock']:
                state['out'].write('[%d] %s | %dB | %s | %s\n'
                                   % (st, url, res['size'], res['title'], '; '.join(res['tags'])))
                state['out'].flush()
        progress(total)


def adaptive_wait(args):
    time.sleep(args.delay + state['throttle'])


def throttle_update(status):
    with state['lock']:
        if status == 429:
            state['throttle'] = min(state['throttle'] + 0.5, 8.0)
        elif state['throttle'] > 0:
            state['throttle'] = max(0.0, state['throttle'] - 0.01)


def worker(path, session, args, baseline, total):
    if state['stop']:
        return
    try:
        adaptive_wait(args)
        r = session.get(base + path, timeout=args.timeout, allow_redirects=args.follow,
                        headers=rand_headers())
        throttle_update(r.status_code)
        report(analyze(path, r, baseline, args.follow), args, total)
    except requests.exceptions.RequestException:
        report(None, args, total)


def check_robots(session, timeout):
    try:
        r = session.get(base + '/robots.txt', timeout=timeout, allow_redirects=True, headers=rand_headers())
    except requests.exceptions.RequestException:
        clear_line()
        print(color('red', '[!]') + ' ' + color('gray', 'robots.txt check failed'))
        return
    text = page_text(r)
    if r.status_code == 200 and '<html' not in text.lower()[:2000]:
        print(color('green', '[+]') + ' ' + color('bold', 'robots.txt found:'))
        print(color('gray', text[:2000]))
    else:
        print(color('gray', '[-] no robots.txt'))


def load_wordlist(path, ftype, expand=False):
    words = []
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if '%EXT%' in line:
                    if not expand:
                        continue
                    for ext in EXTENSIONS:
                        words.append('/' + line.replace('%EXT%', ext).lstrip('/'))
                    continue
                if not line.startswith('/'):
                    line = '/' + line
                if ftype and not line.endswith('/') and ftype not in line:
                    continue
                words.append(line)
    except IOError:
        print(color('yellow', '[!]') + ' ' + color('bold', 'wordlist not found: ') + path)
        return []
    return list(dict.fromkeys(words))


def load_big_wordlist(ftype, expand=False):
    if not os.path.exists(BIG_WORDLIST_FILE):
        return None
    words = load_wordlist(BIG_WORDLIST_FILE, ftype, expand)
    return words or None


def download_big_wordlist(ftype, expand=False):
    print(color('yellow', '[+]') + ' downloading the bigger wordlist online...')
    try:
        r = requests.get(WORDLIST_URL, timeout=25,
                         headers={'User-Agent': 'hexcrow/2.0'})
        r.raise_for_status()
        remote = []
        for line in r.text.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '%EXT%' in line:
                if not expand:
                    continue
                for ext in EXTENSIONS:
                    remote.append('/' + line.replace('%EXT%', ext).lstrip('/'))
                continue
            if not line.startswith('/'):
                line = '/' + line
            remote.append(line)
        merged = list(dict.fromkeys(remote))
        with open(BIG_WORDLIST_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(merged) + '\n')
        print(color('green', '[+]') + ' fetched %d paths and saved to ' % len(merged)
              + color('bold', BIG_WORDLIST_FILE))
        if ftype:
            merged = [p for p in merged if p.endswith('/') or ftype in p]
        return merged
    except requests.exceptions.RequestException as e:
        print(color('red', '[!]') + ' download failed: %s' % e)
        return None
    except IOError as e:
        print(color('red', '[!]') + ' could not save wordlist: %s' % e)
        return None


def wait_futures(futures):
    for f in futures:
        while not f.done():
            time.sleep(0.05)
        f.result()


def choose_wordlist_interactive():
    txts = sorted(glob.glob('*.txt'))
    print(color('cyan', '\u25b8') + ' available wordlists in current directory:')
    if txts:
        for i, t in enumerate(txts, 1):
            try:
                size = os.path.getsize(t)
                sz = '%d KB' % (size // 1024) if size >= 1024 else '%d B' % size
            except OSError:
                sz = '?'
            print('    %s %s %s' % (color('yellow', '[%d]' % i), color('white', t), color('gray', '(' + sz + ')')))
    else:
        print(color('gray', '    (no .txt files found in current directory)'))
    print('    %s %s' % (color('yellow', '[0]'), color('white', 'enter a custom path')))
    while True:
        choice = input(color('cyan', 'wordlist') + color('gray', (' [1]' if txts else ' [0]')) + ': ').strip()
        if not choice:
            return txts[0] if txts else 'paths.txt'
        if choice.isdigit():
            n = int(choice)
            if n == 0:
                custom = input(color('cyan', 'custom wordlist path') + ': ').strip()
                return custom if custom else 'paths.txt'
            if 1 <= n <= len(txts):
                return txts[n - 1]
            print(color('red', '[!]') + ' invalid choice, pick a number from the list')
            continue
        return choice


def scan_paths(paths, session, args, baseline):
    total = len(paths)
    pool = ThreadPoolExecutor(max_workers=args.threads)
    futures = []
    try:
        for p in paths:
            if state['stop']:
                break
            futures.append(pool.submit(worker, p, session, args, baseline, total))
        wait_futures(futures)
    except KeyboardInterrupt:
        pool.shutdown(wait=False, cancel_futures=True)
        raise
    pool.shutdown(wait=False, cancel_futures=True)


def recursive_scan(seed_paths, session, args, baseline, wordlist):
    level = [p for p in seed_paths if p.endswith('/') and p != '/']
    seen = set(seed_paths)
    for depth in range(args.depth):
        if state['stop']:
            break
        if not level:
            break
        print(color('magenta', '\u25b8') + ' recursion level %d: scanning %d director%s'
              % (depth + 1, len(level), 'y' if len(level) == 1 else 'ies'))
        subs = []
        for d in level:
            for w in wordlist:
                sub = d.rstrip('/') + w
                if sub not in seen:
                    seen.add(sub)
                    subs.append(sub)
        if not subs:
            break
        captured = {'dirs': [], 'lock': threading.Lock()}
        rec_total = state['done'] + len(subs)

        def rec_worker(path):
            if state['stop']:
                return
            try:
                adaptive_wait(args)
                r = session.get(base + path, timeout=args.timeout, allow_redirects=args.follow,
                                headers=rand_headers())
                throttle_update(r.status_code)
                res = analyze(path, r, baseline, args.follow)
                if res['score'] >= 5 or (res['status'] < 400 and not res['fp']):
                    with captured['lock']:
                        if path.endswith('/'):
                            captured['dirs'].append(path)
                report(res, args, rec_total)
            except requests.exceptions.RequestException:
                report(None, args, rec_total)

        pool = ThreadPoolExecutor(max_workers=args.threads)
        futures = []
        try:
            for p in subs:
                if state['stop']:
                    break
                futures.append(pool.submit(rec_worker, p))
            wait_futures(futures)
        except KeyboardInterrupt:
            pool.shutdown(wait=False, cancel_futures=True)
            raise
        pool.shutdown(wait=False, cancel_futures=True)
        level = captured['dirs']


def summary_box(elapsed, rps):
    w = 70
    rows = [
        [('  time:      ', 'cyan'), ('%.1fs' % elapsed, 'bold')],
        [('  requests:  ', 'cyan'), ('%d' % state['done'], 'bold'), ('  at %.1f req/s' % rps, 'gray')],
        [('  found:     ', 'green'), ('%d' % state['found'], 'bold')],
        [('  panels:    ', 'green'), ('%d' % state['panels'], 'bold')],
        [('  filtered:  ', 'gray'), ('%d' % state['filtered'], 'bold'), ('  (WAF/404 noise)' if state['filtered'] else '', 'gray')],
        [('  errors:    ', 'red'), ('%d' % state['errors'], 'bold')],
    ]
    print('\n' + color('cyan', '\u2554' + '\u2550' * (w - 2) + '\u2557'))
    print(color('cyan', '\u2551') + color('bold', ' SCAN COMPLETE ').center(w - 2) + color('cyan', '\u2551'))
    print(color('cyan', '\u2560' + '\u2550' * (w - 2) + '\u2563'))
    for row in rows:
        print(color('cyan', '\u2551') + rich_row(row, w - 4) + ' ' + color('cyan', '\u2551'))
    print(color('cyan', '\u255a' + '\u2550' * (w - 2) + '\u255d'))


def panel_section(urls):
    w = 70
    inner = w - 4
    print('\n' + color('green', '\u2554' + '\u2550' * (w - 2) + '\u2557'))
    print(color('green', '\u2551') + color('bold', (' PANELS FOUND  %d ' % len(urls)).center(w - 2)) + color('green', '\u2551'))
    print(color('green', '\u2560' + '\u2550' * (w - 2) + '\u2563'))
    for u in urls:
        plain = u.ljust(inner - 14)
        print(color('green', '\u2551 ') + badge('ADMIN PANEL') + ' ' + color('bold', plain) + ' ' + color('green', '\u2551'))
    print(color('green', '\u255a' + '\u2550' * (w - 2) + '\u255d'))


def main():
    ap = argparse.ArgumentParser(description='hexcrow - modern admin panel hunter')
    ap.add_argument('-u', '--url', dest='target', help='target url, e.g. https://example.com')
    ap.add_argument('-w', '--wordlist', dest='wordlist', default='paths.txt')
    ap.add_argument('-t', '--threads', dest='threads', type=int, default=5)
    ap.add_argument('--delay', dest='delay', type=float, default=0.25,
                    help='delay in seconds between requests per thread (default 0.25)')
    ap.add_argument('-p', '--prefix', dest='prefix', help='custom path prefix added after the domain')
    ap.add_argument('--timeout', dest='timeout', type=float, default=10.0)
    ap.add_argument('--retries', dest='retries', type=int, default=2)
    ap.add_argument('-r', '--recursive', dest='recursive', action='store_true',
                    help='recursively scan found directories')
    ap.add_argument('--depth', dest='depth', type=int, default=2, help='recursion depth (default 2)')
    ap.add_argument('--type', dest='ftype', help='only test paths of this type: php, asp, html')
    ap.add_argument('-o', '--output', dest='output', help='save results to a file')
    ap.add_argument('--show', dest='show', help='only show these status codes, e.g. 200,301,403')
    ap.add_argument('-H', '--header', dest='headers', action='append', default=[],
                    help='extra header, e.g. -H "Cookie: x=1"')
    ap.add_argument('-A', '--user-agent', dest='ua',
                    default='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                            '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')
    ap.add_argument('-x', '--proxy', dest='proxy', help='proxy, e.g. http://127.0.0.1:8080')
    ap.add_argument('--no-follow', dest='follow', action='store_false',
                    help='do not follow redirects')
    ap.add_argument('--no-robots', dest='robots', action='store_false', help='skip robots.txt check')
    ap.add_argument('--update-wordlist', dest='update', action='store_true',
                    help='force download and merge the bigger online wordlist')
    ap.add_argument('--no-update', dest='no_update', action='store_true',
                    help='never auto-upgrade the wordlist online')
    ap.add_argument('--expand-ext', dest='expand_ext', action='store_true',
                    help='expand %%EXT%% entries into real extensions instead of skipping them')
    ap.add_argument('-v', '--verbose', dest='verbose', action='store_true')
    args = ap.parse_args()

    print(BANNER)
    print(color('magenta', '\u2550' * 68))
    print(color('yellow', '\u26a0 ') + color('bold', 'For authorized security testing only.'))
    print(color('magenta', '\u2550' * 68) + '\n')

    if not args.target:
        print(color('yellow', '[?]') + ' no target supplied, starting interactive mode')
        print(color('gray', '    press Ctrl+C anytime to abort\n'))
        try:
            args.target = input(color('cyan', 'target url') + color('gray', ' [e.g. https://example.com]') + ': ').strip()
            if not args.target:
                print(color('red', '[!]') + ' no target given')
                sys.exit(1)
            t = input(color('cyan', 'threads') + color('gray', ' [5]') + ': ').strip()
            if t.isdigit():
                args.threads = int(t)
            to = input(color('cyan', 'timeout (seconds)') + color('gray', ' [10]') + ': ').strip()
            if to:
                try:
                    args.timeout = float(to)
                except ValueError:
                    pass
            rec = input(color('cyan', 'recursive scan') + color('gray', ' [y/N]') + ': ').strip().lower()
            if rec in ('y', 'yes'):
                args.recursive = True
            if '-w' not in sys.argv and '--wordlist' not in sys.argv:
                args.wordlist = choose_wordlist_interactive()
            print()
        except (KeyboardInterrupt, EOFError):
            print()
            print(color('yellow', '[!]') + ' aborted')
            sys.exit(1)

    global base
    target = args.target.strip()
    if not re.match(r'^https?://', target, re.I):
        target = 'https://' + target
    base = target.rstrip('/')
    if args.prefix:
        if not args.prefix.startswith('/'):
            args.prefix = '/' + args.prefix
        base += args.prefix.rstrip('/')

    headers = {}
    for h in args.headers:
        if ':' in h:
            k, v = h.split(':', 1)
            headers[k.strip()] = v.strip()

    session = build_session(args.timeout, args.retries, args.ua, headers, args.proxy)

    try:
        probe = session.get(base, timeout=args.timeout, allow_redirects=True, headers=rand_headers())
    except requests.exceptions.SSLError:
        alt = base.replace('https://', 'http://', 1)
        print(color('yellow', '[!]') + ' SSL error on https, falling back to ' + color('bold', alt))
        base = alt
        try:
            probe = session.get(base, timeout=args.timeout, allow_redirects=True, headers=rand_headers())
        except requests.exceptions.RequestException:
            print(color('red', '[!]') + ' target is not reachable: ' + color('bold', base))
            sys.exit(1)
    except requests.exceptions.RequestException:
        print(color('red', '[!]') + ' target is not reachable: ' + color('bold', base))
        sys.exit(1)

    print(color('green', '[+]') + ' target online: ' + color('bold', probe.url) + ' '
          + status_badge(probe.status_code) + color('gray', '  %d B' % len(probe.content)))
    print('    ' + color('cyan', 'title:') + ' ' + color('white', title_of(probe) or '(none)'))

    if probe.status_code >= 400:
        print(color('red', '[!]') + ' the site itself returns ' + color('bold', '%d' % probe.status_code)
              + color('red', ' on the root page - the WAF/anti-bot is blocking all your requests'))
        print(color('red', '    ') + ' results will likely be empty. try a ' + color('bold', 'proxy')
              + color('red', ' (-x) from another region,') + color('bold', ' use a VPN,')
              + color('red', ' check if it opens in a browser,')
              + color('red', ' or use a different network/ISP'))

    if args.robots:
        check_robots(session, args.timeout)

    baseline = calibrate(session, args.timeout, probe=probe)
    if baseline:
        sig = ', '.join('%s:%dB' % (b['status'], b['size']) for b in baseline)
        print(color('gray', '[-] 404 baseline: ') + color('bold', sig) + color('gray', ' (responses matching this are filtered)'))

    words = load_wordlist(args.wordlist, args.ftype, args.expand_ext)
    if args.update or (len(words) < MIN_WORDLIST and not args.no_update):
        if len(words) < MIN_WORDLIST:
            print(color('gray', '[*] local wordlist only has %d paths (minimum %d recommended)'
                        % (len(words), MIN_WORDLIST)))
        if args.update:
            words = download_big_wordlist(args.ftype, args.expand_ext) or words
        else:
            big = load_big_wordlist(args.ftype, args.expand_ext)
            if big is not None:
                try:
                    ans = input(color('yellow', '[?]') + ' found ' + color('bold', BIG_WORDLIST_FILE)
                                + ' in current directory (%d paths), use it? ' % len(big)
                                + color('gray', '[y/N]') + ': ').strip().lower()
                    use_big = ans in ('y', 'yes')
                except (KeyboardInterrupt, EOFError):
                    use_big = False
                if use_big:
                    words = big
                    print(color('green', '[+]') + ' using ' + color('bold', BIG_WORDLIST_FILE)
                          + ' (%d paths)' % len(words))
                else:
                    print(color('gray', '[*] using local wordlist (%d paths)' % len(words)))
            else:
                try:
                    ans = input(color('yellow', '[?]') + ' download a bigger wordlist online and save to '
                                + color('bold', BIG_WORDLIST_FILE) + '? ' + color('gray', '[y/N]') + ': ').strip().lower()
                    do_fetch = ans in ('y', 'yes')
                except (KeyboardInterrupt, EOFError):
                    do_fetch = False
                if do_fetch:
                    words = download_big_wordlist(args.ftype, args.expand_ext) or words
                else:
                    print(color('gray', '[*] skipping online fetch, using local wordlist (%d paths)' % len(words)))
    if not words:
        words = [p for p in EMBEDDED if not args.ftype or p.endswith('/') or args.ftype in p]
    if not words:
        print(color('red', '[!]') + ' no wordlist available')
        sys.exit(1)
    print(color('magenta', '\u25b8') + ' scanning ' + color('bold', '%d paths' % len(words))
          + color('gray', ' with %d threads' % args.threads)
          + color('gray', ' (recursive)' if args.recursive else ''))
    print(color('magenta', '\u2550' * 68))

    if args.show:
        args.show = set(int(x) for x in args.show.split(',') if x.strip().isdigit())
    else:
        args.show = None

    if args.output:
        state['out'] = open(args.output, 'w', encoding='utf-8')

    state['start'] = time.time()
    try:
        scan_paths(words, session, args, baseline)
        if args.recursive:
            seed_paths = list(state['dirs'])
            recursive_scan(seed_paths, session, args, baseline, words)
    except KeyboardInterrupt:
        state['stop'] = True
        clear_line()
        print(color('yellow', '[!]') + ' interrupted by user, aborting...')
        if state['out']:
            state['out'].close()
        sys.stdout.flush()
        os._exit(130)

    elapsed = time.time() - state['start']
    rps = state['done'] / max(elapsed, 0.001)
    clear_line()
    summary_box(elapsed, rps)
    if state['panel_urls']:
        panel_section(state['panel_urls'])
    if state['out']:
        state['out'].close()
        print(color('cyan', '\u2550' * 68))
        print(color('green', '[+]') + ' results saved to ' + color('bold', args.output))


if __name__ == '__main__':
    main()
