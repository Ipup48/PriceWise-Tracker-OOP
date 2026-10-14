"""คลาสสแครปเปอร์จำลองการดึงข้อมูลจากแพลตฟอร์ม Lazada (MockLazadaScraper)

จำลองโครงสร้างข้อมูล API ของ Lazada ที่เก็บราคาเป็นตัวเลขทศนิยมในรูปแบบสตริง (String Float)
และมีรายการสินค้านำเข้าระหว่างประเทศ (Cross-border) ในสกุลเงินต่างประเทศ เช่น USD
"""

from datetime import datetime, timezone
from typing import Any

from models.product import Product
from scrapers.base import BaseScraper


class MockLazadaScraper(BaseScraper):
    """สแครปเปอร์รูปธรรมจำลองการดึงข้อมูลสินค้าจาก Lazada Marketplace

    จำลองโครงสร้างการตอบกลับแบบ REST/Web API ของ Lazada
    ครอบคลุมสินค้า 26 รายการหลากหลายหมวดหมู่เพื่อการเปรียบเทียบราคาที่มีประสิทธิภาพ
    """

    def __init__(self) -> None:
        self._platform_name: str = "Lazada"
        self._base_url: str = "https://www.lazada.co.th"

        # แคตตาล็อกสินค้า 26 รายการ สอดคล้องกับ Shopee และมีราคาแข่งขันกัน
        self._catalog: list[dict[str, Any]] = [
            # 1. หูฟัง & ระบบเสียง (Audio)
            {
                "nid": "laz_8801",
                "title": "Sony WH-1000XM5 หูฟังไร้สายครอบหูตัดเสียงรบกวนพรีเมียม",
                "sale_price": "11450.00",  # ถูกกว่า Shopee!
                "currency_code": "THB",
                "is_available": True,
                "sku_path": "products/sony-wh-1000xm5-i8801.html",
            },
            {
                "nid": "laz_8802",
                "title": "Apple AirPods Pro (รุ่นที่ 2) เคส MagSafe พอร์ต USB-C",
                "sale_price": "219.00",  # แสดงเป็น USD (~7,993.50 THB)
                "currency_code": "USD",
                "is_available": True,
                "sku_path": "products/apple-airpods-pro-2-i8802.html",
            },
            {
                "nid": "laz_8806",
                "title": "Bose QuietComfort 45 หูฟังบลูทูธไร้สายตัดเสียงรบกวน",
                "sale_price": "10800.00",
                "currency_code": "THB",
                "is_available": False,  # สินค้าหมดสต็อกบน Lazada
                "sku_path": "products/bose-qc-45-i8806.html",
            },
            {
                "nid": "laz_8807",
                "title": "Marshall Major IV หูฟังครอบหูไร้สาย สไตล์คลาสสิก แบตอึด",
                "sale_price": "4590.00",  # ถูกกว่า Shopee!
                "currency_code": "THB",
                "is_available": True,
                "sku_path": "products/marshall-major-iv-i8807.html",
            },
            {
                "nid": "laz_8808",
                "title": "Marshall Emberton II ลำโพงบลูทูธพกพา กันน้ำ IP67",
                "sale_price": "6290.00",
                "currency_code": "THB",
                "is_available": True,
                "sku_path": "products/marshall-emberton-ii-i8808.html",
            },
            {
                "nid": "laz_8809",
                "title": "Shure SM7B ไมโครโฟนสำหรับจัดรายการและบันทึกเสียงร้องมืออาชีพ",
                "sale_price": "14800.00",
                "currency_code": "THB",
                "is_available": True,
                "sku_path": "products/shure-sm7b-i8809.html",
            },

            # 2. คอมพิวเตอร์ คีย์บอร์ด & อุปกรณ์ต่อพ่วง (PC & Gadgets)
            {
                "nid": "laz_8803",
                "title": "Logitech MX Master 3S เมาส์ไร้สายเสียงคลิกเงียบ Quiet Clicks",
                "sale_price": "3190.00",  # มีสินค้าบน Lazada (Shopee หมด)
                "currency_code": "THB",
                "is_available": True,
                "sku_path": "products/logitech-mx-master-3s-i8803.html",
            },
            {
                "nid": "laz_8804",
                "title": "Keychron K2 V2 เมคานิคอลคีย์บอร์ดไร้สาย Hot-Swappable",
                "sale_price": "2990.00",
                "currency_code": "THB",
                "is_available": True,
                "sku_path": "products/keychron-k2-v2-i8804.html",
            },
            {
                "nid": "laz_8810",
                "title": "Apple MacBook Air 13 นิ้ว ชิป M2 รุ่นเริ่มต้น 256GB Space Gray",
                "sale_price": "33500.00",
                "currency_code": "THB",
                "is_available": True,
                "sku_path": "products/macbook-air-m2-i8810.html",
            },
            {
                "nid": "laz_8811",
                "title": "ASUS ROG Zephyrus G14 โน้ตบุ๊กเกมมิ่งระดับไฮเอนด์ หน้าจอ 120Hz",
                "sale_price": "48900.00",  # ถูกกว่า Shopee และมีของพร้อมส่ง!
                "currency_code": "THB",
                "is_available": True,
                "sku_path": "products/asus-rog-zephyrus-g14-i8811.html",
            },
            {
                "nid": "laz_8812",
                "title": "Dell UltraSharp U2723QE จอมอนิเตอร์ IPS 4K สำหรับงานกราฟิก",
                "sale_price": "19900.00",
                "currency_code": "THB",
                "is_available": True,
                "sku_path": "products/dell-ultrasharp-u2723qe-i8812.html",
            },
            {
                "nid": "laz_8813",
                "title": "Elgato Stream Deck MK.2 แผงปุ่มลัดควบคุมคอนเทนต์สตรีมเมอร์",
                "sale_price": "4690.00",  # ถูกกว่า Shopee!
                "currency_code": "THB",
                "is_available": True,
                "sku_path": "products/elgato-stream-deck-mk2-i8813.html",
            },

            # 3. สมาร์ทโฟน & แท็บเล็ต (Smartphones & Tablets)
            {
                "nid": "laz_8805",
                "title": "Samsung Galaxy Tab S9 128GB Wi-Fi แท็บเล็ตหน้าจอคมชัด",
                "sale_price": "24500.00",  # ถูกกว่า Shopee!
                "currency_code": "THB",
                "is_available": True,
                "sku_path": "products/samsung-galaxy-tab-s9-i8805.html",
            },
            {
                "nid": "laz_8814",
                "title": "Apple iPad Air 5 (M1) 64GB Wi-Fi แท็บเล็ตประสิทธิภาพสูง",
                "sale_price": "18490.00",  # ถูกกว่า Shopee!
                "currency_code": "THB",
                "is_available": True,
                "sku_path": "products/ipad-air-5-m1-i8814.html",
            },
            {
                "nid": "laz_8815",
                "title": "Apple iPhone 15 Pro Max 256GB สมาร์ทโฟนชิป A17 Pro",
                "sale_price": "40900.00",  # ถูกกว่า Shopee!
                "currency_code": "THB",
                "is_available": True,
                "sku_path": "products/iphone-15-pro-max-256-i8815.html",
            },
            {
                "nid": "laz_8816",
                "title": "Samsung Galaxy S24 Ultra 256GB พร้อมฟีเจอร์ Galaxy AI อัจฉริยะ",
                "sale_price": "42500.00",
                "currency_code": "THB",
                "is_available": True,
                "sku_path": "products/galaxy-s24-ultra-256-i8816.html",
            },
            {
                "nid": "laz_8817",
                "title": "Xiaomi 14 Pro 512GB สมาร์ทโฟนเรือธงกล้องระดับมืออาชีพ",
                "sale_price": "29500.00",
                "currency_code": "THB",
                "is_available": True,
                "sku_path": "products/xiaomi-14-pro-512-i8817.html",
            },

            # 4. เกมมิ่งและคอนโซล (Gaming & Consoles)
            {
                "nid": "laz_8818",
                "title": "PlayStation 5 Slim (PS5) เครื่องเล่นเกมคอนโซล รุ่นใส่แผ่น ประกันศูนย์",
                "sale_price": "16990.00",  # ถูกกว่า Shopee!
                "currency_code": "THB",
                "is_available": True,
                "sku_path": "products/playstation-5-slim-disc-i8818.html",
            },
            {
                "nid": "laz_8819",
                "title": "Nintendo Switch OLED Model เครื่องเล่นเกมพกพาจอสวยสดใส",
                "sale_price": "10890.00",
                "currency_code": "THB",
                "is_available": True,
                "sku_path": "products/nintendo-switch-oled-i8819.html",
            },
            {
                "nid": "laz_8820",
                "title": "Xbox Series X เครื่องคอนโซลเจนใหม่ รองรับ Game Pass",
                "sale_price": "18900.00",
                "currency_code": "THB",
                "is_available": True,
                "sku_path": "products/xbox-series-x-i8820.html",
            },

            # 5. สมาร์ทวอทช์ & สุขภาพ (Smartwatches)
            {
                "nid": "laz_8821",
                "title": "Apple Watch Series 9 GPS ตัวเรือนอะลูมิเนียม ขนาด 41 มม.",
                "sale_price": "14200.00",
                "currency_code": "THB",
                "is_available": True,
                "sku_path": "products/apple-watch-s9-41-i8821.html",
            },
            {
                "nid": "laz_8822",
                "title": "Garmin Forerunner 265 สมาร์ทวอทช์สายวิ่งและออกกำลังกายระดับโปร",
                "sale_price": "15190.00",  # ถูกกว่า Shopee!
                "currency_code": "THB",
                "is_available": True,
                "sku_path": "products/garmin-forerunner-265-i8822.html",
            },

            # 6. กล้อง & ไลฟ์สไตล์ (Cameras & Smart Living)
            {
                "nid": "laz_8823",
                "title": "DJI Osmo Pocket 3 Creator Combo เซนเซอร์ CMOS 1 นิ้ว จอหมุนได้",
                "sale_price": "22500.00",
                "currency_code": "THB",
                "is_available": True,
                "sku_path": "products/dji-osmo-pocket-3-combo-i8823.html",
            },
            {
                "nid": "laz_8824",
                "title": "GoPro HERO12 Black กล้องแอคชั่นบันทึกวิดีโอ HDR และกันสั่น HyperSmooth",
                "sale_price": "14200.00",
                "currency_code": "THB",
                "is_available": True,
                "sku_path": "products/gopro-hero12-black-i8824.html",
            },
            {
                "nid": "laz_8825",
                "title": "Dyson Supersonic ไดร์เป่าผมควบคุมความร้อนอัจฉริยะ ผมไม่เสีย",
                "sale_price": "14500.00",  # ถูกกว่า Shopee!
                "currency_code": "THB",
                "is_available": True,
                "sku_path": "products/dyson-supersonic-i8825.html",
            },
            {
                "nid": "laz_8826",
                "title": "Xiaomi Smart Air Purifier 4 Pro เครื่องฟอกอากาศห้องขนาดใหญ่",
                "sale_price": "5790.00",
                "currency_code": "THB",
                "is_available": True,
                "sku_path": "products/xiaomi-air-purifier-4-pro-i8826.html",
            },
        ]

    @property
    def platform_name(self) -> str:
        """ส่งคืนชื่อแพลตฟอร์มของร้านค้า"""
        return self._platform_name

    @property
    def base_url(self) -> str:
        """ส่งคืน URL หลักของร้านค้า"""
        return self._base_url

    def fetch(self, keyword: str) -> list[dict[str, Any]]:
        """จำลองการค้นหาและดึงข้อมูลดิบจาก API ของ Lazada ตามคำค้นหา"""
        clean_kw = keyword.strip().lower()
        if clean_kw in ("all", "ทั้งหมด", "*"):
            return [dict(item) for item in self._catalog]

        search_terms = clean_kw.split()
        results: list[dict[str, Any]] = []

        for item in self._catalog:
            title = item["title"].lower()
            if any(term in title for term in search_terms):
                results.append(dict(item))

        return results

    def parse(self, raw_data: list[dict[str, Any]]) -> list[Product]:
        """แปลงข้อมูลดิบของ Lazada ให้อยู่ในรูปอ็อบเจกต์โดเมน Product"""
        products: list[Product] = []

        for raw_item in raw_data:
            try:
                price_val = float(raw_item.get("sale_price", 0.0))
            except (ValueError, TypeError):
                price_val = 0.0

            sku_path = raw_item.get("sku_path", "")
            currency = raw_item.get("currency_code", "THB")
            is_available = bool(raw_item.get("is_available", False))

            product = Product(
                name=raw_item.get("title", "สินค้าไม่ระบุชื่อ"),
                price=round(price_val, 2),
                currency=currency,
                platform=self.platform_name,
                url=f"{self.base_url}/{sku_path}",
                in_stock=is_available,
                scraped_at=datetime.now(timezone.utc),
            )
            products.append(product)

        return products
