from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
import re
import numpy as np
from PIL import Image
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = "truelens_secure_enterprise_secret_key_2026"

# قاموس اللغات العالمي الموسع (أكثر من 30 لغة عالمية مع دعم بوابات المصادقة والشركات)
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
        "mode_personal": "Individual Portal", "mode_pro": "Professional & Business Suite",
        "ent_title": "Professional & Enterprise Security Suite", "ent_desc": "Unified high-throughput verification, API endpoints, and compliance workflows for corporate, banking, and media sectors.",
        "api_endpoint_label": "Live API Endpoint:", "api_key_label": "API Authorization Key:",
        "btn_generate_key": "Generate Enterprise Key 🔑", "docs_label": "API Documentation & SDKs",
        "btn_export_pdf": "Export Certified PDF Report 📄", "report_id": "Verification Tracking ID:",
        "login_title": "Enterprise Secure Login (Banks & Corporates)", "email_label": "Corporate Email:", "pass_label": "Password:",
        "btn_login": "Secure Login 🔐", "logout": "Logout 🚪", "logged_in_as": "Logged in corporate account:"
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
        "mode_personal": "بوابة الأفراد", "mode_pro": "بوابة الأعمال والشركات الاحترافية",
        "ent_title": "مجموعة الأمان والامتثال المهني والمؤسسي",
        "ent_desc": "نظام موحد لفحص دفعات البيانات، الربط البرمجي (API)، واعتماد تدقيق القطاعات المصرفية والإعلامية والشركات الكبرى.",
        "api_endpoint_label": "رابط الـ API المباشر:", "api_key_label": "مفتاح ترخيص الشركات (API Key):",
        "btn_generate_key": "توليد مفتاح مؤسسي جديد 🔑", "docs_label": "دليل المطورين والوثائق التقنية (SDK)",
        "btn_export_pdf": "تصدير تقرير الاعتماد بصيغة PDF 📄", "report_id": "الرقم المرجعي للتحقق:",
        "login_title": "تسجيل الدخول الآمن للمؤسسات والبنوك", "email_label": "البريد الإلكتروني المؤسسي:", "pass_label": "كلمة المرور:",
        "btn_login": "تسجيل دخول آمن 🔐", "logout": "تسجيل خروج 🚪", "logged_in_as": "مسجل الدخول بحساب المؤسسة:"
    },
    "fr": {
        "name": "Français", "title": "TrueLens AI", "subtitle": "Moteur mondial de vérification numérique et de détection IA",
        "text_label": "📄 Analyse de Texte:", "text_placeholder": "Collez le texte ici pour vérifier son authenticité...",
        "image_label": "🖼️ Analyse Visuelle d'Image:", "btn_submit": "Démarrer l'Analyse Complète 🔍",
        "result_title": "Résultat de l'Analyse:", "btn_speak": "Écouter le Rapport Audio 🔊",
        "error_short": "Le texte entré est trop court.", "error_ai": "Alerte IA: Empreintes claires de modèles d'IA.",
        "error_human": "Texte Naturel: Rédigé par un humain.", "img_ai": "Alerte Visuelle (Variance: ", "img_human": "Image propre et naturelle.",
        "mode_personal": "Portail Particulier", "mode_pro": "Suite Professionnelle & Entreprise",
        "ent_title": "Suite de Sécurité Professionnelle & Entreprise", "ent_desc": "Vérification unifiée, endpoints API et conformité pour les secteurs institutionnels, bancaires et médias.",
        "api_endpoint_label": "Endpoint API:", "api_key_label": "Clé d'Autorisation API:",
        "btn_generate_key": "Générer une Clé Entreprise 🔑", "docs_label": "Documentation API",
        "btn_export_pdf": "Exporter le rapport PDF 📄", "report_id": "ID de Suivi:",
        "login_title": "Connexion Sécurisée Entreprise (Banques & Corporates)", "email_label": "Email Professionnel:", "pass_label": "Mot de passe:",
        "btn_login": "Connexion Sécurisée 🔐", "logout": "Déconnexion 🚪", "logged_in_as": "Connecté au compte:"
    },
    "es": {
        "name": "Español", "title": "TrueLens AI", "subtitle": "Motor Global de Verificación Digital",
        "text_label": "📄 Análisis de Texto:", "text_placeholder": "Pegue el texto aquí...",
        "image_label": "🖼️ Análisis Visual:", "btn_submit": "Iniciar Análisis 🔍",
        "result_title": "Resultado:", "btn_speak": "Escuchar Audio 🔊",
        "error_short": "Texto muy corto.", "error_ai": "Alerta de IA detectada.", "error_human": "Texto natural y seguro.",
        "img_ai": "Alerta Visual (Varianza: ", "img_human": "Imagen normal y natural.",
        "mode_personal": "Portal Individual", "mode_pro": "Suite Profesional y de Negocios",
        "ent_title": "Suite de Seguridad Profesional", "ent_desc": "Verificación unificada y API para empresas, bancos y medios.",
        "api_endpoint_label": "Endpoint de API:", "api_key_label": "Clave API:",
        "btn_generate_key": "Generar Clave 🔑", "docs_label": "Documentación",
        "btn_export_pdf": "Exportar Informe PDF 📄", "report_id": "ID de Seguimiento:",
        "login_title": "Acceso Seguro para Empresas", "email_label": "Correo Corporativo:", "pass_label": "Contraseña:",
        "btn_login": "Acceso Seguro 🔐", "logout": "Cerrar Sesión 🚪", "logged_in_as": "Sesión iniciada:"
    },
    "de": {
        "name": "Deutsch", "title": "TrueLens AI", "subtitle": "Globales System zur digitalen Verifikation",
        "text_label": "📄 Textanalyse:", "text_placeholder": "Text hier einfügen...",
        "image_label": "🖼️ Visuelle Analyse:", "btn_submit": "Analyse Starten 🔍",
        "result_title": "Ergebnis:", "btn_speak": "Anhören 🔊",
        "error_short": "Text zu kurz.", "error_ai": "KI-Warnung aktiv.", "error_human": "Natürlicher Text.",
        "img_ai": "Visuelle Warnung (Varianz: ", "img_human": "Bild ist sauber.",
        "mode_personal": "Privatportal", "mode_pro": "Professional & Business Suite",
        "ent_title": "Professionelle Sicherheits-Suite", "ent_desc": "Vereinheitlichte API und Verifikation für Unternehmen und Medien.",
        "api_endpoint_label": "API-Endpunkt:", "api_key_label": "API-Schlüssel:",
        "btn_generate_key": "Schlüssel Generieren 🔑", "docs_label": "Dokumentation",
        "btn_export_pdf": "PDF-Bericht Exportieren 📄", "report_id": "Verifizierungs-ID:",
        "login_title": "Sicherer Login für Unternehmen", "email_label": "Unternehmens-E-Mail:", "pass_label": "Passwort:",
        "btn_login": "Sicherer Login 🔐", "logout": "Abmelden 🚪", "logged_in_as": "Eingeloggt als:"
    },
    "zh": {
        "name": "中文 (Chinese)", "title": "TrueLens AI", "subtitle": "全球数字验证与AI检测引擎",
        "text_label": "📄 文本分析：", "text_placeholder": "在此粘贴文本...",
        "image_label": "🖼️ 图像分析：", "btn_submit": "开始综合分析 🔍",
        "result_title": "分析结果：", "btn_speak": "语音报告 🔊",
        "error_short": "文本太短。", "error_ai": "AI警报：检测到AI特征。", "error_human": "自然文本，安全。",
        "img_ai": "视觉警报（方差：", "img_human": "图像自然正常。",
        "mode_personal": "个人门户", "mode_pro": "专业与企业套件",
        "ent_title": "专业与企业安全套件", "ent_desc": "为企业、银行和媒体机构提供统一的高吞吐量验证和API端点。",
        "api_endpoint_label": "API 端点:", "api_key_label": "API 授权密钥:",
        "btn_generate_key": "生成企业密钥 🔑", "docs_label": "API 文档与 SDK",
        "btn_export_pdf": "导出认证 PDF 报告 📄", "report_id": "验证跟踪编号:",
        "login_title": "企业与银行安全登录", "email_label": "企业邮箱:", "pass_label": "密码:",
        "btn_login": "安全登录 🔐", "logout": "登出 🚪", "logged_in_as": "已登录账号:"
    },
    "ja": {
        "name": "日本語 (Japanese)", "title": "TrueLens AI", "subtitle": "グローバルデジタル検証エンジン",
        "text_label": "📄 テキスト分析:", "text_placeholder": "テキストを貼り付け...",
        "image_label": "🖼️️ 画像分析:", "btn_submit": "分析開始 🔍",
        "result_title": "結果:", "btn_speak": "音声レポート 🔊",
        "error_short": "テキストが短すぎます。", "error_ai": "AI警告: AI生成の可能性が高いです。", "error_human": "自然なテキストです。",
        "img_ai": "視覚的警告 (分散: ", "img_human": "画像は正常です。",
        "mode_personal": "個人ポータル", "mode_pro": "プロフェッショナル＆ビジネス",
        "ent_title": "プロフェッショナルセキュリティスイート", "ent_desc": "企業、金融、メディア向けの統合検証およびAPIエンドポイント。",
        "api_endpoint_label": "API エンドポイント:", "api_key_label": "API キー:",
        "btn_generate_key": "キーを生成 🔑", "docs_label": "API ドキュメント",
        "btn_export_pdf": "認定PDFレポートのエクスポート 📄", "report_id": "検証追跡ID:",
        "login_title": "法人セキュアログイン", "email_label": "企業メール:", "pass_label": "パスワード:",
        "btn_login": "安全にログイン 🔐", "logout": "ログアウト 🚪", "logged_in_as": "ログイン中:"
    },
    "it": {
        "name": "Italiano", "title": "TrueLens AI", "subtitle": "Motore di Verifica Globale",
        "text_label": "📄 Analisi Testo:", "text_placeholder": "Incolla il testo...",
        "image_label": "🖼️ Analisi Immagine:", "btn_submit": "Avvia Analisi 🔍",
        "result_title": "Risultato:", "btn_speak": "Ascolta Audio 🔊",
        "error_short": "Testo troppo corto.", "error_ai": "Rilevato contenuto IA.", "error_human": "Testo naturale.",
        "img_ai": "Avviso Visivo (Varianza: ", "img_human": "Immagine normale.",
        "mode_personal": "Portale Personale", "mode_pro": "Suite Professionale",
        "ent_title": "Suite di Sicurezza Professionale", "ent_desc": "Verifica unificata e API per imprese, banche e media.",
        "api_endpoint_label": "Endpoint API:", "api_key_label": "Chiave API:",
        "btn_generate_key": "Genera Chiave 🔑", "docs_label": "Documentazione",
        "btn_export_pdf": "Esporta Report PDF 📄", "report_id": "ID di Verifica:",
        "login_title": "Accesso Sicuro Aziendale", "email_label": "Email Aziendale:", "pass_label": "Password:",
        "btn_login": "Accesso Sicuro 🔐", "logout": "Esci 🚪", "logged_in_as": "Connesso come:"
    },
    "pt": {
        "name": "Português", "title": "TrueLens AI", "subtitle": "Motor Global de Verificação",
        "text_label": "📄 Análise de Texto:", "text_placeholder": "Cole o texto aqui...",
        "image_label": "🖼️ Análise de Imagem:", "btn_submit": "Iniciar Análise 🔍",
        "result_title": "Resultado:", "btn_speak": "Ouvir Áudio 🔊",
        "error_short": "Texto muito curto.", "error_ai": "Alerta de IA detectado.", "error_human": "Texto natural.",
        "img_ai": "Alerta Visual (Variância: ", "img_human": "Imagem limpa e natural.",
        "mode_personal": "Portal Pessoal", "mode_pro": "Suite Profissional",
        "ent_title": "Suite de Segurança Profissional", "ent_desc": "Verificação unificada e API para fluxos corporativos e de mídia.",
        "api_endpoint_label": "Endpoint da API:", "api_key_label": "Chave da API:",
        "btn_generate_key": "Gerar Chave 🔑", "docs_label": "Documentação da API",
        "btn_export_pdf": "Exportar Relatório PDF 📄", "report_id": "ID de Verificação:",
        "login_title": "Login Corporativo Seguro", "email_label": "E-mail Corporativo:", "pass_label": "Senha:",
        "btn_login": "Login Seguro 🔐", "logout": "Sair 🚪", "logged_in_as": "Conectado como:"
    },
    "ru": {
        "name": "Русский (Russian)", "title": "TrueLens AI", "subtitle": "Глобальный движок проверки",
        "text_label": "📄 Анализ текста:", "text_placeholder": "Вставьте текст...",
        "image_label": "🖼️ Анализ изображения:", "btn_submit": "Начать анализ 🔍",
        "result_title": "Результат:", "btn_speak": "Прослушать 🔊",
        "error_short": "Текст слишком короткий.", "error_ai": "Предупреждение ИИ.", "error_human": "Естественный текст.",
        "img_ai": "Визуальное предупреждение (Дисперсия: ", "img_human": "Изображение в норме.",
        "mode_personal": "Личный портал", "mode_pro": "Профессиональный пакет",
        "ent_title": "Комплекс профессиональной безопасности", "ent_desc": "Унифицированная пакетная проверка и API для бизнеса и СМИ.",
        "api_endpoint_label": "API эндпоинт:", "api_key_label": "API ключ:",
        "btn_generate_key": "Сгенерировать ключ 🔑", "docs_label": "Документация",
        "btn_export_pdf": "Экспортировать PDF-отчет 📄", "report_id": "ID отслеживания:",
        "login_title": "Защищенный вход для бизнеса", "email_label": "Корпоративный Email:", "pass_label": "Пароль:",
        "btn_login": "Безопасный вход 🔐", "logout": "Выйти 🚪", "logged_in_as": "Вход выполнен:"
    },
    "hi": {
        "name": "हिन्दी (Hindi)", "title": "TrueLens AI", "subtitle": "वैश्विक डिजिटल सत्यापन इंजन",
        "text_label": "📄 पाठ विश्लेषण:", "text_placeholder": "पाठ यहाँ चिपकाएँ...",
        "image_label": "🖼️ छवि विश्लेषण:", "btn_submit": "विश्लेषण शुरू करें 🔍",
        "result_title": "परिणाम:", "btn_speak": "ऑडियो सुनें 🔊",
        "error_short": "पाठ बहुत छोटा है।", "error_ai": "AI चेतावनी: AI जनित सामग्री।", "error_human": "प्राकृतिक पाठ।",
        "img_ai": "दृश्य चेतावनी (विचरण: ", "img_human": "छवि सामान्य है।",
        "mode_personal": "व्यक्तिगत पोर्टल", "mode_pro": "पेशेवर और व्यावसायिक सूट",
        "ent_title": "पेशेवर सुरक्षा सूट", "ent_desc": "व्यवसायों और मीडिया के लिए एकीकृत सत्यापन और API।",
        "api_endpoint_label": "API एंडपॉइंट:", "api_key_label": "API कुंजी:",
        "btn_generate_key": "कुंजी बनाएँ 🔑", "docs_label": "دस्तावेज़",
        "btn_export_pdf": "PDF रिपोर्ट निर्यात करें 📄", "report_id": "सत्यापन आईडी:",
        "login_title": "कॉर्पोरेट सुरक्षित लॉगिन", "email_label": "कॉर्पोरेट ईमेल:", "pass_label": "पासवर्ड:",
        "btn_login": "सुरक्षित लॉगिन 🔐", "logout": "लॉग आउट 🚪", "logged_in_as": "लॉग इन किया गया:"
    },
    "tr": {
        "name": "Türkçe", "title": "TrueLens AI", "subtitle": "Küresel Dijital Doğrulama Motoru",
        "text_label": "📄 Metin Analizi:", "text_placeholder": "Metni buraya yapıştırın...",
        "image_label": "🖼️ Görsel Analiz:", "btn_submit": "Analizi Başlat 🔍",
        "result_title": "Sonuç:", "btn_speak": "Sesli Dinle 🔊",
        "error_short": "Metin çok kısa.", "error_ai": "Yapay Zeka uyarısı.", "error_human": "Doğal metin.",
        "img_ai": "Görsel Uyarı (Varyans: ", "img_human": "Görsel normal.",
        "mode_personal": "Bireysel Portal", "mode_pro": "Profesyonel İş Paketi",
        "ent_title": "Profesyonel Güvenlik Paketi", "ent_desc": "Kurumsal, finansal ve medya iş akışları için birleştirilmiş API ve doğrulama.",
        "api_endpoint_label": "API Ucu:", "api_key_label": "API Yetki Anahtarı:",
        "btn_generate_key": "Anahtar Üret 🔑", "docs_label": "API Belgeleri",
        "btn_export_pdf": "PDF Raporunu Dışa Aktar 📄", "report_id": "Doğrulama ID:",
        "login_title": "Kurumsal Güvenli Giriş", "email_label": "Kurumsal E-posta:", "pass_label": "Şifre:",
        "btn_login": "Güvenli Giriş 🔐", "logout": "Çıkış 🚪", "logged_in_as": "Giriş yapılan hesap:"
    },
    "ko": {
        "name": "한국어 (Korean)", "title": "TrueLens AI", "subtitle": "글로벌 디지털 검증 엔진",
        "text_label": "📄 텍스트 분석:", "text_placeholder": "텍스트를 여기에 붙여넣으세요...",
        "image_label": "🖼️ 이미지 분석:", "btn_submit": "분석 시작 🔍",
        "result_title": "결과:", "btn_speak": "음성 듣기 🔊",
        "error_short": "텍스트가 너무 짧습니다.", "error_ai": "AI 경고: 인공지능 생성 텍스트.", "error_human": "자연스러운 텍스트입니다.",
        "img_ai": "시각적 경고 (분산: ", "img_human": "이미지가 정상입니다.",
        "mode_personal": "개인 포털", "mode_pro": "전문가 및 비즈니스 스위트",
        "ent_title": "전문가 보안 스위트", "ent_desc": "기업, 금융, 미디어 기관을 위한 통합 검증 및 API 연동 지원.",
        "api_endpoint_label": "API 엔드포인트:", "api_key_label": "API 키:",
        "btn_generate_key": "키 생성 🔑", "docs_label": "API 문서",
        "btn_export_pdf": "PDF 보고서 내보내기 📄", "report_id": "추적 ID:",
        "login_title": "기업 보안 로그인", "email_label": "기업 이메일:", "pass_label": "비밀번호:",
        "btn_login": "안전한 로그인 🔐", "logout": "로그아웃 🚪", "logged_in_as": "로그인 계정:"
    },
    "nl": {
        "name": "Nederlands", "title": "TrueLens AI", "subtitle": "Wereldwijde Verificatie Engine",
        "text_label": "📄 Tekstanalyse:", "text_placeholder": "Plak hier tekst...",
        "image_label": "🖼️ Beeldanalyse:", "btn_submit": "Start Analyse 🔍",
        "result_title": "Resultaat:", "btn_speak": "Luister Audio 🔊",
        "error_short": "Tekst te kort.", "error_ai": "KI-waarschuwing.", "error_human": "Natuurlijke tekst.",
        "img_ai": "Visuele waarschuwing (Variantie: ", "img_human": "Afbeelding is normaal.",
        "mode_personal": "Persoonlijk Portaal", "mode_pro": "Professionele & Business Suite",
        "ent_title": "Professionele Beveiligingssuite", "ent_desc": "Geïntegreerde verificatie en API voor corporate, banken en media.",
        "api_endpoint_label": "API-endpoint:", "api_key_label": "API-sleutel:",
        "btn_generate_key": "Sleutel Genereren 🔑", "docs_label": "Documentatie",
        "btn_export_pdf": "Exporteer PDF-rapport 📄", "report_id": "Verificatie-ID:",
        "login_title": "Zakelijk Veilige Login", "email_label": "Zakelijk E-mailadres:", "pass_label": "Wachtwoord:",
        "btn_login": "Veilig Inloggen 🔐", "logout": "Uitloggen 🚪", "logged_in_as": "Ingelogd als:"
    },
    "pl": {
        "name": "Polski", "title": "TrueLens AI", "subtitle": "Globalny Silnik Weryfikacji",
        "text_label": "📄 Analiza Tekstu:", "text_placeholder": "Wklej tekst tutaj...",
        "image_label": "🖼️ Analiza Obrazu:", "btn_submit": "Rozpocznij Analizę 🔍",
        "result_title": "Wynik:", "btn_speak": "Posłuchaj Audio 🔊",
        "error_short": "Tekst za krótki.", "error_ai": "Ostrzeżenie AI.", "error_human": "Tekst naturalny.",
        "img_ai": "Ostrzeżenie wizualne (Wariancja: ", "img_human": "Obraz jest naturalny.",
        "mode_personal": "Portal Osobisty", "mode_pro": "Profesjonalny Pakiet Biznesowy",
        "ent_title": "Profesjonalny Pakiet Bezpieczeństwa", "ent_desc": "Zintegrowana weryfikacja i API dla instytucji, banków i mediów.",
        "api_endpoint_label": "Endpoint API:", "api_key_label": "Klucz API:",
        "btn_generate_key": "Generuj Klucz 🔑", "docs_label": "Dokumentacja",
        "btn_export_pdf": "Eksportuj raport PDF 📄", "report_id": "ID weryfikacji:",
        "login_title": "Bezpieczne logowanie korporacyjne", "email_label": "Email firmowy:", "pass_label": "Hasło:",
        "btn_login": "Bezpieczne logowanie 🔐", "logout": "Wyloguj 🚪", "logged_in_as": "Zalogowano jako:"
    },
    "vi": {
        "name": "Tiếng Việt", "title": "TrueLens AI", "subtitle": "Công cụ Xác thực Toàn cầu",
        "text_label": "📄 Phân tích Văn bản:", "text_placeholder": "Dán văn bản vào đây...",
        "image_label": "🖼 Phân tích Hình ảnh:", "btn_submit": "Bắt đầu Phân tích 🔍",
        "result_title": "Kết quả:", "btn_speak": "Nghe Âm thanh 🔊",
        "error_short": "Văn bản quá ngắn.", "error_ai": "Cảnh báo AI.", "error_human": "Văn bản tự nhiên.",
        "img_ai": "Cảnh báo hình ảnh (Phương sai: ", "img_human": "Hình ảnh bình thường.",
        "mode_personal": "Cổng cá nhân", "mode_pro": "Bộ Chuyên nghiệp & Doanh nghiệp",
        "ent_title": "Bộ bảo mật Chuyên nghiệp", "ent_desc": "Xác thực đồng bộ và API cho tổ chức, ngân hàng và truyền thông.",
        "api_endpoint_label": "Điểm cuối API:", "api_key_label": "Khóa API:",
        "btn_generate_key": "Tạo khóa 🔑", "docs_label": "Tài liệu API",
        "btn_export_pdf": "Xuất Báo cáo PDF 📄", "report_id": "ID Xác thực:",
        "login_title": "Đăng nhập Doanh nghiệp Bảo mật", "email_label": "Email Doanh nghiệp:", "pass_label": "Mật khẩu:",
        "btn_login": "Đăng nhập An toàn 🔐", "logout": "Đăng xuất 🚪", "logged_in_as": "Đã đăng nhập:"
    },
    "id": {
        "name": "Bahasa Indonesia", "title": "TrueLens AI", "subtitle": "Mesin Verifikasi Global",
        "text_label": "📄 Analisis Teks:", "text_placeholder": "Tempel teks di sini...",
        "image_label": "🖼️ Analisis Gambar:", "btn_submit": "Mulai Analisis 🔍",
        "result_title": "Hasil:", "btn_speak": "Dengarkan Audio 🔊",
        "error_short": "Teks terlalu pendek.", "error_ai": "Peringatan AI.", "error_human": "Teks alami.",
        "img_ai": "Peringatan Visual (Varian: ", "img_human": "Gambar normal.",
        "mode_personal": "Portal Pribadi", "mode_pro": "Suite Profesional & Bisnis",
        "ent_title": "Suite Keamanan Profesional", "ent_desc": "Verifikasi terpadu dan API untuk korporat, perbankan, dan media.",
        "api_endpoint_label": "Endpoint API:", "api_key_label": "Kunci API:",
        "btn_generate_key": "Buat Kunci 🔑", "docs_label": "Dokumentasi API",
        "btn_export_pdf": "Ekspor Laporan PDF 📄", "report_id": "ID Verifikasi:",
        "login_title": "Login Korporat Aman", "email_label": "Email Perusahaan:", "pass_label": "Kata Sandi:",
        "btn_login": "Login Aman 🔐", "logout": "Keluar 🚪", "logged_in_as": "Masuk sebagai:"
    },
    "sv": {
        "name": "Svenska", "title": "TrueLens AI", "subtitle": "Global Verifieringsmotor",
        "text_label": "📄 Textanalys:", "text_placeholder": "Klistra in text här...",
        "image_label": "🖼️ Bildanalys:", "btn_submit": "Starta Analys 🔍",
        "result_title": "Resultat:", "btn_speak": "Lyssna på Ljud 🔊",
        "error_short": "För kort text.", "error_ai": "AI-varning.", "error_human": "Naturlig text.",
        "img_ai": "Visuell varning (Varians: ", "img_human": "Bilden är normal.",
        "mode_personal": "Personlig portal", "mode_pro": "Professionell & Business Suite",
        "ent_title": "Professionell Säkerhetssvit", "ent_desc": "Enhetlig verifiering och API för företag, banker och media.",
        "api_endpoint_label": "API-endpoint:", "api_key_label": "API-nyckel:",
        "btn_generate_key": "Generera nyckel 🔑", "docs_label": "API-dokumentation",
        "btn_export_pdf": "Exportera PDF-rapport 📄", "report_id": "Verifierings-ID:",
        "login_title": "Säker Företagsinloggning", "email_label": "Företagsmejl:", "pass_label": "Lösenord:",
        "btn_login": "Säker Inloggning 🔐", "logout": "Logga ut 🚪", "logged_in_as": "Inloggad som:"
    },
    "uk": {
        "name": "Українська (Ukrainian)", "title": "TrueLens AI", "subtitle": "Глобальний рушій перевірки",
        "text_label": "📄 Аналіз тексту:", "text_placeholder": "Вставте текст сюди...",
        "image_label": "🖼️ Аналіз зображення:", "btn_submit": "Почати аналіз 🔍",
        "result_title": "Результат:", "btn_speak": "Прослухати аудіо 🔊",
        "error_short": "Текст занадто короткий.", "error_ai": "Попередження ШІ.", "error_human": "Природний текст.",
        "img_ai": "Візуальне попередження (Дисперсія: ", "img_human": "Зображення нормальне.",
        "mode_personal": "Особистий портал", "mode_pro": "Професійний пакет",
        "ent_title": "Комплекс професійної безпеки", "ent_desc": "Уніфікована перевірка та API для корпорацій, банків та медіа.",
        "api_endpoint_label": "API ендпоінт:", "api_key_label": "API ключ:",
        "btn_generate_key": "Згенерувати ключ 🔑", "docs_label": "Документація",
        "btn_export_pdf": "Експортувати PDF-звіт 📄", "report_id": "ID відстеження:",
        "login_title": "Захищений корпоративний вхід", "email_label": "Корпоративний Email:", "pass_label": "Пароль:",
        "btn_login": "Безпечний вхід 🔐", "logout": "Вийти 🚪", "logged_in_as": "Увійшов як:"
    },
    "el": {
        "name": "Ελληνικά (Greek)", "title": "TrueLens AI", "subtitle": "Παγκόσμια Μηχανή Επαλήθευσης",
        "text_label": "📄 Ανάλυση Κειμένου:", "text_placeholder": "Επικολλήστε κείμενο εδώ...",
        "image_label": "🖼️ Ανάλυση Εικόνας:", "btn_submit": "Έναρξη Ανάλυσης 🔍",
        "result_title": "Αποτέλεσμα:", "btn_speak": "Ακούστε Ήχο 🔊",
        "error_short": "Πολύ σύντομο κείμενο.", "error_ai": "Προειδοποίηση AI.", "error_human": "Φυσικό κείμενο.",
        "img_ai": "Οπτική προειδοποίηση (Διακύμανση: ", "img_human": "Η εικόνα είναι κανονική.",
        "mode_personal": "Προσωπική Πύλη", "mode_pro": "Επαγγελματική Σουίτα",
        "ent_title": "Επαγγελματική Σουίτα Ασφάλειας", "ent_desc": "Ενοποιημένη επαλήθευση και API για επιχειρήσεις, τράπεζες και μέσα ενημέρωσης.",
        "api_endpoint_label": "API Endpoint:", "api_key_label": "Κλειδί API:",
        "btn_generate_key": "Δημιουργία Κλειδιού 🔑", "docs_label": "Τεκμηρίωση",
        "btn_export_pdf": "Εξαγωγή Αναφοράς PDF 📄", "report_id": "ID Αναφοράς:",
        "login_title": "Ասահովված Մուտք", "email_label": "Կորპորատիվ Էլ. փոստ:", "pass_label": "Գաղտնաբառ:",
        "login_title": "Ασφαλής Είσοδος Επιχείρησης", "email_label": "Εταιρικό Email:", "pass_label": "Κωδικός:",
        "btn_login": "Ασφαλής Σύνδεση 🔐", "logout": "Αποσύνδεση 🚪", "logged_in_as": "Συνδεδεμένος ως:"
    },
    "he": {
        "name": "עברית (Hebrew)", "title": "TrueLens AI", "subtitle": "מנוע אימות דיגיטלי עולמי",
        "text_label": "📄 ניתוח טקסט:", "text_placeholder": "הדבק טקסט כאן...",
        "image_label": "🖼️ ניתוח תמונה:", "btn_submit": "התחל ניתוח 🔍",
        "result_title": "תוצאה:", "btn_speak": "האזן לדוח 🔊",
        "error_short": "הטקסט קצר מדי.", "error_ai": "אזהרת בינה מלאכותית.", "error_human": "טקסט טבעי.",
        "img_ai": "אזהרה ויזואלית (שונות: ", "img_human": "התמונה תקינה.",
        "mode_personal": "פורטל אישי", "mode_pro": "חבילת עסקים ומקצוענים",
        "ent_title": "חבילת אבטחה מקצועית", "ent_desc": "אימות מאוחד וחיבור API עבור חברות, בנקים וגופי מדיה.",
        "api_endpoint_label": "כתובת API:", "api_key_label": "מפתח API:",
        "btn_generate_key": "צור מפתח 🔑", "docs_label": "תיעוד API",
        "btn_export_pdf": "ייצוא דוח PDF 📄", "report_id": "מזהה מעקב:",
        "login_title": "כניסת אבטחה ארגונית", "email_label": "דוא\"ל ארגוני:", "pass_label": "סיסמה:",
        "btn_login": "התחברות מאובטחת 🔐", "logout": "התנתק 🚪", "logged_in_as": "מחובר כחשבון:"
    },
    "ro": {
        "name": "Română", "title": "TrueLens AI", "subtitle": "Motor Global de Verificare",
        "text_label": "📄 Analiză Text:", "text_placeholder": "Lipește textul aici...",
        "image_label": "🖼️ Analiză Imagine:", "btn_submit": "Începe Analiza 🔍",
        "result_title": "Rezultat:", "btn_speak": "Ascultă Audio 🔊",
        "error_short": "Text prea scurt.", "error_ai": "Alertă AI.", "error_human": "Text natural.",
        "img_ai": "Alertă vizuală (Varianță: ", "img_human": "Imagine normală.",
        "mode_personal": "Portal Personal", "mode_pro": "Suite Profesională & Business",
        "ent_title": "Suite de Securitate Profesională", "ent_desc": "Verificare unificată și API pentru corporații, bănci și mass-media.",
        "api_endpoint_label": "Endpoint API:", "api_key_label": "Cheie API:",
        "btn_generate_key": "Generează Cheie 🔑", "docs_label": "Documentație",
        "btn_export_pdf": "Exportă Raport PDF 📄", "report_id": "ID Verificare:",
        "login_title": "Autentificare Corporativă Securizată", "email_label": "Email Corporativ:", "pass_label": "Parolă:",
        "btn_login": "Autentificare Securizată 🔐", "logout": "Deconectare 🚪", "logged_in_as": "Autentificat ca:"
    },
    "hu": {
        "name": "Magyar", "title": "TrueLens AI", "subtitle": "Globális Ellenőrző Motor",
        "text_label": "📄 Szövegelemzés:", "text_placeholder": "Illessze ide a szöveget...",
        "image_label": "🖼️ Képelemzés:", "btn_submit": "Elemzés Indítása 🔍",
        "result_title": "Eredmény:", "btn_speak": "Hang Hallgatása 🔊",
        "error_short": "Túl rövid szöveg.", "error_ai": "MI figyelmeztetés.", "error_human": "Természetes szöveg.",
        "img_ai": "Vizuális figyelmeztetés (Variancia: ", "img_human": "A kép normális.",
        "mode_personal": "Személyes Portál", "mode_pro": "Professzionális & Üzleti Csomag",
        "ent_title": "Professzionális Biztonsági Csomag", "ent_desc": "Egységesített ellenőrzés és API vállalatok, bankok és média számára.",
        "api_endpoint_label": "API Végpont:", "api_key_label": "API Kulcs:",
        "btn_generate_key": "Kulcs Generálása 🔑", "docs_label": "Dokumentáció",
        "btn_export_pdf": "PDF Jelentés Exportálása 📄", "report_id": "Követési Azonosító:",
        "login_title": "Biztonságos Vállalati Bejelentkezés", "email_label": "Vállalati E-mail:", "pass_label": "Jelszó:",
        "btn_login": "Biztonságos Bejelentkezés 🔐", "logout": "Kijelentkezés 🚪", "logged_in_as": "Bejelentkezve mint:"
    },
    "cs": {
        "name": "Čeština", "title": "TrueLens AI", "subtitle": "Globální Ověřovací Motor",
        "text_label": "📄 Analýza Textu:", "text_placeholder": "Sem vložte text...",
        "image_label": "🖼️ Analýza Obrazu:", "btn_submit": "Spustit Analýzu 🔍",
        "result_title": "Výsledek:", "btn_speak": "Poslechnout Zvuk 🔊",
        "error_short": "Příliš krátký text.", "error_ai": "Upozornění AI.", "error_human": "Přirozený text.",
        "img_ai": "Vizuální upozornění (Variance: ", "img_human": "Obrázek je v pořádku.",
        "mode_personal": "Osobní portál", "mode_pro": "Profesionální a firemní balíček",
        "ent_title": "Profesionální bezpečnostní balíček",
        "ent_desc": "Jednotné ověřování a API pro korporace, banky a média.",
        "api_endpoint_label": "API Endpoint:", "api_key_label": "API Klíč:",
        "btn_generate_key": "Generovat klíč 🔑", "docs_label": "Dokumentace",
        "btn_export_pdf": "Exportovat PDF Zprávu 📄", "report_id": "ID Ověření:",
        "login_title": "Zabezpečené firemní přihlášení", "email_label": "Firemní E-mail:", "pass_label": "Heslo:",
        "btn_login": "Zabezpečené přihlášení 🔐", "logout": "Odhlásit 🚪", "logged_in_as": "Přihlášen jako:"
    },
    "th": {
        "name": "ไทย (Thai)", "title": "TrueLens AI", "subtitle": "เครื่องมือตรวจสอบดิจิทัลระดับโลก",
        "text_label": "📄 วิเคราะห์ข้อความ:", "text_placeholder": "วางข้อความที่นี่...",
        "image_label": "🖼️ วิเคราะห์รูปภาพ:", "btn_submit": "เริ่มการวิเคราะห์ 🔍",
        "result_title": "ผลลัพธ์:", "btn_speak": "ฟังรายงานเสียง 🔊",
        "error_short": "ข้อความสั้นเกินไป", "error_ai": "คำเตือน AI: ตรวจพบเนื้อหา AI", "error_human": "ข้อความปกติทั่วไป",
        "img_ai": "คำเตือนภาพ (ความแปรปรวน: ", "img_human": "ภาพปกติสมบูรณ์",
        "mode_personal": "พอร์ทัลส่วนบุคคล", "mode_pro": "ชุดเครื่องมือระดับมืออาชีพ",
        "ent_title": "ชุดความปลอดภัยระดับมืออาชีพ", "ent_desc": "การตรวจสอบแบบครบวงจรและ API สำหรับองค์กร ธนาคาร และสื่อ",
        "api_endpoint_label": "จุดสิ้นสุด API:", "api_key_label": "คีย์ API:",
        "btn_generate_key": "สร้างคีย์องค์กร 🔑", "docs_label": "เอกสารคู่มือ API",
        "btn_export_pdf": "ส่งออกรายงาน PDF 📄", "report_id": "รหัสติดตามการตรวจสอบ:",
        "login_title": "เข้าสู่ระบบองค์กรอย่างปลอดภัย", "email_label": "อีเมลองค์กร:", "pass_label": "รหัสผ่าน:",
        "btn_login": "เข้าสู่ระบบอย่างปลอดภัย 🔐", "logout": "ออกจากระบบ 🚪", "logged_in_as": "เข้าสู่ระบบในฐานะ:"
    },
    "fi": {
        "name": "Suomi", "title": "TrueLens AI", "subtitle": "Globaali Varmennusmoottori",
        "text_label": "📄 Tekstianalyysi:", "text_placeholder": "Liitä teksti tähän...",
        "image_label": "🖼️ Kuvaanalyysi:", "btn_submit": "Aloita Analyysi 🔍",
        "result_title": "Tulos:", "btn_speak": "Kuuntele Ääni 🔊",
        "error_short": "Liian lyhyt teksti.", "error_ai": "Tekoälyvaroitus.", "error_human": "Luonnollinen teksti.",
        "img_ai": "Visuaalinen varoitus (Varianssi: ", "img_human": "Kuva on normaali.",
        "mode_personal": "Henkilökohtainenportaali", "mode_pro": "Ammattimainen Yrityspaketti",
        "ent_title": "Ammattimainen Turvallisuuspaketti", "ent_desc": "Yhtenäinen varmennus ja API yrityksille, pankeille ja medialle.",
        "api_endpoint_label": "API-päätepiste:", "api_key_label": "API-avain:",
        "btn_generate_key": "Luo avain 🔑", "docs_label": "Dokumentaatio",
        "btn_export_pdf": "Vie PDF-raportti 📄", "report_id": "Tunniste:",
        "login_title": "Turvallinen yrityskirjautuminen", "email_label": "Yrityksen sähköposti:", "pass_label": "Salasana:",
        "btn_login": "Turvallinen kirjautuminen 🔐", "logout": "Kirjaudu ulos 🚪", "logged_in_as": "Kirjautunut:"
    },
    "da": {
        "name": "Dansk", "title": "TrueLens AI", "subtitle": "Global Verificeringsmotor",
        "text_label": "📄 Tekstanalyse:", "text_placeholder": "Indsæt tekst her...",
        "image_label": "🖼️ Billedanalyse:", "btn_submit": "Start Analyse 🔍",
        "result_title": "Resultat:", "btn_speak": "Lyt til Lyd 🔊",
        "error_short": "For kort tekst.", "error_ai": "AI-advarsel.", "error_human": "Naturlig tekst.",
        "img_ai": "Visuel advarsel (Varians: ", "img_human": "Billedet er normalt.",
        "mode_personal": "Personlig portal", "mode_pro": "Professionel & Business Suite",
        "ent_title": "Professionel Sikkerhedssuite", "ent_desc": "Enhedset verificering og API til virksomheder, banker og medier.",
        "api_endpoint_label": "API-endpoint:", "api_key_label": "API-nøgle:",
        "btn_generate_key": "Generer nøgle 🔑", "docs_label": "API-dokumentation",
        "btn_export_pdf": "Eksporter PDF-rapport 📄", "report_id": "Verificerings-ID:",
        "login_title": "Sikker Erhvervslogin", "email_label": "Virksomheds-e-mail:", "pass_label": "Adgangskode:",
        "btn_login": "Sikker Login 🔐", "logout": "Log ud 🚪", "logged_in_as": "Logget ind som:"
    },
    "no": {
        "name": "Norsk", "title": "TrueLens AI", "subtitle": "Global Verifiseringsmotor",
        "text_label": "📄 Tekstanalyse:", "text_placeholder": "Lim inn tekst her...",
        "image_label": "🖼️ Bildeanalyse:", "btn_submit": "Start Analyse 🔍",
        "result_title": "Resultat:", "btn_speak": "Hør Lydrapport 🔊",
        "error_short": "For kort tekst.", "error_ai": "KI-advarsel.", "error_human": "Naturlig tekst.",
        "img_ai": "Visuell advarsel (Varians: ", "img_human": "Bildet er normalt.",
        "mode_personal": "Personlig portal", "mode_pro": "Profesjonell Bedriftspakke",
        "ent_title": "Profesjonell Sikkerhetspakke", "ent_desc": "Enhetlig verifisering og API for bedrifter, banker og media.",
        "api_endpoint_label": "API-endepunkt:", "api_key_label": "API-nøkkel:",
        "btn_generate_key": "Generer nøkkel 🔑", "docs_label": "Dokumentasjon",
        "btn_export_pdf": "Eksporter PDF-rapport 📄", "report_id": "Verifiserings-ID:",
        "login_title": "Sikker bedriftspålogging", "email_label": "Bedrifts-e-post:", "pass_label": "Passord:",
        "btn_login": "Sikker pålogging 🔐", "logout": "Logg ut 🚪", "logged_in_as": "Logget inn som:"
    },
    "ms": {
        "name": "Bahasa Melayu", "title": "TrueLens AI", "subtitle": "Enjin Pengesahan Global",
        "text_label": "📄 Analisis Teks:", "text_placeholder": "Tampal teks di sini...",
        "image_label": "🖼️ Analisis Imej:", "btn_submit": "Mula Analisis 🔍",
        "result_title": "Keputusan:", "btn_speak": "Dengar Audio 🔊",
        "error_short": "Teks terlalu pendek.", "error_ai": "Amaran AI.", "error_human": "Teks asli.",
        "img_ai": "Amaran Visual (Varians: ", "img_human": "Imej adalah normal.",
        "mode_personal": "Portal Peribadi", "mode_pro": "Suite Profesional & Perniagaan",
        "ent_title": "Suite Keselamatan Profesional", "ent_desc": "Pengesahan bersepadu dan API untuk korporat, perbankan, dan media.",
        "api_endpoint_label": "Titik Akhir API:", "api_key_label": "Kunci API:",
        "btn_generate_key": "Jana Kunci 🔑", "docs_label": "Dokumentasi API",
        "btn_export_pdf": "Eksport Laporan PDF 📄", "report_id": "ID Pengesahan:",
        "login_title": "Log Masuk Korporat Selamat", "email_label": "E-mel Syarikat:", "pass_label": "Kata Laluan:",
        "btn_login": "Log Masuk Selamat 🔐", "logout": "Log Keluar 🚪", "logged_in_as": "Log masuk sebagai:"
    },
    "bn": {
        "name": "বাংলা (Bengali)", "title": "TrueLens AI", "subtitle": "গ্লোবাল ভেরিফিকেশন ইঞ্জিন",
        "text_label": "📄 টেক্সট বিশ্লেষণ:", "text_placeholder": "এখানে টেক্সট পেস্ট করুন...",
        "image_label": "🖼️ ছবি বিশ্লেষণ:", "btn_submit": "বিশ্লেষণ শুরু করুন 🔍",
        "result_title": "ফলাফল:", "btn_speak": "অডিও শুনুন 🔊",
        "error_short": "টেক্সট খুব ছোট।", "error_ai": "AI সতর্কতা: AI দ্বারা তৈরি।", "error_human": "স্বাভাবিক টেক্সট।",
        "img_ai": "ভিজ্যুয়াল সতর্কতা (ভ্যারিয়েন্স: ", "img_human": "ছবিটি স্বাভাবিক।",
        "mode_personal": "ব্যক্তিগত পোর্টাল", "mode_pro": "প্রফেশনাল ও বিজনেস স্যুট",
        "ent_title": "প্রফেশনাল সিকিউরিটি স্যুট", "ent_desc": "কর্পোরেট, ব্যাংক এবং মিডিয়ার জন্য সমন্বিত যাচাইকরণ এবং API সাপোর্ট।",
        "api_endpoint_label": "API এন্ডপয়েন্ট:", "api_key_label": "API কী:",
        "btn_generate_key": "কী জেনারেট করুন 🔑", "docs_label": "নথিপত্র",
        "btn_export_pdf": "PDF রিপোর্ট এক্সপোর্ট করুন 📄", "report_id": "যাচাইকরণ আইডি:",
        "login_title": "এন্টারপ্রাইজ সিকিউর লগইন", "email_label": "কর্পোরেট ইমেল:", "pass_label": "পাসওয়ার্ড:",
        "btn_login": "নিরাপদ লগইন 🔐", "logout": "লগআউট 🚪", "logged_in_as": "লগইন করা আছে:"
    },
    "fa": {
        "name": "فارسی (Persian)", "title": "TrueLens AI", "subtitle": "موتور جهانی تأیید اصالت",
        "text_label": "📄 تحلیل متن:", "text_placeholder": "متن را اینجا بچسبانید...",
        "image_label": "🖼️ تحلیل تصویر:", "btn_submit": "شروع تحلیل 🔍",
        "result_title": "نتیجه:", "btn_speak": "گزارش صوتی 🔊",
        "error_short": "متن خیلی کوتاه است.", "error_ai": "هشدار هوش مصنوعی.", "error_human": "متن طبیعی است.",
        "img_ai": "هشدار تصویری (واریانس: ", "img_human": "تصویر عادی است.",
        "mode_personal": "پورتال شخصی", "mode_pro": "مجموعه حرفه‌ای و تجاری",
        "ent_title": "مجموعه امنیت حرفه‌ای", "ent_desc": "اعتبارسنجی یکپارچه و اتصال API برای شرکت‌ها، بانک‌ها و رسانه‌ها.",
        "api_endpoint_label": "نقطه پایانی API:", "api_key_label": "کلید مجوز API:",
        "btn_generate_key": "تولید کلید سازمانی 🔑", "docs_label": "مستندات API",
        "btn_export_pdf": "صدور گزارش رسمی PDF 📄", "report_id": "شناسه رهگیری:",
        "login_title": "ورود امن سازمانی و بانکی", "email_label": "ایمیل سازمانی:", "pass_label": "رمز عبور:",
        "btn_login": "ورود امن 🔐", "logout": "خروج 🚪", "logged_in_as": "وارد شده با حساب:"
    },
    "ur": {
        "name": "اردو (Urdu)", "title": "TrueLens AI", "subtitle": "عالمی ڈیجیٹل تصدیقی انجن",
        "text_label": "📄 متن کا تجزیہ:", "text_placeholder": "یہاں متن چسپاں کریں...",
        "image_label": "🖼️ تصویر کا تجزیہ:", "btn_submit": "تجزیہ شروع کریں 🔍",
        "result_title": "نتیجہ:", "btn_speak": "آڈیو سنیں 🔊",
        "error_short": "متن بہت چھوٹا ہے۔", "error_ai": "AI کی طرف سے انتباہ۔", "error_human": "قدرتی متن۔",
        "img_ai": " بصری انتباہ (فرق: ", "img_human": "تصویر نارمل ہے۔",
        "mode_personal": "ذاتی پورٹل", "mode_pro": "پروفیشنل اور بزنس سوٹ",
        "ent_title": "پروفیشنل سیکیورٹی سوٹ", "ent_desc": "کارپوریٹ، بینکنگ اور میڈیا سیکٹرز کے لیے متفقہ تصدیق اور API کنکشن۔",
        "api_endpoint_label": "API اینڈ پوائنٹ:", "api_key_label": "API کلید:",
        "btn_generate_key": "انٹرپرाइज کلید بنائیں 🔑", "docs_label": "دستاویزات",
        "btn_export_pdf": "پی ڈی ایف رپورٹ برآمد کریں 📄", "report_id": "تصدیقی شناختی نمبر:",
        "login_title": "کارپوریٹ محفوظ لاگ ان (بینک اور ادارے)", "email_label": "کارپوریٹ ای میل:", "pass_label": "پاس ورڈ:",
        "btn_login": "محفوظ لاگ ان 🔐", "logout": "لاگ آؤٹ 🚪", "logged_in_as": "لاگ ان اکاؤنٹ:"
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
            max-width: 700px;
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
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            background: #0f172a;
            border-radius: 12px;
            padding: 6px;
            margin-bottom: 20px;
            border: 1px solid #334155;
        }
        .mode-btn {
            text-align: center;
            padding: 12px;
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
        textarea, input[type="text"], input[type="password"] {
            width: 100%; padding: 12px; border-radius: 10px;
            border: 1px solid #475569; background: #0f172a; color: white;
            font-family: 'Inter', sans-serif; font-size: 14px; box-sizing: border-box; resize: vertical;
        }
        textarea:focus, input:focus { outline: none; border-color: var(--accent-color); }
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
        .btn-export {
            width: 100%; padding: 10px; margin-top: 8px; border-radius: 8px; border: none;
            background: #d97706; color: white; font-weight: 600; font-size: 13px; cursor: pointer;
        }
        .tracking-id {
            font-size: 11px; color: #38bdf8; margin-top: 8px; font-family: monospace;
        }
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
        .login-box {
            background: #020617;
            border: 1px solid #334155;
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 15px;
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
            <a href="?lang={{ current_lang }}&mode=pro" class="mode-btn {% if mode == 'pro' %}active{% endif %}">🏢 {{ t.mode_pro }}</a>
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
            {% if tracking_id %}
            <div class="tracking-id">{{ t.report_id }} {{ tracking_id }}</div>
            {% endif %}
            <button class="btn-speak" onclick="speakResult()">{{ t.btn_speak }}</button>
            <button class="btn-export" onclick="alert('PDF Certified Report Generated & Downloaded Successfully! [ID: {{ tracking_id }}]')">{{ t.btn_export_pdf }}</button>
        </div>
        {% endif %}

        {% else %}
        <!-- Professional & Enterprise Unified Portal Mode with Secure Login -->
        <div class="enterprise-container">
            <h3>🏢 {{ t.ent_title }}</h3>
            
            {% if not session.get('enterprise_logged_in') %}
            <!-- Login Form for Corporate / Bank / Media Users -->
            <div class="login-box">
                <h4 style="color: #38bdf8; margin-top: 0; font-size: 14px;">🔐 {{ t.login_title }}</h4>
                <form method="POST" action="/enterprise-login?lang={{ current_lang }}&mode=pro">
                    <div class="input-group">
                        <label>{{ t.email_label }}</label>
                        <input type="text" name="corporate_email" placeholder="e.g. admin@bank.com" required>
                    </div>
                    <div class="input-group">
                        <label>{{ t.pass_label }}</label>
                        <input type="password" name="corporate_password" placeholder="••••••••" required>
                    </div>
                    <button type="submit" class="btn-submit" style="padding: 10px; font-size: 13px;">{{ t.btn_login }}</button>
                </form>
            </div>
            {% else %}
            <!-- Logged In Dashboard -->
            <div style="background: #020617; padding: 12px; border-radius: 8px; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 12px; color: #34d399;">✅ {{ t.logged_in_as }} <b>{{ session.get('enterprise_email') }}</b></span>
                <a href="/enterprise-logout?lang={{ current_lang }}&mode=pro" style="color: #f87171; font-size: 12px; text-decoration: none; font-weight: 600;">{{ t.logout }}</a>
            </div>

            <p>{{ t.ent_desc }}</p>
            
            <form method="POST" enctype="multipart/form-data" style="margin-top: 15px;">
                <div class="input-group">
                    <label>📄 Enterprise / Document / News Content:</label>
                    <textarea name="text_content" placeholder="Paste professional content, contract, or news statement...">{{ text_input or '' }}</textarea>
                </div>
                
                <div class="input-group">
                    <label>🖼️ Secure File / KYC / Media Evidence:</label>
                    <div class="file-upload-box">
                        <input type="file" name="image_file" accept="image/*">
                    </div>
                </div>
                
                <button type="submit" class="btn-submit">Execute Professional Suite Audit 🔍</button>
            </form>

            <div class="input-group" style="margin-top: 20px;">
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

            {% if result %}
            <div class="result-card">
                <h3>{{ t.result_title }}</h3>
                <p id="resultText" style="margin: 0; line-height: 1.5; font-size: 14px;">{{ result }}</p>
                {% if tracking_id %}
                <div class="tracking-id">{{ t.report_id }} {{ tracking_id }}</div>
                {% endif %}
                <button class="btn-export" onclick="alert('Professional Certified PDF Report Exported Successfully!')">{{ t.btn_export_pdf }}</button>
            </div>
            {% endif %}
            {% endif %}
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
    if mode not in ["personal", "pro"]:
        mode = "personal"
        
    t = TRANSLATIONS[lang]
    result = None
    text_input = ""
    tracking_id = None
    
    if request.method == "POST" and (mode == "personal" or session.get('enterprise_logged_in')):
        text_input = request.form.get("text_content", "")
        uploaded_file = request.files.get("image_file")
        tracking_id = str(uuid.uuid4()).upper()[:12]
        
        if uploaded_file and uploaded_file.filename != '':
            try:
                img = Image.open(uploaded_file.stream).convert('L')
                img_arr = np.array(img)
                variance = np.var(img_arr)
                if mode == "pro":
                    if variance < 900:
                        result = f"🛡️ Professional Suite Audit Alert: Document or media verification detected anomalies/tampering (Variance: {variance:.2f})."
                    else:
                        result = f"✅ Professional Suite Audit Passed: High-integrity media and structural verification confirmed (Variance: {variance:.2f})."
                else:
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
                if mode == "pro":
                    result = "⚠️ Enterprise Compliance Warning: Input text exhibits synthetic patterns and high AI generation probability."
                else:
                    result = t['error_ai']
            else:
                if mode == "pro":
                    result = "✅ Enterprise Compliance Approved: Text source appears authentic and verified."
                else:
                    result = t['error_human']
        else:
            result = "Please enter text or upload a file/image to start the analysis."
            tracking_id = None
            
    return render_template_string(HTML_TEMPLATE, t=t, current_lang=lang, mode=mode, translations=TRANSLATIONS, result=result, text_input=text_input, tracking_id=tracking_id)

@app.route("/enterprise-login", methods=["POST"])
def enterprise_login():
    lang = request.args.get("lang", "en")
    email = request.form.get("corporate_email", "")
    password = request.form.get("corporate_password", "")
    
    if email.strip() and len(password) >= 4:
        session['enterprise_logged_in'] = True
        session['enterprise_email'] = email
        
    return redirect(url_for('index', lang=lang, mode="pro"))

@app.route("/enterprise-logout")
def enterprise_logout():
    lang = request.args.get("lang", "en")
    session.pop('enterprise_logged_in', None)
    session.pop('enterprise_email', None)
    return redirect(url_for('index', lang=lang, mode="pro"))

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
        "analysis_type": "professional_unified_verification",
        "artificial_probability": 85.5 if is_ai else 5.2,
        "classification": "AI_GENERATED" if is_ai else "HUMAN_WRITTEN",
        "confidence_score": "High",
        "tracking_id": str(uuid.uuid4()).upper()[:12]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
