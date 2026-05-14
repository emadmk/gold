# 🥇 KeyhanGold — پلتفرم جامع خرید و فروش آنلاین طلا و نقره

> پرامپت تخصصی برای Claude Code جهت پیاده‌سازی end-to-end پلتفرم خرید و فروش طلا و نقره (مدل میلی‌گلد + مارکت‌پلیس چندفروشندگی) برای بازار ایران.

---

## 🎯 مأموریت (Mission)

یک پلتفرم تولیدی، production-ready، scalable و امن بساز که:

1. **بخش اصلی (First-Party):** فروش طلای آب‌شده ۱۸ عیار و نقره ۹۹۹ به‌صورت دیجیتال (مدل میلی)، با کیف پول طلا و کیف پول ریالی، خرید/فروش لحظه‌ای، انتقال داخلی، و درخواست تحویل فیزیکی.
2. **بخش مارکت‌پلیس (Third-Party):** فروشندگان متعدد می‌توانند محصولات زیر را عرضه کنند:
   - طلای آب‌شده با اجرت/سود شخصی فروشنده
   - طلای ساخته‌شده (دستبند، انگشتر، گردنبند، گوشواره، النگو) با عیار/وزن/اجرت‌ساخت/سود
   - سکه (تمام، نیم، ربع، گرمی، بهار آزادی، امامی)
3. **پنل ادمین کامل** برای کنترل تمام پارامترها (کارمزدها، ضرایب، فروشندگان، سفارش‌ها، احراز هویت، گزارش‌ها).

**نام پروژه:** `keyhan-gold` (با اشاره به برند Keyhan Kian — قابل تغییر).

---

## 🏗️ Stack فنی (اجباری — تخطی نکن)

### Backend
- **Python:** 3.13+
- **Django:** 5.2 LTS (مجاز فقط `>=5.2,<5.3`)
- **DRF:** Django REST Framework آخرین نسخه
- **DB:** PostgreSQL 16+
- **Cache & Broker:** Redis 7+
- **Async tasks:** Celery 5.4+ با Redis broker
- **Realtime:** Django Channels 4 + Daphne (برای WebSocket قیمت لحظه‌ای و وضعیت پرداخت)
- **Auth:** JWT با `djangorestframework-simplejwt`، rotation و blacklist فعال
- **API Docs:** drf-spectacular (OpenAPI 3.1)

### Frontend
- **Next.js:** 16.x (App Router، نه Pages Router)
- **React:** Canary built-in در Next 16 (شامل 19.2)
- **TypeScript:** strict mode فعال
- **Styling:** Tailwind CSS v4 + shadcn/ui (RTL adapted)
- **State:** Zustand برای client state، React Server Components برای server data
- **Forms:** react-hook-form + zod
- **Charts:** Recharts برای نمودار قیمت
- **i18n:** فارسی پیش‌فرض با next-intl، اعداد فارسی، تقویم شمسی با `dayjs-jalali`
- **Font:** IRANSans X یا IRANYekan WebFont (هر دو در `/public/fonts` و در `globals.css` با `@font-face` بارگذاری شوند)

### DevOps
- **Containerization:** Docker + Docker Compose
- **Reverse proxy:** Traefik 3 یا Nginx (انتخاب: Traefik برای auto-SSL با Let's Encrypt)
- **Storage:** MinIO برای فایل‌های احراز هویت (S3-compatible)
- **Monitoring:** Sentry برای error tracking، Prometheus + Grafana برای metrics
- **Logging:** structlog با خروجی JSON

### Monorepo Layout
```
keyhan-gold/
├── backend/                    # Django 5.2
│   ├── apps/
│   │   ├── accounts/           # User, OTP, KYC
│   │   ├── wallet/             # Rial wallet + Gold wallet
│   │   ├── pricing/            # Live price engine + tgju crawler
│   │   ├── orders/             # Orders + payment lifecycle
│   │   ├── marketplace/        # Vendors + their products
│   │   ├── coins/              # Coin types catalog
│   │   ├── jewelry/            # Crafted gold products
│   │   ├── delivery/           # Physical delivery requests
│   │   ├── payments/           # Multi-gateway abstraction
│   │   ├── notifications/      # SMS + push + email
│   │   ├── admin_panel/        # Custom admin business logic
│   │   └── audit/              # Audit log + compliance
│   ├── core/                   # settings, urls, asgi, wsgi, celery
│   ├── manage.py
│   └── requirements/
│       ├── base.txt
│       ├── dev.txt
│       └── prod.txt
├── frontend/                   # Next.js 16
│   ├── app/
│   │   ├── (auth)/
│   │   ├── (shop)/
│   │   ├── (account)/
│   │   ├── (admin)/
│   │   ├── (vendor)/
│   │   └── api/
│   ├── components/
│   ├── lib/
│   ├── hooks/
│   ├── public/fonts/
│   └── next.config.ts
├── docker/
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── nginx/  (or traefik/)
├── compose.yml                 # production
├── compose.dev.yml             # development
└── README.md
```

---

## 🎨 طراحی و هویت بصری

### تم رنگ — برگرفته از GSM.ir
استایل را عیناً مطابق سایت جی‌اس‌ام بساز. متغیرهای CSS اصلی:

```css
:root {
  /* Primary — آبی درخشان CTA */
  --color-primary: #2D87F0;
  --color-primary-hover: #1B6FD9;
  --color-primary-light: #E8F2FD;

  /* Secondary — بنفش (مخصوص بخش اعتباری / اقساط / اکانت پلاس) */
  --color-secondary: #7C5CFF;
  --color-secondary-hover: #6644EB;
  --color-secondary-light: #F1ECFF;

  /* Surface */
  --color-bg: #FFFFFF;
  --color-bg-alt: #F7F8FA;
  --color-card: #FFFFFF;
  --color-border: #E5E7EB;

  /* Footer / Dark sections */
  --color-footer: #1A2540;
  --color-footer-text: #B8C2D9;

  /* Text */
  --color-text: #111827;
  --color-text-muted: #6B7280;
  --color-text-link: #2D87F0;

  /* Gold accent (مخصوص قیمت طلا و نمودار صعودی) */
  --color-gold: #D4AF37;
  --color-gold-light: #FFF6DA;

  /* Status */
  --color-success: #16A34A;
  --color-success-light: #DCFCE7;
  --color-danger: #DC2626;
  --color-danger-light: #FEE2E2;
  --color-warning: #F59E0B;

  /* Shadows */
  --shadow-card: 0 1px 3px rgba(16,24,40,0.04), 0 1px 2px rgba(16,24,40,0.06);
  --shadow-card-hover: 0 4px 12px rgba(16,24,40,0.08);

  /* Radii */
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 24px;
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #0E1218;
    --color-bg-alt: #161B22;
    --color-card: #1A2028;
    --color-border: #2A323D;
    --color-text: #E6E8EB;
    --color-text-muted: #8B94A3;
  }
}
```

### قواعد طراحی
- **RTL کامل** با `dir="rtl"` و `lang="fa"` در `<html>`.
- **فونت:** IRANSans X (Regular/Medium/Bold) — `font-family: 'IRANSans X', 'Vazirmatn', system-ui, sans-serif`.
- **اعداد:** همیشه با فارسی نمایش بده (تبدیل با تابع `toPersianNumber`) به جز در URLها و فرم‌های ورودی.
- **کارت‌محور:** تمام لیست محصولات و سفارش‌ها در `Card` با `border-radius: 16px` و `shadow-card`.
- **CTAها:** دکمه‌های اصلی با `bg-primary`، رادیوس 12px، padding `px-6 py-3`، با hover transition.
- **هدر:** فیکس، شفاف با blur (`backdrop-blur-md`)، شامل: لوگو سمت راست، منوی اصلی، قیمت لحظه‌ی طلا 18، آیکن سبد خرید، آیکن نوتیفیکیشن، avatar کاربر.
- **بنر بالای هدر** (مثل جی‌اس‌ام): قیمت لحظه‌ای طلای ۱۸ عیار + مظنه + سکه با اسکرول نرم.
- **فوتر:** بک‌گراند `--color-footer`، 4 ستون: درباره‌ی ما / لینک‌های پربازدید / دسترسی سریع / شبکه‌های اجتماعی + لوگو enamad/samandehi.

### لوگو
یک لوگوی SVG ساده بساز شامل: نام برند با وزن Bold + آیکن یک شمش طلا که از یک منحنی نموداری بالا می‌آید. ذخیره در `frontend/public/logo.svg` و `frontend/public/logo-dark.svg`.

---

## 💰 منطق دامنه (Domain Logic) — مهم‌ترین بخش

### 1. واحدها و مقیاس‌ها

تمام محاسبات داخلی بر اساس **میلی‌گرم برای وزن** و **ریال برای پول** انجام می‌شود (هیچ‌گاه تومان یا گرم نباشد در سطح دیتابیس). تبدیل فقط در لایه‌ی presentation انجام می‌شود.

```python
# apps/wallet/units.py
WEIGHT_UNIT = "milligram"   # 1 gram = 1000 milligrams
MONEY_UNIT = "rial"         # 1 toman = 10 rials

# مثال: 5 گرم طلا = 5000 milligrams
# مثال: 1,000,000 تومان = 10,000,000 ریال
```

### 2. فرمول‌های قیمت‌گذاری (الزامی)

این فرمول‌ها **پیش‌فرض** هستند و باید از پنل ادمین قابل تغییر باشند:

#### فرمول اصلی مظنه ← گرم طلای ۱۸ عیار
```
مظنه (Mesghal) = قیمت یک مثقال 17 عیار (= 4.6083 گرم با عیار 705/1000)

قیمت هر گرم طلای 18 عیار = (مظنه × 750) / (4.6083 × 705)
                       = مظنه × 0.2308
```

#### فرمول مظنه ← اونس جهانی و دلار
```
مظنه = (قیمت اونس جهانی × قیمت دلار آزاد) / 9.5742
```

#### فرمول قیمت خرید مشتری (Buy Price برای کاربر = ما می‌فروشیم)
```
buy_price_per_mg = (base_18k_price_per_gram / 1000) × (1 + buy_spread) × (1 + commission_buy)
```

#### فرمول قیمت فروش مشتری (Sell Price برای کاربر = ما می‌خریم)
```
sell_price_per_mg = (base_18k_price_per_gram / 1000) × (1 − sell_spread) × (1 − commission_sell)
```

#### پیش‌فرض ضرایب (قابل تغییر از پنل)
```
buy_spread: 0.005   (نیم درصد بالاتر از مظنه)
sell_spread: 0.005  (نیم درصد پایین‌تر از مظنه)
commission_buy: 0.005   (نیم درصد کارمزد خرید — مدل میلی)
commission_sell: 0.005  (نیم درصد کارمزد فروش)
min_commission_fixed_mg: 1   (حداقل کارمزد ثابت = 1 میلی‌گرم برای خریدهای زیر 200 میلی‌گرم)
withdraw_fee_rial: 20000     (2000 تومان کارمزد ثابت برداشت)
delivery_processing_fee_pct: 0.03   (3% کارمزد ضرب و پلمپ هنگام تحویل فیزیکی)
min_physical_delivery_mg: 5000   (حداقل ۵ گرم برای تحویل فیزیکی)
delivery_lot_step_mg: 1000   (مضربی از ۱ گرم باشد، اما تحویل به صورت شمش‌های ۱، ۲، ۵، ۱۰ گرمی)
```

#### فرمول تحویل طلای دارای عیار غیر ۱۸
```
وزن معادل ۱۸ = (وزن گرمی × عیار) / 750
```

#### نقره
```
silver_999_price_per_gram = از tgju کراول شود
silver_buy_per_mg = (silver_999_price / 1000) × (1 + silver_buy_spread) × (1 + silver_commission)
silver_sell_per_mg = (silver_999_price / 1000) × (1 − silver_sell_spread) × (1 − silver_commission)
```

#### سکه و طلای ساخته‌شده در مارکت‌پلیس
این محصولات قیمت **توسط فروشنده** تعیین می‌شود، اما باید همخوانی با قیمت روز را نشان دهد:
```
suggested_coin_price = base_coin_price_from_tgju × (1 + bubble_pct)
final_jewelry_price = (weight_g × per_gram_18k) + manufacturing_fee + vendor_margin + vat
                      where VAT = 9% فقط روی manufacturing_fee + vendor_margin (نه روی خود طلا)
```

> توضیح مالیات: طبق قانون ایران، مالیات بر ارزش افزوده **فقط روی اجرت ساخت و سود فروشنده** اعمال می‌شود، نه روی ارزش طلای خام.

### 3. منبع قیمت — کراولر tgju.org

از سایت `https://www.tgju.org` کراول کن. صفحات profile زیر منابع تمیز هستند:

| داده | URL | DOM Path / Pattern |
|---|---|---|
| طلای ۱۸ عیار ۷۵۰ گرم | `/profile/geram18` | جدول `table.table-padding-lg` ← span با data-col="info.last_trade.PDrCotVal" |
| طلای ۱۸ عیار ۷۴۰ گرم | `/profile/gold_740k` | همان pattern |
| طلای ۲۴ عیار | `/profile/geram24` | همان pattern |
| مثقال طلا | `/profile/mesghal` | همان pattern |
| آبشده نقدی | `/profile/gold_futures` | همان pattern |
| سکه امامی | `/profile/sekee` | همان pattern |
| سکه بهار آزادی | `/profile/sekeb` | همان pattern |
| نیم سکه | `/profile/nim` | همان pattern |
| ربع سکه | `/profile/rob` | همان pattern |
| سکه گرمی | `/profile/gerami` | همان pattern |
| نقره ۹۹۹ | `/profile/silver_999` | همان pattern |
| نقره ۹۲۵ | `/profile/silver_925` | همان pattern |
| اونس طلا | `/profile/ons` | همان pattern |
| دلار آزاد | `/profile/price_dollar_rl` | همان pattern |

**نکته‌ی کلیدی:** قیمت‌های tgju به **ریال** هستند. مقدار با کاما جدا شده و در `<span class="info-price">` یا داخل جدول اصلی صفحه (`#table_xz_lj_o_d_t_p_box`) قرار دارد. برای استخراج پایدار، از **هر دو روش** استفاده کن (fallback):

1. **روش اول (ترجیحی):** انتخاب با CSS selector `span[data-col="info.last_trade.PDrCotVal"]` یا `td[data-col="info.last_trade.PDrCotVal"]`.
2. **روش دوم (fallback):** پارس HTML با BeautifulSoup و جستجو در جدول بر اساس عنوان فارسی ستون.

```python
# apps/pricing/crawler.py
import httpx
from bs4 import BeautifulSoup
import re
from decimal import Decimal

class TgjuCrawler:
    BASE = "https://www.tgju.org"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (compatible; KeyhanGoldBot/1.0)",
        "Accept-Language": "fa-IR,fa;q=0.9,en;q=0.8",
    }
    PROFILES = {
        "gold_18k_750": "/profile/geram18",
        "gold_18k_740": "/profile/gold_740k",
        "gold_24k": "/profile/geram24",
        "mesghal": "/profile/mesghal",
        "gold_melted_cash": "/profile/gold_futures",
        "coin_emami": "/profile/sekee",
        "coin_bahar": "/profile/sekeb",
        "coin_half": "/profile/nim",
        "coin_quarter": "/profile/rob",
        "coin_gerami": "/profile/gerami",
        "silver_999": "/profile/silver_999",
        "silver_925": "/profile/silver_925",
        "ons_gold": "/profile/ons",
        "usd_free": "/profile/price_dollar_rl",
    }

    async def fetch(self, key: str) -> Decimal:
        url = self.BASE + self.PROFILES[key]
        async with httpx.AsyncClient(timeout=10, headers=self.HEADERS) as c:
            r = await c.get(url)
            r.raise_for_status()
        return self._parse(r.text)

    def _parse(self, html: str) -> Decimal:
        soup = BeautifulSoup(html, "lxml")
        # روش اول
        node = soup.select_one('[data-col="info.last_trade.PDrCotVal"]')
        if node:
            return self._to_decimal(node.get_text(strip=True))
        # روش دوم: meta tag یا li#last-change
        meta = soup.find("meta", {"name": "price"})
        if meta and meta.get("content"):
            return self._to_decimal(meta["content"])
        # روش سوم: regex
        m = re.search(r'data-price="([\d,]+)"', html)
        if m:
            return self._to_decimal(m.group(1))
        raise ValueError("Price not found in HTML")

    @staticmethod
    def _to_decimal(s: str) -> Decimal:
        s = s.replace(",", "").replace("٬", "").strip()
        # تبدیل اعداد فارسی به انگلیسی
        trans = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
        return Decimal(s.translate(trans))
```

**Celery Beat schedule:**
- هر ۳۰ ثانیه: کراول قیمت‌ها → ذخیره در Redis با key `price:gold_18k_750`، TTL = ۱۲۰ ثانیه + insert در جدول `PriceTick` برای تاریخچه.
- اگر TGJU پاسخ نداد، fallback به API رایگان `brsapi.ir/free-api-gold-currency-webservice` (آدرس واقعی موجود).
- **publish به Redis Pub/Sub** روی channel `prices:live` → Django Channels consumer برای broadcast به WebSocket.

### 4. مدل‌های دیتابیس (Django Models — حداقلی)

#### `accounts/models.py`
```python
class User(AbstractBaseUser, PermissionsMixin):
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    phone = CharField(max_length=11, unique=True, db_index=True)  # 09123456789
    email = EmailField(blank=True, null=True, unique=True)
    first_name = CharField(max_length=80, blank=True)
    last_name = CharField(max_length=80, blank=True)
    national_id = CharField(max_length=10, blank=True, db_index=True)  # کد ملی
    birth_date = DateField(null=True, blank=True)  # شمسی → میلادی هنگام ذخیره
    father_name = CharField(max_length=80, blank=True)
    address = TextField(blank=True)
    postal_code = CharField(max_length=10, blank=True)
    iban = CharField(max_length=26, blank=True)  # IR + 24 digit
    is_verified = BooleanField(default=False)   # KYC تأیید نهایی
    is_phone_verified = BooleanField(default=False)
    is_vendor = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    USERNAME_FIELD = "phone"

class OTPCode(Model):
    phone = CharField(max_length=11, db_index=True)
    code = CharField(max_length=6)  # کد ۶ رقمی
    purpose = CharField(max_length=20, choices=[("login","ورود/ثبت‌نام"), ("withdraw","تأیید برداشت"), ("transfer","تأیید انتقال")])
    expires_at = DateTimeField()
    used = BooleanField(default=False)
    attempts = PositiveSmallIntegerField(default=0)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [Index(fields=["phone", "purpose", "expires_at"])]

class KYCSubmission(Model):
    user = ForeignKey(User, on_delete=CASCADE, related_name="kyc_submissions")
    national_card_front = FileField(upload_to="kyc/")
    national_card_back = FileField(upload_to="kyc/")
    selfie_with_card = FileField(upload_to="kyc/")
    birth_certificate = FileField(upload_to="kyc/", null=True, blank=True)
    video_attestation = FileField(upload_to="kyc/", null=True, blank=True)  # ویدیوی متن خواندنی
    status = CharField(max_length=20, choices=[("pending","در انتظار بررسی"),("approved","تأیید شد"),("rejected","رد شد"),("requires_more","نیاز به اطلاعات بیشتر")], default="pending")
    rejection_reason = TextField(blank=True)
    reviewed_by = ForeignKey(User, on_delete=SET_NULL, null=True, related_name="kyc_reviews")
    reviewed_at = DateTimeField(null=True, blank=True)
    created_at = DateTimeField(auto_now_add=True)
```

#### `wallet/models.py`
```python
class RialWallet(Model):
    user = OneToOneField(User, on_delete=CASCADE, related_name="rial_wallet")
    balance_rial = BigIntegerField(default=0)   # ریال
    locked_rial = BigIntegerField(default=0)    # ریال قفل‌شده برای سفارشات pending
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    @property
    def available_rial(self):
        return self.balance_rial - self.locked_rial

class GoldWallet(Model):
    user = OneToOneField(User, on_delete=CASCADE, related_name="gold_wallet")
    address = CharField(max_length=42, unique=True, default=generate_gold_address)  # GLD-xxxxxxxx
    balance_mg = BigIntegerField(default=0)     # میلی‌گرم طلای 18 عیار
    locked_mg = BigIntegerField(default=0)
    silver_balance_mg = BigIntegerField(default=0)  # میلی‌گرم نقره 999
    silver_locked_mg = BigIntegerField(default=0)

class WalletTransaction(Model):
    TYPES = [
        ("deposit", "واریز ریالی"),
        ("withdraw", "برداشت ریالی"),
        ("buy_gold", "خرید طلا"),
        ("sell_gold", "فروش طلا"),
        ("buy_silver", "خرید نقره"),
        ("sell_silver", "فروش نقره"),
        ("transfer_in", "انتقال ورودی طلا"),
        ("transfer_out", "انتقال خروجی طلا"),
        ("yield_payout", "پرداخت سود روزانه"),
        ("delivery_burn", "تحویل فیزیکی"),
        ("commission", "کارمزد"),
        ("adjustment", "اصلاح ادمین"),
    ]
    id = UUIDField(primary_key=True, default=uuid4)
    user = ForeignKey(User, on_delete=PROTECT, related_name="wallet_txs")
    type = CharField(max_length=20, choices=TYPES)
    rial_amount = BigIntegerField(default=0)   # +/- ریال
    mg_amount = BigIntegerField(default=0)     # +/- میلی‌گرم (طلا یا نقره)
    asset = CharField(max_length=8, choices=[("rial","ریال"),("gold","طلا"),("silver","نقره")])
    related_order = ForeignKey("orders.Order", on_delete=SET_NULL, null=True, blank=True)
    balance_after_rial = BigIntegerField(null=True, blank=True)
    balance_after_mg = BigIntegerField(null=True, blank=True)
    description = CharField(max_length=255, blank=True)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [Index(fields=["user", "-created_at"]), Index(fields=["related_order"])]
```

#### `pricing/models.py`
```python
class PriceTick(Model):
    """ذخیره‌ی هر اسنپ‌شات قیمت از منبع"""
    source_key = CharField(max_length=40, db_index=True)  # gold_18k_750, silver_999, ...
    rial_price = BigIntegerField()
    captured_at = DateTimeField(db_index=True)
    source = CharField(max_length=20, default="tgju")

    class Meta:
        indexes = [Index(fields=["source_key", "-captured_at"])]

class PricingFormula(Model):
    """ضرایب قابل ویرایش از پنل ادمین"""
    key = CharField(max_length=80, unique=True)  # buy_spread, sell_spread, commission_buy, ...
    value = DecimalField(max_digits=12, decimal_places=8)
    description = CharField(max_length=255)
    updated_by = ForeignKey(User, on_delete=SET_NULL, null=True)
    updated_at = DateTimeField(auto_now=True)

class PriceQuote(Model):
    """قیمت لحظه‌ای محاسبه‌شده برای نمایش به کاربر — اعتبار 30 ثانیه"""
    quote_id = UUIDField(primary_key=True, default=uuid4)
    asset = CharField(max_length=10)  # gold, silver
    side = CharField(max_length=4)    # buy, sell
    price_per_mg_rial = BigIntegerField()
    valid_until = DateTimeField()
    base_tick = ForeignKey(PriceTick, on_delete=PROTECT)
    created_at = DateTimeField(auto_now_add=True)
```

#### `orders/models.py`
```python
class Order(Model):
    KINDS = [
        ("buy_gold", "خرید طلا از سامانه"),
        ("sell_gold", "فروش طلا به سامانه"),
        ("buy_silver", "خرید نقره از سامانه"),
        ("sell_silver", "فروش نقره به سامانه"),
        ("marketplace", "خرید از فروشنده"),
        ("wallet_topup", "شارژ کیف پول"),
    ]
    STATUSES = [
        ("draft", "پیش‌نویس"),
        ("awaiting_payment", "در انتظار پرداخت"),    # ⏰ تایمر 30 دقیقه
        ("paid", "پرداخت شد"),
        ("processing", "در حال پردازش"),
        ("completed", "تکمیل شد"),
        ("expired", "منقضی شد"),
        ("cancelled", "لغو شد"),
        ("refunded", "بازگشت داده شد"),
        ("failed", "ناموفق"),
    ]
    id = UUIDField(primary_key=True, default=uuid4)
    order_number = CharField(max_length=20, unique=True, db_index=True)  # KG-202605-000001
    user = ForeignKey(User, on_delete=PROTECT, related_name="orders")
    kind = CharField(max_length=20, choices=KINDS)
    status = CharField(max_length=20, choices=STATUSES, default="draft")

    # snapshot قیمت در لحظه‌ی ثبت
    quote = ForeignKey(PriceQuote, on_delete=PROTECT, null=True, blank=True)
    price_per_mg_rial = BigIntegerField(default=0)
    mg_amount = BigIntegerField(default=0)
    rial_amount = BigIntegerField()        # مبلغ کل قابل پرداخت
    commission_rial = BigIntegerField(default=0)
    commission_mg = BigIntegerField(default=0)

    # تایمر پرداخت
    payment_deadline = DateTimeField(null=True, blank=True)   # = paid_at + 30min
    # پرداخت
    payment_gateway = CharField(max_length=20, blank=True)  # zarinpal, idpay, payping
    payment_ref = CharField(max_length=100, blank=True)
    paid_at = DateTimeField(null=True, blank=True)

    # برای marketplace
    vendor = ForeignKey("marketplace.Vendor", on_delete=PROTECT, null=True, blank=True)
    invoice_pdf = FileField(upload_to="invoices/", null=True, blank=True)

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            Index(fields=["user", "-created_at"]),
            Index(fields=["status", "payment_deadline"]),
            Index(fields=["vendor", "-created_at"]),
        ]

class OrderItem(Model):
    """فقط برای مارکت‌پلیس استفاده می‌شود — برای buy_gold/sell_gold یک ردیف هست"""
    order = ForeignKey(Order, on_delete=CASCADE, related_name="items")
    product = ForeignKey("marketplace.Product", on_delete=PROTECT, null=True, blank=True)
    title_snapshot = CharField(max_length=255)
    quantity = PositiveIntegerField(default=1)
    unit_price_rial = BigIntegerField()
    line_total_rial = BigIntegerField()
    metadata = JSONField(default=dict)  # weight, karat, manufacturing_fee, ...
```

#### `marketplace/models.py`
```python
class Vendor(Model):
    user = OneToOneField(User, on_delete=CASCADE, related_name="vendor_profile")
    shop_name = CharField(max_length=120)
    shop_slug = SlugField(unique=True)
    legal_name = CharField(max_length=200)
    business_license = FileField(upload_to="vendor/licenses/")
    union_license = FileField(upload_to="vendor/licenses/", null=True, blank=True)  # پروانه اتحادیه طلا و جواهر
    iban = CharField(max_length=26)
    commission_rate = DecimalField(max_digits=5, decimal_places=4, default=0.02)  # 2% کمیسیون سامانه
    status = CharField(max_length=20, choices=[("pending","در انتظار"),("approved","تأیید شد"),("suspended","تعلیق"),("rejected","رد شد")], default="pending")
    rating = DecimalField(max_digits=3, decimal_places=2, default=0)
    total_sales = PositiveIntegerField(default=0)
    description = TextField(blank=True)
    logo = ImageField(upload_to="vendor/logos/", null=True, blank=True)
    city = CharField(max_length=80, blank=True)
    address = TextField(blank=True)
    phone = CharField(max_length=15, blank=True)
    created_at = DateTimeField(auto_now_add=True)

class Product(Model):
    CATEGORIES = [
        ("melted", "طلای آب‌شده"),
        ("jewelry", "طلای ساخته‌شده"),
        ("coin", "سکه"),
        ("silver", "نقره"),
    ]
    id = UUIDField(primary_key=True, default=uuid4)
    vendor = ForeignKey(Vendor, on_delete=CASCADE, related_name="products")
    category = CharField(max_length=10, choices=CATEGORIES)
    title = CharField(max_length=200)
    slug = SlugField()
    sku = CharField(max_length=40, unique=True)
    weight_mg = BigIntegerField()      # وزن دقیق
    karat = PositiveSmallIntegerField(default=750)   # 750, 705, 999, 925, ...
    manufacturing_fee_pct = DecimalField(max_digits=5, decimal_places=4, default=0)  # اجرت ساخت %
    vendor_margin_pct = DecimalField(max_digits=5, decimal_places=4, default=0)      # سود فروشنده %
    fixed_extra_rial = BigIntegerField(default=0)    # هزینه ثابت اضافی (در سکه گاهی استفاده می‌شود)
    coin_type = CharField(max_length=20, blank=True)  # emami, bahar, half, quarter, gerami
    image_urls = JSONField(default=list)
    description = TextField(blank=True)
    stock = PositiveIntegerField(default=1)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)

    @property
    def computed_price_rial(self):
        # محاسبه از live price + فرمول
        ...
```

#### `delivery/models.py`
```python
class DeliveryRequest(Model):
    STATUSES = [
        ("pending", "در انتظار تأیید"),
        ("approved", "تأیید شد"),
        ("minting", "در حال ضرب و پلمپ"),
        ("shipped", "ارسال شد"),
        ("delivered", "تحویل داده شد"),
        ("cancelled", "لغو شد"),
    ]
    id = UUIDField(primary_key=True, default=uuid4)
    user = ForeignKey(User, on_delete=PROTECT, related_name="delivery_requests")
    asset = CharField(max_length=10)  # gold, silver
    requested_mg = BigIntegerField()
    bars_breakdown = JSONField(default=dict)  # {"1g": 2, "5g": 1}
    processing_fee_rial = BigIntegerField(default=0)
    tracking_code = CharField(max_length=40, blank=True)
    shipping_address = TextField()
    recipient_name = CharField(max_length=120)
    recipient_national_id = CharField(max_length=10)
    recipient_phone = CharField(max_length=15)
    status = CharField(max_length=20, choices=STATUSES, default="pending")
    notes = TextField(blank=True)
    created_at = DateTimeField(auto_now_add=True)
```

#### `payments/models.py`
```python
class PaymentAttempt(Model):
    GATEWAYS = [("zarinpal","زرین‌پال"), ("idpay","آیدی‌پی"), ("payping","پی‌پینگ")]
    STATUSES = [("pending","در انتظار"),("redirected","در درگاه"),("succeeded","موفق"),("failed","ناموفق"),("cancelled","لغو شده"),("expired","منقضی")]
    id = UUIDField(primary_key=True, default=uuid4)
    order = ForeignKey(Order, on_delete=PROTECT, related_name="payment_attempts")
    gateway = CharField(max_length=20, choices=GATEWAYS)
    amount_rial = BigIntegerField()
    authority = CharField(max_length=120, blank=True)
    ref_id = CharField(max_length=120, blank=True)
    card_pan_masked = CharField(max_length=20, blank=True)
    status = CharField(max_length=20, choices=STATUSES, default="pending")
    raw_request = JSONField(default=dict)
    raw_response = JSONField(default=dict)
    created_at = DateTimeField(auto_now_add=True)
    completed_at = DateTimeField(null=True, blank=True)
```

### 5. State Machine سفارش (مدل دیجی‌کالا)

```
draft → awaiting_payment (payment_deadline = now + 30min)
        ↓
        (پرداخت موفق در ≤ 30min) → paid → processing → completed
        ↓
        (انقضای 30min) → expired (Celery beat هر دقیقه چک می‌کند)
        ↓
        (کاربر لغو کرد) → cancelled
```

**جزئیات مهم:**
- وقتی سفارش `awaiting_payment` می‌شود، **مبلغ از کیف پول قفل می‌شود** (افزایش `locked_rial` اگر از کیف خرید می‌کند، یا قفل MG اگر می‌فروشد).
- اگر `expired` شد، قفل برمی‌گردد + در audit log ثبت می‌شود.
- اگر `paid` شد، transaction اتمیک انجام بده: کسر از locked → افزایش طلا/نقره.
- **idempotent webhook handler:** هر گیت‌وی ممکن است چندبار callback بفرستد. استفاده از `select_for_update` در PostgreSQL.
- **race condition protection:** حتماً همه‌ی عملیات مالی داخل `transaction.atomic()` + `Order.objects.select_for_update().get(...)`.

### 6. درگاه‌های پرداخت (Multi-Gateway)

abstraction روی هر سه درگاه با interface مشترک:

```python
# apps/payments/gateways/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class PaymentRequest:
    order_id: str
    amount_rial: int
    callback_url: str
    description: str
    mobile: str | None = None
    email: str | None = None

@dataclass
class PaymentResponse:
    success: bool
    authority: str           # یا ref برای idpay
    redirect_url: str
    error_code: str | None = None
    error_message: str | None = None

@dataclass
class VerifyResponse:
    success: bool
    ref_id: str
    card_pan_masked: str | None = None
    raw: dict

class BaseGateway(ABC):
    name: str

    @abstractmethod
    def request(self, req: PaymentRequest) -> PaymentResponse: ...

    @abstractmethod
    def verify(self, authority: str, amount_rial: int) -> VerifyResponse: ...
```

پیاده‌سازی هر سه:
- **Zarinpal:** v4 REST API (`https://api.zarinpal.com/pg/v4/payment/request.json`)
- **IDPay:** REST v1.1 (`https://api.idpay.ir/v1.1/payment`)
- **Payping:** REST v2 (`https://api.payping.ir/v2/pay`)

تمام credentials در `.env` و `SETTINGS_PAYMENT_GATEWAYS` (django settings).
انتخاب درگاه: کاربر در صفحه‌ی پرداخت بین سه گزینه انتخاب می‌کند، آیکن و نام نمایش داده می‌شود.

### 7. احراز هویت (KYC کامل با تأیید دستی ادمین)

مراحل برای کاربر:

1. **مرحله ۱ — تأیید موبایل:** ورود شماره → OTP کاوه‌نگار (template `verify-login`) → ثبت‌نام/ورود.
2. **مرحله ۲ — اطلاعات هویتی:** فرم با کد ملی، نام، نام خانوادگی، نام پدر، تاریخ تولد، آدرس کامل، کد پستی.
   - استعلام شاهکار (در صورت دسترسی به API): تطبیق کد ملی + شماره موبایل.
3. **مرحله ۳ — مدارک:** آپلود تصویر کارت ملی (پشت/رو)، سلفی با کارت ملی در دست (هندنوشت با تاریخ روز + متن "این تصویر برای KeyhanGold است")، اختیاری: ویدئوی ۵ ثانیه‌ای متن خوانده شود.
4. **مرحله ۴ — کارت بانکی شتاب:** ورود شماره کارت ۱۶ رقمی + استعلام تطبیق نام و کد ملی (در صورت دسترسی، از سامانه شاپرک یا third-party).
5. **مرحله ۵ — انتظار بررسی ادمین:** وضعیت کاربر `pending` → ادمین در پنل بررسی می‌کند → تأیید/رد + ارسال SMS اطلاع‌رسانی.

تا قبل از تأیید: کاربر می‌تواند **فقط قیمت‌ها را ببیند**؛ امکان شارژ، خرید، فروش، برداشت، تحویل ندارد.

### 8. کیف پول و سود روزانه

سود روزانه (مدل صندوق):
- پنل ادمین یک رقم `daily_yield_apr` (مثلاً 24% سالانه) قابل تنظیم دارد.
- یک Celery beat هر شب ساعت ۲۴:۰۰ روی موجودی کیف پول ریالی هر کاربر، سود روز را به‌صورت زیر محاسبه می‌کند:
  ```
  daily_yield = balance_rial × (daily_yield_apr / 365)
  ```
- نتیجه به `WalletTransaction(type="yield_payout")` افزوده می‌شود.
- توضیح حقوقی: این سود به‌عنوان "هدیه‌ی نگهداری" یا "پاداش وفاداری" در ToS تعریف شود (نه ربا).

برداشت ریالی:
- حداقل: ۱۰۰,۰۰۰ ریال.
- مقصد: فقط شبا/شماره کارت متعلق به خود کاربر (با KYC تأیید‌شده).
- زمان واریز: تا ۳ روز کاری (پایا/ساتنا)، با اعلام شفاف به کاربر.
- کارمزد ثابت: قابل تنظیم در پنل (پیش‌فرض ۲۰,۰۰۰ ریال).

### 9. WebSocket — قیمت لحظه‌ای

`/ws/prices/` consumer روی Django Channels:
- subscriber join شدن به group `prices_live`.
- هر ۳۰ ثانیه (یا هر زمان TgjuCrawler قیمت جدید گرفت)، یک message:
  ```json
  {
    "type": "price_update",
    "ts": "2026-05-14T17:30:00Z",
    "data": {
      "gold_18k_750": {"rial": 17241600, "change_pct": 0.92},
      "silver_999": {"rial": 396000, "change_pct": 1.02},
      "buy_per_mg": 17328000,
      "sell_per_mg": 17155000
    }
  }
  ```
- frontend با hook `useLivePrice()` به این WS متصل می‌شود.

---

## 🛒 جریان‌های کلیدی کاربر (User Flows)

### جریان خرید طلا (Buy Gold — مدل میلی)
1. کاربر در داشبورد روی "خرید طلا" کلیک می‌کند.
2. فرم: انتخاب بر اساس **میلی‌گرم** یا **ریال** (دو فیلد همگام، یکی پر شد دیگری محاسبه می‌شود live).
3. نمایش breakdown: قیمت پایه + کارمزد + جمع کل، با ذکر **اعتبار قیمت ۳۰ ثانیه**.
4. کاربر "تأیید خرید" می‌زند → اگر موجودی کیف پول کافی است، **بدون پرداخت دروازه** انجام می‌شود. در غیر این صورت → هدایت به صفحه‌ی شارژ/درگاه.
5. backend در یک transaction:
   - PriceQuote ایجاد (valid_until = now + 30s)
   - Order(status="paid", kind="buy_gold")
   - WalletTransaction debit ریال + WalletTransaction credit MG
   - emit websocket event به کاربر برای refresh موجودی
6. فاکتور PDF ساخته می‌شود (با weasyprint) و در `order.invoice_pdf` ذخیره.

### جریان شارژ کیف پول با تایمر ۳۰ دقیقه
1. کاربر مبلغ شارژ + درگاه انتخاب می‌کند.
2. Order(kind="wallet_topup", status="awaiting_payment", payment_deadline=now+30min) ساخته می‌شود.
3. PaymentAttempt و request به gateway → redirect_url.
4. کاربر به درگاه می‌رود؛ صفحه‌ی sticky timer در ahead صفحه و در صورت بستن، در صفحه‌ی سفارش‌ها هم نمایش داده می‌شود.
5. callback از درگاه → verify → status = "paid" + balance_rial افزایش.
6. اگر کاربر در طول ۳۰ دقیقه بازنگشت یا پرداخت ناموفق بود، **Celery beat** هر دقیقه orderهای منقضی را به `expired` تغییر می‌دهد.

### جریان مارکت‌پلیس (خرید جواهر از فروشنده)
1. کاربر محصول را به سبد می‌افزاید.
2. Checkout → آدرس ارسال + روش پرداخت.
3. Order(kind="marketplace", vendor=X) با `payment_deadline=now+30min`.
4. پرداخت → آزاد شدن کالا برای ارسال.
5. tracking + وضعیت در صفحه‌ی سفارش کاربر.
6. تسویه با فروشنده: روزانه، با کسر `vendor.commission_rate`.

### جریان درخواست تحویل فیزیکی
1. در داشبورد طلا، "درخواست تحویل فیزیکی" → انتخاب وزن (مضرب ۱ گرم، حداقل ۵ گرم) و breakdown شمش‌ها (شمش‌های ۱، ۲، ۵، ۱۰ گرمی موجود).
2. نمایش processing_fee (3% پیش‌فرض) و کسر از کیف پول.
3. آدرس تحویل (با پست پیشتاز یا تیپاکس).
4. ادمین تأیید می‌کند → status = "minting" → "shipped" (با tracking code) → "delivered".

---

## 🔐 امنیت و Compliance

### امنیت
- HTTPS اجباری (HSTS با `SECURE_HSTS_SECONDS=31536000`).
- JWT cookies با `HttpOnly`, `Secure`, `SameSite=Strict`.
- Rate limiting: per-IP و per-user با `django-ratelimit` یا Redis-based:
  - ورود OTP: ۵ تلاش در ۱۵ دقیقه per phone.
  - برداشت: ۳ تلاش در ساعت.
  - API عمومی: ۶۰ درخواست در دقیقه.
- 2FA اختیاری: کاربر می‌تواند برای برداشت، تأیید OTP اضافی فعال کند.
- audit log کامل: هر تغییر مالی + هر اقدام ادمین + هر login.
- SQL Injection: استفاده‌ی الزامی از ORM، هیچ raw query بدون parameterization.
- XSS: فرانت با React (auto-escape)، CSP header در nginx.
- پشتیبان‌گیری: pg_dump روزانه به MinIO (با encryption).
- secrets management: `django-environ` + `.env` (هرگز در گیت کامیت نشود).

### Compliance (مهم — بخوان)
- این پلتفرم زیر نظر **اتحادیه‌ی صنف طلا، جواهر، نقره و سکه** فعالیت می‌کند → باید پروانه‌ی کسب رسته‌ی خرده‌فروشی طلای آب‌شده داشته باشد.
- در نهایت ممکن است نیاز به مجوز از **بانک مرکزی** (به‌خاطر کیف پول و سود) و **سازمان بورس کالا** باشد. در ToS اشاره شود.
- ضوابط AML: تراکنش‌های بالای ۱۰۰ میلیون تومان flag شوند و در گزارش روزانه به ادمین نمایش داده شوند.
- ToS و حریم خصوصی در `app/(legal)/terms` و `app/(legal)/privacy`.
- **enamad + samandehi**: placeholderی برای logoها در فوتر بساز، با لینک خارجی.
- در ToS صریحاً ذکر شود: "این پلتفرم خدمت سرمایه‌گذاری ارائه نمی‌دهد و سود روزانه پاداش وفاداری است نه ربا/بهره"؛ به علاوه disclaimer ریسک نوسان بازار.

---

## 🧰 پنل ادمین (Admin Panel)

پنل **سفارشی** (نه فقط Django Admin پیش‌فرض) با Next.js در `app/(admin)/`. در عین حال Django Admin هم برای superuser فعال باشد. بخش‌ها:

1. **Dashboard:** کارت‌های KPI — کاربران فعال امروز، سفارش‌های امروز، حجم خرید/فروش (mg و ریال)، موجودی کل طلا در سامانه، موجودی ریال، سود کارمزد امروز.
2. **کاربران:** لیست، فیلتر بر اساس KYC، جستجو با موبایل/کد ملی، باز کردن پروفایل، قفل/آنبلاک، مشاهده تراکنش‌ها.
3. **احراز هویت:** صف KYC، نمایش مدارک، دکمه‌ی تأیید/رد + درج علت.
4. **سفارش‌ها:** filter بر اساس kind/status/vendor/تاریخ، export Excel، invoice دانلود.
5. **پرداخت‌ها:** PaymentAttemptها، reconciliation با گزارش بانکی.
6. **فروشندگان (Vendors):** صف pending، تأیید/رد + تنظیم commission rate per vendor، گزارش فروش، تسویه‌ی روزانه، تعلیق.
7. **محصولات:** approve/reject محصول مارکت‌پلیس.
8. **قیمت‌ها:** نمایش live + تاریخچه، **ویرایش ضرایب فرمول‌ها** (PricingFormula)، تنظیم spread/commission، on/off هر منبع.
9. **کیف پول و مالیه:** نمای کلی موجودی سامانه، گزارش tax، export برای حسابدار.
10. **تحویل فیزیکی:** صف، تغییر وضعیت، چاپ برچسب پست.
11. **سود روزانه:** تنظیم APR، تاریخچه پرداخت‌ها، on/off کلی.
12. **نوتیفیکیشن:** قالب‌های SMS، اعلان push، broadcast.
13. **گزارش‌ها:** AML flags، transaction summary، audit log.
14. **تنظیمات:** درگاه‌های پرداخت، API keys (کاوه‌نگار)، general settings، featured products.

دسترسی‌ها (RBAC):
- `superadmin`: همه چیز.
- `kyc_reviewer`: فقط احراز هویت.
- `support`: read-only + پاسخ به تیکت.
- `finance`: تراکنش‌ها، گزارش‌های مالی، تسویه.
- `vendor`: فقط داشبورد فروشنده.

---

## 📱 صفحات Frontend (Next.js 16)

### Public (بدون login)
- `/` — صفحه اصلی با hero (قیمت لحظه‌ای + CTA "همین حالا شروع کن")، 3 ستون مزایا (بدون اجرت، خرید از ۱ میلی‌گرم، تحویل فیزیکی)، نمودار قیمت ۷ روز اخیر، FAQ، testimonial.
- `/prices` — جدول کامل قیمت‌ها (مثل tgju gold-chart) + نمودار interactive 1D/1W/1M/1Y.
- `/marketplace` — لیست محصولات مارکت‌پلیس با فیلتر دسته/فروشنده/وزن/قیمت.
- `/marketplace/[slug]` — صفحه محصول.
- `/vendors/[slug]` — صفحه فروشگاه فروشنده.
- `/about`, `/contact`, `/faq`, `/terms`, `/privacy`, `/blog`, `/blog/[slug]`

### Auth
- `/login` — وارد کردن موبایل → step 2: OTP.
- `/signup` — مشابه ولی برای ثبت‌نام (یک flow ادغام شده مثل میلی).

### Account (Login required)
- `/dashboard` — کیف پول طلا + ریال، charts، last 5 transactions.
- `/wallet/rial` — جزئیات + شارژ + برداشت.
- `/wallet/gold` — جزئیات + خرید + فروش + انتقال.
- `/trade/buy` — خرید سریع طلا.
- `/trade/sell` — فروش سریع طلا.
- `/trade/silver` — خرید/فروش نقره.
- `/orders` — لیست سفارش‌ها با فیلتر.
- `/orders/[id]` — جزئیات + تایمر 30 دقیقه برای orderهای awaiting_payment.
- `/delivery` — درخواست تحویل + تاریخچه.
- `/transfer` — انتقال طلا به آدرس کیف کاربر دیگر.
- `/kyc` — مراحل احراز هویت.
- `/profile` — اطلاعات شخصی، تنظیمات امنیتی، کارت‌های بانکی.
- `/notifications`

### Vendor Dashboard (`/vendor/*`)
- `/vendor/dashboard` — KPI، فروش امروز، موجودی محصولات.
- `/vendor/products` — CRUD محصولات.
- `/vendor/orders` — سفارشات دریافتی.
- `/vendor/settlements` — تاریخچه تسویه.
- `/vendor/profile` — اطلاعات فروشگاه.

### Admin Dashboard (`/admin/*`)
بر اساس بخش "پنل ادمین" بالا.

---

## ✅ تست‌ها و کیفیت

- **Backend:** pytest + pytest-django + factory_boy. حداقل ۸۰٪ coverage در apps حساس مالی (`orders`, `wallet`, `pricing`, `payments`).
  - تست‌های ضروری:
    - race condition دو سفارش همزمان از یک کیف پول
    - expiry order در دقیقه‌ی ۲۹:۵۹ و ۳۰:۰۱
    - حسابداری دقیق MG و ریال (بدون floating point — همه integer)
    - webhook idempotency
    - KYC state transitions
    - فرمول‌های قیمت‌گذاری با snapshot tests
- **Frontend:** Vitest + React Testing Library + Playwright برای E2E روی flows اصلی.
- **Linting:** ruff + black + mypy strict برای پایتون؛ ESLint + Prettier + TypeScript strict برای next.
- **Pre-commit:** ruff, black, mypy, eslint, prettier, typecheck.
- **CI:** GitHub Actions با build + test + lint.

---

## 📦 Docker و Deploy

### compose.yml (production)
سرویس‌ها:
- `postgres:16` با volume
- `redis:7-alpine`
- `minio` با volume
- `backend` (gunicorn + uvicorn workers): build از `backend.Dockerfile`، command `gunicorn core.asgi:application -k uvicorn.workers.UvicornWorker -w 4`
- `celery_worker`: command `celery -A core worker -l info -Q default,priority`
- `celery_beat`: command `celery -A core beat -l info`
- `daphne`: command `daphne -b 0.0.0.0 -p 9000 core.asgi:application` (برای WebSocket مجزا از gunicorn)
- `frontend` (next.js production build): `node server.js` با standalone output
- `traefik`: reverse proxy + automatic SSL with Let's Encrypt
- `prometheus` + `grafana` + `node-exporter`

### Health checks
هر سرویس باید `/health` endpoint داشته باشد. backend چک می‌کند: db connection + redis ping + celery worker alive.

### Migration و seed
- اسکریپت `scripts/seed.py`:
  - admin superuser (موبایل: `09120000000`)
  - PricingFormula با مقادیر پیش‌فرض
  - ۳ vendor فیک
  - ۲۰ محصول فیک
  - قیمت‌های اولیه از crawler

### `.env.example`
کامل با تمام متغیرها و توضیحات (DJANGO_SECRET_KEY، DB، REDIS، KAVENEGAR_API_KEY، KAVENEGAR_OTP_TEMPLATE، ZARINPAL_MERCHANT_ID، IDPAY_API_KEY، PAYPING_API_KEY، SENTRY_DSN، MINIO_*، JWT_*، ...).

---

## 📝 درخواست از Claude Code (نحوه‌ی ساخت)

### نظم پیاده‌سازی (Step-by-step)

به ترتیب زیر پیش برو، **در هر مرحله یک commit جداگانه**:

1. **Bootstrap monorepo:** ساختار پوشه‌ها، `.gitignore`، `README.md` اولیه، Dockerfileها.
2. **Backend skeleton:** Django 5.2 با apps خالی، settings تفکیک‌شده (base/dev/prod)، PostgreSQL connection، Redis، Celery.
3. **Accounts:** User custom model، OTP، Kavenegar integration، JWT auth، رجیستر/لاگین API + تست.
4. **KYC:** فرم‌ها، آپلود به MinIO، صف ادمین.
5. **Wallet:** RialWallet, GoldWallet, transaction model، transactional helpers.
6. **Pricing:** Crawler، Celery beat، PriceTick، فرمول‌ها، PriceQuote API، WebSocket consumer.
7. **Orders & Payments:** lifecycle کامل + 3 gateway + idempotent webhooks + تایمر expiry.
8. **Delivery & Marketplace:** Vendor، Product، DeliveryRequest.
9. **Frontend skeleton:** Next 16 app، routing، theme، Tailwind، fonts، RTL.
10. **Auth pages:** login/OTP/signup.
11. **Dashboard, Wallet, Trade pages.**
12. **Marketplace pages.**
13. **Admin panel pages.**
14. **Vendor pages.**
15. **Live price WebSocket integration در frontend.**
16. **Invoices PDF (weasyprint).**
17. **Notifications (SMS + in-app).**
18. **Tests (پایتون و فرانت).**
19. **Docker compose نهایی + Traefik + monitoring.**
20. **Seed data + README کامل با راهنمای local dev.**

### قواعد اجباری حین نوشتن کد

- ✅ **هیچ کد copy-paste از LLM-generated پر از TODO نده.** تمام functionها باید پیاده‌سازی واقعی داشته باشند.
- ✅ **هیچ floating-point برای پول و وزن.** فقط `int` (ریال و میلی‌گرم) یا `Decimal` (برای ضرایب).
- ✅ **هر اپ یک README کوچک داشته باشد** که role و models و key APIs را توضیح دهد.
- ✅ **type hints کامل** در پایتون (`mypy --strict` بدون error).
- ✅ **در فرانت همه‌چیز TypeScript strict**؛ هیچ `any` بی‌دلیل.
- ✅ **error messages فارسی** برای endpoints مصرفی کاربر، اما log messages انگلیسی.
- ✅ **اعداد فارسی** فقط در نمایش، نه در ذخیره‌سازی.
- ✅ **commit messages:** Conventional Commits با اسکوپ (`feat(orders): add 30min expiry`).
- ✅ **هر endpoint API باید در OpenAPI schema باشد** (drf-spectacular).
- ✅ **migrationها مرتب و قابل rollback.**
- ✅ **i18n-ready حتی اگر فقط فارسی است:** همه‌ی stringها از `_("...")` یا `t()`.

### قواعد منع‌شده

- ❌ **استفاده از Django Pages Router در Next** — فقط App Router.
- ❌ **استفاده از Class-based components در React** — فقط functional + hooks.
- ❌ **localStorage برای token حساس** — همیشه HttpOnly cookies.
- ❌ **هیچ‌گونه ذخیره‌ی plaintext password** (با اینکه auth با OTP است، در KYC هم احتیاط شود).
- ❌ **هیچ‌گاه نام برند "میلی" یا "ملی‌گلد" یا "تکنوگلد" را در کد یا UI استفاده نکن** (مالکیت معنوی).
- ❌ **هیچ‌گاه قیمت‌ها رو از training data یا hard-code نگذار** — همیشه از crawler/cache.

### چه چیزی اول بنویس؟

پس از اتمام Step 1 (bootstrap)، در Step 2-7 (Backend skeleton تا Orders) **یک smoke E2E test** بنویس که این flow رو پاس کند:
1. ثبت‌نام کاربر با OTP
2. submit KYC
3. (mock) تأیید KYC توسط ادمین
4. شارژ کیف پول با درگاه mock
5. خرید 1000 میلی‌گرم طلا
6. فروش 500 میلی‌گرم طلا
7. درخواست تحویل 5 گرم

اگر این flow پاس شد، MVP داری.

---

## 🚀 پایان

این پرامپت کل scope رو پوشش می‌دهد. اگر در حین پیاده‌سازی به مسئله‌ای برخوردی که در این سند ابهام دارد:
- **مسائل مالی/حقوقی** (مثلاً rounding ریال، VAT دقیق، logic سود): بر اساس practice‌های ایرانی (میلی، ملی گلد، طلابانک) عمل کن و در `docs/decisions/` یک ADR (Architecture Decision Record) ثبت کن.
- **مسائل فنی** (مثلاً انتخاب کتابخانه): defaultهای modern و مورد تأیید جامعه‌ی Python/Next رو انتخاب کن.
- **مسائل UX:** الگوی میلی + دیجی‌کالا را دنبال کن.

**نهایت هدف:** یک پلتفرم تولیدی، امن، مقیاس‌پذیر، با UX مدرن و بومی، که فردا بشود deploy کرد و کاربر واقعی گرفت.

— پایان پرامپت —
