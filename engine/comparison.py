"""เครื่องยนต์เปรียบเทียบราคาสินค้า (Price Comparison Engine)

ปฏิบัติตามหลักการออกแบบ OOAD:
    - Composition: ถือครองคอลเลกชันของสแครปเปอร์ (BaseScraper)
    - Dependency Injection: รับ Scrapers และ Currency Converter ผ่านคอนสตรัคเตอร์
    - Open/Closed Principle: ขยายระบบรองรับสแครปเปอร์ใหม่ได้โดยไม่ต้องแก้ไขโค้ดเดิม
    - Single Responsibility Principle: รับผิดชอบเฉพาะการประสานงาน ปรับค่าเงิน และจัดอันดับราคา
    - Fault Isolation: การล้มเหลวของร้านค้าใดร้านค้าหนึ่งจะไม่ทำให้ระบบหยุดทำงาน
"""

from dataclasses import dataclass, field
import logging
from typing import Sequence

from engine.currency import FixedRateCurrencyConverter, ICurrencyConverter
from models.product import Product
from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ComparisonItem:
    """แทนข้อมูลสินค้าคู่กับราคาที่ปรับเทียบเป็นสกุลเงินเป้าหมายแล้ว

    Attributes:
        product: อ็อบเจกต์โดเมน Product ดั้งเดิมที่ดึงมาจากร้านค้า
        normalized_price: ราคาที่แปลงเป็นสกุลเงินเปรียบเทียบเป้าหมายแล้ว
        target_currency: รหัสสกุลเงินเป้าหมาย
    """

    product: Product
    normalized_price: float
    target_currency: str

    def formatted_normalized_price(self) -> str:
        """ส่งคืนข้อความแสดงราคาเปรียบเทียบในสกุลเงินเป้าหมายที่จัดรูปแบบแล้ว"""
        return f"{self.target_currency.upper()} {self.normalized_price:,.2f}"


@dataclass
class ComparisonResult:
    """รายงานผลการเปรียบเทียบราคาที่รวบรวมจากทุกแพลตฟอร์ม

    Attributes:
        keyword: คำค้นหาที่ใช้ค้นหาในแต่ละแพลตฟอร์ม
        target_currency: สกุลเงินที่ใช้ปรับมาตรฐานเพื่อการเปรียบเทียบราคา
        items: รายการอ็อบเจกต์ ComparisonItem ที่จัดเรียงจากราคาต่ำสุดไปสูงสุด
        errors: พจนานุกรมเก็บข้อความแจ้งเตือนข้อผิดพลาดของแต่ละแพลตฟอร์ม (ถ้ามี)
    """

    keyword: str
    target_currency: str
    items: list[ComparisonItem] = field(default_factory=list)
    errors: dict[str, str] = field(default_factory=dict)

    @property
    def total_count(self) -> int:
        """จำนวนสินค้าทั้งหมดที่ค้นพบ"""
        return len(self.items)

    @property
    def in_stock_items(self) -> list[ComparisonItem]:
        """รายการสินค้าที่มีจำหน่ายในสต็อก"""
        return [item for item in self.items if item.product.in_stock]

    @property
    def best_deal(self) -> ComparisonItem | None:
        """สินค้าที่มีราคาต่ำที่สุดที่มีของในสต็อก หรือราคาต่ำสุดทั้งหมดหากของหมดทุกร้าน"""
        in_stock = self.in_stock_items
        if in_stock:
            return in_stock[0]
        return self.items[0] if self.items else None

    @property
    def min_price(self) -> float:
        """ราคาต่ำสุดในชุดผลลัพธ์ (คืนค่า 0.0 หากไม่มีสินค้า)"""
        return self.items[0].normalized_price if self.items else 0.0

    @property
    def max_price(self) -> float:
        """ราคาสูงสุดในชุดผลลัพธ์ (คืนค่า 0.0 หากไม่มีสินค้า)"""
        return self.items[-1].normalized_price if self.items else 0.0

    @property
    def average_price(self) -> float:
        """ราคาเฉลี่ยของสินค้าทั้งหมดที่ค้นพบ"""
        if not self.items:
            return 0.0
        return round(sum(item.normalized_price for item in self.items) / len(self.items), 2)


class PriceComparisonEngine:
    """คลาสหลักที่ประสานงานสแครปเปอร์ร้านค้า ปรับค่าเงิน และจัดอันดับราคาดีลที่ดีที่สุด

    ปฏิบัติตามหลักการ:
        - Composition: รวบรวมอ็อบเจกต์ BaseScraper หลายรายการ
        - Dependency Injection: รับตัวดึงข้อมูลและตัวแปลงค่าเงินผ่านคอนสตรัคเตอร์
        - Open/Closed Principle: เปิดรับสแครปเปอร์ใหม่โดยไม่กระทบตรรกะการเปรียบเทียบ
        - Single Responsibility Principle: รับผิดชอบประสานงาน รวบรวมข้อมูล ปรับค่าเงิน และจัดอันดับ
    """

    def __init__(
        self,
        scrapers: Sequence[BaseScraper] | None = None,
        currency_converter: ICurrencyConverter | None = None,
        target_currency: str = "THB",
    ) -> None:
        """เริ่มต้นอินสแตนซ์ของระบบเปรียบเทียบราคา

        Args:
            scrapers: รายการสแครปเปอร์เริ่มต้นที่ต้องการลงทะเบียนในระบบ
            currency_converter: เซอร์วิสแปลงค่าเงินตาม ICurrencyConverter (ค่าเริ่มต้นคือ FixedRateCurrencyConverter)
            target_currency: สกุลเงินเป้าหมายที่ใช้เทียบเคียงราคา (ค่าเริ่มต้นคือ 'THB')
        """
        self._scrapers: dict[str, BaseScraper] = {}
        self._currency_converter: ICurrencyConverter = (
            currency_converter if currency_converter is not None else FixedRateCurrencyConverter()
        )
        self._target_currency: str = target_currency.upper()

        if scrapers:
            for scraper in scrapers:
                self.register_scraper(scraper)

    @property
    def target_currency(self) -> str:
        """รหัสสกุลเงินเป้าหมายที่ใช้เปรียบเทียบราคา"""
        return self._target_currency

    @target_currency.setter
    def target_currency(self, currency: str) -> None:
        """กำหนดรหัสสกุลเงินเป้าหมาย"""
        if not currency or len(currency.strip()) != 3:
            raise ValueError(f"รหัสสกุลเงินไม่ถูกต้อง: {currency}")
        self._target_currency = currency.strip().upper()

    def register_scraper(self, scraper: BaseScraper) -> None:
        """ลงทะเบียนสแครปเปอร์ตัวใหม่เข้าสู่ระบบ

        Args:
            scraper: อ็อบเจกต์ที่สืบทอดมาจาก BaseScraper
        """
        if not isinstance(scraper, BaseScraper):
            raise TypeError(f"สแครปเปอร์ต้องเป็นอินสแตนซ์ของ BaseScraper ได้รับประเภท: {type(scraper)}")

        platform_key = scraper.platform_name.strip().lower()
        self._scrapers[platform_key] = scraper
        logger.info(f"ลงทะเบียนสแครปเปอร์สำหรับแพลตฟอร์ม: '{scraper.platform_name}'")

    def unregister_scraper(self, platform_name: str) -> bool:
        """ยกเลิกการลงทะเบียนสแครปเปอร์ตามชื่อแพลตฟอร์ม

        Args:
            platform_name: ชื่อแพลตฟอร์มที่ต้องการถอดออก

        Returns:
            True หากถอดสำเร็จ, False หากไม่พบแพลตฟอร์มดังกล่าว
        """
        platform_key = platform_name.strip().lower()
        if platform_key in self._scrapers:
            del self._scrapers[platform_key]
            logger.info(f"ยกเลิกการลงทะเบียนสแครปเปอร์แพลตฟอร์ม: '{platform_name}'")
            return True
        return False

    def get_registered_scrapers(self) -> list[BaseScraper]:
        """ส่งคืนรายการสแครปเปอร์ทั้งหมดที่ลงทะเบียนอยู่ในระบบปัจจุบัน"""
        return list(self._scrapers.values())

    def compare(
        self,
        keyword: str,
        in_stock_only: bool = False,
    ) -> ComparisonResult:
        """ดึงข้อมูลจากทุกแพลตฟอร์ม รวบรวม แปลงค่าเงิน และเรียงลำดับจากราคาถูกสุดไปแพงสุด

        Args:
            keyword: คำค้นหาสินค้า
            in_stock_only: หากเป็น True จะคัดกรองเฉพาะสินค้าที่มีของในสต็อก

        Returns:
            อ็อบเจกต์ ComparisonResult พร้อมสินค้าที่จัดเรียงและสถิติสรุปผล
        """
        if not keyword or not keyword.strip():
            raise ValueError("คำค้นหาสินค้าต้องไม่เป็นค่าว่าง")

        clean_keyword = keyword.strip()
        all_comparison_items: list[ComparisonItem] = []
        errors: dict[str, str] = {}

        # 1. รวบรวมข้อมูลจากสแครปเปอร์ทั้งหมดพร้อมระบบแยกความผิดพลาด (Fault Isolation)
        for platform_key, scraper in self._scrapers.items():
            try:
                products = scraper.scrape(clean_keyword)
                for product in products:
                    if in_stock_only and not product.in_stock:
                        continue

                    # 2. ปรับมาตรฐานราคาเป็นสกุลเงินเป้าหมาย
                    normalized = self._currency_converter.convert(
                        amount=product.price,
                        from_currency=product.currency,
                        to_currency=self._target_currency,
                    )

                    all_comparison_items.append(
                        ComparisonItem(
                            product=product,
                            normalized_price=normalized,
                            target_currency=self._target_currency,
                        )
                    )
            except Exception as exc:
                error_msg = f"ไม่สามารถดึงข้อมูลจากแพลตฟอร์ม {scraper.platform_name}: {exc}"
                logger.error(error_msg, exc_info=True)
                errors[scraper.platform_name] = str(exc)

        # 3. จัดเรียงสินค้าจากราคาต่ำสุดไปสูงสุด
        all_comparison_items.sort(key=lambda item: item.normalized_price)

        return ComparisonResult(
            keyword=clean_keyword,
            target_currency=self._target_currency,
            items=all_comparison_items,
            errors=errors,
        )
