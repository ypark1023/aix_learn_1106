import json
import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://www.kobis.or.kr"
LIST_URL = f"{BASE_URL}/kobis/business/stat/boxs/findFormerBoxOfficeList.do"
OUTPUT_FILE = "kobis_top100_movies.json"


def create_driver():
    """Selenium 4 Chrome 드라이버 생성"""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(options=options)


def fetch_top_movie_codes(driver, limit=100):
    """역대 박스오피스 페이지에서 상위 100편의 영화 코드와 기본 정보를 추출합니다."""
    driver.get(LIST_URL)
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "tr[id^='tr_']"))
    )

    rows = driver.find_elements(By.CSS_SELECTOR, "tr[id^='tr_']")[:limit]
    movies = []

    for idx, row in enumerate(rows, start=1):
        try:
            link = row.find_element(By.CSS_SELECTOR, "a[onclick*='mstView']")
            onclick = link.get_attribute("onclick") or ""
            match = re.search(r"mstView\(\s*['\"]movie['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*\)", onclick)
            if not match:
                continue

            cols = [td.text.strip() for td in row.find_elements(By.TAG_NAME, "td")]
            movies.append({
                "rank": idx,
                "movieCd": match.group(1),
                "title": link.text.strip(),
                "release_date_list": cols[2] if len(cols) > 2 else "",
                "audience": cols[4] if len(cols) > 4 else "",
            })
        except Exception:
            continue

    return movies


def parse_genre_from_summary(summary_text):
    """'장편 | 일반영화 | 사극, 액션 | 128분...' 형식에서 장르만 깔끔하게 추출합니다."""
    if not summary_text:
        return ""
    parts = [p.strip() for p in summary_text.split("|") if p.strip()]
    if len(parts) >= 3:
        return parts[2]
    return summary_text


def fetch_movie_detail_via_js(driver, item):
    """
    페이지 이동 없이 현재 페이지에서 JS로 mstView('movie', movieCd)를 직접 실행해
    동적으로 열리는 레이어 팝업(DOM)에서 정보를 추출합니다.
    """
    movie_cd = item["movieCd"]

    # 기존에 열려있는 상세 레이어 팝업 제거
    driver.execute_script(
        """
        document.querySelectorAll('.ui-dialog, .layer_popup, .pop_container, #ui-id-1').forEach(el => el.remove());
        """
    )

    # KOBIS 페이지 내장 JS 함수 mstView 직접 호출
    driver.execute_script(f"mstView('movie', '{movie_cd}');")

    # 팝업 내부에 해당 영화코드(dd)나 기본정보(dl)가 렌더링될 때까지 대기
    WebDriverWait(driver, 10).until(
        lambda d: movie_cd in d.page_source and (
            len(d.find_elements(By.CSS_SELECTOR, ".ui-dialog dl dt, .pop_container dl dt, .info_list dt, dl.ovf dt")) > 0
        )
    )
    time.sleep(0.25)

    # 현재 페이지에서 팝업 영역만 파싱 (없으면 전체 페이지에서 추출)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    popup = soup.select_one(".ui-dialog, .pop_container, .layer_popup") or soup

    # 1) 모든 dt / dd 쌍을 딕셔너리로 수집
    info_map = {}
    director = ""
    actors = []

    for dt in popup.select("dl dt"):
        label = dt.get_text(" ", strip=True)
        dd = dt.find_next_sibling("dd")
        if not dd:
            continue
        val_text = dd.get_text(" ", strip=True)
        if label and label not in info_map:
            info_map[label] = val_text

        people_links = [
            a.get_text(strip=True)
            for a in dd.select("a[onclick*='people'], a[href*='people'], a")
            if a.get_text(strip=True)
        ]
        if "감독" in label and not director:
            director = ", ".join(people_links) if people_links else val_text
        elif "배우" in label or "출연" in label:
            if people_links:
                actors.extend(people_links)
            else:
                # 괄호 배역명 제거 후 이름 분리
                cleaned = re.sub(r"\([^)]*\)", "", val_text)
                actors.extend([n.strip() for n in cleaned.split(",") if n.strip()])

    # 2) 시놉시스 (줄거리) 추출 - 클래스명 또는 '시놉시스' 제목 태그 기준
    synopsis = ""
    syn_el = popup.select_one(".synopsis .desc, .synopsis p, p.desc_info, .desc_story")
    if syn_el:
        synopsis = syn_el.get_text(" ", strip=True)
    else:
        for h_tag in popup.find_all(["h3", "h4", "strong", "dt"]):
            if "시놉시스" in h_tag.get_text():
                nxt = h_tag.find_next_sibling(["div", "p", "dd"])
                if nxt:
                    synopsis = nxt.get_text(" ", strip=True)
                    break

    # 3) 포스터 이미지 URL 추출
    poster_url = ""
    poster_el = popup.select_one(".thumb img, .fl_info img, .poster img, img[src*='/upload/']")
    if poster_el and poster_el.get("src"):
        src = poster_el["src"].strip()
        poster_url = (BASE_URL + src) if src.startswith("/") else src

    # 4) 장르 및 개봉일 정리
    raw_summary = info_map.get("요약정보", "")
    genre = info_map.get("홍보용장르") or parse_genre_from_summary(raw_summary)
    release_date = info_map.get("개봉일") or item["release_date_list"]

    return {
        "rank": item["rank"],
        "movieCd": movie_cd,
        "title": item["title"],
        "synopsis": synopsis,
        "genre": genre,
        "summary": raw_summary,
        "director": director,
        "actors": list(dict.fromkeys(actors))[:10],
        "release_date": release_date,
        "audience": item["audience"],
        "poster_url": poster_url,
    }


def main():
    driver = create_driver()
    try:
        movie_codes = fetch_top_movie_codes(driver, limit=100)
        print(f"목록 추출 완료: {len(movie_codes)}편")

        results = []
        for i, item in enumerate(movie_codes, start=1):
            try:
                detail = fetch_movie_detail_via_js(driver, item)
                results.append(detail)
                print(
                    f"[{i}/{len(movie_codes)}] {detail['title']} | "
                    f"감독: {detail['director']} | 장르: {detail['genre']} | "
                    f"배우: {len(detail['actors'])}명 | 줄거리: {len(detail['synopsis'])}자"
                )
            except Exception as e:
                print(f"[{i}/{len(movie_codes)}] {item['title']} 수집 실패: {e}")

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"\n저장 완료: {OUTPUT_FILE} (총 {len(results)}편)")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()