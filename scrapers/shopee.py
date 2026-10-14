"""คลาสสแครปเปอร์จำลองการดึงข้อมูลจากแพลตฟอร์ม Shopee (MockShopeeScraper)

จำลองโครงสร้างข้อมูล API ของ Shopee ที่มักเก็บราคาเป็นหน่วยสตางค์ (Satang)
และมีข้อมูลจำนวนสินค้าคงคลัง (Stock Count)
"""

from datetime import datetime, timezone
from typing import Any

from models.product import Product
from scrapers.base import BaseScraper


class MockShopeeScraper(BaseScraper):
    """สแครปเปอร์รูปธรรมจำลองการดึงข้อมูลสินค้าจาก Shopee Marketplace

    จำลองโครงสร้าง JSON API ของ Shopee ที่ราคาแสดงผลเป็นหน่วยสตางค์ (คูณด้วย 100)
    และมีข้อมูลสินค้าหลากหลายหมวดหมู่เพื่อการเปรียบเทียบราคาอย่างสมจริง
    """

    def __init__(self) -> None:
        self._platform_name: str = "Shopee"
        self._base_url: str = "https://shopee.co.th"

        # แคตตาล็อกสินค้า 26 รายการครอบคลุมหลากหลายหมวดหมู่ยอดนิยม
        # url = Shopee search URL จริง (รับประกันใช้งานได้เสมอ)
        self._catalog: list[dict[str, Any]] = [
            # 1. หูฟัง & ระบบเสียง (Audio)
            {
                "item_id": "sp_101",
                "item_name": "Sony WH-1000XM5 หูฟังไร้สายตัดเสียงรบกวน (สีดำ)",
                "price_satang": 1199000,
                "currency": "THB",
                "stock_count": 14,
                "url": "https://shopee.co.th/search?keyword=Sony+WH-1000XM5",
            },
            {
                "item_id": "sp_102",
                "item_name": "Apple AirPods Pro (รุ่นที่ 2) พร้อมเคสชาร์จ MagSafe (USB-C)",
                "price_satang": 789000,
                "currency": "THB",
                "stock_count": 8,
                "url": "https://shopee.co.th/search?keyword=Apple+AirPods+Pro+2+USB-C",
            },
            {
                "item_id": "sp_106",
                "item_name": "Bose QuietComfort 45 หูฟังไร้สายตัดเสียงรบกวน",
                "price_satang": 1050000,
                "currency": "THB",
                "stock_count": 6,
                "url": "https://shopee.co.th/search?keyword=Bose+QuietComfort+45",
            },
            {
                "item_id": "sp_107",
                "item_name": "Marshall Major IV หูฟังบลูทูธไร้สาย แบตเตอรี่ 80 ชั่วโมง",
                "price_satang": 479000,
                "currency": "THB",
                "stock_count": 12,
                "url": "https://shopee.co.th/search?keyword=Marshall+Major+IV",
            },
            {
                "item_id": "sp_108",
                "item_name": "Marshall Emberton II ลำโพงบลูทูธพกพา พลังเสียงรอบทิศทาง",
                "price_satang": 599000,
                "currency": "THB",
                "stock_count": 9,
                "url": "https://shopee.co.th/search?keyword=Marshall+Emberton+II",
            },
            {
                "item_id": "sp_109",
                "item_name": "Shure SM7B ไมโครโฟนไดนามิกระดับสตูดิโอ สำหรับพอดแคสต์และสตรีมมิ่ง",
                "price_satang": 1420000,
                "currency": "THB",
                "stock_count": 4,
                "url": "https://shopee.co.th/search?keyword=Shure+SM7B",
            },

            # 2. คอมพิวเตอร์ คีย์บอร์ด & อุปกรณ์ต่อพ่วง (PC & Gadgets)
            {
                "item_id": "sp_103",
                "item_name": "Logitech MX Master 3S เมาส์ไร้สายบลูทูธเพื่อการทำงาน (สี Graphite)",
                "price_satang": 339000,
                "currency": "THB",
                "stock_count": 0,  # สินค้าหมดสต็อกบน Shopee
                "url": "https://shopee.co.th/search?keyword=Logitech+MX+Master+3S",
            },
            {
                "item_id": "sp_104",
                "item_name": "Keychron K2 V2 คีย์บอร์ดไร้สาย Mechanical Keyboard (Gateron Brown)",
                "price_satang": 285000,
                "currency": "THB",
                "stock_count": 7,
                "url": "https://shopee.co.th/search?keyword=Keychron+K2+V2",
            },
            {
                "item_id": "sp_110",
                "item_name": "Apple MacBook Air 13 นิ้ว ชิป M2 (RAM 8GB / SSD 256GB)",
                "price_satang": 3290000,
                "currency": "THB",
                "stock_count": 5,
                "url": "https://shopee.co.th/search?keyword=MacBook+Air+M2+13",
            },
            {
                "item_id": "sp_111",
                "item_name": "ASUS ROG Zephyrus G14 โน้ตบุ๊กเกมมิ่งสเปกแรง Ryzen 9",
                "price_satang": 4990000,
                "currency": "THB",
                "stock_count": 0,  # สินค้าหมด
                "url": "https://shopee.co.th/search?keyword=ASUS+ROG+Zephyrus+G14",
            },
            {
                "item_id": "sp_112",
                "item_name": "Dell UltraSharp U2723QE จอมอนิเตอร์ 27 นิ้ว 4K IPS Black",
                "price_satang": 1950000,
                "currency": "THB",
                "stock_count": 3,
                "url": "https://shopee.co.th/search?keyword=Dell+UltraSharp+U2723QE",
            },
            {
                "item_id": "sp_113",
                "item_name": "Elgato Stream Deck MK.2 คอนโทรลเลอร์ควบคุมการสตรีม 15 ปุ่ม LCD",
                "price_satang": 489000,
                "currency": "THB",
                "stock_count": 11,
                "url": "https://shopee.co.th/search?keyword=Elgato+Stream+Deck+MK2",
            },

            # 3. สมาร์ทโฟน & แท็บเล็ต (Smartphones & Tablets)
            {
                "item_id": "sp_105",
                "item_name": "Samsung Galaxy Tab S9 128GB Wi-Fi แท็บเล็ต (สี Graphite)",
                "price_satang": 2490000,
                "currency": "THB",
                "stock_count": 4,
                "url": "https://shopee.co.th/search?keyword=Samsung+Galaxy+Tab+S9",
            },
            {
                "item_id": "sp_114",
                "item_name": "Apple iPad Air 5 (M1) 64GB Wi-Fi หน้าจอ Liquid Retina 10.9 นิ้ว",
                "price_satang": 1890000,
                "currency": "THB",
                "stock_count": 10,
                "url": "https://shopee.co.th/search?keyword=iPad+Air+5+M1+64GB",
            },
            {
                "item_id": "sp_115",
                "item_name": "Apple iPhone 15 Pro Max 256GB ไทเทเนียมธรรมชาติ",
                "price_satang": 4150000,
                "currency": "THB",
                "stock_count": 6,
                "url": "https://shopee.co.th/search?keyword=iPhone+15+Pro+Max+256GB",
            },
            {
                "item_id": "sp_116",
                "item_name": "Samsung Galaxy S24 Ultra 256GB กล้อง 200MP พร้อมปากกา S-Pen",
                "price_satang": 4190000,
                "currency": "THB",
                "stock_count": 5,
                "url": "https://shopee.co.th/search?keyword=Samsung+Galaxy+S24+Ultra",
            },
            {
                "item_id": "sp_117",
                "item_name": "Xiaomi 14 Pro 512GB สมาร์ทโฟนเลนส์กล้อง Leica Summilux",
                "price_satang": 2890000,
                "currency": "THB",
                "stock_count": 8,
                "url": "https://shopee.co.th/search?keyword=Xiaomi+14+Pro+512GB",
            },

            # 4. เกมมิ่งและคอนโซล (Gaming & Consoles)
            {
                "item_id": "sp_118",
                "item_name": "PlayStation 5 Slim (PS5) เครื่องเล่นเกมคอนโซล รุ่นใส่แผ่น",
                "price_satang": 1749000,
                "currency": "THB",
                "stock_count": 7,
                "url": "https://shopee.co.th/search?keyword=PlayStation+5+Slim",
            },
            {
                "item_id": "sp_119",
                "item_name": "Nintendo Switch OLED Model คอนโซลเกมหน้าจอโอเล็ด 7 นิ้ว",
                "price_satang": 1049000,
                "currency": "THB",
                "stock_count": 15,
                "url": "https://shopee.co.th/search?keyword=Nintendo+Switch+OLED",
            },
            {
                "item_id": "sp_120",
                "item_name": "Xbox Series X คอนโซล 1TB 4K 120FPS พลังประมวลผลสูง",
                "price_satang": 1820000,
                "currency": "THB",
                "stock_count": 4,
                "url": "https://shopee.co.th/search?keyword=Xbox+Series+X",
            },

            # 5. สมาร์ทวอทช์ & สุขภาพ (Smartwatches)
            {
                "item_id": "sp_121",
                "item_name": "Apple Watch Series 9 GPS ตัวเรือนอะลูมิเนียม ขนาด 41 มม.",
                "price_satang": 1390000,
                "currency": "THB",
                "stock_count": 9,
                "url": "https://shopee.co.th/search?keyword=Apple+Watch+Series+9+41mm",
            },
            {
                "item_id": "sp_122",
                "item_name": "Garmin Forerunner 265 นาฬิกาวิ่ง GPS จอ AMOLED ระบบสัมผัส",
                "price_satang": 1549000,
                "currency": "THB",
                "stock_count": 6,
                "url": "https://shopee.co.th/search?keyword=Garmin+Forerunner+265",
            },

            # 6. กล้อง & ไลฟ์สไตล์ (Cameras & Smart Living)
            {
                "item_id": "sp_123",
                "item_name": "DJI Osmo Pocket 3 Creator Combo กล้องพกพากิมบอลกันสั่น 3 แกน",
                "price_satang": 2190000,
                "currency": "THB",
                "stock_count": 5,
                "url": "https://shopee.co.th/search?keyword=DJI+Osmo+Pocket+3",
            },
            {
                "item_id": "sp_124",
                "item_name": "GoPro HERO12 Black กล้องแอคชั่นแคม กันน้ำ 10 เมตร วิดีโอ 5.3K",
                "price_satang": 1390000,
                "currency": "THB",
                "stock_count": 8,
                "url": "https://shopee.co.th/search?keyword=GoPro+HERO12+Black",
            },
            {
                "item_id": "sp_125",
                "item_name": "Dyson Supersonic ไดร์เป่าผมเทคโนโลยีมอเตอร์ดิจิทัล V9",
                "price_satang": 1490000,
                "currency": "THB",
                "stock_count": 6,
                "url": "https://shopee.co.th/search?keyword=Dyson+Supersonic",
            },
            {
                "item_id": "sp_126",
                "item_name": "Xiaomi Smart Air Purifier 4 Pro เครื่องฟอกอากาศอัจฉริยะกรอง PM2.5",
                "price_satang": 549000,
                "currency": "THB",
                "stock_count": 18,
                "url": "https://shopee.co.th/search?keyword=Xiaomi+Smart+Air+Purifier+4+Pro",
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
        """จำลองการค้นหาและดึงข้อมูลดิบจาก API ของ Shopee ตามคำค้นหา"""
        clean_kw = keyword.strip().lower()
        if clean_kw in ("all", "ทั้งหมด", "*"):
            return [dict(item) for item in self._catalog]

        search_terms = clean_kw.split()
        results: list[dict[str, Any]] = []

        for item in self._catalog:
            item_name = item["item_name"].lower()
            if any(term in item_name for term in search_terms):
                results.append(dict(item))

        return results

    def parse(self, raw_data: list[dict[str, Any]]) -> list[Product]:
        """แปลงข้อมูลดิบของ Shopee ให้อยู่ในรูปอ็อบเจกต์โดเมน Product"""
        products: list[Product] = []

        for raw_item in raw_data:
            price_satang = raw_item.get("price_satang", 0)
            price_thb = round(price_satang / 100.0, 2)
            url = raw_item.get("url", self._base_url)
            stock_count = raw_item.get("stock_count", 0)

            product = Product(
                name=raw_item.get("item_name", "สินค้าไม่ระบุชื่อ"),
                price=price_thb,
                currency=raw_item.get("currency", "THB"),
                platform=self.platform_name,
                url=url,
                in_stock=stock_count > 0,
                scraped_at=datetime.now(timezone.utc),
            )
            products.append(product)

        return products
