"""การทดสอบหน่วยย่อย (Unit Tests) สำหรับเครื่องยนต์เปรียบเทียบราคา PriceComparisonEngine

ครอบคลุม:
    - ตรรกะการแปลงสกุลเงิน (Currency Converter)
    - การประกอบอ็อบเจกต์และการฉีดความขึ้นต่อกัน (Composition & Dependency Injection)
    - การจัดเรียงราคาจากต่ำสุดไปสูงสุด
    - การปรับมาตรฐานสกุลเงินข้ามพรมแดน
    - การกรองสถานะสินค้าคงคลัง (In-Stock Filtering)
    - การแยกความผิดพลาดของระบบ (Fault Isolation)
    - การตรวจสอบความถูกต้องของข้อมูลนำเข้า
"""

from typing import Any
import pytest

from engine.comparison import PriceComparisonEngine
from engine.currency import FixedRateCurrencyConverter
from models.product import Product
from scrapers.base import BaseScraper
from scrapers.lazada import MockLazadaScraper
from scrapers.shopee import MockShopeeScraper


class BrokenScraper(BaseScraper):
    """สแครปเปอร์จำลองข้อผิดพลาดเพื่อทดสอบการแยกความผิดพลาด (Fault Isolation)"""

    @property
    def platform_name(self) -> str:
        return "BrokenPlatform"

    @property
    def base_url(self) -> str:
        return "https://broken.example.com"

    def fetch(self, keyword: str) -> list[dict[str, Any]]:
        raise ConnectionError("Simulated network timeout connecting to BrokenPlatform")

    def parse(self, raw_data: list[dict[str, Any]]) -> list[Product]:
        return []


def test_currency_converter_logic() -> None:
    """ทดสอบตรรกะการแปลงอัตราแลกเปลี่ยนและการอัปเดตอัตราแลกเปลี่ยนแบบกำหนดเอง"""
    converter = FixedRateCurrencyConverter({"EUR": 0.90, "THB": 36.00})

    # สกุลเงินเดียวกัน ไม่ต้องแปลง
    assert converter.convert(100.0, "USD", "USD") == 100.0

    # 100 USD เป็น THB = 3600.0 THB
    assert converter.convert(100.0, "USD", "THB") == 3600.0

    # แปลง THB กลับเป็น USD: 3600 / 36 = 100.0
    assert converter.convert(3600.0, "THB", "USD") == 100.0

    # อัปเดตอัตราแลกเปลี่ยนใหม่ขณะทำงาน
    converter.set_rate("THB", 40.0)
    assert converter.convert(100.0, "USD", "THB") == 4000.0

    with pytest.raises(ValueError):
        converter.convert(10.0, "XYZ", "THB")


def test_engine_composition_and_dependency_injection() -> None:
    """ทดสอบการประกอบอ็อบเจกต์และการฉีดความขึ้นต่อกันผ่าน Constructor และเมธอดลงทะเบียน"""
    shopee = MockShopeeScraper()
    lazada = MockLazadaScraper()

    # ฉีดผ่าน Constructor Injection
    engine = PriceComparisonEngine(scrapers=[shopee])
    assert len(engine.get_registered_scrapers()) == 1

    # ลงทะเบียนเพิ่มเติมผ่านเมธอด
    engine.register_scraper(lazada)
    assert len(engine.get_registered_scrapers()) == 2

    # ถอดการลงทะเบียน (Unregister)
    removed = engine.unregister_scraper("Shopee")
    assert removed is True
    assert len(engine.get_registered_scrapers()) == 1

    # กรณีลงทะเบียนอ็อบเจกต์ที่ไม่ถูกต้อง
    with pytest.raises(TypeError):
        engine.register_scraper("not a scraper")  # type: ignore[arg-type]


def test_engine_sorts_lowest_to_highest_price() -> None:
    """ตรวจสอบว่าระบบจัดเรียงสินค้าจากราคาต่ำสุดไปสูงสุดข้ามแพลตฟอร์มอย่างถูกต้อง"""
    shopee = MockShopeeScraper()
    lazada = MockLazadaScraper()
    engine = PriceComparisonEngine(scrapers=[shopee, lazada], target_currency="THB")

    # ค้นหาหูฟัง Sony
    result = engine.compare("Sony")
    assert result.total_count == 2
    assert len(result.items) == 2

    # ตรวจสอบการเรียงลำดับจากน้อยไปมาก
    # Lazada ราคา 11,450.00 THB vs Shopee ราคา 11,990.00 THB
    first_item = result.items[0]
    second_item = result.items[1]

    assert first_item.normalized_price <= second_item.normalized_price
    assert first_item.product.platform == "Lazada"
    assert first_item.normalized_price == 11450.00
    assert second_item.product.platform == "Shopee"
    assert second_item.normalized_price == 11990.00

    # สถิติสรุปผล
    assert result.best_deal is not None
    assert result.best_deal.product.platform == "Lazada"
    assert result.min_price == 11450.00
    assert result.max_price == 11990.00
    assert result.average_price == 11720.00


def test_engine_normalizes_cross_border_currencies() -> None:
    """ทดสอบการปรับมาตรฐานสกุลเงินข้ามพรมแดนให้เป็นสกุลเงินเป้าหมายเดียวกัน"""
    shopee = MockShopeeScraper()
    lazada = MockLazadaScraper()
    # 1 USD = 36.50 THB
    converter = FixedRateCurrencyConverter({"THB": 36.50, "USD": 1.00})
    engine = PriceComparisonEngine(
        scrapers=[shopee, lazada],
        currency_converter=converter,
        target_currency="THB",
    )

    # ค้นหา AirPods
    # ราคา Shopee: 7,890.00 THB
    # ราคา Lazada: 219.00 USD -> 219 * 36.50 = 7,993.50 THB
    result = engine.compare("AirPods")
    assert result.total_count == 2

    cheapest = result.items[0]
    pricier = result.items[1]

    assert cheapest.product.platform == "Shopee"
    assert cheapest.normalized_price == 7890.00
    assert cheapest.product.currency == "THB"

    assert pricier.product.platform == "Lazada"
    assert pricier.normalized_price == 7993.50
    assert pricier.product.currency == "USD"
    assert result.best_deal == cheapest


def test_engine_in_stock_filter() -> None:
    """ทดสอบการกรองเฉพาะสินค้าที่มีในสต็อก"""
    shopee = MockShopeeScraper()
    lazada = MockLazadaScraper()
    engine = PriceComparisonEngine(scrapers=[shopee, lazada])

    # Logitech สินค้าหมดบน Shopee แต่มีจำหน่ายบน Lazada
    unfiltered = engine.compare("Logitech", in_stock_only=False)
    assert unfiltered.total_count == 2

    filtered = engine.compare("Logitech", in_stock_only=True)
    assert filtered.total_count == 1
    assert filtered.items[0].product.platform == "Lazada"
    assert filtered.items[0].product.in_stock is True


def test_engine_fault_isolation() -> None:
    """ทดสอบระบบแยกความผิดพลาด: ร้านค้าที่ล่มต้องไม่ทำให้ระบบทั้งหมดหยุดทำงาน"""
    shopee = MockShopeeScraper()
    broken = BrokenScraper()

    engine = PriceComparisonEngine(scrapers=[shopee, broken])
    result = engine.compare("Sony")

    # ผลลัพธ์จาก Shopee ต้องยังคงได้สำเร็จ
    assert result.total_count >= 1
    assert result.items[0].product.platform == "Shopee"

    # ข้อผิดพลาดของ BrokenPlatform ถูกบันทึกไว้ใน errors
    assert "BrokenPlatform" in result.errors
    assert "Simulated network timeout" in result.errors["BrokenPlatform"]


def test_engine_empty_input_validation() -> None:
    """ทดสอบการตรวจสอบความถูกต้องเมื่อส่งคำค้นหาที่เป็นค่าว่าง"""
    engine = PriceComparisonEngine()
    with pytest.raises(ValueError, match="คำค้นหาสินค้าต้องไม่เป็นค่าว่าง"):
        engine.compare("   ")
