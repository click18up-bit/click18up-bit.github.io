# ระบบสร้างหน้าคู่มือติดตั้งแอพ (multi-brand)

โฟลเดอร์ `_src/` นี้ **ไม่ถูก publish** ขึ้นเว็บ (GitHub Pages/Jekyll ข้ามโฟลเดอร์ที่ขึ้นต้นด้วย `_`)
มันคือ "เครื่องมือ" ไว้ปั๊มหน้าเว็บของแต่ละเจ้า

## โครงสร้าง
```
_src/
  template.html                 ← ดีไซน์กลาง (แก้ที่เดียว มีผลทุกเจ้า)
  build.py / build.sh           ← generator
  brands/
    Royalplus789/
      brand.json                ← config เจ้านั้น (ชื่อ, ข้อความ, caption)
      ios.pdf                   ← สไลด์ iOS (หน้า1=ปก, หน้า2..N=สเต็ป)
      android.pdf               ← สไลด์ Android
```
ผลลัพธ์ที่ถูก deploy: `/<slug>/index.html` + `/<slug>/img/*` (แยกอิสระต่อเจ้า)
เช่น `https://click18up-bit.github.io/Royalplus789`

## เพิ่มเจ้าใหม่ (เช่น "Bestlao888")
1. สร้างโฟลเดอร์ `_src/brands/Bestlao888/`
2. วางไฟล์ `ios.pdf` + `android.pdf` (รูปแบบเดียวกับ Royalplus789: หน้าแรกเป็นปก)
3. ก็อป `brand.json` จากเจ้าเดิมมาแก้ `name`, `slug`, `heroTitle`, และ `caption` แต่ละสเต็ป
   - จำนวนสเต็ปอิงตามจำนวนหน้า PDF จริง (หน้า−1) — ถ้า caption ไม่ครบจะเติม "ຂັ້ນຕອນທີ N" ให้เอง
   - โลโก้ crop จากปก ปรับกรอบได้ที่ `logo.crop = [x0,y0,x1,y1]` (สัดส่วน 0–1)
4. รัน:
   ```bash
   ./build.sh Bestlao888        # หรือ ./build.sh --all เพื่อปั๊มทุกเจ้า
   ```
5. commit + push → หน้าใหม่ขึ้นที่ `/Bestlao888`

## แก้ดีไซน์ให้ทุกเจ้าพร้อมกัน
แก้ `template.html` แล้วรัน `./build.sh --all` เพื่อปั๊มใหม่ทุกเจ้า

## หมายเหตุ
- `brand.json` รับ HTML ใน `caption`/`done` ได้ (ใช้ `<em>…</em>` ทำตัวเน้นสีทอง) — เนื้อหามาจากเราเอง ไม่ใช่ input ภายนอก
- รูป render ที่ DPI 170 JPEG q86 (คมพอ ไฟล์ไม่ใหญ่) ปรับได้ในหัว `build.py`
