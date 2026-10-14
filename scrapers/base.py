"""คลาสฐานนามธรรม (Abstract Base Class) สำหรับตัวดึงข้อมูลสินค้า

ประยุกต์ใช้ดีไซน์แพตเทิร์น:
    - Template Method Pattern: กำหนดโครงสร้างขั้นตอนการทำงานที่แน่นอนใน scrape()
      และมอบหมายหน้าที่ดึงข้อมูล (fetch) และแปลงข้อมูล (parse) ให้คลาสลูกไปทำ
    - Liskov Substitution Principle: คลาสลูกทุกคลาสสามารถทำงานแทน BaseScraper ได้อย่างสมบูรณ์
"""

from abc import ABC, abstractmethod
import logging
from typing import Any

from models.product import Product

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """คลาสฐานนามธรรมสำหรับสแครปเปอร์สินค้าตามรูปแบบ Template Method Pattern

    เมธอด `scrape()` กำหนดโครงสร้างการทำงานแบบตายตัวของอัลกอริทึม
    โดยมอบหมายให้คลาสลูกเขียนรายละเอียดการดึงข้อมูลเฉพาะแพลตฟอร์มใน `fetch()`
    และการแปลงข้อมูลใน `parse()` พร้อมมีระบบตรวจสอบความถูกต้อง (validate) ที่ได้มาตรฐาน

    คลาสลูกต้องอิมพลีเมนต์:
        - `platform_name`: พร็อพเพอร์ตี้ส่งคืนชื่อร้านค้า/แพลตฟอร์ม
        - `base_url`: พร็อพเพอร์ตี้ส่งคืน URL หลักของแพลตฟอร์ม
        - `fetch(keyword)`: ดึงข้อมูลดิบ (Raw Data) สำหรับคำค้นหานั้น
        - `parse(raw_data)`: แปลงข้อมูลดิบของแพลตฟอร์มให้เป็นอ็อบเจกต์โดเมน Product

    คลาสลูกสามารถ Override เพิ่มเติมได้:
        - `validate(products)`: ฮุกตรวจสอบความถูกต้องเพิ่มเติมตามกฎธุรกิจเฉพาะ
    """

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """ส่งคืนชื่อที่แสดงของแพลตฟอร์มอีคอมเมิร์ซ"""
        pass

    @property
    @abstractmethod
    def base_url(self) -> str:
        """ส่งคืน URL เริ่มต้นของแพลตฟอร์ม"""
        pass

    @abstractmethod
    def fetch(self, keyword: str) -> list[dict[str, Any]]:
        """ดึงข้อมูลดิบจากแพลตฟอร์มร้านค้า

        Args:
            keyword: คำค้นหาสินค้า

        Returns:
            รายการข้อมูลดิบ (Dictionary) ที่ได้รับจากแพลตฟอร์ม
        """
        pass

    @abstractmethod
    def parse(self, raw_data: list[dict[str, Any]]) -> list[Product]:
        """แปลงข้อมูลดิบที่ได้จากร้านค้าให้อยู่ในรูปอ็อบเจกต์โดเมน Product

        Args:
            raw_data: รายการข้อมูลดิบที่ได้จาก `fetch()`

        Returns:
            รายการอ็อบเจกต์ `Product` ที่แปลงเรียบร้อยแล้ว
        """
        pass

    def validate(self, products: list[Product]) -> list[Product]:
        """ตรวจสอบความถูกต้องและกรองสินค้าที่ไม่ได้คุณภาพออก

        การตรวจสอบมาตรฐานครอบคลุม:
            1. ต้องเป็นอินสแตนซ์ของคลาส `Product`
            2. ราคาสินค้าต้องมากกว่าศูนย์ (> 0)
            3. ชื่อสินค้าต้องไม่เป็นค่าว่าง
            4. ต้องมี URL ของสินค้าที่ถูกต้อง

        Args:
            products: รายการสินค้า `Product` ที่ต้องการตรวจสอบ

        Returns:
            รายการสินค้า `Product` ที่ผ่านเกณฑ์คุณภาพทั้งหมด
        """
        validated_products: list[Product] = []
        for product in products:
            if not isinstance(product, Product):
                logger.warning(f"[{self.platform_name}] ข้ามอ็อบเจกต์ที่ไม่ใช่ Product: {product}")
                continue

            if product.price <= 0:
                logger.warning(
                    f"[{self.platform_name}] ข้ามสินค้าที่ราคาไม่ถูกต้อง (<= 0): {product.name} ({product.price})"
                )
                continue

            if not product.name.strip():
                logger.warning(f"[{self.platform_name}] ข้ามสินค้าที่ไม่มีชื่อ")
                continue

            if not product.url.strip():
                logger.warning(f"[{self.platform_name}] ข้ามสินค้าที่ไม่มี URL: {product.name}")
                continue

            validated_products.append(product)

        return validated_products

    def scrape(self, keyword: str) -> list[Product]:
        """Template Method ที่กำหนดวงจรชีวิตการทำงานมาตรฐานในการดึงข้อมูลสินค้า

        ขั้นตอนในวงจรชีวิต (Lifecycle Steps):
            1. ดึงข้อมูลดิบ: `fetch(keyword)`
            2. แปลงข้อมูลดิบเป็นโดเมนโมเดล: `parse(raw_data)`
            3. ตรวจสอบความถูกต้องของโดเมนโมเดล: `validate(products)`

        Args:
            keyword: คำค้นหาสินค้า

        Returns:
            รายการอ็อบเจกต์โดเมน `Product` ที่ผ่านการตรวจสอบแล้ว
        """
        logger.info(f"[{self.platform_name}] เริ่มต้นวงจรชีวิตการดึงข้อมูลสำหรับคำค้นหา '{keyword}'...")

        # ขั้นตอนที่ 1: ดึงข้อมูลดิบ (Fetch)
        raw_data = self.fetch(keyword)
        logger.debug(f"[{self.platform_name}] ดึงข้อมูลดิบสำเร็จ {len(raw_data)} รายการ")

        # ขั้นตอนที่ 2: แปลงข้อมูล (Parse)
        parsed_products = self.parse(raw_data)
        logger.debug(f"[{self.platform_name}] แปลงข้อมูลเป็น Product สำเร็จ {len(parsed_products)} รายการ")

        # ขั้นตอนที่ 3: ตรวจสอบความถูกต้อง (Validate)
        validated_products = self.validate(parsed_products)
        logger.info(
            f"[{self.platform_name}] ดึงและตรวจสอบข้อมูลเสร็จสมบูรณ์ {len(validated_products)} รายการ"
        )

        return validated_products
