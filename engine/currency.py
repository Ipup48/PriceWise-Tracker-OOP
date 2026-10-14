"""บริการแปลงอัตราแลกเปลี่ยนเงินตรา (Currency Converter Service)

ปฏิบัติตามหลักการออกแบบ:
    - Interface Segregation & Dependency Inversion: ให้บริการผ่าน Abstract Base Class (ICurrencyConverter)
    - Open/Closed Principle: สามารถเพิ่มหรือปรับเปลี่ยนอัตราแลกเปลี่ยนได้ขณะทำงานโดยไม่ต้องแก้ไขโค้ดเดิม
"""

from abc import ABC, abstractmethod


class ICurrencyConverter(ABC):
    """อินเทอร์เฟซนามธรรมสำหรับการแปลงอัตราแลกเปลี่ยนสกุลเงิน."""

    @abstractmethod
    def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        """แปลงมูลค่าเงินจากสกุลเงินหนึ่งไปยังอีกสกุลเงินหนึ่ง

        Args:
            amount: จำนวนเงินตัวเลขที่ต้องการแปลง
            from_currency: รหัส ISO 4217 ของสกุลเงินต้นทาง
            to_currency: รหัส ISO 4217 ของสกุลเงินเป้าหมาย

        Returns:
            จำนวนเงินในสกุลเงินเป้าหมายที่ปัดเศษทศนิยม 2 ตำแหน่ง
        """
        pass

    @abstractmethod
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """ส่งคืนอัตราแลกเปลี่ยนระหว่างสองสกุลเงิน."""
        pass


class FixedRateCurrencyConverter(ICurrencyConverter):
    """คลาสแปลงอัตราแลกเปลี่ยนที่ใช้อัตราคงที่ที่สามารถกำหนดค่าได้

    เก็บอัตราแลกเปลี่ยนโดยอ้างอิงเทียบกับ USD เป็นสกุลเงินแกนกลาง (Pivot Currency)
    ปฏิบัติตาม Open/Closed Principle: สามารถเพิ่มสกุลเงินหรืออัปเดตอัตราแลกเปลี่ยน
    ได้ในขณะทำงานโดยไม่ต้องแก้ไขตรรกะภายในของคลาส
    """

    def __init__(self, rates_to_usd: dict[str, float] | None = None) -> None:
        """เริ่มต้นตัวแปลงสกุลเงินด้วยอัตราแลกเปลี่ยนเทียบกับ 1 USD

        Args:
            rates_to_usd: พจนานุกรมจับคู่รหัสสกุลเงินตัวพิมพ์ใหญ่กับมูลค่าต่อ 1 USD
        """
        # อัตราแลกเปลี่ยนอ้างอิงเริ่มต้น (1 USD = X หน่วยของสกุลเงินนั้น)
        self._rates_to_usd: dict[str, float] = {
            "USD": 1.0,
            "THB": 36.50,
            "EUR": 0.92,
            "GBP": 0.79,
            "JPY": 155.00,
            "SGD": 1.35,
        }
        if rates_to_usd:
            self._rates_to_usd.update({k.upper(): v for k, v in rates_to_usd.items()})

    def set_rate(self, currency: str, rate_to_usd: float) -> None:
        """อัปเดตหรือลงทะเบียนอัตราแลกเปลี่ยนของสกุลเงินเทียบกับ 1 USD"""
        if rate_to_usd <= 0:
            raise ValueError(f"อัตราแลกเปลี่ยนต้องเป็นจำนวนบวก: {rate_to_usd}")
        self._rates_to_usd[currency.upper()] = rate_to_usd

    def get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """คำนวณหาตัวคูณอัตราแลกเปลี่ยนจากสกุลเงินต้นทางไปยังสกุลเงินเป้าหมาย"""
        from_code = from_currency.upper()
        to_code = to_currency.upper()

        if from_code == to_code:
            return 1.0

        if from_code not in self._rates_to_usd:
            raise ValueError(f"ไม่รองรับสกุลเงินต้นทาง: {from_code}")
        if to_code not in self._rates_to_usd:
            raise ValueError(f"ไม่รองรับสกุลเงินเป้าหมาย: {to_code}")

        # การแปลงผ่านแกนกลาง USD:
        # 1 from_currency = (1 / rates[from]) USD
        # USD to target = USD * rates[to]
        # rate = rates[to] / rates[from]
        rate = self._rates_to_usd[to_code] / self._rates_to_usd[from_code]
        return rate

    def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        """แปลงจำนวนเงินระหว่างสองสกุลเงิน"""
        if amount == 0:
            return 0.0
        rate = self.get_exchange_rate(from_currency, to_currency)
        return round(amount * rate, 2)
