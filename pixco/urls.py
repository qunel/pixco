"""
URL configuration for pixco project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time

_board_cache = {}  # {(board_url, page): (timestamp, threads)}
CACHE_TTL = 300    # 5分
MAX_PAGES = 10

def _fetch_board_page(board_url, page_num):
    key = (board_url, page_num)
    now = time.time()
    cached = _board_cache.get(key)
    if cached and now - cached[0] < CACHE_TTL:
        return cached[1]

    parsed = urlparse(board_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    board_dir = parsed.path.rsplit("/", 1)[0]
    page_url = board_url if page_num == 0 else f"{base_url}{board_dir}/{page_num}.htm"

    res = requests.get(page_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    if res.status_code != 200:
        return []
    soup = BeautifulSoup(res.content, "html.parser", from_encoding="shift_jis")

    threads = []
    for div in soup.find_all("div", class_="thre"):
        img_tag = div.find("img", src=True)
        subject = div.find("span", class_="csb")
        comment = div.find("blockquote")
        reply_link = div.find("a", class_="hsbn")
        if not img_tag:
            continue
        thumb_src = img_tag["src"]
        full_src = thumb_src.replace("/thumb/", "/src/").replace("s.jpg", ".jpg")
        res_url = (base_url + board_dir + "/" + reply_link["href"].lstrip("/")) if reply_link else ""
        threads.append({
            "thumb": base_url + thumb_src,
            "full": base_url + full_src,
            "title": subject.get_text(strip=True) if subject else "無題",
            "comment": comment.get_text(strip=True)[:80] if comment else "",
            "res_url": res_url,
        })
    _board_cache[key] = (now, threads)
    return threads

def home(request):
    return render(request, 'home.html')

def profile(request):
    return render(request, 'profile.html')


BOARDS = [
    {"name": "ホロライブ",   "url": "https://dec.2chan.net/84/futaba.htm"},
    {"name": "避難所",       "url": "https://www.2chan.net/hinan/futaba.htm"},
    {"name": "野球",         "url": "https://zip.2chan.net/1/futaba.htm"},
    {"name": "サッカー",     "url": "https://zip.2chan.net/12/futaba.htm"},
    {"name": "麻雀",         "url": "https://may.2chan.net/25/futaba.htm"},
    {"name": "うま",         "url": "https://may.2chan.net/26/futaba.htm"},
    {"name": "ねこ",         "url": "https://may.2chan.net/27/futaba.htm"},
    {"name": "どうぶつ",     "url": "https://dat.2chan.net/d/futaba.htm"},
    {"name": "しょくぶつ",   "url": "https://zip.2chan.net/z/futaba.htm"},
    {"name": "虫",           "url": "https://dat.2chan.net/w/futaba.htm"},
    {"name": "アクア",       "url": "https://dat.2chan.net/49/futaba.htm"},
    {"name": "アウトドア",   "url": "https://dec.2chan.net/62/futaba.htm"},
    {"name": "料理",         "url": "https://dat.2chan.net/t/futaba.htm"},
    {"name": "甘味",         "url": "https://dat.2chan.net/20/futaba.htm"},
    {"name": "ラーメン",     "url": "https://dat.2chan.net/21/futaba.htm"},
    {"name": "のりもの",     "url": "https://dat.2chan.net/e/futaba.htm"},
    {"name": "二輪",         "url": "https://dat.2chan.net/j/futaba.htm"},
    {"name": "自転車",       "url": "https://nov.2chan.net/37/futaba.htm"},
    {"name": "カメラ",       "url": "https://dat.2chan.net/45/futaba.htm"},
    {"name": "家電",         "url": "https://dat.2chan.net/48/futaba.htm"},
    {"name": "鉄道",         "url": "https://dat.2chan.net/r/futaba.htm"},
    {"name": "二次元",       "url": "https://dat.2chan.net/img2/futaba.htm"},
    {"name": "二次元裏①",   "url": "https://dec.2chan.net/dec/futaba.htm"},
    {"name": "二次元裏②",   "url": "https://jun.2chan.net/jun/futaba.htm"},
    {"name": "二次元裏③",   "url": "https://may.2chan.net/b/futaba.htm"},
    {"name": "転載不可",     "url": "https://dec.2chan.net/58/futaba.htm"},
    {"name": "転載可",       "url": "https://dec.2chan.net/59/futaba.htm"},
    {"name": "二次元ID",     "url": "https://may.2chan.net/id/futaba.htm"},
    {"name": "スピグラ",     "url": "https://dat.2chan.net/23/futaba.htm"},
    {"name": "二次元ネタ",   "url": "https://dat.2chan.net/16/futaba.htm"},
    {"name": "二次元業界",   "url": "https://dat.2chan.net/43/futaba.htm"},
    {"name": "FGO",          "url": "https://dec.2chan.net/74/futaba.htm"},
    {"name": "アイマス",     "url": "https://dec.2chan.net/75/futaba.htm"},
    {"name": "ZOIDS",        "url": "https://dec.2chan.net/86/futaba.htm"},
    {"name": "ウメハラ総合", "url": "https://dec.2chan.net/78/futaba.htm"},
    {"name": "ゲーム",       "url": "https://jun.2chan.net/31/futaba.htm"},
    {"name": "ネトゲ",       "url": "https://nov.2chan.net/28/futaba.htm"},
    {"name": "ソシャゲ",     "url": "https://dec.2chan.net/56/futaba.htm"},
    {"name": "艦これ",       "url": "https://dec.2chan.net/60/futaba.htm"},
    {"name": "モアイ",       "url": "https://dec.2chan.net/69/futaba.htm"},
    {"name": "刀剣乱舞",     "url": "https://dec.2chan.net/65/futaba.htm"},
    {"name": "占い",         "url": "https://dec.2chan.net/64/futaba.htm"},
    {"name": "ファッション", "url": "https://dec.2chan.net/66/futaba.htm"},
    {"name": "旅行",         "url": "https://dec.2chan.net/67/futaba.htm"},
    {"name": "子育て",       "url": "https://dec.2chan.net/68/futaba.htm"},
    {"name": "webm",         "url": "https://may.2chan.net/webm/futaba.htm"},
    {"name": "そうだね",     "url": "https://dec.2chan.net/71/futaba.htm"},
    {"name": "任天堂",       "url": "https://dec.2chan.net/82/futaba.htm"},
    {"name": "ソニー",       "url": "https://dec.2chan.net/61/futaba.htm"},
    {"name": "ネットキャラ", "url": "https://dat.2chan.net/10/futaba.htm"},
    {"name": "なりきり",     "url": "https://nov.2chan.net/34/futaba.htm"},
    {"name": "自作絵",       "url": "https://zip.2chan.net/11/futaba.htm"},
    {"name": "自作絵裏",     "url": "https://zip.2chan.net/14/futaba.htm"},
    {"name": "女装",         "url": "https://zip.2chan.net/32/futaba.htm"},
    {"name": "ばら",         "url": "https://zip.2chan.net/15/futaba.htm"},
    {"name": "ゆり",         "url": "https://zip.2chan.net/7/futaba.htm"},
    {"name": "やおい",       "url": "https://zip.2chan.net/8/futaba.htm"},
    {"name": "二次元グロ",   "url": "https://cgi.2chan.net/o/guro2-enter.html"},
    {"name": "二次元グロ裏", "url": "https://jun.2chan.net/51/51enter.htm"},
    {"name": "えろげ",       "url": "https://zip.2chan.net/5/enter.html"},
    {"name": "あぷ",         "url": "https://dec.2chan.net/up/up.htm"},
    {"name": "あぷ小",       "url": "https://dec.2chan.net/up2/up.htm"},
    {"name": "自作PC",       "url": "https://zip.2chan.net/3/futaba.htm"},
    {"name": "特撮",         "url": "https://cgi.2chan.net/g/futaba.htm"},
    {"name": "ろぼ",         "url": "https://zip.2chan.net/2/futaba.htm"},
    {"name": "映画",         "url": "https://dec.2chan.net/63/futaba.htm"},
    {"name": "おもちゃ",     "url": "https://dat.2chan.net/44/futaba.htm"},
    {"name": "模型",         "url": "https://dat.2chan.net/v/futaba.htm"},
    {"name": "模型裏①",     "url": "https://nov.2chan.net/y/futaba.htm"},
    {"name": "模型裏②",     "url": "https://jun.2chan.net/47/futaba.htm"},
    {"name": "VTuber",       "url": "https://dec.2chan.net/73/futaba.htm"},
    {"name": "合成音声",     "url": "https://dec.2chan.net/81/futaba.htm"},
    {"name": "3DCG",         "url": "https://dat.2chan.net/x/futaba.htm"},
    {"name": "人工知能",     "url": "https://dec.2chan.net/85/futaba.htm"},
    {"name": "政治",         "url": "https://nov.2chan.net/35/futaba.htm"},
    {"name": "経済",         "url": "https://nov.2chan.net/36/futaba.htm"},
    {"name": "宗教",         "url": "https://dec.2chan.net/79/futaba.htm"},
    {"name": "三次実況",     "url": "https://dec.2chan.net/50/futaba.htm"},
    {"name": "軍",           "url": "https://cgi.2chan.net/f/futaba.htm"},
    {"name": "軍裏",         "url": "https://may.2chan.net/39/futaba.htm"},
    {"name": "数学",         "url": "https://cgi.2chan.net/m/futaba.htm"},
    {"name": "flash",        "url": "https://cgi.2chan.net/i/futaba.htm"},
    {"name": "壁紙",         "url": "https://cgi.2chan.net/k/futaba.htm"},
    {"name": "壁紙二",       "url": "https://dat.2chan.net/l/futaba.htm"},
    {"name": "東方",         "url": "https://may.2chan.net/40/futaba.htm"},
    {"name": "東方裏",       "url": "https://dec.2chan.net/55/futaba.htm"},
    {"name": "お絵かき",     "url": "https://zip.2chan.net/p/futaba.htm"},
    {"name": "落書き",       "url": "https://nov.2chan.net/q/futaba.htm"},
    {"name": "落書き裏",     "url": "https://cgi.2chan.net/u/futaba.htm"},
    {"name": "ニュース表",   "url": "https://zip.2chan.net/6/futaba.htm"},
    {"name": "昭和",         "url": "https://dec.2chan.net/76/futaba.htm"},
    {"name": "平成",         "url": "https://dec.2chan.net/77/futaba.htm"},
    {"name": "発電",         "url": "https://dec.2chan.net/53/futaba.htm"},
    {"name": "自然災害",     "url": "https://dec.2chan.net/52/futaba.htm"},
    {"name": "コロナ",       "url": "https://dec.2chan.net/83/futaba.htm"},
    {"name": "雑談",         "url": "https://img.2chan.net/9/futaba.htm"},
    {"name": "配布",         "url": "https://www.2chan.net/script/"},
    {"name": "お絵sql",      "url": "https://jun.2chan.net/oe/futaba.htm"},
    {"name": "お絵sqlip",    "url": "https://jun.2chan.net/72/futaba.htm"},
    {"name": "半角",         "url": "https://jun.2chan.net/ascii/index2.html"},
    {"name": "レイアウト",   "url": "https://may.2chan.net/layout/futaba.htm"},
]

def collect(request):
    board_url = request.GET.get("board", "")
    threads = []
    selected_board = None
    error = None

    if board_url:
        selected_board = next((b for b in BOARDS if b["url"] == board_url), None)
        try:
            threads = _fetch_board_page(board_url, 0)
        except Exception as e:
            error = f"取得に失敗しました: {e}"

    return render(request, 'collect.html', {
        "boards": BOARDS,
        "threads": threads,
        "selected_board": selected_board,
        "board_url": board_url,
        "error": error,
    })

from django.http import JsonResponse

def collect_more(request):
    board_url = request.GET.get("board", "")
    page = int(request.GET.get("page", 1))
    if not board_url or page < 1 or page >= MAX_PAGES:
        return JsonResponse({"threads": []})
    try:
        threads = _fetch_board_page(board_url, page)
    except Exception:
        return JsonResponse({"threads": []})
    return JsonResponse({"threads": threads})

def thread_detail(request):
    res_url = request.GET.get("url", "")
    images = []
    title = ""
    error = None

    if res_url:
        try:
            res = requests.get(res_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            res.encoding = "shift_jis"
            soup = BeautifulSoup(res.text, "html.parser")
            parsed = urlparse(res_url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            board_path = "/" + parsed.path.split("/")[1]

            subject = soup.find("span", class_="csb")
            title = subject.get_text(strip=True) if subject else "無題"

            for img in soup.find_all("img", src=True):
                src = img["src"]
                if "/thumb/" in src:
                    full = base_url + src.replace("/thumb/", "/src/").replace("s.jpg", ".jpg")
                    images.append({"thumb": base_url + src, "full": full})
        except Exception as e:
            error = f"取得に失敗しました: {e}"

    return render(request, "thread.html", {
        "images": images,
        "title": title,
        "res_url": res_url,
        "error": error,
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('profile/', profile, name='profile'),
    path('collect/', collect, name='collect'),
    path('collect/more/', collect_more, name='collect_more'),
    path('collect/thread/', thread_detail, name='thread_detail'),
]
