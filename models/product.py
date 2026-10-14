"""โมเดลข้อมูลโดเมน (Domain Model) สำหรับสินค้าในระบบเปรียบเทียบราคา

ปฏิบัติตามหลักการเชิงวัตถุ:
    - Encapsulation: ห่อหุ้มแอตทริบิวต์และตรวจสอบความถูกต้องของข้อมูล (Invariants)
    - Immutability: กำหนดให้เป็น dataclass(frozen=True) เพื่อความปลอดภัยของข้อมูล
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _get_utc_now() -> datetime:
    """ฟังก์ชันตัวช่วยส่งคืนวันเวลาปัจจุบันในรูปแบบ UTC พร้อม Timezone."""
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class Product:
    """โมเดลโดเมนแทนข้อมูลสินค้าที่ดึงมาจากแพลตฟอร์มอีคอมเมิร์ซต่าง ๆ

    Attributes:
        name: ชื่อสินค้าที่แสดงผล
        price: ราคาสินค้าเชิงตัวเลข
        currency: รหัสสกุลเงินตามมาตรฐาน ISO 4217 (เช่น 'THB', 'USD')
        platform: ชื่อแพลตฟอร์มของร้านค้า (เช่น 'Shopee', 'Lazada', 'Amazon')
        url: ลิงก์ตรงหรือ URL ไปยังหน้ารายละเอียดสินค้า
        in_stock: สถานะความพร้อมจำหน่าย (True หากมีสินค้าในสต็อก)
        scraped_at: เวลาที่ดึงข้อมูลบันทึกไว้ในรูปแบบ UTC
    """

    name: str
    price: float
    currency: str
    platform: str
    url: str
    in_stock: bool
    scraped_at: datetime = field(default_factory=_get_utc_now)

    def __post_init__(self) -> None:
        """ตรวจสอบความถูกต้องของกฎสถาปัตยกรรม (Domain Invariants) เมื่อสร้างอ็อบเจกต์."""
        if not self.name or not self.name.strip():
            raise ValueError("ชื่อสินค้าต้องไม่เป็นค่าว่าง")
        if self.price < 0:
            raise ValueError(f"ราคาสินค้าต้องไม่ติดลบ: {self.price}")
        if not self.currency or len(self.currency.strip()) != 3:
            raise ValueError(f"รหัสสกุลเงินไม่ถูกต้อง: {self.currency} ต้องเป็นรหัส ISO 3 ตัวอักษร")
        if not self.platform or not self.platform.strip():
            raise ValueError("ชื่อแพลตฟอร์มต้องไม่เป็นค่าว่าง")

    def formatted_price(self) -> str:
        """ส่งคืนข้อความแสดงราคาที่จัดรูปแบบพร้อมรหัสสกุลเงินอย่างสวยงาม."""
        return f"{self.currency.upper()} {self.price:,.2f}"

    def to_dict(self) -> dict[str, Any]:
        """แปลงโมเดลโดเมนให้อยู่ในรูปแบบ Dictionary สำหรับ Serialization."""
        return {
            "name": self.name,
            "price": self.price,
            "currency": self.currency,
            "platform": self.platform,
            "url": self.url,
            "in_stock": self.in_stock,
            "scraped_at": self.scraped_at.isoformat(),
        }
