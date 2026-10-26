# مُبتكِر للعناية بالسيارات والحماية (Mubtkir Car Care & Protection)

**mu_car_care** هو تطبيق متكامل مبني لنظام **مُبتكِر ERP** (`Mubtkir ERP`) يخدم مراكز العناية بالسيارات، تركيب أفلام العازل الحراري، وحماية الطلاء (PPF)، والنانو سيراميك، والتلميع الساطع.

Official Website: [https://www.mubtkir.com](https://www.mubtkir.com)

---

## 🌟 الميزات الأساسية (Key Features)

1. **معلومات السيارة في مستندات المبيعات (Vehicle Details in Sales Documents):**
   - إضافة تفاصيل السيارة (النوع، الموديل، رقم اللوحة، اللون، رقم الهيكل، قراءة العداد) في:
     - عروض الأسعار (`Quotation`)
     - طلبات المبيعات (`Sales Order`)
     - فواتير المبيعات (`Sales Invoice`)

2. **جدولة ومتابعة الصيانة الدورية (Automated Maintenance Scheduling):**
   - تفعيل جدول الصيانة بنقرة واحدة تحت قسم المرتجع.
   - تحديد تاريخ البدء، والمدة، وطريقة التوزيع (شهري، ربع سنوي، نصف سنوي، سنوي).
   - توليد آلي لكافة مواعيد الزيارات في جدول الصيانة مع متابعة حالة كل زيارة وتاريخها وقراءة العداد.

3. **زر إجراء سريع لتسجيل حضور وزيارة الصيانة (Quick Action - Record Maintenance):**
   - زر سريع أعلى الفاتورة المعتمدة (`Submitted Sales Invoice`) يتيح لموظف المبيعات تسجيل الحضور الفعلي للعميل وتحديث حالة الزيارة إلى "تمت الصيانة" بنقرة واحدة ونافذة منبثقة سريعة.

4. **شاشة استلام وفحص السيارة (Vehicle Reception & Inspection):**
   - بطاقة استلام وفحص لحماية المركز وتوثيق الخدوش والملاحظات المسبقة، مستوى الوقود، قراءة العداد، ومتعلقات العميل.
   - تسلسل ترقيم رسمي معتمد: `REC-.YY.-.MM.-###`.

---

## 🚀 التثبيت (Installation)

```bash
bench get-app https://github.com/Mubtkir-ERP/mu_car_care.git
bench --site [site-name] install-app mu_car_care
bench --site [site-name] migrate
```

---

## 📄 الترخيص (License)
MIT License - Copyright (c) 2026 [Mubtkir](https://www.mubtkir.com)
