"""การทดสอบหน่วยย่อย (Unit Tests) สำหรับสแครปเปอร์ร้านค้าและวงจรชีวิต Template Method

ครอบคลุม:
    - ลำดับวงจรชีวิตของ Template Method (fetch -> parse -> validate)
    - ระบบการตรวจสอบความถูกต้องและการกรองข้อมูลที่ไม่สมบูรณ์ (BaseScraper.validate)
    - การแปลงข้อมูลราคาและลิงก์ของ Shopee (สตางค์ -> บาท)
    - การจัดการสินค้าที่หมดสต็อก
    - การแปลงข้อมูลและราคาสตริงของ Lazada
    - การจัดการสินค้านำเข้าระหว่างประเทศ (USD)
    - พฤติกรรมเมื่อไม่พบสินค้า
"""

from typing import Any
import pytest

from models.product import Product
from scrapers.base import BaseScraper
from scrapers.lazada import MockLazadaScraper
from scrapers.shopee import MockShopeeScraper


class DummyTrackingScraper(BaseScraper):
    """สแครปเปอร์จำลองสำหรับตรวจสอบลำดับขั้นตอนการทำงานของ Template Method"""

    def __init__(self) -> None:
        self.call_log: list[str] = []

    @property
    def platform_name(self) -> str:
        return "DummyPlatform"

    @property
    def base_url(self) -> str:
        return "https://dummy.example.com"

    def fetch(self, keyword: str) -> list[dict[str, Any]]:
        self.call_log.append("fetch")
        return [
            {"name": f"{keyword} Item A", "price": 100.0, "valid": True},
            {"name": f"{keyword} Item B (Invalid Price)", "price": -50.0, "valid": True},
            {"name": "", "price": 200.0, "valid": False},
        ]

    def parse(self, raw_data: list[dict[str, Any]]) -> list[Product]:
        self.call_log.append("parse")
        parsed: list[Product] = []
        for item in raw_data:
            try:
                prod = Product(
                    name=item["name"],
                    price=item["price"],
                    currency="THB",
                    platform=self.platform_name,
                    url=f"{self.base_url}/item",
                    in_stock=True,
                )
                parsed.append(prod)
            except ValueError:
                # หากกฎ Invariant ของโดเมนตรวจพบข้อผิดพลาด (เช่น ชื่อว่างหรือราคาติดลบ)
                pass
        return parsed

    def validate(self, products: list[Product]) -> list[Product]:
        self.call_log.append("validate")
        return super().validate(products)


def test_base_scraper_template_method_lifecycle() -> None:
    """ตรวจสอบว่า scrape() ทำงานเรียงลำดับ fetch -> parse -> validate เสมอ"""
    scraper = DummyTrackingScraper()
    results = scraper.scrape("TestQuery")

    assert scraper.call_log == ["fetch", "parse", "validate"]
    assert len(results) == 1
    assert results[0].name == "TestQuery Item A"
    assert results[0].price == 100.0


def test_base_scraper_validation_filters_invalid_items() -> None:
    """ทดสอบว่า BaseScraper.validate กรองอ็อบเจกต์ที่ผิดปกติหรือราคาไม่ถูกต้องออก"""
    scraper = DummyTrackingScraper()

    valid_prod = Product(
        name="Valid",
        price=50.0,
        currency="THB",
        platform="Dummy",
        url="https://dummy.com/1",
        in_stock=True,
    )

    class TestableScraper(BaseScraper):
        @property
        def platform_name(self) -> str:
            return "Test"

        @property
        def base_url(self) -> str:
            return "https://test.com"

        def fetch(self, keyword: str) -> list[dict[str, Any]]:
            return []

        def parse(self, raw_data: list[dict[str, Any]]) -> list[Product]:
            return []

    test_scraper = TestableScraper()
    # ส่งสินค้าผสมระหว่างอ็อบเจกต์ที่ถูกต้อง และสิ่งที่ไม่ใช่อ็อบเจกต์ Product
    filtered = test_scraper.validate([valid_prod, "not-a-product"])  # type: ignore[list-item]

    assert len(filtered) == 1
    assert filtered[0].name == "Valid"


def test_shopee_scraper_fetch_and_parse() -> None:
    """ทดสอบการดึงและแปลงข้อมูลของ MockShopeeScraper รวมถึงการแปลงสตางค์เป็นบาท"""
    scraper = MockShopeeScraper()
    assert scraper.platform_name == "Shopee"
    assert "shopee.co.th" in scraper.base_url

    results = scraper.scrape("Sony")
    assert len(results) >= 1

    sony_item = next((p for p in results if "Sony" in p.name), None)
    assert sony_item is not None
    assert sony_item.price == 11990.00  # แปลงจาก 1,199,000 สตางค์
    assert sony_item.currency == "THB"
    assert sony_item.in_stock is True
    assert "shopee.co.th/product/" in sony_item.url


def test_shopee_scraper_out_of_stock_item() -> None:
    """ทดสอบว่า MockShopeeScraper จัดการสินค้าที่หมดสต็อกได้อย่างถูกต้อง"""
    scraper = MockShopeeScraper()
    results = scraper.scrape("Logitech")

    assert len(results) >= 1
    logitech = next((p for p in results if "Logitech" in p.name), None)
    assert logitech is not None
    assert logitech.in_stock is False
    assert logitech.price == 3390.00


def test_lazada_scraper_fetch_and_parse() -> None:
    """ทดสอบการแปลงข้อมูลราคาสตริงและ URL ของ MockLazadaScraper"""
    scraper = MockLazadaScraper()
    assert scraper.platform_name == "Lazada"
    assert "lazada.co.th" in scraper.base_url

    results = scraper.scrape("Sony")
    assert len(results) >= 1

    sony_item = next((p for p in results if "Sony" in p.name), None)
    assert sony_item is not None
    assert sony_item.price == 11450.00
    assert sony_item.currency == "THB"
    assert sony_item.in_stock is True
    assert "lazada.co.th/products/" in sony_item.url


def test_lazada_scraper_currency_variation() -> None:
    """ทดสอบว่า MockLazadaScraper ส่งคืนสินค้าที่มีสกุลเงินต่างประเทศ (USD) ได้ถูกต้อง"""
    scraper = MockLazadaScraper()
    results = scraper.scrape("AirPods")

    assert len(results) >= 1
    airpods = next((p for p in results if "AirPods" in p.name), None)
    assert airpods is not None
    assert airpods.currency == "USD"
    assert airpods.price == 219.00
    assert airpods.in_stock is True


def test_scraper_no_match() -> None:
    """ทดสอบพฤติกรรมเมื่อคำค้นหาไม่ตรงกับสินค้าใด ๆ ในระบบ"""
    shopee = MockShopeeScraper()
    lazada = MockLazadaScraper()

    assert shopee.scrape("NonExistentItemXYZ123") == []
    assert lazada.scrape("NonExistentItemXYZ123") == []
