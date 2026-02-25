import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def get_naver_rank(keywords, target_id):
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    final_report = {}

    def check_current_page_rank(tab="blog"):
        """현재 페이지(홈 또는 블로그탭)에서 광고 제외 순위 탐색"""
        # 블로그 글 단위 컨테이너 선택 (현재 DOM 구조 기준)
        items = driver.find_elements(By.CSS_SELECTOR, "div.Rpk3YFQcZBMzoLEWz9U_")

        current_rank = 0
        for item in items:
            # 광고 제외
            if item.find_elements(By.CSS_SELECTOR, ".sp_ad, .ad_section"):
                continue

            current_rank += 1

            # 컨테이너 안에서 대표 블로그 링크 찾기
            links = item.find_elements(By.CSS_SELECTOR, "a[href^='https://blog.naver.com/']")
            if not links:
                continue

            href = links[0].get_attribute("href")  # 첫 번째 링크만 사용
            if href.startswith(f"https://blog.naver.com/{target_id}"):
                return current_rank

            if current_rank >= 30:  # 상위 30개까지만 확인
                break
        return 999

    try:
        for keyword in keywords:
            print(f"🔍 '{keyword}' 분석 시작...")

            # --- [Step 1] 통합 검색(홈) 확인 ---
            driver.get(f"https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query={keyword}")
            time.sleep(2.5)
            home_rank = check_current_page_rank(tab="home")

            # --- [Step 2] 블로그 탭 이동 및 확인 ---
            driver.get(f"https://search.naver.com/search.naver?ssc=tab.blog.all&sm=tab_jum&query={keyword}")
            time.sleep(2.5)
            blog_rank = check_current_page_rank(tab="blog")

            # --- [Step 3] 결과 비교 및 저장 ---
            best = min(home_rank, blog_rank)
            if best == 999:
                final_report[keyword] = "권외"
                print(f"❌ {keyword} : 권외")
            else:
                final_report[keyword] = f"{best}위"
                print(f"✅ {keyword} 발견: {best}위 (홈:{home_rank}, 블로그:{blog_rank})")

    finally:
        driver.quit()

    return final_report


if __name__ == "__main__":
    MY_ID = "300bank"  # 내 블로그 ID
    KEYWORD_LIST = ["스마트워치KC인증", "속눈썹고데기KC인증", "에어컨KC인증"]

    results = get_naver_rank(KEYWORD_LIST, MY_ID)

    print("\n" + "="*40)
    print("📊 최종 순위 결과 보고 (광고 제외)")
    print("="*40)
    for kw, rk in results.items():
        print(f"{kw.ljust(15)} : {rk}")
    print("="*40)
