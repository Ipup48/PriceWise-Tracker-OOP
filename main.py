"""จุดเริ่มต้นหลักและการสาธิตการทำงานของ PriceWise Tracker (ระบบเปรียบเทียบราคา)

สาธิตแนวคิดการออกแบบเชิงวัตถุ:
    - Object-Oriented Analysis & Design (OOAD)
    - Template Method Pattern ในการดึงข้อมูลของ Scraper
    - Composition & Dependency Injection ใน PriceComparisonEngine
    - Separation of Concerns ในการปรับมาตรฐานสกุลเงิน (Currency Normalization)
    - Open/Closed Principle (การเพิ่ม Scraper ตัวใหม่ได้แบบไดนามิกขณะทำงาน)
"""

import sys
from typing import Any
import unicodedata

# กำหนดค่ามาตรฐานการแสดงผลภาษาไทยและ Unicode บน Terminal ทุกระบบปฏิบัติการ
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from engine.comparison import ComparisonResult, PriceComparisonEngine
from engine.currency import FixedRateCurrencyConverter
from models.product import Product
from scrapers.base import BaseScraper
from scrapers.lazada import MockLazadaScraper
from scrapers.shopee import MockShopeeScraper


def visual_len(text: str) -> int:
    """คำนวณความกว้างการแสดงผลจริงของข้อความ โดยไม่นับสระบน/ล่างและวรรณยุกต์ภาษาไทย."""
    return sum(0 if unicodedata.category(c) in ("Mn", "Me") else 1 for c in text)


def pad_visual(text: str, width: int, align: str = "<") -> str:
    """เติมช่องว่างให้พอดีกับความกว้างการแสดงผลจริงบนหน้าจอ."""
    vlen = visual_len(text)
    pad = max(0, width - vlen)
    if align == ">":
        return " " * pad + text
    return text + " " * pad


def truncate_visual(text: str, max_width: int) -> str:
    """ตัดทอนข้อความให้พอดีกับความกว้างการแสดงผลพร้อมต่อท้ายด้วยจุดไข่ปลา (...)"""
    if visual_len(text) <= max_width:
        return text
    curr = ""
    for c in text:
        if visual_len(curr + c + "...") > max_width:
            break
        curr += c
    return curr + "..."


def print_comparison_table(result: ComparisonResult) -> None:
    """แสดงผลตารางเปรียบเทียบราคา ASCII ที่จัดรูปแบบอย่างสวยงามและเป็นระเบียบ."""
    print(f"\n{'=' * 95}")
    print(f" ผลการเปรียบเทียบราคาสำหรับ: '{result.keyword}' (แปลงเป็นสกุลเงิน: {result.target_currency})")
    print(f"{'=' * 95}")

    if not result.items:
        print(f"  [!] ไม่พบสินค้าที่ตรงกับคำค้นหา '{result.keyword}'")
        print(f"{'=' * 95}\n")
        return

    # หัวตาราง (Table Header)
    c_rank = pad_visual("อันดับ", 6)
    c_plat = pad_visual("ร้านค้า", 9)
    c_name = pad_visual("ชื่อสินค้า", 40)
    c_orig = pad_visual("ราคาต้นทาง", 14)
    c_norm = pad_visual("ราคาเทียบเคียง", 14)
    c_stock = pad_visual("สต็อก", 8)

    header = f"{c_rank} | {c_plat} | {c_name} | {c_orig} | {c_norm} | {c_stock}"
    print(header)
    print(f"{'-' * 6}-+-{'-' * 9}-+-{'-' * 40}-+-{'-' * 14}-+-{'-' * 14}-+-{'-' * 8}")

    for idx, item in enumerate(result.items, start=1):
        prod = item.product
        stock_str = "มีสินค้า" if prod.in_stock else "สินค้าหมด"
        display_name = truncate_visual(prod.name, 40)
        orig_price = prod.formatted_price()
        norm_price = item.formatted_normalized_price()

        r_rank = pad_visual(f"#{idx}", 6)
        r_plat = pad_visual(prod.platform, 9)
        r_name = pad_visual(display_name, 40)
        r_orig = pad_visual(orig_price, 14)
        r_norm = pad_visual(norm_price, 14)
        r_stock = pad_visual(stock_str, 8)

        row = f"{r_rank} | {r_plat} | {r_name} | {r_orig} | {r_norm} | {r_stock}"
        print(row)

    print(f"{'=' * 95}")

    # สถิติและข้อมูลสรุป
    if result.best_deal:
        best_p = result.best_deal.product
        stock_label = "มีสินค้า" if best_p.in_stock else "สินค้าหมด"
        print(
            f"[*] ดีลที่ดีที่สุด (BEST DEAL): {best_p.name} บน [{best_p.platform}] "
            f"ในราคา {result.best_deal.formatted_normalized_price()} "
            f"({stock_label})"
        )
    print(
        f"[*] สรุปผล (SUMMARY) : พบทั้งหมด: {result.total_count} รายการ | "
        f"มีในสต็อก: {len(result.in_stock_items)} รายการ | "
        f"ต่ำสุด: {result.target_currency} {result.min_price:,.2f} | "
        f"สูงสุด: {result.target_currency} {result.max_price:,.2f} | "
        f"เฉลี่ย: {result.target_currency} {result.average_price:,.2f}"
    )
    if result.errors:
        print(f"[!] ข้อผิดพลาดจากแพลตฟอร์ม: {result.errors}")
    print(f"{'=' * 95}\n")


# ----------------------------------------------------------------------
# การสาธิตหลักการ Open/Closed Principle:
# เพิ่ม Scraper ตัวใหม่ได้ทันทีโดยไม่ต้องแก้ไขโค้ดของ Scraper เดิมหรือ Engine!
# ----------------------------------------------------------------------
class MockAmazonScraper(BaseScraper):
    """สแครปเปอร์ส่วนขยายแบบไดนามิกที่สาธิตหลักการ Open/Closed Principle (OCP)."""

    def __init__(self) -> None:
        self._platform_name = "Amazon"
        self._base_url = "https://www.amazon.com"
        self._catalog = [
            # 1. หูฟัง & ระบบเสียง
            {
                "asin": "B09XS7JWHH",
                "title": "Sony WH-1000XM5 Wireless Noise Canceling Headphones (Silver Edition)",
                "price_usd": 328.00,  # ~11,972 THB
                "is_prime_in_stock": True,
            },
            {
                "asin": "B0BDHWDR12",
                "title": "Apple AirPods Pro (รุ่นที่ 2) with MagSafe Case (USB-C)",
                "price_usd": 199.00,  # ~7,263.50 THB - ถูกที่สุด!
                "is_prime_in_stock": True,
            },
            {
                "asin": "B07Q9MJKBV",
                "title": "Bose QuietComfort 45 Bluetooth Wireless Noise Cancelling Headphones",
                "price_usd": 279.00,  # ~10,183.50 THB
                "is_prime_in_stock": True,
            },
            {
                "asin": "B08KSFRLJ2",
                "title": "Marshall Major IV On-Ear Bluetooth Headphones (Black)",
                "price_usd": 119.00,  # ~4,343.50 THB
                "is_prime_in_stock": True,
            },
            {
                "asin": "B09W266PCH",
                "title": "Marshall Emberton II Portable Bluetooth Speaker",
                "price_usd": 149.99,  # ~5,474.63 THB
                "is_prime_in_stock": True,
            },
            {
                "asin": "B0002E4Z8M",
                "title": "Shure SM7B Cardioid Dynamic Vocal Microphone",
                "price_usd": 389.00,  # ~14,198.50 THB
                "is_prime_in_stock": True,
            },

            # 2. คอมพิวเตอร์ คีย์บอร์ด & อุปกรณ์ต่อพ่วง
            {
                "asin": "B09HM94VDS",
                "title": "Logitech MX Master 3S Wireless Bluetooth Mouse (Space Gray)",
                "price_usd": 89.00,  # ~3,248.50 THB
                "is_prime_in_stock": True,
            },
            {
                "asin": "B0875X346W",
                "title": "Keychron K2 Wireless Bluetooth Mechanical Gaming Keyboard",
                "price_usd": 79.99,  # ~2,919.63 THB
                "is_prime_in_stock": True,
            },
            {
                "asin": "B0B3C57XLR",
                "title": "Apple MacBook Air 13.6-inch Laptop M2 Chip (8GB RAM, 256GB SSD)",
                "price_usd": 899.00,  # ~32,813.50 THB
                "is_prime_in_stock": True,
            },
            {
                "asin": "B0BT184R4T",
                "title": "ASUS ROG Zephyrus G14 14-inch Gaming Laptop QHD 165Hz",
                "price_usd": 1299.00,  # ~47,413.50 THB - ถูกที่สุด!
                "is_prime_in_stock": True,
            },
            {
                "asin": "B09TBC6P74",
                "title": "Dell UltraSharp U2723QE 27-inch 4K UHD Hub Monitor",
                "price_usd": 519.00,  # ~18,943.50 THB
                "is_prime_in_stock": True,
            },
            {
                "asin": "B09738CV2G",
                "title": "Elgato Stream Deck MK.2 Studio Controller (15 Macro Keys)",
                "price_usd": 124.99,  # ~4,562.13 THB
                "is_prime_in_stock": True,
            },

            # 3. สมาร์ทโฟน & แท็บเล็ต
            {
                "asin": "B0C79Y5WJ4",
                "title": "Samsung Galaxy Tab S9 11-inch 128GB Android Tablet",
                "price_usd": 679.99,  # ~24,819.63 THB
                "is_prime_in_stock": True,
            },
            {
                "asin": "B09V3HN1KC",
                "title": "Apple iPad Air 5 (M1) 10.9-inch 64GB Wi-Fi Space Gray",
                "price_usd": 499.00,  # ~18,213.50 THB - ถูกที่สุด!
                "is_prime_in_stock": True,
            },
            {
                "asin": "B0CMZ6R8K1",
                "title": "Apple iPhone 15 Pro Max 256GB Unlocked Natural Titanium",
                "price_usd": 1099.00,  # ~40,113.50 THB - ถูกที่สุด!
                "is_prime_in_stock": True,
            },
            {
                "asin": "B0CR2V4H6N",
                "title": "Samsung Galaxy S24 Ultra 256GB AI Smartphone Titanium Black",
                "price_usd": 1149.00,  # ~41,938.50 THB
                "is_prime_in_stock": True,
            },
            {
                "asin": "B0CSG2W1R5",
                "title": "Xiaomi 14 Pro 5G Leica Optical Lens 512GB",
                "price_usd": 799.00,  # ~29,163.50 THB
                "is_prime_in_stock": True,
            },

            # 4. เกมมิ่งและคอนโซล
            {
                "asin": "B0CL5KNB9M",
                "title": "PlayStation 5 Slim (PS5) Console Disc Edition",
                "price_usd": 449.00,  # ~16,388.50 THB - ถูกที่สุด!
                "is_prime_in_stock": True,
            },
            {
                "asin": "B098RKWHHZ",
                "title": "Nintendo Switch OLED Model with White Joy-Con",
                "price_usd": 299.99,  # ~10,949.63 THB
                "is_prime_in_stock": True,
            },
            {
                "asin": "B08H75RTR8",
                "title": "Xbox Series X 1TB Video Game Console",
                "price_usd": 489.00,  # ~17,848.50 THB
                "is_prime_in_stock": True,
            },

            # 5. สมาร์ทวอทช์ & สุขภาพ
            {
                "asin": "B0CHX5TBN2",
                "title": "Apple Watch Series 9 GPS 41mm Smartwatch Midnight",
                "price_usd": 349.00,  # ~12,738.50 THB - ถูกที่สุด!
                "is_prime_in_stock": True,
            },
            {
                "asin": "B0BW5Y1JLM",
                "title": "Garmin Forerunner 265 Running GPS Smartwatch",
                "price_usd": 429.99,  # ~15,694.63 THB
                "is_prime_in_stock": True,
            },

            # 6. กล้อง & ไลฟ์สไตล์
            {
                "asin": "B0CHMXFXBG",
                "title": "DJI Osmo Pocket 3 Creator Combo 4K 120fps Vlog Camera",
                "price_usd": 599.00,  # ~21,863.50 THB
                "is_prime_in_stock": True,
            },
            {
                "asin": "B0CCZXB9J2",
                "title": "GoPro HERO12 Black Waterproof Action Camera with HDR",
                "price_usd": 349.99,  # ~12,774.63 THB - ถูกที่สุด!
                "is_prime_in_stock": True,
            },
            {
                "asin": "B0798VGBM5",
                "title": "Dyson Supersonic Hair Dryer Special Edition Iron/Fuchsia",
                "price_usd": 399.99,  # ~14,599.63 THB
                "is_prime_in_stock": True,
            },
            {
                "asin": "B09V7H1V99",
                "title": "Xiaomi Smart Air Purifier 4 Pro HEPA Filter 99.97%",
                "price_usd": 169.00,  # ~6,168.50 THB
                "is_prime_in_stock": True,
            },
        ]

    @property
    def platform_name(self) -> str:
        return self._platform_name

    @property
    def base_url(self) -> str:
        return self._base_url

    def fetch(self, keyword: str) -> list[dict[str, Any]]:
        tokens = keyword.lower().split()
        return [
            item
            for item in self._catalog
            if any(token in item["title"].lower() for token in tokens)
        ]

    def parse(self, raw_data: list[dict[str, Any]]) -> list[Product]:
        return [
            Product(
                name=raw["title"],
                price=float(raw["price_usd"]),
                currency="USD",
                platform=self.platform_name,
                url=f"{self.base_url}/s?k={raw['title'].replace(' ', '+')[:60]}",
                in_stock=raw["is_prime_in_stock"],
            )
            for raw in raw_data
        ]


def main() -> None:
    """รันสถานการณ์การสาธิตที่แสดงถึงพลังของการออกแบบ OOP และ OOAD."""
    print("=" * 95)
    print(" ระบบเปรียบเทียบราคาสินค้า PRICEWISE TRACKER (สาธิตสถาปัตยกรรม OOAD & OOP)")
    print("=" * 95)

    # 1. Dependency Injection: กำหนดค่าตัวแปลงค่าเงินและสแครปเปอร์
    currency_converter = FixedRateCurrencyConverter(
        {
            "USD": 1.0,
            "THB": 36.50,
            "EUR": 0.92,
        }
    )

    shopee_scraper = MockShopeeScraper()
    lazada_scraper = MockLazadaScraper()

    # 2. Composition: Engine ได้รับ Dependency ผ่าน Constructor Injection
    engine = PriceComparisonEngine(
        scrapers=[shopee_scraper, lazada_scraper],
        currency_converter=currency_converter,
        target_currency="THB",
    )

    print(f"\n[+] สแครปเปอร์ที่ลงทะเบียน: {[s.platform_name for s in engine.get_registered_scrapers()]}")
    print("[+] สกุลเงินหลักในการเปรียบเทียบ: THB (อัตราแลกเปลี่ยน: 1 USD = 36.50 THB)")

    # สถานการณ์ที่ 1: การเปรียบเทียบราคาในสกุลเงินเดียวกัน (หูฟัง Sony)
    print("\n--- สถานการณ์ที่ 1: การเปรียบเทียบราคาโดยตรงในสกุลเงินเดียวกัน (Sony WH-1000XM5) ---")
    result_sony = engine.compare("Sony")
    print_comparison_table(result_sony)

    # สถานการณ์ที่ 2: การแปลงค่าเงินข้ามพรมแดน (Apple AirPods Pro - THB vs USD)
    print("\n--- สถานการณ์ที่ 2: การปรับมาตรฐานสกุลเงินข้ามพรมแดน (Apple AirPods) ---")
    result_airpods = engine.compare("AirPods")
    print_comparison_table(result_airpods)

    # สถานการณ์ที่ 3: การตรวจสอบและกรองตามสถานะสต็อก (เมาส์ Logitech MX Master 3S)
    print("\n--- สถานการณ์ที่ 3: สถานะสินค้าคงเหลือและการกรองสินค้าที่มีสต็อก (เมาส์ Logitech) ---")
    print(">>> (A) สินค้าทั้งหมด (รวมรายการที่สินค้าหมดสต็อก):")
    result_mouse_all = engine.compare("Logitech", in_stock_only=False)
    print_comparison_table(result_mouse_all)

    print(">>> (B) เฉพาะสินค้าที่มีในสต็อก (In-Stock Only):")
    result_mouse_instock = engine.compare("Logitech", in_stock_only=True)
    print_comparison_table(result_mouse_instock)

    # สถานการณ์ที่ 4: สาธิตหลักการ Open/Closed Principle (ขยายระบบด้วย Amazon Scraper)
    print("\n--- สถานการณ์ที่ 4: หลักการ Open/Closed Principle (เพิ่ม Amazon Scraper แบบไดนามิกขณะทำงาน) ---")
    amazon_scraper = MockAmazonScraper()
    engine.register_scraper(amazon_scraper)
    print(f"[+] ลงทะเบียนสแครปเปอร์ใหม่แบบไดนามิก: '{amazon_scraper.platform_name}'")
    print(f"[+] รวมสแครปเปอร์ที่เปิดใช้งานทั้งหมด: {[s.platform_name for s in engine.get_registered_scrapers()]}")

    print(">>> เปรียบเทียบ 'AirPods' ใหม่อีกครั้งโดยรวมข้อมูลจาก Amazon:")
    result_expanded = engine.compare("AirPods")
    print_comparison_table(result_expanded)


if __name__ == "__main__":
    # รองรับการส่งคำค้นหาผ่าน CLI: python main.py <คำค้นหา>
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        eng = PriceComparisonEngine(
            scrapers=[MockShopeeScraper(), MockLazadaScraper(), MockAmazonScraper()],
            currency_converter=FixedRateCurrencyConverter(),
            target_currency="THB",
        )
        res = eng.compare(query)
        print_comparison_table(res)
    else:
        main()
