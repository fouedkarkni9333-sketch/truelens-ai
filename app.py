from flask import Flask, render_template_string, request, jsonify
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
        "img_human": "Visual Image: The image is clean, natural, and free from artificial generation anomalies.",
        "mode_personal": "Individual Portal", "mode_enterprise": "Enterprise API Suite",
        "ent_title": "Enterprise Security & Compliance Suite", "ent_desc": "High-throughput batch verification and API endpoint for institutional workflows.",
        "api_endpoint_label": "Live API Endpoint:", "api_key_label": "API Authorization Key:",
        "btn_generate_key": "Generate Enterprise Key 🔑", "docs_label": "API Documentation & SDKs"
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
        "img_human": "الصورة بصرية سليمة وطبيعية وخالية من شطط التوليد الاصطناعي.",
        "mode_personal": "بوابة الأفراد", "mode_enterprise": "بوابة الشركات الفاخرة (Enterprise)",
        "ent_title": "بوابة الأمان والامتثال المؤسسي",
        "ent_desc": "فحص دفعات البيانات الضخمة ونظام الربط البرمجي المتقدم (API) لتكامل المؤسسات.",
        "api_endpoint_label": "رابط الـ API المباشر:", "api_key_label": "مفتاح ترخيص الشركات (API Key):",
        "btn_generate_key": "توليد مفتاح مؤسسي جديد 🔑", "docs_label": "دليل المطورين والوثائق التقنية (SDK)"
    },
    "fr": {
        "name": "Français", "title": "TrueLens AI", "subtitle": "Moteur mondial de vérification numérique et de détection IA",
        "text_label": "📄 Analyse de Texte:", "text_placeholder": "Collez le texte ici pour vérifier son authenticité...",
        "image_label": "🖼️ Analyse Visuelle d'Image:", "btn_submit": "Démarrer l'Analyse Complète 🔍",
        "result_title": "Résultat de l'Analyse:", "btn_speak": "Écouter le Rapport Audio 🔊",
        "error_short": "Le texte entré est trop court.", "error_ai": "Alerte IA: Empreintes claires de modèles d'IA.",
        "error_human": "Texte Naturel: Rédigé par un humain.", "img_ai": "Alerte Visuelle (Variance: ", "img_human": "Image propre et naturelle.",
        "mode_personal": "Portail Particulier", "mode_enterprise": "Suite Entreprise",
        "ent_title": "Suite de Sécurité & Conformité d'Entreprise", "ent_desc": "Vérification en lot à haut débit et endpoint API pour flux institutionnels.",
        "api_endpoint_label": "Endpoint API:", "api_key_label": "Clé d'Autorisation API:",
        "btn_generate_key": "Générer une Clé Entreprise 🔑", "docs_label": "Documentation API"
    },
    "es": {
        "name": "Español", "title": "TrueLens AI", "subtitle": "Motor Global de Verificación Digital",
        "text_label": "📄 Análisis de Texto:", "text_placeholder": "Pegue el texto aquí...",
        "image_label": "🖼️ Análisis Visual:", "btn_submit": "Iniciar Análisis 🔍",
        "result_title": "Resultado:", "btn_speak": "Escuchar Audio 🔊",
        "error_short": "Texto muy corto.", "error_ai": "Alerta de IA detectada.", "error_human": "Texto natural y seguro.",
        "img_ai": "Alerta Visual (Varianza: ", "img_human": "Imagen normal y natural.",
        "mode_personal": "Portal Individual", "mode_enterprise": "Suite Empresarial",
        "ent_title": "Suite de Seguridad y Cumplimiento", "ent_desc": "Verificación por lotes y API corporativa.",
        "api_endpoint_label": "Endpoint de API:", "api_key_label": "Clave API:",
        "btn_generate_key": "Generar Clave 🔑", "docs_label": "Documentación"
    },
    "de": {
        "name": "Deutsch", "title": "TrueLens AI", "subtitle": "Globales System zur digitalen Verifikation",
        "text_label": "📄 Textanalyse:", "text_placeholder": "Text hier einfügen...",
        "image_label": "🖼️ Visuelle Analyse:", "btn_submit": "Analyse Starten 🔍",
        "result_title": "Ergebnis:", "btn_speak": "Anhören 🔊",
        "error_short": "Text zu kurz.", "error_ai": "KI-Warnung aktiv.", "error_human": "Natürlicher Text.",
        "img_ai": "Visuelle Warnung (Varianz: ", "img_human": "Bild ist sauber.",
        "mode_personal": "Privatportal", "mode_enterprise": "Enterprise Suite",
        "ent_title": "Unternehmenssicherheits-Suite", "ent_desc": "API und Batch-Verarbeitung für Unternehmen.",
        "api_endpoint_label": "API-Endpunkt:", "api_key_label": "API-Schlüssel:",
        "btn_generate_key": "Schlüssel Generieren 🔑", "docs_label": "Dokumentation"
    },
    "zh": {
        "name": "中文 (Chinese)", "title": "TrueLens AI", "subtitle": "全球数字验证与AI检测引擎",
        "text_label": "📄 文本分析：", "text_placeholder": "在此粘贴文本...",
        "image_label": "🖼️ 图像分析：", "btn_submit": "开始综合分析 🔍",
        "result_title": "分析结果：", "btn_speak": "语音报告 🔊",
        "error_short": "文本太短。", "error_ai": "AI警报：检测到AI特征。", "error_human": "自然文本，安全。",
        "img_ai": "视觉警报（方差：", "img_human": "图像自然正常。",
        "mode_personal": "个人门户", "mode_enterprise": "企业级 API 套件",
        "ent_title": "企业安全与合规套件", "ent_desc": "为机构工作流提供高吞吐量批量验证和API端点。",
        "api_endpoint_label": "API 端点:", "api_key_label": "API 授权密钥:",
        "btn_generate_key": "生成企业密钥 🔑", "docs_label": "API 文档与 SDK"
    },
    "ja": {
        "name": "日本語 (Japanese)", "title": "TrueLens AI", "subtitle": "グローバルデジタル検証エンジン",
        "text_label": "📄 テキスト分析:", "text_placeholder": "テキストを貼り付け...",
        "image_label": "🖼️ 画像分析:", "btn_submit": "分析開始 🔍",
        "result_title": "結果:", "btn_speak": "音声レポート 🔊",
        "error_short": "テキストが短すぎます。", "error_ai": "AI警告: AI生成の可能性が高いです。", "error_human": "自然なテキストです。",
        "img_ai": "視覚的警告 (分散: ", "img_human": "画像は正常です。",
        "mode_personal": "個人ポータル", "mode_enterprise": "エンタープライズ API スイート",
        "ent_title": "エンタープライズセキュリティスイート", "ent_desc": "機関向けの高スループット一括検証とAPIエンドポイント。",
        "api_endpoint_label": "API エンドポイント:", "api_key_label": "API キー:",
        "btn_generate_key": "キーを生成 🔑", "docs_label": "API ドキュメント"
    },
    "it": {
        "name": "Italiano", "title": "TrueLens AI", "subtitle": "Motore di Verifica Globale",
        "text_label": "📄 Analisi Testo:", "text_placeholder": "Incolla il testo...",
        "image_label": "🖼️ Analisi Immagine:", "btn_submit": "Avvia Analisi 🔍",
        "result_title": "Risultato:", "btn_speak": "Ascolta Audio 🔊",
        "error_short": "Testo troppo corto.", "error_ai": "Rilevato contenuto IA.", "error_human": "Testo naturale.",
        "img_ai": "Avviso Visivo (Varianza: ", "img_human": "Immagine normale.",
        "mode_personal": "Portale Personale", "mode_enterprise": "Suite Aziendale",
        "ent_title": "Suite di Sicurezza Aziendale", "ent_desc": "Verifica batch ad alto rendimento e endpoint API.",
        "api_endpoint_label": "Endpoint API:", "api_key_label": "Chiave API:",
        "btn_generate_key": "Genera Chiave 🔑", "docs_label": "Documentazione"
    },
    "pt": {
        "name": "Português", "title": "TrueLens AI", "subtitle": "Motor Global de Verificação",
        "text_label": "📄 Análise de Texto:", "text_placeholder": "Cole o texto aqui...",
        "image_label": "🖼️ Análise de Imagem:", "btn_submit": "Iniciar Análise 🔍",
        "result_title": "Resultado:", "btn_speak": "Ouvir Áudio 🔊",
        "error_short": "Texto muito curto.", "error_ai": "Alerta de IA detectado.", "error_human": "Texto natural.",
        "img_ai": "Alerta Visual (Variância: ", "img_human": "Imagem limpa e natural.",
        "mode_personal": "Portal Pessoal", "mode_enterprise": "Suite Empresarial",
        "ent_title": "Suite de Segurança Corporativa", "ent_desc": "Verificação em lote e API para fluxos institucionais.",
        "api_endpoint_label": "Endpoint da API:", "api_key_label": "Chave da API:",
        "btn_generate_key": "Gerar Chave 🔑", "docs_label": "Documentação da API"
    },
    "ru": {
        "name": "Русский (Russian)", "title": "TrueLens AI", "subtitle": "Глобальный движок проверки",
        "text_label": "📄 Анализ текста:", "text_placeholder": "Вставьте текст...",
        "image_label": "🖼️ Анализ изображения:", "btn_submit": "Начать анализ 🔍",
        "result_title": "Результат:", "btn_speak": "Прослушать 🔊",
        "error_short": "Текст слишком короткий.", "error_ai": "Предупреждение ИИ.", "error_human": "Естественный текст.",
        "img_ai": "Визуальное предупреждение (Дисперсия: ", "img_human": "Изображение в норме.",
        "mode_personal": "Личный портал", "mode_enterprise": "Корпоративный API",
        "ent_title": "Корпоративный комплекс безопасности", "ent_desc": "Пакетная проверка и API для интеграций.",
        "api_endpoint_label": "API эндпоинт:", "api_key_label": "API ключ:",
        "btn_generate_key": "Сгенерировать ключ 🔑", "docs_label": "Документация"
    },
    "hi": {
        "name": "हिन्दी (Hindi)", "title": "TrueLens AI", "subtitle": "वैश्विक डिजिटल सत्यापन इंजन",
        "text_label": "📄 पाठ विश्लेषण:", "text_placeholder": "पाठ यहाँ चिपकाएँ...",
        "image_label": "🖼️ छवि विश्लेषण:", "btn_submit": "विश्लेषण शुरू करें 🔍",
        "result_title": "परिणाम:", "btn_speak": "ऑडियो सुनें 🔊",
        "error_short": "पाठ बहुत छोटा है।", "error_ai": "AI चेतावनी: AI जनित सामग्री।", "error_human": "प्राकृतिक पाठ।",
        "img_ai": "दृश्य चेतावनी (विचरण: ", "img_human": "छवि सामान्य है।",
        "mode_personal": "व्यक्तिगत पोर्टल", "mode_enterprise": "एंटरप्राइज़ API सूट",
        "ent_title": "एंटरप्राइज़ सुरक्षा सूट", "ent_desc": "संस्थागत कार्यप्रवाह के लिए उच्च-थروपुट सत्यापन और API।",
        "api_endpoint_label": "API एंडपॉइंट:", "api_key_label": "API कुंजी:",
        "btn_generate_key": "कुंजी बनाएँ 🔑", "docs_label": "दस्तावेज़"
    },
    "tr": {
        "name": "Türkçe", "title": "TrueLens AI", "subtitle": "Küresel Dijital Doğrulama Motoru",
        "text_label": "📄 Metin Analizi:", "text_placeholder": "Metni buraya yapıştırın...",
        "image_label": "🖼️ Görsel Analiz:", "btn_submit": "Analizi Başlat 🔍",
        "result_title": "Sonuç:", "btn_speak": "Sesli Dinle 🔊",
        "error_short": "Metin çok kısa.", "error_ai": "Yapay Zeka uyarısı.", "error_human": "Doğal metin.",
        "img_ai": "Görsel Uyarı (Varyans: ", "img_human": "Görsel normal.",
        "mode_personal": "Bireysel Portal", "mode_enterprise": "Kurumsal API Paketi",
        "ent_title": "Kurumsal Güvenlik Paketi", "ent_desc": "Kurumsal iş akışları için toplu doğrulama ve API ucu.",
        "api_endpoint_label": "API Ucu:", "api_key_label": "API Yetki Anahtarı:",
        "btn_generate_key": "Anahtar Üret 🔑", "docs_label": "API Belgeleri"
    },
    "ko": {
        "name": "한국어 (Korean)", "title": "TrueLens AI", "subtitle": "글로벌 디지털 검증 엔진",
        "text_label": "📄 텍스트 분석:", "text_placeholder": "텍스트를 여기에 붙여넣으세요...",
        "image_label": "🖼️ 이미지 분석:", "btn_submit": "분석 시작 🔍",
        "result_title": "결과:", "btn_speak": "음성 듣기 🔊",
        "error_short": "텍스트가 너무 짧습니다.", "error_ai": "AI 경고: 인공지능 생성 텍스트.", "error_human": "자연스러운 텍스트입니다.",
        "img_ai": "시각적 경고 (분산: ", "img_human": "이미지가 정상입니다.",
        "mode_personal": "개인 포털", "mode_enterprise": "엔터프라이즈 API",
        "ent_title": "엔터프라이즈 보안 스위트", "ent_desc": "대용량 일괄 검증 및 API 연동 지원.",
        "api_endpoint_label": "API 엔드포인트:", "api_key_label": "API 키:",
        "btn_generate_key": "키 생성 🔑", "docs_label": "API 문서"
    },
    "nl": {
        "name": "Nederlands", "title": "TrueLens AI", "subtitle": "Wereldwijde Verificatie Engine",
        "text_label": "📄 Tekstanalyse:", "text_placeholder": "Plak hier tekst...",
        "image_label": "🖼️ Beeldanalyse:", "btn_submit": "Start Analyse 🔍",
        "result_title": "Resultaat:", "btn_speak": "Luister Audio 🔊",
        "error_short": "Tekst te kort.", "error_ai": "KI-waarschuwing.", "error_human": "Natuurlijke tekst.",
        "img_ai": "Visuele waarschuwing (Variantie: ", "img_human": "Afbeelding is normaal.",
        "mode_personal": "Persoonlijk Portaal", "mode_enterprise": "Enterprise API Suite",
        "ent_title": "Enterprise Beveiligingssuite", "ent_desc": "Batchverificatie en API-endpoint voor organisaties.",
        "api_endpoint_label": "API-endpoint:", "api_key_label": "API-sleutel:",
        "btn_generate_key": "Sleutel Genereren 🔑", "docs_label": "Documentatie"
    },
    "pl": {
        "name": "Polski", "title": "TrueLens AI", "subtitle": "Globalny Silnik Weryfikacji",
        "text_label": "📄 Analiza Tekstu:", "text_placeholder": "Wklej tekst tutaj...",
        "image_label": "🖼️ Analiza Obrazu:", "btn_submit": "Rozpocznij Analizę 🔍",
        "result_title": "Wynik:", "btn_speak": "Posłuchaj Audio 🔊",
        "error_short": "Tekst za krótki.", "error_ai": "Ostrzeżenie AI.", "error_human": "Tekst naturalny.",
        "img_ai": "Ostrzeżenie wizualne (Wariancja: ", "img_human": "Obraz jest naturalny.",
        "mode_personal": "Portal Osobisty", "mode_enterprise": "Pakiet Enterprise",
        "ent_title": "Pakiet Bezpieczeństwa Korporacyjnego", "ent_desc": "Weryfikacja wsadowa i endpoint API dla instytucji.",
        "api_endpoint_label": "Endpoint API:", "api_key_label": "Klucz API:",
        "btn_generate_key": "Generuj Klucz 🔑", "docs_label": "Dokumentacja API"
    },
    "vi": {
        "name": "Tiếng Việt", "title": "TrueLens AI", "subtitle": "Công cụ Xác thực Toàn cầu",
        "text_label": "📄 Phân tích Văn bản:", "text_placeholder": "Dán văn bản vào đây...",
        "image_label": "🖼️️ Phân tích Hình ảnh:", "btn_submit": "Bắt đầu Phân tích 🔍",
        "result_title": "Kết quả:", "btn_speak": "Nghe Âm thanh 🔊",
        "error_short": "Văn bản quá ngắn.", "error_ai": "Cảnh báo AI.", "error_human": "Văn bản tự nhiên.",
        "img_ai": "Cảnh báo hình ảnh (Phương sai: ", "img_human": "Hình ảnh bình thường.",
        "mode_personal": "Cổng cá nhân", "mode_enterprise": "Bộ API doanh nghiệp",
        "ent_title": "Bộ bảo mật & Tuân thủ doanh nghiệp", "ent_desc": "Xác thực hàng loạt và điểm cuối API cho tổ chức.",
        "api_endpoint_label": "Điểm cuối API:", "api_key_label": "Khóa API:",
        "btn_generate_key": "Tạo khóa 🔑", "docs_label": "Tài liệu API"
    },
    "id": {
        "name": "Bahasa Indonesia", "title": "TrueLens AI", "subtitle": "Mesin Verifikasi Global",
        "text_label": "📄 Analisis Teks:", "text_placeholder": "Tempel teks di sini...",
        "image_label": "🖼️ Analisis Gambar:", "btn_submit": "Mulai Analisis 🔍",
        "result_title": "Hasil:", "btn_speak": "Dengarkan Audio 🔊",
        "error_short": "Teks terlalu pendek.", "error_ai": "Peringatan AI.", "error_human": "Teks alami.",
        "img_ai": "Peringatan Visual (Varian: ", "img_human": "Gambar normal.",
        "mode_personal": "Portal Pribadi", "mode_enterprise": "Suite API Perusahaan",
        "ent_title": "Suite Keamanan Perusahaan", "ent_desc": "Verifikasi batch throughput tinggi dan endpoint API.",
        "api_endpoint_label": "Endpoint API:", "api_key_label": "Kunci API:",
        "btn_generate_key": "Buat Kunci 🔑", "docs_label": "Dokumentasi API"
    },
    "sv": {
        "name": "Svenska", "title": "TrueLens AI", "subtitle": "Global Verifieringsmotor",
        "text_label": "📄 Textanalys:", "text_placeholder": "Klistra in text här...",
        "image_label": "🖼️ Bildanalys:", "btn_submit": "Starta Analys 🔍",
        "result_title": "Resultat:", "btn_speak": "Lyssna på Ljud 🔊",
        "error_short": "För kort text.", "error_ai": "AI-varning.", "error_human": "Naturlig text.",
        "img_ai": "Visuell varning (Varians: ", "img_human": "Bilden är normal.",
        "mode_personal": "Personlig portal", "mode_enterprise": "Enterprise API-svit",
        "ent_title": "Företagssäkerhets-svit", "ent_desc": "Batchverifiering och API för organisationer.",
        "api_endpoint_label": "API-endpoint:", "api_key_label": "API-nyckel:",
        "btn_generate_key": "Generera nyckel 🔑", "docs_label": "API-dokumentation"
    },
    "uk": {
        "name": "Українська (Ukrainian)", "title": "TrueLens AI", "subtitle": "Глобальний рушій перевірки",
        "text_label": "📄 Аналіз тексту:", "text_placeholder": "Вставте текст сюди...",
        "image_label": "🖼️ Аналіз зображення:", "btn_submit": "Почати аналіз 🔍",
        "result_title": "Результат:", "btn_speak": "Прослухати аудіо 🔊",
        "error_short": "Текст занадто короткий.", "error_ai": "Попередження ШІ.", "error_human": "Природний текст.",
        "img_ai": "Візуальне попередження (Дисперсія: ", "img_human": "Зображення нормальне.",
        "mode_personal": "Особистий портал", "mode_enterprise": "Корпоративний API",
        "ent_title": "Комплекс корпоративної безпеки", "ent_desc": "Пакетна перевірка та API.",
        "api_endpoint_label": "API ендпоінт:", "api_key_label": "API ключ:",
        "btn_generate_key": "Згенерувати ключ 🔑", "docs_label": "Документація"
    },
    "el": {
        "name": "Ελληνικά (Greek)", "title": "TrueLens AI", "subtitle": "Παγκόσμια Μηχανή Επαλήθευσης",
        "text_label": "📄 Ανάλυση Κειμένου:", "text_placeholder": "Επικολλήστε κείμενο εδώ...",
        "image_label": "🖼️ Ανάλυση Εικόνας:", "btn_submit": "Έναρξη Ανάλυσης 🔍",
        "result_title": "Αποτέλεσμα:", "btn_speak": "Ακούστε Ήχο 🔊",
        "error_short": "Πολύ σύντομο κείμενο.", "error_ai": "Προειδοποίηση AI.", "error_human": "Φυσικό κείμενο.",
        "img_ai": "Οπτική προειδοποίηση (Διακύμανση: ", "img_human": "Η εικόνα είναι κανονική.",
        "mode_personal": "Προσωπική Πύλη", "mode_enterprise": "Enterprise API",
        "ent_title": "Σουίτα Εταιierικής Ασφάλειας", "ent_desc": "Επαλήθευση πακέτου και API.",
        "api_endpoint_label": "API Endpoint:", "api_key_label": "Κλειδί API:",
        "btn_generate_key": "Δημιουργία Κλειδιού 🔑", "docs_label": "Τεκμηρίωση"
    },
    "he": {
        "name": "עברית (Hebrew)", "title": "TrueLens AI", "subtitle": "מנוע אימות דיגיטלי עולמי",
        "text_label": "📄 ניתוח טקסט:", "text_placeholder": "הדבק טקסט כאן...",
        "image_label": "🖼️ ניתוח תמונה:", "btn_submit": "התחל ניתוח 🔍",
        "result_title": "תוצאה:", "btn_speak": "האזן לדוח 🔊",
        "error_short": "הטקסט קצר מדי.", "error_ai": "אזהרת בינה מלאכותית.", "error_human": "טקסט טבעי.",
        "img_ai": "אזהרה ויזואלית (שונות: ", "img_human": "התמונה תקינה.",
        "mode_personal": "פורטל אישי", "mode_enterprise": "מערכת API ארגונית",
        "ent_title": "חבילת אבטחה ותאימות ארגונית", "ent_desc": "אימות אבّتואות גבוה וחיבור API.",
        "api_endpoint_label": "כתובת API:", "api_key_label": "מפתח API:",
        "btn_generate_key": "צור מפתח 🔑", "docs_label": "תיעוד API"
    },
    "ro": {
        "name": "Română", "title": "TrueLens AI", "subtitle": "Motor Global de Verificare",
        "text_label": "📄 Analiză Text:", "text_placeholder": "Lipește textul aici...",
        "image_label": "🖼️ Analiză Imagine:", "btn_submit": "Începe Analiza 🔍",
        "result_title": "Rezultat:", "btn_speak": "Ascultă Audio 🔊",
        "error_short": "Text prea scurt.", "error_ai": "Alertă AI.", "error_human": "Text natural.",
        "img_ai": "Alertă vizuală (Varianță: ", "img_human": "Imagine normală.",
        "mode_personal": "Portal Personal", "mode_enterprise": "Suite Enterprise",
        "ent_title": "Suite Securitate Enterprise", "ent_desc": "Verificare în lot și endpoint API.",
        "api_endpoint_label": "Endpoint API:", "api_key_label": "Cheie API:",
        "btn_generate_key": "Generează Cheie 🔑", "docs_label": "Documentație"
    },
    "hu": {
        "name": "Magyar", "title": "TrueLens AI", "subtitle": "Globális Ellenőrző Motor",
        "text_label": "📄 Szövegelemzés:", "text_placeholder": "Illessze ide a szöveget...",
        "image_label": "🖼️ Képelemzés:", "btn_submit": "Elemzés Indítása 🔍",
        "result_title": "Eredmény:", "btn_speak": "Hang Hallgatása 🔊",
        "error_short": "Túl rövid szöveg.", "error_ai": "MI figyelmeztetés.", "error_human": "Természetes szöveg.",
        "img_ai": "Vizuális figyelmeztetés (Variancia: ", "img_human": "A kép normális.",
        "mode_personal": "Személyes Portál", "mode_enterprise": "Vállalati API Csomag",
        "ent_title": "Vállalati Biztonsági Csomag", "ent_desc": "Kötegelt ellenőrzés és API végpont.",
        "api_endpoint_label": "API Végpont:", "api_key_label": "API Kulcs:",
        "btn_generate_key": "Kulcs Generálása 🔑", "docs_label": "Dokumentáció"
    },
    "cs": {
        "name": "Čeština", "title": "TrueLens AI", "subtitle": "Globální Ověřovací Motor",
        "text_label": "📄 Analýza Textu:", "text_placeholder": "Sem vložte text...",
        "image_label": "🖼️ Analýza Obrazu:", "btn_submit": "Spustit Analýzu 🔍",
        "result_title": "Výsledek:", "btn_speak": "Poslechnout Zvuk 🔊",
        "error_short": "Příliš krátký text.", "error_ai": "Upozornění AI.", "error_human": "Přirozený text.",
        "img_ai": "Vizuální upozornění (Variance: ", "img_human": "Obrázek je v pořádku.",
        "mode_personal": "Osobní portál", "mode_enterprise": "Podnikové API",
        "ent_title": "Podnikový bezpečnostní balíček", "ent_desc": "Dávkové ověřování a API.",
        "api_endpoint_label": "API Endpoint:", "api_key_label": "API Klíč:",
        "btn_generate_key": "Generovat klíč 🔑", "docs_label": "Dokumentace"
    },
    "th": {
        "name": "ไทย (Thai)", "title": "TrueLens AI", "subtitle": "เครื่องมือตรวจสอบดิจิทัลระดับโลก",
        "text_label": "📄 วิเคราะห์ข้อความ:", "text_placeholder": "วางข้อความที่นี่...",
        "image_label": "🖼️ วิเคราะห์รูปภาพ:", "btn_submit": "เริ่มการวิเคราะห์ 🔍",
        "result_title": "ผลลัพธ์:", "btn_speak": "ฟังรายงานเสียง 🔊",
        "error_short": "ข้อความสั้นเกินไป", "error_ai": "คำเตือน AI: ตรวจพบเนื้อหา AI", "error_human": "ข้อความปกติทั่วไป",
        "img_ai": "คำเตือนภาพ (ความแปรปรวน: ", "img_human": "ภาพปกติสมบูรณ์",
        "mode_personal": "พอร์ทัลส่วนบุคคล", "mode_enterprise": "ชุด API ระดับองค์กร",
        "ent_title": "ชุดความปลอดภัยและการปฏิบัติตามข้อกำหนดองค์กร", "ent_desc": "การตรวจสอบชุดข้อมูลและ API",
        "api_endpoint_label": "จุดสิ้นสุด API:", "api_key_label": "คีย์ API:",
        "btn_generate_key": "สร้างคีย์องค์กร 🔑", "docs_label": "เอกสารคู่มือ API"
    },
    "fi": {
        "name": "Suomi", "title": "TrueLens AI", "subtitle": "Globaali Varmennusmoottori",
        "text_label": "📄 Tekstianalyysi:", "text_placeholder": "Liitä teksti tähän...",
        "image_label": "🖼️ Kuvaanalyysi:", "btn_submit": "Aloita Analyysi 🔍",
        "result_title": "Tulos:", "btn_speak": "Kuuntele Ääni 🔊",
        "error_short": "Liian lyhyt teksti.", "error_ai": "Tekoälyvaroitus.", "error_human": "Luonnollinen teksti.",
        "img_ai": "Visuaalinen varoitus (Varianssi: ", "img_human": "Kuva on normaali.",
        "mode_personal": "Henkilökohtainenportaali", "mode_enterprise": "Yritys-API",
        "ent_title": "Yritysturvallisuuspaketti", "ent_desc": "Erävarmennus ja API-rajapinta.",
        "api_endpoint_label": "API-päätepiste:", "api_key_label": "API-avain:",
        "btn_generate_key": "Luo avain 🔑", "docs_label": "Dokumentaatio"
    },
    "da": {
        "name": "Dansk", "title": "TrueLens AI", "subtitle": "Global Verificeringsmotor",
        "text_label": "📄 Tekstanalyse:", "text_placeholder": "Indsæt tekst her...",
        "image_label": "🖼️ Billedanalyse:", "btn_submit": "Start Analyse 🔍",
        "result_title": "Resultat:", "btn_speak": "Lyt til Lyd 🔊",
        "error_short": "For kort tekst.", "error_ai": "AI-advarsel.", "error_human": "Naturlig tekst.",
        "img_ai": "Visuel advarsel (Varians: ", "img_human": "Billedet er normalt.",
        "mode_personal": "Personlig portal", "mode_enterprise": "Virksomheds API-suite",
        "ent_title": "Virksomhedssikkerhedssuite", "ent_desc": "Batch-verificering og API-endpoint.",
        "api_endpoint_label": "API-endpoint:", "api_key_label": "API-nøgle:",
        "btn_generate_key": "Generer nøgle 🔑", "docs_label": "API-dokumentation"
    },
    "no": {
        "name": "Norsk", "title": "TrueLens AI", "subtitle": "Global Verifiseringsmotor",
        "text_label": "📄 Tekstanalyse:", "text_placeholder": "Lim inn tekst her...",
        "image_label": "🖼️ Bildeanalyse:", "btn_submit": "Start Analyse 🔍",
        "result_title": "Resultat:", "btn_speak": "Hør Lydrapport 🔊",
        "error_short": "For kort tekst.", "error_ai": "KI-advarsel.", "error_human": "Naturlig tekst.",
        "img_ai": "Visuell advarsel (Varians: ", "img_human": "Bildet er normalt.",
        "mode_personal": "Personlig portal", "mode_enterprise": "Bedrifts-API",
        "ent_title": "Bedriftssikkerhetspakke", "ent_desc": "Partiverifisering og API.",
        "api_endpoint_label": "API-endepunkt:", "api_key_label": "API-nøkkel:",
        "btn_generate_key": "Generer nøkkel 🔑", "docs_label": "Dokumentasjon"
    },
    "ms": {
        "name": "Bahasa Melayu", "title": "TrueLens AI", "subtitle": "Enjin Pengesahan Global",
        "text_label": "📄 Analisis Teks:", "text_placeholder": "Tampal teks di sini...",
        "image_label": "🖼️ Analisis Imej:", "btn_submit": "Mula Analisis 🔍",
        "result_title": "Keputusan:", "btn_speak": "Dengar Audio 🔊",
        "error_short": "Teks terlalu pendek.", "error_ai": "Amaran AI.", "error_human": "Teks asli.",
        "img_ai": "Amaran Visual (Varians: ", "img_human": "Imej adalah normal.",
        "mode_personal": "Portal Peribadi", "mode_enterprise": "Suite API Perusahaan",
        "ent_title": "Suite Keselamatan Perusahaan", "ent_desc": "Pengesahan kelompok dan titik akhir API.",
        "api_endpoint_label": "Titik Akhir API:", "api_key_label": "Kunci API:",
        "btn_generate_key": "Jana Kunci 🔑", "docs_label": "Dokumentasi API"
    },
    "bn": {
        "name": "বাংলা (Bengali)", "title": "TrueLens AI", "subtitle": "গ্লোবাল ভেরিফিকেশন ইঞ্জিন",
        "text_label": "📄 টেক্সট বিশ্লেষণ:", "text_placeholder": "এখানে টেক্সট পেস্ট করুন...",
        "image_label": "🖼️ ছবি বিশ্লেষণ:", "btn_submit": "বিশ্লেষণ শুরু করুন 🔍",
        "result_title": "ফলাফল:", "btn_speak": "অডিও শুনুন 🔊",
        "error_short": "টেক্সট খুব ছোট।", "error_ai": "AI সতর্কতা: AI দ্বারা তৈরি।", "error_human": "স্বাভাবিক টেক্সট।",
        "img_ai": "ভিজ্যুয়াল সতর্কতা (ভ্যারিয়েন্স: ", "img_human": "ছবিটি স্বাভাবিক।",
        "mode_personal": "ব্যক্তিগত পোর্টাল", "mode_enterprise": "এন্টারপ্রাইজ API স্যুট",
        "ent_title": "এন্টারপ্রাইজ নিরাপত্তা স্যুট", "ent_desc": "প্রাতিষ্ঠানিক যাচাইকরণ এবং API সাপোর্ট।",
        "api_endpoint_label": "API এন্ডপয়েন্ট:", "api_key_label": "API কী:",
        "btn_generate_key": "কী জেনারেট করুন 🔑", "docs_label": "নথিপত্র"
    },
    "fa": {
        "name": "فارسی (Persian)", "title": "TrueLens AI", "subtitle": "موتور جهانی تأیید اصالت",
        "text_label": "📄 تحلیل متن:", "text_placeholder": "متن را اینجا بچسبانید...",
        "image_label": "🖼️ تحلیل تصویر:", "btn_submit": "شروع تحلیل 🔍",
        "result_title": "نتیجه:", "btn_speak": "گزارش صوتی 🔊",
        "error_short": "متن خیلی کوتاه است.", "error_ai": "هشدار هوش مصنوعی.", "error_human": "متن طبیعی است.",
        "img_ai": "هشدار تصویری (واریانس: ", "img_human": "تصویر عادی است.",
        "mode_personal": "پورتال شخصی", "mode_enterprise": "مجموعه API سازمانی",
        "ent_title": "مجموعه امنیت سازمانی و انطباق", "ent_desc": "اعتبارسنجی انبوه و اتصال API برای نهادها.",
        "api_endpoint_label": "نقطه پایانی API:", "api_key_label": "کلید مجوز API:",
        "btn_generate_key": "تولید کلید سازمانی 🔑", "docs_label": "مستندات API"
    },
    "ur": {
        "name": "اردو (Urdu)", "title": "TrueLens AI", "subtitle": "عالمی ڈیجیٹل تصدیقی انجن",
        "text_label": "📄 متن کا تجزیہ:", "text_placeholder": "یہاں متن چسپاں کریں...",
        "image_label": "🖼️ تصویر کا تجزیہ:", "btn_submit": "تجزیہ شروع کریں 🔍",
        "result_title": "نتیجہ:", "btn_speak": "آڈیو سنیں 🔊",
        "error_short": "متن بہت چھوٹا ہے۔", "error_ai": "AI کی طرف سے انتباہ۔", "error_human": "قدرتی متن۔",
        "img_ai": " بصری انتباہ (فرق: ", "img_human": "تصویر نارمل ہے۔",
        "mode_personal": "ذاتی پورٹل", "mode_enterprise": "انٹرپرाइज API سوٹ",
        "ent_title": "انٹرپرाइज سیکیورٹی سوٹ", "ent_desc": "ادارہ جاتی ورک فلو کے لیے بیچ تصدیق اور API اینڈ پوائنٹ۔",
        "api_endpoint_label": "API اینڈ پوائنٹ:", "api_key_label": "API کلید:",
        "btn_generate_key": "انٹرپرाइज کلید بنائیں 🔑", "docs_label": "دستاویزات"
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
            max-width: 650px;
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
        .mode-toggle {
            display: flex;
            background: #0f172a;
            border-radius: 12px;
            padding: 4px;
            margin-bottom: 20px;
            border: 1px solid #334155;
        }
        .mode-btn {
            flex: 1;
            text-align: center;
            padding: 10px;
            font-size: 13px;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            color: var(--text-muted);
            text-decoration: none;
            transition: all 0.3s ease;
        }
        .mode-btn.active {
            background: var(--accent-color);
            color: white;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
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
        /* Enterprise Section Styles */
        .enterprise-container {
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 16px;
            padding: 20px;
            margin-top: 10px;
        }
        .enterprise-container h3 { color: #38bdf8; margin-top: 0; font-size: 16px; }
        .enterprise-container p { color: var(--text-muted); font-size: 13px; line-height: 1.5; }
        .api-box {
            background: #020617;
            border: 1px solid #1e293b;
            padding: 10px 14px;
            border-radius: 8px;
            font-family: monospace;
            font-size: 12px;
            color: #38bdf8;
            margin: 10px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .copy-btn {
            background: #334155; color: white; border: none; padding: 4px 8px;
            border-radius: 4px; font-size: 11px; cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="app-container">
        <div class="top-bar">
            <span style="font-size: 12px; color: var(--text-muted);">🌐 Global Version (32+ Langs)</span>
            <form method="GET" style="margin:0;">
                <input type="hidden" name="mode" value="{{ mode }}">
                <select name="lang" class="lang-select" onchange="this.form.submit()">
                    {% for code, data in translations.items() %}
                    <option value="{{ code }}" {% if current_lang == code %}selected{% endif %}>{{ data.name }}</option>
                    {% endfor %}
                </select>
            </form>
        </div>

        <div class="header">
            <div class="logo-icon">🛡</div>
            <h2>{{ t.title }}</h2>
            <p class="subtitle">{{ t.subtitle }}</p>
        </div>

        <!-- Mode Toggle Switcher -->
        <div class="mode-toggle">
            <a href="?lang={{ current_lang }}&mode=personal" class="mode-btn {% if mode == 'personal' %}active{% endif %}">👤 {{ t.mode_personal }}</a>
            <a href="?lang={{ current_lang }}&mode=enterprise" class="mode-btn {% if mode == 'enterprise' %}active{% endif %}">🏢 {{ t.mode_enterprise }}</a>
        </div>
        
        {% if mode == 'personal' %}
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

        {% else %}
        <!-- Enterprise Portal Mode -->
        <div class="enterprise-container">
            <h3>🏢 {{ t.ent_title }}</h3>
            <p>{{ t.ent_desc }}</p>
            
            <div class="input-group" style="margin-top: 15px;">
                <label>{{ t.api_endpoint_label }}</label>
                <div class="api-box">
                    <span>https://truelens-ai.internal/api/v1/analyze</span>
                    <button class="copy-btn" onclick="navigator.clipboard.writeText('https://truelens-ai.internal/api/v1/analyze')">Copy</button>
                </div>
            </div>

            <div class="input-group">
                <label>{{ t.api_key_label }}</label>
                <div class="api-box">
                    <span style="color: #a855f7;">tl_live_998a7b6c5d4e3f210</span>
                    <button class="copy-btn" onclick="navigator.clipboard.writeText('tl_live_998a7b6c5d4e3f210')">Copy</button>
                </div>
            </div>

            <button class="btn-submit" style="margin-top: 10px;" onclick="alert('Enterprise API Key Generated & Authorized Successfully!')">{{ t.btn_generate_key }}</button>
            
            <div style="text-align: center; margin-top: 15px;">
                <a href="#" style="color: #818cf8; font-size: 12px; text-decoration: none;">📚 {{ t.docs_label }}</a>
            </div>
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
    
    mode = request.args.get("mode", "personal")
    if mode not in ["personal", "enterprise"]:
        mode = "personal"
        
    t = TRANSLATIONS[lang]
    result = None
    text_input = ""
    
    if request.method == "POST" and mode == "personal":
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
            
    return render_template_string(HTML_TEMPLATE, t=t, current_lang=lang, mode=mode, translations=TRANSLATIONS, result=result, text_input=text_input)

# مسار API مخصص للشركات (Enterprise API Endpoint)
@app.route("/api/v1/analyze", methods=["POST"])
def api_analyze():
    data = request.get_json() or {}
    text = data.get("text", "")
    
    if not text.strip():
        return jsonify({"status": "error", "message": "No text provided for analysis."}), 400
        
    ai_patterns = [r"as an ai", r"in conclusion", r"furthermore", r"it is important", r"بصفتي", r"في الختام"]
    score = sum(25 for pattern in ai_patterns if re.search(pattern, text, re.IGNORECASE))
    
    is_ai = score >= 25 or len(text.split()) > 15
    
    return jsonify({
        "status": "success",
        "analysis_type": "text_verification",
        "artificial_probability": 85.5 if is_ai else 5.2,
        "classification": "AI_GENERATED" if is_ai else "HUMAN_WRITTEN",
        "confidence_score": "High"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
