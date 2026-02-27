import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def get_naver_rank(keywords, target_id):
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    )
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    final_report = []

    def check_current_page_rank(target_id, tab="home"):
        """현재 페이지에서 광고 제외 후 순위 탐색 (홈: 글 단위 / 블로그: 블록 단위)"""
        if tab == "blog":
            # 블로그 탭은 블로그 글 블록 단위로 탐색
            items = driver.find_elements(By.CSS_SELECTOR, "div.Rpk3YFQcZBMzoLEWz9U_")
        else:
            # 홈 탭은 기존 로직 (main_pack 내 div 탐색)
            items = driver.find_elements(By.CSS_SELECTOR, "div.main_pack div")

        current_rank = 0
        seen_posts = set()  # 홈 탭에서 글 단위 중복 제거

        for item in items:
            # 광고 제외
            if item.find_elements(By.CSS_SELECTOR, ".sp_ad, .ad_section"):
                continue

            # 블로그 링크 탐색
            links = item.find_elements(By.CSS_SELECTOR, "a[href^='https://blog.naver.com/']")
            if not links:
                continue

            if tab == "blog":
                # 블로그 탭: 블록 안에 블로그 글이 하나라도 있으면 블록을 1개로 카운트
                current_rank += 1
                for link in links:
                    href = link.get_attribute("href")
                    parts = href.split("/")
                    if len(parts) < 5:  # 아이디만 있는 경우 제외
                        continue
                    blog_id = parts[3]
                    post_id = parts[4]
                    if blog_id == target_id:
                        return current_rank
            else:
                # 홈 탭: 글 단위로 카운트, 중복 제거
                href = links[0].get_attribute("href")
                if href in seen_posts:
                    continue
                seen_posts.add(href)

                parts = href.split("/")
                if len(parts) < 5:  # 아이디만 있는 경우 제외
                    continue
                blog_id = parts[3]
                post_id = parts[4]

                current_rank += 1
                if blog_id == target_id:
                    return current_rank

            if current_rank >= 30:
                break

        return 999

    try:
        for keyword in keywords:
            print(f"🔍 '{keyword}' 분석 시작...")

            # 1️⃣ 통합검색 (홈)
            driver.get(
                f"https://search.naver.com/search.naver?where=nexearch&query={keyword}"
            )
            time.sleep(2.5)
            home_rank = check_current_page_rank(target_id, tab="home")

            # 2️⃣ 블로그 탭
            driver.get(
                f"https://search.naver.com/search.naver?ssc=tab.blog.all&query={keyword}"
            )
            time.sleep(2.5)
            blog_rank = check_current_page_rank(target_id, tab="blog")

            best = min(home_rank, blog_rank)

            if best == 999:
                final_report.append((keyword, "권외"))
                print(f"❌ {keyword} : 권외")
            else:
                final_report.append((keyword, f"{best}"))
                print(f"✅ {keyword} 발견: {best}위 (홈:{home_rank}, 블로그:{blog_rank})")

    finally:
        driver.quit()

    return final_report


if __name__ == "__main__":
    MY_ID = "300bank"

    with open(
        r"keywords.txt",
        "r",
        encoding="utf-8"
    ) as f:
        KEYWORD_LIST = [line.strip() for line in f if line.strip()]

    results = get_naver_rank(KEYWORD_LIST, MY_ID)

    print("\n" + "=" * 40)
    print("📊 최종 순위 결과 보고 (광고 제외)")
    print("=" * 40)
    for kw, rk in results:
        print(f"{kw.ljust(15)} : {rk}")
    print("=" * 40)

    with open(
        r"result.txt",
        "w",
        encoding="utf-8"
    ) as f:
        f.write("📊 최종 순위 결과 보고 (광고 제외)\n")
        f.write("=" * 40 + "\n")
        for kw, rk in results:
            f.write(f"{rk}\n")

    print("\n결과가 result.txt 파일로 저장되었습니다 ✅")
