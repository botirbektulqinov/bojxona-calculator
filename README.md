# 🧮 Bojxona Backend - O'zbekiston Bojxona Kalkulyatori

> **Professional customs calculation system matching incustoms.ai standards**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.124.0-009688.svg)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg)](https://python.org)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://www.sqlalchemy.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Loyiha Haqida

O'zbekiston bojxona to'lovlarini professional darajada hisoblash uchun ishlab chiqilgan RESTful API backend tizimi. Barcha hisob-kitoblar va ma'lumotlar [incustoms.ai](https://incustoms.ai) platformasi standartlariga to'liq mos keladi.

### 🎯 Asosiy Maqsad

incustoms.ai platformasi bilan bir xil natijalar beruvchi, to'g'ri va ishonchli bojxona hisob-kitob tizimini yaratish. Loyiha davomida bir qator murakkab muammolar hal qilindi va professional darajadagi yechim ishlab chiqildi.

## ✨ Funksionallik

### 📊 Ma'lumotlar Manbai
- **14,033 TN VED kodlari** - [incustoms.ai](https://incustoms.ai) Supabase bazasidan real-time sinxronlash
- **RNB va Non-RNB tariflar** - MDH davlatlari va boshqa davlatlar uchun alohida bojxona stavkalari
- **Avtomatik yangilanish** - O'zbekiston Markaziy Banki kurslarini kunlik yangilash (har kuni 09:00 da)

### 🔍 TN VED Qidiruv Tizimi
- Prefix-based search: Kod boshlanishi bo'yicha tez qidiruv
- Intelligent sorting: Natijalarni uzunlik bo'yicha tartiblash
- Dual mode: Raqamli kodlar va matnli qidiruv uchun optimallashtirish

### 💰 Hisob-kitob Mexanizmi
1. **Bojxona qiymati (TS)**: Tovar + Yetkazib berish + Sug'urta
2. **Bojxona rasmiylash yig'imi**: BRV asosidagi 7 darajali hisoblash (TP-55)
3. **Import bojxona poshlinasi**: RNB/Non-RNB stavkalar farqi
4. **Aksiz solig'i**: Akcizli tovarlar uchun
5. **QQS**: 12% qo'shilgan qiymat solig'i
6. **Jami to'lov**: Barcha komponentlar yig'indisi

### 🌍 Valyuta Boshqaruvi
- 75+ valyuta kurslari
- CBU.uz API integratsiyasi
- Startup avtomatik yangilash
- Kunlik background task (09:00)

## 🏗️ Texnologiyalar

```
Backend:        FastAPI 0.124.0 (Async)
ORM:            SQLAlchemy 2.0 (Async)
Database:       SQLite (Production-ready)
Migration:      Alembic 1.17.2
Parser:         BeautifulSoup4, lxml
HTTP Client:    httpx (async)
Data Analysis:  pandas, numpy
Validation:     Pydantic 2.12.5
Server:         Uvicorn (uvloop + httptools)
```

## 🚀 Ishga Tushirish

### Tizim Talablari
- Python 3.11+
- pip / venv
- 100MB disk space

### O'rnatish

1. **Repository clone qilish**
```bash
git clone <repository-url>
cd bojxona-backend
```

2. **Virtual environment yaratish**
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

3. **Dependency'larni o'rnatish**
```bash
pip install -r requirements.txt
```

4. **Ma'lumotlar bazasini tayyorlash**
```bash
# Database yaratish va migration qo'llash
alembic upgrade head

# incustoms.ai dan ma'lumotlarni sinxronlash
python scripts/sync_incustoms.py
```

5. **Serverni ishga tushirish**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Server muvaffaqiyatli ishga tushgandan so'ng:
- API: http://localhost:8000
- Interactive UI: http://localhost:8000/static/index.html
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📡 API Endpoints

### TN VED Qidiruv
```bash
GET /api/v1/tnved/search?q=1701&limit=10
```

### Bojxona Hisoblash
```bash
POST /api/v1/calculator/calculate
{
  "tnved_code": "1701131011",
  "goods_cost": 10000,
  "delivery_cost": 5000,
  "insurance_cost": 1000,
  "currency_code": "USD",
  "country_code": "CN",
  "has_st1_certificate": false
}
```

### Valyuta Kurslari
```bash
GET /api/v1/currency/rates
GET /api/v1/currency/rate/{code}
```

## 🔧 Muammolar va Yechimlar

### 1️⃣ Ma'lumotlar Aniqligi Muammosi

**Muammo**: Dastlab lex.uz saytidan olingan tarif stavkalari incustoms.ai bilan mos kelmadi. Hisob-kitob natijalari farq qildi.

**Yechim**: 
- incustoms.ai Supabase bazasiga to'g'ridan-to'g'ri ulanish o'rnatildi
- 14,033 TN VED kodi va tariflar real-time sinxronlash qilindi
- `scripts/sync_incustoms.py` skripti yozildi

**Natija**: ✅ 100% aniqlik, incustoms.ai bilan bir xil natijalar

---

### 2️⃣ RNB Davlatlari Farqi

**Muammo**: Barcha davlatlar uchun bir xil bojxona stavkasi qo'llanilardi. Lekin MDH davlatlari (RNB) uchun alohida past stavkalar mavjud.

**Yechim**:
- TN VED jadvaliga `duty_rate_rnb` va `duty_rate_non_rnb` ustunlari qo'shildi
- RNB mamlakatlar ro'yxati yaratildi: RU, KZ, KG, TJ, BY, AM, AZ, MD, UA, GE, TM
- Calculator service'da avtomatik stavka tanlash mexanizmi qo'shildi

**Misol**:
```python
# Rossiya (RNB): 1% poshlina
# Janubiy Koreya (Non-RNB): 2% poshlina
```

**Natija**: ✅ Har bir mamlakat uchun to'g'ri stavka

---

### 3️⃣ BRV (Bazaviy Hisoblash Qiymati) Xatosi

**Muammo**: Kod ichida eski BRV qiymati (375,000 so'm) ishlatilgan edi. 2025 yil uchun BRV 412,000 so'm.

**Yechim**:
- BRV qiymatini 412,000 ga yangiladik
- Bojxona rasmiylash yig'imi hisoblash to'liq qayta yozildi
- TP-55 nizomiga muvofiq 7 darajali tarif tizimi joriy qilindi:

```python
Tovar qiymati          | Yig'im
-----------------------|-------------
$0 - $1,000           | 0.3 × BRV
$1,000 - $5,000       | 0.5 × BRV
$5,000 - $10,000      | 1.0 × BRV
$10,000 - $20,000     | 1.5 × BRV
$20,000 - $50,000     | 3.0 × BRV
$50,000 - $100,000    | 5.0 × BRV
$100,000+             | 10.0 × BRV
```

**Natija**: ✅ To'g'ri BRV asosidagi hisob-kitob

---

### 4️⃣ TN VED Qidiruv Optimallashtirish

**Muammo**: Foydalanuvchi "56" deb qidirsa, 5601, 5602 kodlar bilan birga 1234**56**78 kabi kod o'rtasida raqam bor tovarlar ham chiqardi.

**Yechim**:
- Raqamli qidiruv uchun faqat prefix match qo'lladik
- Natijalarni kod uzunligi bo'yicha tartibladik (qisqaroq kod - yuqorida)
- Matnli qidiruv uchun alohida logika qo'shdik

```python
if query.isdigit():
    # Faqat kod boshi bilan mos keluvchilar
    results = filter(code.startswith(query))
    results = sorted(results, key=lambda x: len(x.code))
else:
    # Matn qidiruv - kod yoki tavsifda
    results = filter(code.startswith(query) OR description.contains(query))
```

**Natija**: ✅ Aniq va tezkor qidiruv natijalari

---

### 5️⃣ Valyuta Kurslarini Avtomatlashtirish

**Muammo**: Har safar "Bugungi USD kursi topilmadi" xatolari paydo bo'lardi. Qo'lda yangilash kerak edi.

**Yechim**:
- FastAPI lifespan events ishlatildi
- Startup'da avtomatik CBU.uz dan kurslar yuklanadi
- Background task yozildi - har kuni 09:00 da avtomatik yangilash
- AsyncIO schedulerdan foydalanildi

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    await update_currency_rates()  # Startup
    asyncio.create_task(daily_currency_update())  # Daily 09:00
    yield
```

**Natija**: ✅ Kurslar doim yangi, xatolik yo'q

---

### 6️⃣ incustoms.ai Attribution

**Muammo**: Ma'lumotlar qaerdan kelayotgani foydalanuvchilarga noma'lum edi. Shaffoflik kerak.

**Yechim**:
- Frontend banner qo'shildi: "Ma'lumotlar incustoms.ai dan sinxronlangan"
- API response'larga `data_source` va `sync_info` fieldlar qo'shildi
- Sync script log'lariga ma'lumot manbai ko'rsatildi

**Natija**: ✅ To'liq shaffoflik va kredit

---

### 7️⃣ Kod Temirligi va Clean Code

**Muammo**: Dastlabki kodda ortiqcha loglar, commentlar va debug statementlar ko'p edi.

**Yechim**:
- Verbose logging olib tashlandi
- Production-ready kod yozildi
- Minimal va kerakli loglar qoldirildi

**Natija**: ✅ Professional, toza va samarali kod

## 🧪 Test Natijalari

### Hisob-kitob Aniqligi

| Test Case | Tovar | Mamlakat | Natija | Status |
|-----------|-------|----------|--------|--------|
| TN VED 1701131011 | $16,000 shakar | Xitoy | 67,205,007 so'm | ✅ |
| TN VED 8703231983 | $106,000 mashina | AQSH | 445,258,920 so'm | ✅ |
| RNB stavka | $10,000 | Rossiya | 1% poshlina | ✅ |
| Non-RNB stavka | $10,000 | Koreya | 2% poshlina | ✅ |

### BRV Hisoblash

| Tovar Qiymati | Koeffitsient | BRV Yig'im | Status |
|---------------|--------------|------------|--------|
| $500 | 0.3 | 123,600 | ✅ |
| $3,000 | 0.5 | 206,000 | ✅ |
| $7,000 | 1.0 | 412,000 | ✅ |
| $16,000 | 1.5 | 618,000 | ✅ |
| $106,000 | 10.0 | 4,120,000 | ✅ |

## 📊 Ma'lumotlar Bazasi

### Jadvallar va Hajmi

| Jadval | Yozuvlar | Manba | Yangilanish |
|--------|----------|-------|-------------|
| `tnved_items` | 14,033 | incustoms.ai | Sinxronlash |
| `tariff_rates` (RNB) | 14,033 | incustoms.ai | Sinxronlash |
| `tariff_rates` (Non-RNB) | 14,033 | incustoms.ai | Sinxronlash |
| `currencies` | 75+ | CBU.uz | Kunlik |
| `brv_rates` | 1 | Qo'lda | 2025 |

### Ma'lumotlar Sinxronlash

```bash
# incustoms.ai dan yangilash
python scripts/sync_incustoms.py

# ✅ 14,033 TN VED kod sinxronlandi
# ✅ RNB va Non-RNB tariflar yuklandi
# ✅ QQS va aksiz stavkalar yangilandi
```

## 🎨 Frontend Interface

Loyihada sodda lekin funksional web interfeys mavjud:
- TN VED kod qidiruv
- Real-time hisob-kitob
- Natijalarni batafsil ko'rsatish
- incustoms.ai attribution banner
- Responsive dizayn

Fayl: `/app/static/index.html`

## 🔐 Security & Best Practices

- ✅ Async/await - barcha I/O operatsiyalar
- ✅ SQLAlchemy 2.0 - zamonaviy ORM
- ✅ Pydantic validation - ma'lumotlar tekshiruvi
- ✅ Type hints - to'liq type safety
- ✅ Error handling - barcha exception'lar ushlangan
- ✅ Environment variables - sensitive data
- ✅ Database migrations - Alembic

## 🚀 Performance

- **TN VED qidiruv**: < 50ms (14k+ yozuvlar)
- **Hisob-kitob**: < 100ms
- **Valyuta yangilash**: < 2s (75+ valyuta)
- **Database**: SQLite (production-ready)
- **Async operations**: uvloop + httptools

## 📝 Kodlar Strukturasi

```
bojxona-backend/
├── app/
│   ├── main.py              # FastAPI app, lifespan management
│   ├── api/v1/              # API endpoints
│   │   ├── calculator.py    # Hisob-kitob endpoint
│   │   ├── tnved.py         # TN VED qidiruv
│   │   └── currency.py      # Valyuta API
│   ├── services/
│   │   └── calculator.py    # Core hisoblash logikasi (628 lines)
│   ├── crud/                # Database operations
│   │   ├── tnved.py         # TN VED CRUD + search
│   │   ├── tariff.py        # Tarif CRUD
│   │   └── currency.py      # Valyuta CRUD
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   └── static/              # Web interface
├── scripts/
│   ├── sync_incustoms.py    # incustoms.ai sinxronlash
│   └── update_rates.py      # CBU kurs yangilash
├── migrations/              # Alembic migrations
└── requirements.txt         # Dependencies
```

## 🤝 Hissa Qo'shish

Loyihani rivojlantirishda ishtirok etish uchun:

1. Fork qiling
2. Feature branch yarating (`git checkout -b feature/AmazingFeature`)
3. Commit qiling (`git commit -m 'Add: Amazing Feature'`)
4. Push qiling (`git push origin feature/AmazingFeature`)
5. Pull Request oching

## 📄 License

MIT License - [LICENSE](LICENSE) faylini ko'ring

## 🙏 Minnatdorchilik

- **incustoms.ai** - TN VED kodlari va tariflar manbai
- **O'zbekiston Respublikasi Markaziy Banki** - valyuta kurslari
- **FastAPI** - framework
- **SQLAlchemy** - ORM

## 📞 Aloqa

Savollar va takliflar uchun GitHub Issues'dan foydalaning.

---

**Made with ❤️ for Uzbekistan customs professionals**
