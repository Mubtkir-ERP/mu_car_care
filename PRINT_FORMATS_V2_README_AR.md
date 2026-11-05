# تحديث استلام السيارة والطباعة - 05-11-2026

## التطبيق
- أضيف حقل الشركة `company` من نوع Link إلى Company في `Vehicle Reception` (إلزامي).
- عند إنشاء استلام جديد، تظهر الشركة الافتراضية للمستخدم.
- عند الحفظ عبر API، يتحقق الخادم من وجود الشركة ويملأ الافتراضي إن غاب.
- تنتقل الشركة إلى Sales Invoice / Sales Order / Quotation الناتجة من الاستلام.
- Patch للبيانات القديمة: يستنتج الشركة من المستندات المرتبطة عند الإمكان، ثم الافتراضية.

## أكواد الطباعة
ستجد ملفات الكود الكاملة في `print_formats_v2/`.
- `Letter_Head_Header.html` إلى قسم HTML للترويسة في Letter Head.
- `Letter_Head_Footer.html` إلى قسم HTML للفوتر في Letter Head.
- `Print_Sales_Invoice.html` إلى Print Format «فاتورة مبيعات ضريبية».
- `Print_Sales_Order.html` إلى Print Format «طلب مبيعات مع الصيانة».
- `Print_Quotation.html` إلى Print Format «عرض سعر مع الصيانة».
- `Print_Vehicle_Reception.html` إلى Print Format «نموذج استلام السيارة».

تم أيضًا وضع القوالب الأربعة في `mu_car_care/fixtures/print_format.json` داخل التطبيق.
لتجنب تعديل Letter Head الخاص بك دون موافقة، **لم نغيّر قاعدة بيانات Letter Head تلقائيًا**.
بعد تحديث التطبيق على السيرفر وتشغيل bench migrate، الصق كود الترويسة والفوتر مرة واحدة في مستند Letter Head المستخدم.

## كيفية التحديث
1. خذ نسخة احتياطية من الموقع قبل التحديث.
2. استبدل ملفات تطبيق `mu_car_care` بالإصدار المرفق مع المحافظة على تعديلاتك المحلية.
3. نفذ داخل bench: `bench --site YOUR_SITE migrate`، ثم `bench build --app mu_car_care` و `bench --site YOUR_SITE clear-cache`.
4. افتح Vehicle Reception وتأكد من حقل الشركة.
5. حدّث مستند Letter Head من ملفي Header وFooter.
6. جرّب فاتورة من صفحة واحدة وأخرى متعددة الصفحات ثم تحقق من جدول الصيانة وملف PDF.

## حدود مهمة
- Jinja تم فحصه نحويًا، لكن لم يمكن اختبار القوالب مباشرة في قاعدة بياناتك أو محرك PDF الخاص بالسيرفر.
- تكرار كل صفحة يدويًا مع الفوتر؛ إدخالات وصفوص طويلة جدًا قد تحتاج ضبط `items_per_page` و `visits_per_page`.
- يتم إخفاء الترويسة والفوتر عند عدم اختيار Letter Head صراحةً في طلب الطباعة.
- إذا كانت الصورة مفقودة رغم تثبيت التطبيق، تحقق من ملفات `/assets/mu_car_care/images/header_car.png` و `/assets/mu_car_care/images/car_care_footer.png`.
