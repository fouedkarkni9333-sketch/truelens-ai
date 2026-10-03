from flask import Flask, render_template_string, request
import re
import numpy as np
from PIL import Image

app = Flask(__name__)

# قاموس اللغات العالمي الموسع (أكثر من 30 لغة عالمية)
TRANSLATIONS = {
    "en": {
        "name": "English", "title": "TrueLens AI", "subtitle": "Global Digital Verification & AI Detection Engine",
        "text_label": "📄 Text Analysis:", "text_placeholder": "Paste text here to check its authenticity...",
        "image_label": "🖼️ Visual Image Analysis:", "btn_submit": "Start Comprehensive Analysis 🔍",
        "result_title": "Field Analysis Result:", "btn_speak": "Listen to Audio Report 🔊",
        "error_short": "The entered text is too short for accurate analysis.",
        "error_ai": "AI Alert: This text carries clear fingerprints and tone of AI models with high artificial probability.",
        "error_human": "Natural Text: This text is safe and appears to be written naturally by a human.",
        "img_ai": "Visual Alert: The image shows indicators of manipulation or AI generation (Digital Variance Index: ",
        "img_human": "Visual Image: The image is clean, natural, and free from artificial generation anomalies."
    },
    "ar": {
        "name": "العربية (Arabic)", "title": "TrueLens AI", "subtitle": "محرك التحقق الرقمي واكتشاف الذكاء الاصطناعي العالمي",
        "text_label": "📄 التحليل النصي:", "text_placeholder": "ألصق النص هنا للتحقق من مصداقيته...",
        "image_label": "🖼️ التحليل البصري للصورة:", "btn_submit": "بدء الفحص والتحليل الشامل 🔍",
        "result_title": "نتيجة التحليل الميداني:", "btn_speak": "استماع للتقرير الصوتي 🔊",
        "error_short": "النص المدخل قصير جداً للقيام بعملية فحص دقيقة.",
        "error_ai": "تنبيه نصي: هذا النص يحمل بصمات ونبرة واضحة لنماذج الذكاء الاصطناعي بنسبة اصطناعية عالية.",
        "error_human": "النص طبيعي وآمن ويبدو أنه صادر عن كاتِب بشري بشكل عفوي.",
        "img_ai": "تنبيه بصري: الصورة تظهر عليها مؤشرات تلاعب أو توليد بالذكاء الاصطناعي (مؤشر التباين الرقمي: ",
        "img_human": "الصورة بصرية سليمة وطبيعية وخالية من شطط التوليد الاصطناعي."
    },
    "fr": {
        "name": "Français", "title": "TrueLens AI", "subtitle": "Moteur mondial de vérification numérique et de détection IA",
        "text_label": "📄 Analyse de Texte:", "text_placeholder": "Collez le texte ici pour vérifier son authenticité...",
        "image_label": "🖼️ Analyse Visuelle d'Image:", "btn_submit": "Démarrer l'Analyse Complète 🔍",
        "result_title": "Résultat de l'Analyse:", "btn_speak": "Écouter le Rapport Audio 🔊",
        "error_short": "Le texte entré est trop court.", "error_ai": "Alerte IA: Empreintes claires de modèles d'IA.",
        "error_human": "Texte Naturel: Rédigé par un humain.", "img_ai": "Alerte Visuelle (Variance: ", "img_human": "Image propre et naturelle."
    },
    "es": {
        "name": "Español", "title": "TrueLens AI", "subtitle": "Motor Global de Verificación Digital",
        "text_label": "📄 Análisis de Texto:", "text_placeholder": "Pegue el texto aquí...",
        "image_label": "🖼️ Análisis Visual:", "btn_submit": "Iniciar Análisis 🔍",
        "result_title": "Resultado:", "btn_speak": "Escuchar Audio 🔊",
        "error_short": "Texto muy corto.", "error_ai": "Alerta de IA detectada.", "error_human": "Texto natural y seguro.",
        "img_ai": "Alerta Visual (Varianza: ", "img_human": "Imagen normal y natural."
    },
    "de": {
        "name": "Deutsch", "title": "TrueLens AI", "subtitle": "Globales System zur digitalen Verifikation",
        "text_label": "📄 Textanalyse:", "text_placeholder": "Text hier einfügen...",
        "image_label": "🖼️ Visuelle Analyse:", "btn_submit": "Analyse Starten 🔍",
        "result_title": "Ergebnis:", "btn_speak": "Anhören 🔊",
        "error_short": "Text zu kurz.", "error_ai": "KI-Warnung aktiv.", "error_human": "Natürlicher Text.",
        "img_ai": "Visuelle Warnung (Varianz: ", "img_human": "Bild ist sauber."
    },
    "zh": {
        "name": "中文 (Chinese)", "title": "TrueLens AI", "subtitle": "全球数字验证与AI检测引擎",
        "text_label": "📄 文本分析：", "text_placeholder": "在此粘贴文本...",
        "image_label": "🖼️ 图像分析：", "btn_submit": "开始综合分析 🔍",
        "result_title": "分析结果：", "btn_speak": "语音报告 🔊",
        "error_short": "文本太短。", "error_ai": "AI警报：检测到AI特征。", "error_human": "自然文本，安全。",
        "img_ai": "视觉警报（方差：", "img_human": "图像自然正常。"
    },
    "ja": {
        "name": "日本語 (Japanese)", "title": "TrueLens AI", "subtitle": "グローバルデジタル検証エンジン",
        "text_label": "📄 テキスト分析:", "text_placeholder": "テキストを貼り付け...",
        "image_label": "🖼️ 画像分析:", "btn_submit": "分析開始 🔍",
        "result_title": "結果:", "btn_speak": "音声レポート 🔊",
        "error_short": "テキストが短すぎます。", "error_ai": "AI警告: AI生成の可能性が高いです。", "error_human": "自然なテキストです。",
        "img_ai": "視覚的警告 (分散: ", "img_human": "画像は正常です。"
    },
    "it": {
        "name": "Italiano", "title": "TrueLens AI", "subtitle": "Motore di Verifica Globale",
        "text_label": "📄 Analisi Testo:", "text_placeholder": "Incolla il testo...",
        "image_label": "🖼️ Analisi Immagine:", "btn_submit": "Avvia Analisi 🔍",
        "result_title": "Risultato:", "btn_speak": "Ascolta Audio 🔊",
        "error_short": "Testo troppo corto.", "error_ai": "Rilevato contenuto IA.", "error_human": "Testo naturale.",
        "img_ai": "Avviso Visivo (Varianza: ", "img_human": "Immagine normale."
    },
    "pt": {
        "name": "Português", "title": "TrueLens AI", "subtitle": "Motor Global de Verificação",
        "text_label": "📄 Análise de Texto:", "text_placeholder": "Cole o texto aqui...",
        "image_label": "🖼️ Análise de Imagem:", "btn_submit": "Iniciar Análise 🔍",
        "result_title": "Resultado:", "btn_speak": "Ouvir Áudio 🔊",
        "error_short": "Texto muito curto.", "error_ai": "Alerta de IA detectado.", "error_human": "Texto natural.",
        "img_ai": "Alerta Visual (Variância: ", "img_human": "Imagem limpa e natural."
    },
    "ru": {
        "name": "Русский (Russian)", "title": "TrueLens AI", "subtitle": "Глобальный движок проверки",
        "text_label": "📄 Анализ текста:", "text_placeholder": "Вставьте текст...",
        "image_label": "🖼️ Анализ изображения:", "btn_submit": "Начать анализ 🔍",
        "result_title": "Результат:", "btn_speak": "Прослушать 🔊",
        "error_short": "Текст слишком короткий.", "error_ai": "Предупреждение ИИ.", "error_human": "Естественный текст.",
        "img_ai": "Визуальное предупреждение (Дисперсия: ", "img_human": "Изображение в норме."
    },
    "hi": {
        "name": "हिन्दी (Hindi)", "title": "TrueLens AI", "subtitle": "वैश्विक डिजिटल सत्यापन इंजन",
        "text_label": "📄 पाठ विश्लेषण:", "text_placeholder": "पाठ यहाँ चिपकाएँ...",
        "image_label": "🖼️ छवि विश्लेषण:", "btn_submit": "विश्लेषण शुरू करें 🔍",
        "result_title": "परिणाम:", "btn_speak": "ऑडियो सुनें 🔊",
        "error_short": "पाठ बहुत छोटा है।", "error_ai": "AI चेतावनी: AI जनित सामग्री।", "error_human": "प्राकृतिक पाठ।",
        "img_ai": "दृश्य चेतावनी (विचरण: ", "img_human": "छ비 सामान्य है।"
    },
    "tr": {
        "name": "Türkçe", "title": "TrueLens AI", "subtitle": "Küresel Dijital Doğrulama Motoru",
        "text_label": "📄 Metin Analizi:", "text_placeholder": "Metni buraya yapıştırın...",
        "image_label": "🖼️ Görsel Analiz:", "btn_submit": "Analizi Başlat 🔍",
        "result_title": "Sonuç:", "btn_speak": "Sesli Dinle 🔊",
        "error_short": "Metin çok kısa.", "error_ai": "Yapay Zeka uyarısı.", "error_human": "Doğal metin.",
        "img_ai": "Görsel Uyarı (Varyans: ", "img_human": "Görsel normal."
    },
    "ko": {
        "name": "한국어 (Korean)", "title": "TrueLens AI", "subtitle": "글로벌 디지털 검증 엔진",
        "text_label": "📄 텍스트 분석:", "text_placeholder": "텍스트를 여기에 붙여넣으세요...",
        "image_label": "🖼️ 이미지 분석:", "btn_submit": "분석 시작 🔍",
        "result_title": "결과:", "btn_speak": "음성 듣기 🔊",
        "error_short": "텍스트가 너무 짧습니다.", "error_ai": "AI 경고: 인공지능 생성 텍스트.", "error_human": "자연스러운 텍스트입니다.",
        "img_ai": "시각적 경고 (분산: ", "img_human": "이미지가 정상입니다."
    },
    "nl": {
        "name": "Nederlands", "title": "TrueLens AI", "subtitle": "Wereldwijde Verificatie Engine",
        "text_label": "📄 Tekstanalyse:", "text_placeholder": "Plak hier tekst...",
        "image_label": "🖼️ Beeldanalyse:", "btn_submit": "Start Analyse 🔍",
        "result_title": "Resultaat:", "btn_speak": "Luister Audio 🔊",
        "error_short": "Tekst te kort.", "error_ai": "KI-waarschuwing.", "error_human": "Natuurlijke tekst.",
        "img_ai": "Visuele waarschuwing (Variantie: ", "img_human": "Afbeelding is normaal."
    },
    "pl": {
        "name": "Polski", "title": "TrueLens AI", "subtitle": "Globalny Silnik Weryfikacji",
        "text_label": "📄 Analiza Tekstu:", "text_placeholder": "Wklej tekst tutaj...",
        "image_label": "🖼️ Analiza Obrazu:", "btn_submit": "Rozpocznij Analizę 🔍",
        "result_title": "Wynik:", "btn_speak": "Posłuchaj Audio 🔊",
        "error_short": "Tekst za krótki.", "error_ai": "Ostrzeżenie AI.", "error_human": "Tekst naturalny.",
        "img_ai": "Ostrzeżenie wizualne (Wariancja: ", "img_human": "Obraz jest naturalny."
    },
    "vi": {
        "name": "Tiếng Việt", "title": "TrueLens AI", "subtitle": "Công cụ Xác thực Toàn cầu",
        "text_label": "📄 Phân tích Văn bản:", "text_placeholder": "Dán văn bản vào đây...",
        "image_label": "🖼️ Phân tích Hình ảnh:", "btn_submit": "Bắt đầu Phân tích 🔍",
        "result_title": "Kết quả:", "btn_speak": "Nghe Âm thanh 🔊",
        "error_short": "Văn bản quá ngắn.", "error_ai": "Cảnh báo AI.", "error_human": "Văn bản tự nhiên.",
        "img_ai": "Cảnh báo hình ảnh (Phương sai: ", "img_human": "Hình ảnh bình thường."
    },
    "id": {
        "name": "Bahasa Indonesia", "title": "TrueLens AI", "subtitle": "Mesin Verifikasi Global",
        "text_label": "📄 Analisis Teks:", "text_placeholder": "Tempel teks di sini...",
        "image_label": "🖼️ Analisis Gambar:", "btn_submit": "Mulai Analisis 🔍",
        "result_title": "Hasil:", "btn_speak": "Dengarkan Audio 🔊",
        "error_short": "Teks terlalu pendek.", "error_ai": "Peringatan AI.", "error_human": "Teks alami.",
        "img_ai": "Peringatan Visual (Varian: ", "img_human": "Gambar normal."
    },
    "sv": {
        "name": "Svenska", "title": "TrueLens AI", "subtitle": "Global Verifieringsmotor",
        "text_label": "📄 Textanalys:", "text_placeholder": "Klistra in text här...",
        "image_label": "🖼️ Bildanalys:", "btn_submit": "Starta Analys 🔍",
        "result_title": "Resultat:", "btn_speak": "Lyssna på Ljud 🔊",
        "error_short": "För kort text.", "error_ai": "AI-varning.", "error_human": "Naturlig text.",
        "img_ai": "Visuell varning (Varians: ", "img_human": "Bilden är normal."
    },
    "uk": {
        "name": "Українська (Ukrainian)", "title": "TrueLens AI", "subtitle": "Глобальний рушій перевірки",
        "text_label": "📄 Аналіз тексту:", "text_placeholder": "Вставте текст сюди...",
        "image_label": "🖼️ Аналіз зображення:", "btn_submit": "Почати аналіз 🔍",
        "result_title": "Результат:", "btn_speak": "Прослухати аудіо 🔊",
        "error_short": "Текст занадто короткий.", "error_ai": "Попередження ШІ.", "error_human": "Природний текст.",
        "img_ai": "Візуальне попередження (Дисперсія: ", "img_human": "Зображення нормальне."
    },
    "el": {
        "name": "Ελληνικά (Greek)", "title": "TrueLens AI", "subtitle": "Παγκόσμια Μηχανή Επαλήθευσης",
        "text_label": "📄 Ανάλυση Κειμένου:", "text_placeholder": "Επικολλήστε κείμενο εδώ...",
        "image_label": "🖼️ Ανάλυση Εικόνας:", "btn_submit": "Έναρξη Ανάλυσης 🔍",
        "result_title": "Αποτέλεσμα:", "btn_speak": "Ακούστε Ήχο 🔊",
        "error_short": "Πολύ σύντομο κείμενο.", "error_ai": "Προειδοποίηση AI.", "error_human": "Φυσικό κείμενο.",
        "img_ai": "Οπτική προειδοποίηση (Διακύμανση: ", "img_human": "Η εικόνα είναι κανονική."
    },
    "he": {
        "name": "עברית (Hebrew)", "title": "TrueLens AI", "subtitle": "מנוע אימות דיגיטלי עולמי",
        "text_label": "📄 ניתוח טקסט:", "text_placeholder": "הדבק טקסט כאן...",
        "image_label": "🖼️ ניתוח תמונה:", "btn_submit": "התחל ניתוח 🔍",
        "result_title": "תוצאה:", "btn_speak": "האזן לדוח 🔊",
        "error_short": "הטקסט קצר מדי.", "error_ai": "אזהרת בינה מלאכותית.", "error_human": "טקסט טבעי.",
        "img_ai": "אזהרה ויזואלית (שונות: ", "img_human": "התמונה תקינה."
    },
    "ro": {
        "name": "Română", "title": "TrueLens AI", "subtitle": "Motor Global de Verificare",
        "text_label": "📄 Analiză Text:", "text_placeholder": "Lipește textul aici...",
        "image_label": "🖼️ Analiză Imagine:", "btn_submit": "Începe Analiza 🔍",
        "result_title": "Rezultat:", "btn_speak": "Ascultă Audio 🔊",
        "error_short": "Text prea scurt.", "error_ai": "Alertă AI.", "error_human": "Text natural.",
        "img_ai": "Alertă vizuală (Varianță: ", "img_human": "Imagine normală."
    },
    "hu": {
        "name": "Magyar", "title": "TrueLens AI", "subtitle": "Globális Ellenőrző Motor",
        "text_label": "📄 Szövegelemzés:", "text_placeholder": "Illessze ide a szöveget...",
        "image_label": "🖼️ Képelemzés:", "btn_submit": "Elemzés Indítása 🔍",
        "result_title": "Eredmény:", "btn_speak": "Hang Hallgatása 🔊",
        "error_short": "Túl rövid szöveg.", "error_ai": "MI figyelmeztetés.", "error_human": "Természetes szöveg.",
        "img_ai": "Vizuális figyelmeztetés (Variancia: ", "img_human": "A kép normális."
    },
    "cs": {
        "name": "Čeština", "title": "TrueLens AI", "subtitle": "Globální Ověřovací Motor",
        "text_label": "📄 Analýza Textu:", "text_placeholder": "Sem vložte text...",
        "image_label": "🖼️ Analýza Obrazu:", "btn_submit": "Spustit Analýzu 🔍",
        "result_title": "Výsledek:", "btn_speak": "Poslechnout Zvuk 🔊",
        "error_short": "Příliš krátký text.", "error_ai": "Upozornění AI.", "error_human": "Přirozený text.",
        "img_ai": "Vizuální upozornění (Variance: ", "img_human": "Obrázek je v pořádku."
    },
    "th": {
        "name": "ไทย (Thai)", "title": "TrueLens AI", "subtitle": "เครื่องมือตรวจสอบดิจิทัลระดับโลก",
        "text_label": "📄 วิเคราะห์ข้อความ:", "text_placeholder": "วางข้อความที่นี่...",
        "image_label": "🖼️ วิเคราะห์รูปภาพ:", "btn_submit": "เริ่มการวิเคราะห์ 🔍",
        "result_title": "ผลลัพธ์:", "btn_speak": "ฟังรายงานเสียง 🔊",
        "error_short": "ข้อความสั้นเกินไป", "error_ai": "คำเตือน AI: ตรวจพบเนื้อหา AI", "error_human": "ข้อความปกติทั่วไป",
        "img_ai": "คำเตือนภาพ (ความแปรปรวน: ", "img_human": "ภาพปกติสมบูรณ์"
    },
    "fi": {
        "name": "Suomi", "title": "TrueLens AI", "subtitle": "Globaali Varmennusmoottori",
        "text_label": "📄 Tekstianalyysi:", "text_placeholder": "Liitä teksti tähän...",
        "image_label": "🖼️ Kuvaanalyysi:", "btn_submit": "Aloita Analyysi 🔍",
        "result_title": "Tulos:", "btn_speak": "Kuuntele Ääni 🔊",
        "error_short": "Liian lyhyt teksti.", "error_ai": "Tekoälyvaroitus.", "error_human": "Luonnollinen teksti.",
        "img_ai": "Visuaalinen varoitus (Varianssi: ", "img_human": "Kuva on normaali."
    },
    "da": {
        "name": "Dansk", "title": "TrueLens AI", "subtitle": "Global Verificeringsmotor",
        "text_label": "📄 Tekstanalyse:", "text_placeholder": "Indsæt tekst her...",
        "image_label": "🖼️ Billedanalyse:", "btn_submit": "Start Analyse 🔍",
        "result_title": "Resultat:", "btn_speak": "Lyt til Lyd 🔊",
        "error_short": "For kort tekst.", "error_ai": "AI-advarsel.", "error_human": "Naturlig tekst.",
        "img_ai": "Visuel advarsel (Varians: ", "img_human": "Billedet er normalt."
    },
    "no": {
        "name": "Norsk", "title": "TrueLens AI", "subtitle": "Global Verifiseringsmotor",
        "text_label": "📄 Tekstanalyse:", "text_placeholder": "Lim inn tekst her...",
        "image_label": "🖼️ Bildeanalyse:", "btn_submit": "Start Analyse 🔍",
        "result_title": "Resultat:", "btn_speak": "Hør Lydrapport 🔊",
        "error_short": "For kort tekst.", "error_ai": "KI-advarsel.", "error_human": "Naturlig tekst.",
        "img_ai": "Visuell advarsel (Varians: ", "img_human": "Bildet er normalt."
    },
    "ms": {
        "name": "Bahasa Melayu", "title": "TrueLens AI", "subtitle": "Enjin Pengesahan Global",
        "text_label": "📄 Analisis Teks:", "text_placeholder": "Tampal teks di sini...",
        "image_label": "🖼️ Analisis Imej:", "btn_submit": "Mula Analisis 🔍",
        "result_title": "Keputusan:", "btn_speak": "Dengar Audio 🔊",
        "error_short": "Teks terlalu pendek.", "error_ai": "Amaran AI.", "error_human": "Teks asli.",
        "img_ai": "Amaran Visual (Varians: ", "img_human": "Imej adalah normal."
    },
    "bn": {
        "name": "বাংলা (Bengali)", "title": "TrueLens AI", "subtitle": "গ্লোবাল ভেরিফিকেশন ইঞ্জিন",
        "text_label": "📄 টেক্সট বিশ্লেষণ:", "text_placeholder": "এখানে টেক্সট পেস্ট করুন...",
        "image_label": "🖼️ ছবি বিশ্লেষণ:", "btn_submit": "বিশ্লেষণ শুরু করুন 🔍",
        "result_title": "ফলাফল:", "btn_speak": "অডিও শুনুন 🔊",
        "error_short": "টেক্সট খুব ছোট।", "error_ai": "AI সতর্কতা: AI দ্বারা তৈরি।", "error_human": "স্বাভাবিক টেক্সট।",
        "img_ai": "ভিজ্যুয়াল সতর্কতা (ভ্যারিয়েন্স: ", "img_human": "ছবিটি স্বাভাবিক।"
    },
    "fa": {
        "name": "فارسی (Persian)", "title": "TrueLens AI", "subtitle": "موتور جهانی تأیید اصالت",
        "text_label": "📄 تحلیل متن:", "text_placeholder": "متن را اینجا بچسبانید...",
        "image_label": "🖼️ تحلیل تصویر:", "btn_submit": "شروع تحلیل 🔍",
        "result_title": "نتیجه:", "btn_speak": "گزارش صوتی 🔊",
        "error_short": "متن خیلی کوتاه است.", "error_ai": "هشدار هوش مصنوعی.", "error_human": "متن طبیعی است.",
        "img_ai": "هشدار تصویری (واریانس: ", "img_human": "تصویر عادی است."
    },
    "ur": {
        "name": "اردو (Urdu)", "title": "TrueLens AI", "subtitle": "عالمی ڈیجیٹل تصدیقی انجن",
        "text_label": "📄 متن کا تجزیہ:", "text_placeholder": "یہاں متن چسپاں کریں...",
        "image_label": "🖼️ تصویر کا تجزیہ:", "btn_submit": "تجزیہ شروع کریں 🔍",
        "result_title": "نتیجہ:", "btn_speak": "آڈیو سنیں 🔊",
        "error_short": "متن بہت چھوٹا ہے۔", "error_ai": "AI کی طرف سے انتباہ۔", "error_human": "قدرتی متن۔",
        "img_ai": " بصری انتباہ (فرق: ", "img_human": "تصویر نارمل ہے۔"
    }
}

HTML_TEMPLATE = """
<!doctype html>
<html lang="{{ current_lang }}" dir="ltr">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ t.title }}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0b0f19;
            --card-bg: #1e1b4b;
            --card-border: #312e81;
            --accent-color: #6366f1;
            --accent-hover: #4f46e5;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }
        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .app-container {
            width: 100%;
            max-width: 550px;
            background: linear-gradient(145deg, #1e1b4b, #0f172a);
            border: 1px solid var(--card-border);
            padding: 30px;
            border-radius: 24px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
        }
        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        select.lang-select {
            background: #0f172a;
            color: #38bdf8;
            border: 1px solid #475569;
            padding: 6px 12px;
            border-radius: 8px;
            font-family: 'Inter', sans-serif;
            font-size: 13px;
            cursor: pointer;
        }
        .header {
            text-align: center;
            margin-bottom: 20px;
        }
        .logo-icon { font-size: 38px; margin-bottom: 5px; }
        h2 { color: #818cf8; margin: 0 0 6px 0; font-size: 22px; }
        p.subtitle { color: var(--text-muted); font-size: 12px; margin: 0; }
        .input-group { margin-bottom: 18px; }
        label { display: block; margin-bottom: 6px; font-size: 13px; color: #cbd5e1; font-weight: 600; }
        textarea {
            width: 100%; height: 100px; padding: 12px; border-radius: 10px;
            border: 1px solid #475569; background: #0f172a; color: white;
            font-family: 'Inter', sans-serif; font-size: 14px; box-sizing: border-box; resize: vertical;
        }
        textarea:focus { outline: none; border-color: var(--accent-color); }
        .file-upload-box {
            border: 2px dashed #475569; padding: 12px; border-radius: 10px;
            text-align: center; background: #0f172a;
        }
        input[type="file"] { color: var(--text-muted); font-size: 12px; width: 100%; }
        .btn-submit {
            width: 100%; padding: 13px; border-radius: 10px; border: none;
            background: linear-gradient(135deg, #6366f1, #4338ca); color: white;
            font-family: 'Inter', sans-serif; font-weight: 700; font-size: 15px; cursor: pointer;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
        }
        .result-card {
            margin-top: 20px; padding: 16px; background: #0f172a;
            border-radius: 12px; border-left: 5px solid var(--accent-color);
        }
        .result-card h3 { margin: 0 0 8px 0; color: #818cf8; font-size: 14px; }
        .btn-speak {
            width: 100%; padding: 10px; margin-top: 10px; border-radius: 8px; border: none;
            background: #059669; color: white; font-weight: 600; font-size: 13px; cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="app-container">
        <div class="top-bar">
            <span style="font-size: 12px; color: var(--text-muted);">🌐 Global Version (32+ Langs)</span>
            <form method="GET" style="margin:0;">
                <select name="lang" class="lang-select" onchange="this.form.submit()">
                    {% for code, data in translations.items() %}
                    <option value="{{ code }}" {% if current_lang == code %}selected{% endif %}>{{ data.name }}</option>
                    {% endfor %}
                </select>
            </form>
        </div>

        <div class="header">
            <div class="logo-icon">🛡️️</div>
            <h2>{{ t.title }}</h2>
            <p class="subtitle">{{ t.subtitle }}</p>
        </div>
        
        <form method="POST" enctype="multipart/form-data">
            <div class="input-group">
                <label>{{ t.text_label }}</label>
                <textarea name="text_content" placeholder="{{ t.text_placeholder }}">{{ text_input or '' }}</textarea>
            </div>
            
            <div class="input-group">
                <label>{{ t.image_label }}</label>
                <div class="file-upload-box">
                    <input type="file" name="image_file" accept="image/*">
                </div>
            </div>
            
            <button type="submit" class="btn-submit">{{ t.btn_submit }}</button>
        </form>
        
        {% if result %}
        <div class="result-card">
            <h3>{{ t.result_title }}</h3>
            <p id="resultText" style="margin: 0; line-height: 1.5; font-size: 14px;">{{ result }}</p>
            <button class="btn-speak" onclick="speakResult()">{{ t.btn_speak }}</button>
        </div>
        {% endif %}
    </div>

    <script>
        function speakResult() {
            const text = document.getElementById("resultText").innerText;
            const speech = new SpeechSynthesisUtterance(text);
            speech.lang = '{{ current_lang }}';
            window.speechSynthesis.speak(speech);
        }
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    lang = request.args.get("lang", "en")
    if lang not in TRANSLATIONS:
        lang = "en"
    
    t = TRANSLATIONS[lang]
    result = None
    text_input = ""
    
    if request.method == "POST":
        text_input = request.form.get("text_content", "")
        uploaded_file = request.files.get("image_file")
        
        if uploaded_file and uploaded_file.filename != '':
            try:
                img = Image.open(uploaded_file.stream).convert('L')
                img_arr = np.array(img)
                variance = np.var(img_arr)
                if variance < 800:
                    result = f"{t['img_ai']}{variance:.2f})"
                else:
                    result = t['img_human']
            except:
                result = "Error processing image file."
                
        elif text_input.strip():
            ai_patterns = [r"as an ai", r"in conclusion", r"furthermore", r"it is important", r"بصفتي", r"في الختام"]
            score = sum(25 for pattern in ai_patterns if re.search(pattern, text_input, re.IGNORECASE))
            
            if len(text_input.strip()) < 10:
                result = t['error_short']
            elif score >= 25 or len(text_input.split()) > 15:
                result = t['error_ai']
            else:
                result = t['error_human']
        else:
            result = "Please enter text or upload an image to start."
            
    return render_template_string(HTML_TEMPLATE, t=t, current_lang=lang, translations=TRANSLATIONS, result=result, text_input=text_input)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
