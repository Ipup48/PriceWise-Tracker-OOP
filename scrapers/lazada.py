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
        # url = Lazada search URL จริง (รับประกันใช้งานได้เสมอ)
        self._catalog: list[dict[str, Any]] = [
            # 1. หูฟัง & ระบบเสียง (Audio)
            {
                "nid": "laz_8801",
                "title": "Sony WH-1000XM5 หูฟังไร้สายครอบหูตัดเสียงรบกวนพรีเมียม",
                "sale_price": "11450.00",
                "currency_code": "THB",
                "is_available": True,
                "url": "https://www.lazada.co.th/catalog/?q=Sony+WH-1000XM5",
            },
            {
                "nid": "laz_8802",
                "title": "Apple AirPods Pro (รุ่นที่ 2) เคส MagSafe พอร์ต USB-C",
                "sale_price": "219.00",
                "currency_code": "USD",
                "is_available": True,
                "url": "https://www.lazada.co.th/catalog/?q=Apple+AirPods+Pro+2+USB-C",
            },
            {
                "nid": "laz_8806",
                "title": "Bose QuietComfort 45 หูฟังบลูทูธไร้สายตัดเสียงรบกวน",
                "sale_price": "10800.00",
                "currency_code": "THB",
                "is_available": False,
                "url": "https://www.lazada.co.th/catalog/?q=Bose+QuietComfort+45",
            },
            {
                "nid": "laz_8807",
                "title": "Marshall Major IV หูฟังครอบหูไร้สาย สไตล์คลาสสิก แบตอึด",
                "sale_price": "4590.00",
                "currency_code": "THB",
                "is_available": True,
                "url": "https://www.lazada.co.th/catalog/?q=Marshall+Major+IV",
            },
            {
                "nid": "laz_8808",
                "title": "Marshall Emberton II ลำโพงบลูทูธพกพา กันน้ำ IP67",
                "sale_price": "6290.00",
                "currency_code": "THB",
                "is_available": True,
                "url": "https://www.lazada.co.th/catalog/?q=Marshall+Emberton+II",
            },
            {
                "nid": "laz_8809",
                "title": "Shure SM7B ไมโครโฟนสำหรับจัดรายการและบันทึกเสียงร้องมืออาชีพ",
                "sale_price": "14800.00",
                "currency_code": "THB",
                "is_available": True,
                "url": "https://www.lazada.co.th/catalog/?q=Shure+SM7B",
            },

            # 2. คอมพิวเตอร์ คีย์บอร์ด & อุปกรณ์ต่อพ่วง (PC & Gadgets)
            {
                "nid": "laz_8803",
                "title": "Logitech MX Master 3S เมาส์ไร้สายเสียงคลิกเงียบ Quiet Clicks",
                "sale_price": "3190.00",
                "currency_code": "THB",
                "is_available": True,
                "url": "https://www.lazada.co.th/catalog/?q=Logitech+MX+Master+3S",
            },
            {
                "nid": "laz_8804",
                "title": "Keychron K2 V2 เมคานิคอลคีย์บอร์ดไร้สาย Hot-Swappable",
                "sale_price": "2990.00",
                "currency_code": "THB",
                "is_available": True,
                "url": "https://www.lazada.co.th/catalog/?q=Keychron+K2+V2",
            },
            {
                "nid": "laz_8810",
                "title": "Apple MacBook Air 13 นิ้ว ชิป M2 รุ่นเริ่มต้น 256GB Space Gray",
                "sale_price": "33500.00",
                "currency_code": "THB",
                "is_available": True,
                "url": "https://www.lazada.co.th/catalog/?q=MacBook+Air+M2+13+256GB",
            },
            {
                "nid": "laz_8811",
                "title": "ASUS ROG Zephyrus G14 โน้ตบุ๊กเกมมิ่งระดับไฮเอนด์ หน้าจอ 120Hz",
                "sale_price": "48900.00",
                "currency_code": "THB",
                "is_available": True,
                "url": "https://www.lazada.co.th/catalog/?q=ASUS+ROG+Zephyrus+G14",
            },
            {
                "nid": "laz_8812",
                "title": "Dell UltraSharp U2723QE จอมอนิเตอร์ IPS 4K สำหรับงานกราฟิก",
                "sale_price": "19900.00",
                "currency_code": "THB",
                "is_available": True,
                "url": "https://www.lazada.co.th/catalog/?q=Dell+UltraSharp+U2723QE",
            },
            {
                "nid": "laz_8813",
                "title": "Elgato Stream Deck MK.2 แผงปุ่มลัดควบคุมคอนเทนต์สตรีมเมอร์",
                "sale_price": "4690.00",
                "currency_code": "THB",
                "is_available": True,
                "url": "https://www.lazada.co.th/catalog/?q=Elgato+Stream+Deck+MK2",
            },

            # 3. สมาร์ทโฟน & แท็บเล็ต (Smartphones & Tablets)
            {
                "nid": "laz_8805",
                "title": "Samsung Galaxy Tab S9 128GB Wi-Fi แท็บเล็ตหน้าจอคมชัด",
                "sale_price": "24500.00",
                "currency_code": "THB",
                "is_available": True,
                "url": "https://www.lazada.co.th/catalog/?q=Samsung+Galaxy+Tab+S9+128GB",
            },
            {
                "nid": "laz_8814",
                "title": "Apple iPad Air 5 (M1) 64GB Wi-Fi แท็บเล็ตประสิทธิภาพสูง",
                "sale_price": "18490.00",
                "currency_code": "THB",
                "is_available": True,
                "url": "https://www.lazada.co.th/catalog/?q=iPad+Air+5+M1+64GB",
            },
            {
                "nid": "laz_8815",
                "title": "Apple iPhone 15 Pro Max 256GB สมาร์ทโฟนชิป A17 Pro",
                "sale_price": "40900.00",
                "currency_code": "THB",
                "is_available": True,
                "url": "https://www.lazada.co.th/catalog/?q=iPhone+15+Pro+Max+256GB",
            },
            {
                "nid": "laz_8816",
                "title": "Samsung Galaxy S24 Ultra 256GB พร้อมฟีเจอร์ Galaxy AI อัจฉริยะ",
                "sale_price": "42500.00",
                "currency_code": "THB",
                "is_available": True,
                "url": "https://www.lazada.co.th/catalog/?q=Samsung+Galaxy+S24+Ultra+256GB",
            },
            {
                "nid": "laz_8817",
                "title": "Xiaomi 14 Pro 512GB สมาร์ทโฟนเรือธงกล้องระดับมืออาชีพ",
                "sale_price": "29500.00",
                "currency_code": "THB",
                "is_available": True,
                "url": "https://www.lazada.co.th/catalog/?q=Xiaomi+14+Pro+512GB",
            },

            # 4. เกมมิ่งและคอนโซล (Gaming & Consoles)
            {
                "nid": "laz_8818",
                "title": "PlayStation 5 Slim (PS5) เครื่องเล่นเกมคอนโซล รุ่นใส่แผ่น ประกันศูนย์",
                "sale_price": "16990.00",
                "currency_code": "THB",
                "is_available": True,
                "url": "https://www.lazada.co.th/catalog/?q=PlayStation+5+Slim",
            },
            {
                "nid": "laz_8819",
                "title": "Nintendo Switch OLED Model เครื่องเล่นเกมพกพาจอสวยสดใส",
                "sale_price": "10890.00",
                "currency_code": "THB",
                "is_available": True,
                "url": "https://www.lazada.co.th/catalog/?q=Nintendo+Switch+OLED",
            },
            {
                "nid": "laz_8820",
                "title": "Xbox Series X เครื่องคอนโซลเจนใหม่ รองรับ Game Pass",
                "sale_price": "18900.00",
                "currency_code": "THB",
                "is_available": True,
                "url": "https://www.lazada.co.th/catalog/?q=Xbox+Series+X",
            },

            # 5. สมาร์ทวอทช์ & สุขภาพ (Smartwatches)
            {
                "nid": "laz_8821",
                "title": "Apple Watch Series 9 GPS ตัวเรือนอะลูมิเนียม ขนาด 41 มม.",
                "sale_price": "14200.00",
                "currency_code": "THB",
                "is_available": True,
                "url": "https://www.lazada.co.th/catalog/?q=Apple+Watch+Series+9+41mm",
            },
            {
                "nid": "laz_8822",
                "title": "Garmin Forerunner 265 สมาร์ทวอทช์สายวิ่งและออกกำลังกายระดับโปร",
                "sale_price": "15190.00",
                "currency_code": "THB",
                "is_available": True,
                "url": "https://www.lazada.co.th/catalog/?q=Garmin+Forerunner+265",
            },

            # 6. กล้อง & ไลฟ์สไตล์ (Cameras & Smart Living)
            {
                "nid": "laz_8823",
                "title": "DJI Osmo Pocket 3 Creator Combo เซนเซอร์ CMOS 1 นิ้ว จอหมุนได้",
                "sale_price": "22500.00",
                "currency_code": "THB",
                "is_available": True,
                "url": "https://www.lazada.co.th/catalog/?q=DJI+Osmo+Pocket+3",
            },
            {
                "nid": "laz_8824",
                "title": "GoPro HERO12 Black กล้องแอคชั่นบันทึกวิดีโอ HDR และกันสั่น HyperSmooth",
                "sale_price": "14200.00",
                "currency_code": "THB",
                "is_available": True,
                "url": "https://www.lazada.co.th/catalog/?q=GoPro+HERO12+Black",
            },
            {
                "nid": "laz_8825",
                "title": "Dyson Supersonic ไดร์เป่าผมควบคุมความร้อนอัจฉริยะ ผมไม่เสีย",
                "sale_price": "14500.00",
                "currency_code": "THB",
                "is_available": True,
                "url": "https://www.lazada.co.th/catalog/?q=Dyson+Supersonic",
            },
            {
                "nid": "laz_8826",
                "title": "Xiaomi Smart Air Purifier 4 Pro เครื่องฟอกอากาศห้องขนาดใหญ่",
                "sale_price": "5790.00",
                "currency_code": "THB",
                "is_available": True,
                "url": "https://www.lazada.co.th/catalog/?q=Xiaomi+Smart+Air+Purifier+4+Pro",
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

            url = raw_item.get("url", self._base_url)
            currency = raw_item.get("currency_code", "THB")
            is_available = bool(raw_item.get("is_available", False))

            product = Product(
                name=raw_item.get("title", "สินค้าไม่ระบุชื่อ"),
                price=round(price_val, 2),
                currency=currency,
                platform=self.platform_name,
                url=url,
                in_stock=is_available,
                scraped_at=datetime.now(timezone.utc),
            )
            products.append(product)

        return products
