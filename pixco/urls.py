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

_board_cache = {}  # {url: (timestamp, threads)}
CACHE_TTL = 300    # 5分

def home(request):
    return render(request, 'home.html')

def profile(request):
    return render(request, 'profile.html')


BOARDS = [
    {"name": "ねこ",       "url": "https://may.2chan.net/27/futaba.htm"},
    {"name": "うま",       "url": "https://may.2chan.net/26/futaba.htm"},
    {"name": "どうぶつ",   "url": "https://dat.2chan.net/d/futaba.htm"},
    {"name": "しょくぶつ", "url": "https://zip.2chan.net/z/futaba.htm"},
    {"name": "虫",         "url": "https://dat.2chan.net/w/futaba.htm"},
    {"name": "アクア",     "url": "https://dat.2chan.net/49/futaba.htm"},
    {"name": "料理",       "url": "https://dat.2chan.net/t/futaba.htm"},
    {"name": "甘味",       "url": "https://dat.2chan.net/20/futaba.htm"},
    {"name": "ラーメン",   "url": "https://dat.2chan.net/21/futaba.htm"},
    {"name": "のりもの",   "url": "https://dat.2chan.net/e/futaba.htm"},
    {"name": "二輪",       "url": "https://dat.2chan.net/j/futaba.htm"},
    {"name": "自転車",     "url": "https://nov.2chan.net/37/futaba.htm"},
    {"name": "鉄道",       "url": "https://dat.2chan.net/r/futaba.htm"},
    {"name": "野球",       "url": "https://zip.2chan.net/1/futaba.htm"},
    {"name": "サッカー",   "url": "https://zip.2chan.net/12/futaba.htm"},
    {"name": "カメラ",     "url": "https://dat.2chan.net/45/futaba.htm"},
    {"name": "家電",       "url": "https://dat.2chan.net/48/futaba.htm"},
    {"name": "アウトドア", "url": "https://dec.2chan.net/62/futaba.htm"},
    {"name": "ゲーム",     "url": "https://jun.2chan.net/31/futaba.htm"},
    {"name": "二次元裏①", "url": "https://dec.2chan.net/dec/futaba.htm"},
    {"name": "二次元裏②", "url": "https://jun.2chan.net/jun/futaba.htm"},
    {"name": "二次元裏③", "url": "https://may.2chan.net/b/futaba.htm"},
]

def collect(request):
    board_url = request.GET.get("board", "")
    threads = []
    selected_board = None
    error = None

    if board_url:
        selected_board = next((b for b in BOARDS if b["url"] == board_url), None)
        now = time.time()
        cached = _board_cache.get(board_url)
        if cached and now - cached[0] < CACHE_TTL:
            threads = cached[1]
        else:
            try:
                res = requests.get(board_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                res.encoding = "shift_jis"
                soup = BeautifulSoup(res.text, "html.parser")
                parsed = urlparse(board_url)
                base_url = f"{parsed.scheme}://{parsed.netloc}"

                for div in soup.find_all("div", class_="thre"):
                    img_tag = div.find("img", src=True)
                    subject = div.find("span", class_="csb")
                    comment = div.find("blockquote")
                    reply_link = div.find("a", class_="hsbn")
                    if not img_tag:
                        continue
                    thumb_src = img_tag["src"]
                    full_src = thumb_src.replace("/thumb/", "/src/").replace("s.jpg", ".jpg")
                    board_dir = parsed.path.rsplit("/", 1)[0]
                    res_url = (base_url + board_dir + "/" + reply_link["href"].lstrip("/")) if reply_link else ""
                    threads.append({
                        "thumb": base_url + thumb_src,
                        "full": base_url + full_src,
                        "title": subject.get_text(strip=True) if subject else "無題",
                        "comment": comment.get_text(strip=True)[:80] if comment else "",
                        "res_url": res_url,
                    })
                _board_cache[board_url] = (now, threads)
            except Exception as e:
                error = f"取得に失敗しました: {e}"

    return render(request, 'collect.html', {
        "boards": BOARDS,
        "threads": threads,
        "selected_board": selected_board,
        "board_url": board_url,
        "error": error,
    })

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
    path('collect/thread/', thread_detail, name='thread_detail'),
]
