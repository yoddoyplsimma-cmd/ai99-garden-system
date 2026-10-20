import streamlit as st
import urllib.parse
import time
from datetime import datetime

# ==========================================================
# 1. การตั้งค่าระบบหลัก & ท่อรับเงิน & โครงสร้างราคา 3 สกุลเงิน
# ==========================================================
AMAZON_AFFILIATE_TAG = "ybcai99garden-20"
ACCESS_PERIOD_DAYS = 120  # สิทธิ์เข้าถึง 4 เดือนเต็ม (1 ไตรมาส)

# ลิงก์ท่อรับเงินจริง
STRIPE_URL_USD = "https://buy.stripe.com/your_actual_stripe_link_usd"
STRIPE_URL_EUR = "https://buy.stripe.com/your_actual_stripe_link_eur"
PROMPTPAY_ID = "0812345678"  # เบอร์โทร หรือ PromptPay ID ของพี่ยอด

# โครงสร้างราคา 3 สกุลเงิน (คุมเพดานไม่ต่ำกว่าฐาน $139.95)
PRICING_CONFIG = {
    "USD": {
        "symbol": "$",
        "rate": 139.95,
        "format": "$139.95",
        "multiplier": 1.0,
        "label": "USD ($139.95)"
    },
    "EUR": {
        "symbol": "€",
        "rate": 129.00,
        "format": "€129.00",
        "multiplier": 0.92,
        "label": "EUR (€129.00)"
    },
    "THB": {
        "symbol": "฿",
        "rate": 5090.00,
        "format": "5,090 บาท",
        "multiplier": 36.37,
        "label": "THB (฿5,090)"
    }
}

# แผนผังผูกภาษาเข้ากับสกุลเงินเริ่มต้นอัตโนมัติ (Language to Currency Mapping)
LANG_TO_CURR = {
    "TH": "THB",
    "EN": "USD",
    "DE": "EUR"
}

st.set_page_config(
    page_title="AI99 Garden Spatial System",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling + Infinite Smooth Carousel
st.markdown("""
    <style>
    .stApp { background-color: #FAFAFA; }
    .main-title { font-size: 2.1rem; font-weight: 800; color: #1B4D3E; margin-bottom: 0px; }
    .sub-title { font-size: 1.0rem; color: #64748B; margin-bottom: 20px; }
    .white-card { 
        background-color: #FFFFFF; 
        border: 1px solid #E2E8F0; 
        border-radius: 14px; 
        padding: 20px; 
        margin-bottom: 15px; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
    .spec-tag { 
        background-color: #F1F5F9; 
        color: #0F172A; 
        font-weight: 600; 
        padding: 5px 12px; 
        border-radius: 6px; 
        font-size: 0.85rem; 
        margin-right: 6px; 
        border: 1px solid #E2E8F0;
    }
    .legal-box { 
        background-color: #FFFFFF; 
        border-left: 5px solid #F59E0B; 
        border-top: 1px solid #E2E8F0;
        border-right: 1px solid #E2E8F0;
        border-bottom: 1px solid #E2E8F0;
        padding: 18px; 
        border-radius: 8px; 
        margin: 15px 0px; 
        font-size: 0.95rem; 
        color: #334155;
    }
    .guide-bubble { 
        background-color: #FFFFFF; 
        border-left: 4px solid #10B981; 
        border-top: 1px solid #E2E8F0;
        border-right: 1px solid #E2E8F0;
        border-bottom: 1px solid #E2E8F0;
        padding: 12px; 
        border-radius: 6px; 
        margin-bottom: 10px; 
        font-size: 0.9rem; 
        color: #1E293B;
    }
    /* Carousel Styling */
    .carousel-track-container {
        overflow: hidden;
        width: 100%;
        border-radius: 12px;
        margin-top: 15px;
        border: 1px solid #E2E8F0;
        background: #FFFFFF;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .carousel-track {
        display: flex;
        width: calc(230px * 8);
        animation: scroll-left 22s linear infinite;
    }
    .carousel-track:hover {
        animation-play-state: paused;
    }
    .carousel-slide {
        width: 230px;
        padding: 8px;
        box-sizing: border-box;
        flex-shrink: 0;
    }
    .carousel-slide img {
        width: 100%;
        height: 140px;
        object-fit: cover;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        transition: transform 0.3s ease;
    }
    .carousel-slide img:hover {
        transform: scale(1.03);
    }
    .carousel-caption {
        font-size: 0.8rem;
        color: #475569;
        text-align: center;
        margin-top: 6px;
        font-weight: 600;
    }
    @keyframes scroll-left {
        0% { transform: translateX(0); }
        100% { transform: translateX(calc(-230px * 4)); }
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================================
# 2. พจนานุกรม 3 ภาษา (TH / EN / DE)
# ==========================================================
I18N = {
    "TH": {
        "title": "🌿 ระบบคำนวณและออกแบบจัดสวนอัจฉริยะ AI99",
        "subtitle": "คำนวณสัดส่วนพื้นที่ตรงรุ่น • ปรับแต่งทรงและสีตามต้องการ • สั่งซื้อชุดอุปกรณ์ครบวงจร",
        "sidebar_guide": "🤖 ผู้ช่วยแนะนำระบบ (AI Guide)",
        "sidebar_safety": "ระบบคุมตรรกะความปลอดภัย: Zero-Hallucination Guard",
        "quick_questions": "คำถามยอดนิยม:",
        "btn_how": "🚩 วิธีใช้งานเว็บ",
        "btn_dim": "📐 เช็กขนาดพื้นที่",
        "btn_pot": "🪴 ปรับทรงกระถาง",
        "btn_pass": "⏳ สิทธิ์ 4 เดือน",
        "ask_input_label": "พิมพ์ถาม AI ไกด์:",
        "ask_placeholder": "พิมพ์คำถามที่นี่...",
        "btn_send": "ส่งคำถาม",
        "step1_title": "1. เลือกสไตล์สวนที่ต้องการ",
        "style_label": "รูปแบบสไตล์มาตรฐานที่ผ่านการคำนวณแล้ว:",
        "dim_title": "📌 สเปกมิติมาตรฐาน (Standard Dimension)",
        "dim_w": "กว้าง", "dim_h": "สูง", "dim_d": "ลึก", "meter": "เมตร",
        "category_txt": "หมวดหมู่", "arch_name": "ชื่อสถาปัตยกรรม",
        "scan_title": "📷 ถ่ายภาพหรือสแกนพื้นที่จริงของท่าน",
        "cam_choice": ["เปิดกล้องสด (Camera)", "อัปโหลดรูปภาพ (Upload)"],
        "cam_prompt": "สแกนมุมระเบียงหรือห้องที่ต้องการจัด",
        "upload_prompt": "เลือกไฟล์รูปภาพพื้นที่บ้าน",
        "step2_title": "2. ปรับแต่งรูปทรง สี และจำนวนอุปกรณ์ (Interactive Customizer)",
        "pot_shape_label": "เลือกรูปทรงกระถาง / รางปลูก (Planter Style):",
        "pot_shapes": ["รางยาวมินิมอล (Rectangular Trough)", "ทรงกระบอกโมเดิร์น (Cylinder)", "สี่เหลี่ยมลูกบาศก์ (Square Cube)", "ทรงกลมคลาสสิก (Round Pot)"],
        "pot_color_label": "เลือกโทนสีวัสดุ (Color & Texture):",
        "pot_colors": ["ดำด้านลอฟท์ (Matte Black)", "ขาวคลีนมินิมอล (Matte White)", "เทาคอนกรีตโมเดิร์น (Concrete Grey)", "ดินเผาธรรมชาติ (Terracotta)"],
        "bom_title": "📦 ตารางรายการอุปกรณ์ในเซ็ต (Bill of Materials)",
        "est_price": "ประมาณการ", "btn_amazon": "ดูบน Amazon ↗",
        "step3_title": "ราคารวมอุปกรณ์โดยประมาณ:",
        "amazon_note": "ราคาสินค้าจริงขึ้นอยู่กับราคาผู้ขายบน Amazon ณ วันที่สั่งซื้อ",
        "btn_buy_all": "🛒 สั่งซื้ออุปกรณ์ชุดนี้ทั้งหมดบน Amazon (One-Click)",
        "legal_title": "⚖️ ข้อตกลงสิทธิ์การใช้งาน Seasonal Access Pass",
        "legal_rule1": f"- สิทธิ์นี้ครอบคลุมการเข้าถึงไฟล์พิมพ์เขียว แผนผังระบบ และการคำนวณสเปกสถาปัตยกรรมเป็นเวลา <b>{ACCESS_PERIOD_DAYS} วัน (4 เดือนเต็ม)</b>",
        "legal_rule2": "- เมื่อครบกำหนด 4 เดือน สิทธิ์จะสิ้นสุดลงโดยอัตโนมัติ หากต้องการใช้งานต่อในฤดูกาลถัดไปสามารถลงทะเบียนใหม่ได้",
        "legal_rule3": "- การเข้าถึงระบบถือเป็นการส่งมอบสินทรัพย์ดิจิทัลเสร็จสมบูรณ์ทันที มีผลผูกพันตามกฎหมายธุรกรรมอิเล็กทรอนิกส์",
        "chk1_txt": "1. ข้าพเจ้ายอมรับข้อตกลงการให้บริการ และนโยบายทรัพย์สินทางปัญญาของ AI99 (Terms of Service)",
        "chk2_txt": "2. ข้าพเจ้ายืนยันสละสิทธิ์การขอคืนเงินทุกกรณี 100% หลังเข้าถึงระบบ (Strict Non-Refundable Clause)",
        "legal_unlock": "✅ ยืนยันข้อกำหนดเรียบร้อย ปลดล็อกท่อชำระเงินสิทธิ์ 4 เดือน",
        "legal_lock": "กรุณาทำเครื่องหมายติ๊กถูก 2 ปุ่มด้านบนให้ครบถ้วน เพื่อปลดล็อกท่อชำระเงิน",
        "pay_usd_tab": "💳 บัตรเครดิต/เดบิตสากล (USD)",
        "pay_eur_tab": "💶 บัตรเครดิตยุโรป (EUR)",
        "pay_thb_tab": "📱 สแกน QR พร้อมเพย์ (THB)",
        "pay_stripe_desc": "ชำระค่าบริการ Seasonal Pass 4 เดือน ผ่านระบบ Stripe มาตรฐานความปลอดภัยระดับโลก",
        "btn_stripe": "🚀 ปลดล็อกสิทธิ์ 4 เดือน",
        "pay_thb_desc": "สแกน QR Code พร้อมเพย์ ชำระตรงเข้าบัญชี",
        "upload_slip": "แนบสลิปโอนเงินเพื่อปลดล็อกสิทธิ์:",
        "btn_slip": "ยืนยันการส่งสลิป",
        "slip_ok": "ระบบได้รับข้อมูลสลิปแล้ว กำลังตรวจสอบเพื่อเปิดสิทธิ์การใช้งาน 4 เดือนครับ"
    },
    "EN": {
        "title": "🌿 AI99 Intelligent Garden Spatial Design System",
        "subtitle": "Precision Area Computation • Customizable Forms & Colors • Complete Equipment Sourcing",
        "sidebar_guide": "🤖 Assistant Guide (AI Guide)",
        "sidebar_safety": "Logic Control Protocol: Zero-Hallucination Guard",
        "quick_questions": "Frequently Asked Questions:",
        "btn_how": "🚩 How to Use",
        "btn_dim": "📐 Check Dimensions",
        "btn_pot": "🪴 Customize Pots",
        "btn_pass": "⏳ 4-Month Pass",
        "ask_input_label": "Ask AI Guide:",
        "ask_placeholder": "Type your inquiry here...",
        "btn_send": "Send Inquiry",
        "step1_title": "1. Select Desired Garden Architecture",
        "style_label": "Engineered Standard Archetypes:",
        "dim_title": "📌 Standard Specifications & Dimensions",
        "dim_w": "Width", "dim_h": "Height", "dim_d": "Depth", "meter": "m",
        "category_txt": "Category", "arch_name": "Architecture Title",
        "scan_title": "📷 Capture or Upload Your Space",
        "cam_choice": ["Live Camera", "File Upload"],
        "cam_prompt": "Scan your balcony or indoor room corner",
        "upload_prompt": "Upload space image file",
        "step2_title": "2. Customize Shape, Color & Quantities (BOM Configurator)",
        "pot_shape_label": "Select Planter Style / Shape:",
        "pot_shapes": ["Rectangular Trough", "Cylinder Modern", "Square Cube", "Round Pot Classic"],
        "pot_color_label": "Select Material Texture & Color:",
        "pot_colors": ["Matte Black Loft", "Matte White Minimal", "Concrete Grey Modern", "Terracotta Natural"],
        "bom_title": "📦 Bill of Materials (BOM Dataset)",
        "est_price": "Est. Price", "btn_amazon": "View on Amazon ↗",
        "step3_title": "Estimated Equipment Total:",
        "amazon_note": "Actual pricing depends on live vendor listings on Amazon at checkout.",
        "btn_buy_all": "🛒 Order Full Equipment Kit on Amazon (One-Click)",
        "legal_title": "⚖️ Seasonal Access Pass Terms of Service",
        "legal_rule1": f"- Grants full access to system architecture blueprints, dimensional layouts for <b>{ACCESS_PERIOD_DAYS} days (Full 4-Month Quarter)</b>",
        "legal_rule2": "- Automatically expires after 120 days. Renewal is optional for subsequent planting seasons.",
        "legal_rule3": "- System access constitutes immediate and final delivery of digital assets with binding legal enforcement.",
        "chk1_txt": "1. I accept the AI99 Terms of Service and Intellectual Property Policy.",
        "chk2_txt": "2. I acknowledge and agree to the 100% Strict Non-Refundable Clause once access is granted.",
        "legal_unlock": "✅ Terms accepted. Payment gateway for 4-month pass is unlocked.",
        "legal_lock": "Please accept both mandatory checkboxes above to unlock payment checkout.",
        "pay_usd_tab": "💳 International Card (USD)",
        "pay_eur_tab": "💶 European Card (EUR)",
        "pay_thb_tab": "📱 PromptPay QR (THB)",
        "pay_stripe_desc": "Pay 4-Month Seasonal Pass via secure Stripe international gateway.",
        "btn_stripe": "🚀 Unlock 4-Month Access",
        "pay_thb_desc": "Scan PromptPay QR for direct local transfer.",
        "upload_slip": "Upload bank transfer confirmation slip:",
        "btn_slip": "Submit Transfer Slip",
        "slip_ok": "Slip received. Processing instant 4-month account activation."
    },
    "DE": {
        "title": "🌿 AI99 Intelligentes Garten-Raumplanungssystem",
        "subtitle": "Präzise Raumberechnung • Individuelle Formen & Farben • Vollständiges Ausrüstungsset",
        "sidebar_guide": "🤖 Systemassistent (AI Guide)",
        "sidebar_safety": "Logik-Sicherheitskontrolle: Zero-Hallucination Guard",
        "quick_questions": "Häufige Fragen:",
        "btn_how": "🚩 Anleitung",
        "btn_dim": "📐 Maße prüfen",
        "btn_pot": "🪴 Gefäße anpassen",
        "btn_pass": "⏳ 4-Monats-Pass",
        "ask_input_label": "Frage an den AI-Guide:",
        "ask_placeholder": "Ihre Frage hier eingeben...",
        "btn_send": "Frage senden",
        "step1_title": "1. Gewünschten Gartenstil auswählen",
        "style_label": "Berechnete Standard-Architekturmodelle:",
        "dim_title": "📌 Standardspezifikationen & Abmessungen",
        "dim_w": "Breite", "dim_h": "Höhe", "dim_d": "Tiefe", "meter": "m",
        "category_txt": "Kategorie", "arch_name": "Architektur-Titel",
        "scan_title": "📷 Raum fotografieren oder hochladen",
        "cam_choice": ["Live-Kamera", "Datei-Upload"],
        "cam_prompt": "Balkon oder Raumecke scannen",
        "upload_prompt": "Raumbild auswählen",
        "step2_title": "2. Formen, Farben & Stückzahlen anpassen (BOM-Konfigurator)",
        "pot_shape_label": "Pflanzgefäß-Form auswählen:",
        "pot_shapes": ["Rechteckiger Trog (Minimal)", "Zylinder (Modern)", "Würfel (Square)", "Runder Topf (Klassisch)"],
        "pot_color_label": "Farbton & Textur auswählen:",
        "pot_colors": ["Mattschwarz Loft", "Mattweiß Minimal", "Betongrau Modern", "Terrakotta Natur"],
        "bom_title": "📦 Stückliste der Ausrüstung (Bill of Materials)",
        "est_price": "Geschätzt", "btn_amazon": "Auf Amazon ansehen ↗",
        "step3_title": "Geschätzte Gesamtkosten der Ausrüstung:",
        "amazon_note": "Tatsächliche Preise hängen vom jeweiligen Amazon-Händler ab.",
        "btn_buy_all": "🛒 Gesamte Ausrüstung mit einem Klick auf Amazon bestellen",
        "legal_title": "⚖️ Nutzungsbedingungen für den Seasonal Access Pass",
        "legal_rule1": f"- Gültig für vollständigen Zugriff auf Baupläne und Raumspezifikationen für <b>{ACCESS_PERIOD_DAYS} Tage (4 volle Monate)</b>",
        "legal_rule2": "- Endet automatisch nach 120 Tagen. Verlängerung für Folgesaison optional.",
        "legal_rule3": "- Der Systemzugang gilt als vollständige digitale Bereitstellung und ist rechtlich bindend.",
        "chk1_txt": "1. Ich akzeptiere die AI99-Nutzungsbedingungen und die Richtlinien zum geistigen Eigentum.",
        "chk2_txt": "2. Ich bestätige den 100%igen Verzicht auf Rückerstattung nach Bereitstellung des Zugangs.",
        "legal_unlock": "✅ Bedingungen akzeptiert. Zahlungskanäle für den 4-Monats-Pass freigeschaltet.",
        "legal_lock": "Bitte bestätigen Sie die beiden Pflichtfelder, um die Zahlung freizuschalten.",
        "pay_usd_tab": "💳 Internationale Karte (USD)",
        "pay_eur_tab": "💶 Europäische Karte (EUR)",
        "pay_thb_tab": "📱 PromptPay QR (THB)",
        "pay_stripe_desc": "4-Monats-Seasonal Pass sicher über Stripe bezahlen.",
        "btn_stripe": "🚀 4-Monats-Zugang freischalten",
        "pay_thb_desc": "PromptPay QR für direkte Überweisung scannen.",
        "upload_slip": "Zahlungsbeleg hochladen:",
        "btn_slip": "Beleg übermitteln",
        "slip_ok": "Beleg empfangen. Der 4-monatige Zugang wird unverzüglich aktiviert."
    }
}

# ==========================================================
# 3. ฐานข้อมูลสเปกสำเร็จรูป (MASTER BOM DATASET) 4 รูปแบบ
# ==========================================================
CATALOG = {
    "STYLE-BAL-01": {
        "title_th": "สวนผักสลัดแนวตั้งระเบียงคอนโด (Verdant Balcony Kit)",
        "title_en": "Minimalist Vertical Balcony Salad Kit",
        "title_de": "Minimalistischer Vertikaler Balkon-Salatgarten",
        "category": "Balcony Micro-Space",
        "dimensions": {"width": 1.20, "height": 2.00, "depth": 0.45},
        "default_items": [
            {"id": "rack", "name": "โครงชั้นวางกัลวาไนซ์ 4-5 ชั้น ทรง Slim", "name_en": "Slim Galvanized 5-Tier Rack", "name_de": "Schlankes 5-Etagen-Regal Verzinkt", "qty": 1, "price_usd": 45.0, "search": "vertical garden wall planter rack outdoor"},
            {"id": "planter", "name": "รางปลูกผักสลัด Food-grade ทน UV", "name_en": "Food-grade UV Resistant Planter Box", "name_de": "UV-beständiger Pflanzkasten Lebensmittelqualität", "qty": 4, "price_usd": 8.0, "search": "rectangular planter box UV resistant"},
            {"id": "drip", "name": "ชุดระบบน้ำหยดอัตโนมัติ Micro-drip", "name_en": "Automatic Micro-Drip Irrigation Kit", "name_de": "Automatisches Micro-Drip Bewässerungsset", "qty": 1, "price_usd": 18.5, "search": "automatic micro drip irrigation kit balcony"},
            {"id": "soil", "name": "ดินปลูกสูตรมินิมอลระบายน้ำไว (50L)", "name_en": "Organic Lightweight Potting Mix (50L)", "name_de": "Organische Pflanzerde leicht durchlässig (50L)", "qty": 2, "price_usd": 12.0, "search": "organic potting mix perlite lightweight"}
        ]
    },
    "STYLE-MSH-01": {
        "title_th": "สมาร์ทฟังกิพอด ตู้เห็ดในร่มกินได้ (Smart Fungi Pod)",
        "title_en": "Indoor Micro Mushroom Chamber",
        "title_de": "Smarte Indoor-Pilzzuchtkammer",
        "category": "Mushroom Chamber",
        "dimensions": {"width": 0.50, "height": 0.70, "depth": 0.40},
        "default_items": [
            {"id": "chamber", "name": "ตู้โหลแก้ว/อะคริลิก คุมความชื้นมินิมอล", "name_en": "Humidity Controlled Chamber Tent", "name_de": "Feuchtigkeitsgesteuerte Zuchtkammer", "qty": 1, "price_usd": 55.0, "search": "mushroom fruiting chamber grow tent"},
            {"id": "humidifier", "name": "เครื่องพ่นหมอก Ultrasonic + เซนเซอร์", "name_en": "Ultrasonic Mist Maker + Sensor", "name_de": "Ultraschall-Vernebler mit Feuchtigkeitssensor", "qty": 1, "price_usd": 28.0, "search": "ultrasonic mist maker with humidity controller"},
            {"id": "spores", "name": "ก้อนเชื้อเห็ดพรีเมียม (Oyster/Lion's Mane)", "name_en": "Organic Mushroom Grow Kit Substrate", "name_de": "Bio-Pilzzucht Substratblöcke", "qty": 4, "price_usd": 6.5, "search": "organic mushroom grow kit lion mane oyster"},
            {"id": "light", "name": "ไฟ LED Bar 5W สเปกตรัมขาว", "name_en": "5W White Spectrum LED Grow Bar", "name_de": "5W Weißspektrum LED-Wachstumsleiste", "qty": 1, "price_usd": 14.0, "search": "small indoor led grow light bar for plants"}
        ]
    },
    "STYLE-IND-01": {
        "title_th": "ชั้นวางไม้และไฟปลูกในห้องรับแขก (Living Plant Shelf)",
        "title_en": "Living Room Aesthetic Greenery Stand",
        "title_de": "Ästhetisches Wohnzimmer-Pflanzenregal",
        "category": "Indoor Greenery",
        "dimensions": {"width": 1.00, "height": 1.60, "depth": 0.35},
        "default_items": [
            {"id": "wood_rack", "name": "ชั้นวางไม้โครงเหล็กนอร์ดิก 4 ชั้น", "name_en": "4-Tier Nordic Metal Wood Plant Stand", "name_de": "4-stufiges Nordisches Metall-Holz-Pflanzenregal", "qty": 1, "price_usd": 62.0, "search": "tiered plant stand indoor metal wood tall"},
            {"id": "grow_light", "name": "ไฟ Grow Light ซ่อนใต้ชั้น Full Spectrum", "name_en": "Under-shelf Full Spectrum Grow Lights", "name_de": "Full-Spectrum Unterbau-Pflanzenleuchten", "qty": 3, "price_usd": 15.0, "search": "under shelf grow lights full spectrum warm white"},
            {"id": "pots", "name": "กระถางเซรามิกมินิมอลพร้อมจานรอง", "name_en": "Modern Ceramic Pots with Saucers", "name_de": "Moderne Keramiktöpfe mit Untersetzern", "qty": 6, "price_usd": 7.0, "search": "ceramic plant pots with drainage hole saucer modern"}
        ]
    },
    "STYLE-FYD-01": {
        "title_th": "แผงสวนแนวตั้งระแนงหน้าบ้าน (Front Entrance Green Wall)",
        "title_en": "Front Yard Compact Trellis System",
        "title_de": "Kompaktes Vorgarten-Spaliersystem",
        "category": "Front Yard",
        "dimensions": {"width": 1.80, "height": 1.80, "depth": 0.50},
        "default_items": [
            {"id": "trellis", "name": "แผงระแนงเหล็กโมดูลาร์ตั้งพื้น พ่นกันสนิม", "name_en": "Freestanding Modular Garden Trellis", "name_de": "Freistehendes Modulares Gartenspalier", "qty": 1, "price_usd": 78.0, "search": "freestanding garden trellis wall panel metal"},
            {"id": "hook_pots", "name": "กระถางแขวนระบบ Hook Lock เก็บน้ำสำรอง", "name_en": "Hook Lock Self-Watering Hanging Pots", "name_de": "Selbstbewässernde Hängepflanzkübel mit Haken", "qty": 12, "price_usd": 4.5, "search": "hanging wall planter pots self watering hook"},
            {"id": "timer_drip", "name": "ระบบน้ำหยด PE พร้อมไทม์เมอร์ก๊อกน้ำ", "name_en": "Faucet Hose Timer + Drip Kit", "name_de": "Wasserhahn-Timer mit Tropfbewässerung", "qty": 1, "price_usd": 24.0, "search": "outdoor faucet hose timer with drip distribution tubing"}
        ]
    }
}

def get_amazon_link(keyword):
    encoded = urllib.parse.quote_plus(keyword)
    return f"https://www.amazon.com/s?k={encoded}&tag={AMAZON_AFFILIATE_TAG}"

# ==========================================================
# 4. ตัวคุมตรรกะ AI ไกด์นำทัวร์
# ==========================================================
def secure_ai_guide(user_query, active_style_data, lang="TH"):
    now = time.time()
    if "last_request_time" not in st.session_state:
        st.session_state.last_request_time = 0
        st.session_state.req_count = 0

    if now - st.session_state.last_request_time < 2.0:
        st.session_state.req_count += 1
        if st.session_state.req_count > 4:
            if lang == "TH": return "⚠️ ระบบตรวจพบคำขอถี่เกินไป กรุณารอสักครู่เพื่อความปลอดภัยครับ"
            elif lang == "DE": return "⚠️ Zu viele Anfragen in kurzer Zeit. Bitte warten Sie einen Moment."
            else: return "⚠️ Too many requests. Please wait a moment for security verification."
    else:
        st.session_state.req_count = 0

    st.session_state.last_request_time = now

    blacklist = ["ignore previous", "hack", "api key", "password", "system prompt", "database", "token", "root"]
    if any(b in user_query.lower() for b in blacklist):
        if lang == "TH": return "🛡️ ขออภัยครับ ระบบอนุญาตให้สอบถามเฉพาะข้อมูลสถาปัตยกรรมจัดสวนในหน้านี้เท่านั้น"
        elif lang == "DE": return "🛡️ Zugriff verweigert: Nur Anfragen zur Gartenarchitektur erlaubt."
        else: return "🛡️ Access restricted: Queries are strictly confined to spatial garden architecture."

    q = user_query.lower()
    title = active_style_data["title_th"] if lang == "TH" else (active_style_data["title_de"] if lang == "DE" else active_style_data["title_en"])
    dim = active_style_data["dimensions"]

    if any(w in q for w in ["วิธีใช้", "ทำยังไง", "ทัวร์", "start", "how", "anleitung"]):
        if lang == "TH": return "🚩 **ขั้นตอนง่ายๆ 3 สเต็ป:**\n1. เลือกสไตล์สวนด้านบน แล้วเปิดกล้องถ่ายมุมห้องจริง\n2. เลื่อนลงมาปรับแต่งทรงกระถาง สี และจำนวนชิ้นในตาราง\n3. กดสั่งซื้ออุปกรณ์ผ่าน Amazon หรือปลดล็อกพิมพ์เขียว 4 เดือนที่ปุ่มด้านล่างครับ"
        elif lang == "DE": return "🚩 **3 einfache Schritte:**\n1. Stil oben wählen und Raum mit Kamera scannen.\n2. Gefäßform, Farbe und Stückzahlen anpassen.\n3. Ausrüstung über Amazon bestellen oder 4-Monats-Bauplan freischalten."
        else: return "🚩 **3 Quick Steps:**\n1. Select style and scan space.\n2. Customize planter forms and quantities.\n3. Order kit via Amazon or unlock the 4-Month Seasonal Blueprint below."

    elif any(w in q for w in ["ขนาด", "พื้นที่", "กว้าง", "dim", "size", "fläche", "maße"]):
        return f"📐 **{title}** -> {dim['width']}m x {dim['height']}m x {dim['depth']}m"

    elif any(w in q for w in ["กระถาง", "สลับ", "เปลี่ยน", "pot", "planter", "topf"]):
        if lang == "TH": return "💡 ปรับทรงกระถางและสีได้ในสเต็ป 2 ลิงก์ค้นหา Amazon จะปรับตรงรุ่นให้อัตโนมัติครับ"
        elif lang == "DE": return "💡 Passen Sie Gefäßform und Farbe in Schritt 2 an. Amazon-Links aktualisieren sich automatisch."
        else: return "💡 Adjust planter forms in Step 2. Amazon catalog search queries will update dynamically."

    elif any(w in q for w in ["อายุ", "4 เดือน", "ราคา", "pass", "price", "preis"]):
        return f"💳 Seasonal Pass: $139.95 USD / €129.00 EUR / ฿5,090 THB ({ACCESS_PERIOD_DAYS} Days full access)"

    else:
        if lang == "TH": return f"🌿 AI ไกด์พร้อมช่วยเหลือครับ สำหรับสไตล์ **{title}** สามารถปรับแต่งอุปกรณ์ได้ที่ตารางด้านล่างเลยครับ"
        elif lang == "DE": return f"🌿 AI-Guide bereit. Für **{title}** können Sie die Ausrüstung unten anpassen."
        else: return f"🌿 AI Guide standing by. Configure individual BOM units for **{title}** below."

# ==========================================================
# 5. ระบบ Session State & Auto-Sync (ภาษาพ่วงสกุลเงิน)
# ==========================================================
if "user_lang" not in st.session_state:
    st.session_state.user_lang = "TH"
if "user_curr" not in st.session_state:
    st.session_state.user_curr = "THB"

def on_lang_change():
    st.session_state.user_curr = LANG_TO_CURR[st.session_state.user_lang]

with st.sidebar:
    st.markdown("### 🌐 เลือกภาษา / Language / Sprache")
    selected_lang = st.radio(
        "Language Selection:",
        ["TH", "EN", "DE"],
        key="user_lang",
        on_change=on_lang_change,
        horizontal=True,
        label_visibility="collapsed"
    )
    t = I18N[selected_lang]

    st.markdown("---")
    st.markdown("### 💱 สกุลเงินชำระ / Currency")
    currency_keys = list(PRICING_CONFIG.keys())
    
    selected_currency_key = st.radio(
        "Currency Selector:",
        currency_keys,
        key="user_curr",
        format_func=lambda x: PRICING_CONFIG[x]["label"],
        horizontal=False
    )
    curr = PRICING_CONFIG[selected_currency_key]

    st.markdown("---")
    st.markdown(f"### {t['sidebar_guide']}")
    st.caption(t['sidebar_safety'])
    
    st.write(f"**{t['quick_questions']}**")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        ask_how = st.button(t['btn_how'], use_container_width=True)
    with col_b2:
        ask_dim = st.button(t['btn_dim'], use_container_width=True)
        
    col_b3, col_b4 = st.columns(2)
    with col_b3:
        ask_pot = st.button(t['btn_pot'], use_container_width=True)
    with col_b4:
        ask_pass = st.button(t['btn_pass'], use_container_width=True)

    if "guide_msg" not in st.session_state:
        st.session_state.guide_msg = "AI99 Ready. Select your design and ask questions anytime."

    active_style_for_guide = CATALOG["STYLE-BAL-01"]
    if ask_how:
        st.session_state.guide_msg = secure_ai_guide("วิธีใช้", active_style_for_guide, selected_lang)
    elif ask_dim:
        st.session_state.guide_msg = secure_ai_guide("ขนาด", active_style_for_guide, selected_lang)
    elif ask_pot:
        st.session_state.guide_msg = secure_ai_guide("กระถาง", active_style_for_guide, selected_lang)
    elif ask_pass:
        st.session_state.guide_msg = secure_ai_guide("ราคา", active_style_for_guide, selected_lang)

    custom_ask = st.text_input(t['ask_input_label'], placeholder=t['ask_placeholder'])
    if st.button(t['btn_send'], use_container_width=True):
        if custom_ask:
            st.session_state.guide_msg = secure_ai_guide(custom_ask, active_style_for_guide, selected_lang)

    st.markdown(f"<div class='guide-bubble'>{st.session_state.guide_msg}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption(f"Affiliate Tag: `{AMAZON_AFFILIATE_TAG}`")
    st.caption(f"Active Sync: **{selected_lang} ➔ {selected_currency_key}**")

# ==========================================================
# 6. ส่วนหัวของเว็บ (HEADER)
# ==========================================================
st.markdown(f"<div class='main-title'>{t['title']}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='sub-title'>{t['subtitle']}</div>", unsafe_allow_html=True)

# ==========================================================
# 7. สเต็ปที่ 1: เลือกสไตล์และสแกนพื้นที่ (พร้อมภาพสไลด์ไหลวน)
# ==========================================================
st.markdown(f"### {t['step1_title']}")

def get_style_title(k, lang):
    item = CATALOG[k]
    if lang == "TH": return f"{item['category']} - {item['title_th']}"
    elif lang == "DE": return f"{item['category']} - {item['title_de']}"
    else: return f"{item['category']} - {item['title_en']}"

style_keys = list(CATALOG.keys())
selected_key = st.selectbox(
    t['style_label'],
    style_keys,
    format_func=lambda x: get_style_title(x, selected_lang)
)

current_style = CATALOG[selected_key]
dim = current_style["dimensions"]
style_disp_title = current_style["title_th"] if selected_lang == "TH" else (current_style["title_de"] if selected_lang == "DE" else current_style["title_en"])

col1, col2 = st.columns([1, 1])

# โค้ด HTML แบนเนอร์ภาพไหลวนอัตโนมัติ
CAROUSEL_HTML = """
<div class="carousel-track-container">
    <div class="carousel-track">
        <div class="carousel-slide">
            <img src="https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=500&q=80" alt="Vertical Garden">
            <div class="carousel-caption">🌿 สวนแนวตั้งระเบียงคอนโด</div>
        </div>
        <div class="carousel-slide">
            <img src="https://images.unsplash.com/photo-1592417817098-8f3d69104a47?w=500&q=80" alt="Mushroom Pod">
            <div class="carousel-caption">🍄 ตู้เห็ดอัจฉริยะในร่ม</div>
        </div>
        <div class="carousel-slide">
            <img src="https://images.unsplash.com/photo-1545241047-6083a3684587?w=500&q=80" alt="Living Plant Shelf">
            <div class="carousel-caption">🪴 ชั้นวางไม้ห้องนั่งเล่น</div>
        </div>
        <div class="carousel-slide">
            <img src="https://images.unsplash.com/photo-1558904541-efa8c4a08931?w=500&q=80" alt="Entrance Green Wall">
            <div class="carousel-caption">🏡 สวนระแนงหน้าบ้าน</div>
        </div>
        <div class="carousel-slide">
            <img src="https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=500&q=80" alt="Vertical Garden">
            <div class="carousel-caption">🌿 สวนแนวตั้งระเบียงคอนโด</div>
        </div>
        <div class="carousel-slide">
            <img src="https://images.unsplash.com/photo-1592417817098-8f3d69104a47?w=500&q=80" alt="Mushroom Pod">
            <div class="carousel-caption">🍄 ตู้เห็ดอัจฉริยะในร่ม</div>
        </div>
        <div class="carousel-slide">
            <img src="https://images.unsplash.com/photo-1545241047-6083a3684587?w=500&q=80" alt="Living Plant Shelf">
            <div class="carousel-caption">🪴 ชั้นวางไม้ห้องนั่งเล่น</div>
        </div>
        <div class="carousel-slide">
            <img src="https://images.unsplash.com/photo-1558904541-efa8c4a08931?w=500&q=80" alt="Entrance Green Wall">
            <div class="carousel-caption">🏡 สวนระแนงหน้าบ้าน</div>
        </div>
    </div>
</div>
"""

with col1:
    st.markdown(f"""
    <div class='white-card'>
        <h4 style='color: #0F172A; margin-top:0;'>{t['dim_title']}</h4>
        <div style='margin-bottom: 12px;'>
            <span class='spec-tag'>{t['dim_w']}: {dim['width']} {t['meter']}</span>
            <span class='spec-tag'>{t['dim_h']}: {dim['height']} {t['meter']}</span>
            <span class='spec-tag'>{t['dim_d']}: {dim['depth']} {t['meter']}</span>
        </div>
        <p style='margin: 0; color: #475569; font-size: 0.9rem;'>
            <b>{t['category_txt']}:</b> {current_style['category']}<br>
            <b>{t['arch_name']}:</b> {style_disp_title}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # วางภาพไหลวนใต้การ์ดสเปกมิติ
    st.markdown(CAROUSEL_HTML, unsafe_allow_html=True)

with col2:
    st.markdown(f"#### {t['scan_title']}")
    cam_mode = st.radio("Camera Option:", t['cam_choice'], horizontal=True, label_visibility="collapsed")
    if cam_mode == t['cam_choice'][0]:
        st.camera_input(t['cam_prompt'])
    else:
        st.file_uploader(t['upload_prompt'], type=["jpg", "png", "jpeg"])

st.markdown("---")

# ==========================================================
# 8. สเต็ปที่ 2: แผงปรับแต่งสินค้า (BOM CUSTOMIZER)
# ==========================================================
st.markdown(f"### {t['step2_title']}")

col_opt1, col_opt2 = st.columns(2)

with col_opt1:
    pot_shape = st.selectbox(t['pot_shape_label'], t['pot_shapes'])

with col_opt2:
    pot_color = st.selectbox(t['pot_color_label'], t['pot_colors'])

st.markdown(f"#### {t['bom_title']}")

if "quantities" not in st.session_state:
    st.session_state.quantities = {}

total_estimated_base = 0.0

for item in current_style["default_items"]:
    item_id = f"{selected_key}_{item['id']}"
    if item_id not in st.session_state.quantities:
        st.session_state.quantities[item_id] = item["qty"]

    c_name, c_qty, c_price, c_aff = st.columns([4, 2, 2, 3])
    
    with c_name:
        item_name = item["name"] if selected_lang == "TH" else (item["name_de"] if selected_lang == "DE" else item["name_en"])
        if item["id"] in ["planter", "pots", "hook_pots"]:
            item_name = f"{item_name} [{pot_shape.split(' ')[0]} - {pot_color.split(' ')[0]}]"
        
        unit_price = item["price_usd"] * curr["multiplier"]
        st.write(f"**{item_name}**")
        st.caption(f"{t['est_price']}: {curr['symbol']}{unit_price:,.2f}")
        
    with c_qty:
        qty = st.number_input(
            f"Qty ({item['id']})", 
            min_value=0, 
            max_value=50, 
            value=st.session_state.quantities[item_id], 
            key=f"input_{item_id}",
            label_visibility="collapsed"
        )
        st.session_state.quantities[item_id] = qty
        
    with c_price:
        subtotal_base = qty * item["price_usd"]
        total_estimated_base += subtotal_base
        subtotal_converted = subtotal_base * curr["multiplier"]
        st.write(f"**{curr['symbol']}{subtotal_converted:,.2f}**")
        
    with c_aff:
        query = f"{item['search']} {pot_color.split(' ')[0]}"
        st.link_button(t['btn_amazon'], get_amazon_link(query))

st.markdown("---")

# ==========================================================
# 9. สเต็ปที่ 3: สรุปยอด & ท่อรับเงิน (จัดแท็บตามภาษาอัตโนมัติ)
# ==========================================================
col_sum, col_buy = st.columns([1, 1])
total_converted = total_estimated_base * curr["multiplier"]

with col_sum:
    st.markdown(f"### {t['step3_title']} `{curr['symbol']}{total_converted:,.2f}`")
    st.caption(t['amazon_note'])

with col_buy:
    search_all = f"{current_style['category']} {pot_color.split(' ')[0]}"
    st.link_button(t['btn_buy_all'], get_amazon_link(search_all), use_container_width=True)

# ----------------------------------------------------------
# ส่วนสัญญา 2 ปุ่มมหัศจรรย์ และแท็บชำระเงินเรียงตามภาษา
# ----------------------------------------------------------
st.markdown(f"""
<div class='legal-box'>
    <b>{t['legal_title']} ({curr['format']} / {ACCESS_PERIOD_DAYS} Days):</b><br>
    {t['legal_rule1']}<br>
    {t['legal_rule2']}<br>
    {t['legal_rule3']}
</div>
""", unsafe_allow_html=True)

chk1 = st.checkbox(t['chk1_txt'])
chk2 = st.checkbox(t['chk2_txt'])

if chk1 and chk2:
    st.success(t['legal_unlock'])
    
    # เรียงลำดับแท็บชำระเงินให้แท็บแรกตรงกับภาษาที่เลือกอัตโนมัติ
    if selected_lang == "TH":
        tab1, tab2, tab3 = st.tabs([f"{t['pay_thb_tab']} - ฿5,090", f"{t['pay_usd_tab']} - $139.95", f"{t['pay_eur_tab']} - €129.00"])
        active_tab_order = ["THB", "USD", "EUR"]
    elif selected_lang == "DE":
        tab1, tab2, tab3 = st.tabs([f"{t['pay_eur_tab']} - €129.00", f"{t['pay_usd_tab']} - $139.95", f"{t['pay_thb_tab']} - ฿5,090"])
        active_tab_order = ["EUR", "USD", "THB"]
    else:
        tab1, tab2, tab3 = st.tabs([f"{t['pay_usd_tab']} - $139.95", f"{t['pay_eur_tab']} - €129.00", f"{t['pay_thb_tab']} - ฿5,090"])
        active_tab_order = ["USD", "EUR", "THB"]

    tab_map = {active_tab_order[0]: tab1, active_tab_order[1]: tab2, active_tab_order[2]: tab3}

    # แท็บ USD
    with tab_map["USD"]:
        st.write(t['pay_stripe_desc'])
        st.link_button(f"{t['btn_stripe']} ($139.95 USD / 4 Months)", STRIPE_URL_USD, use_container_width=True)

    # แท็บ EUR
    with tab_map["EUR"]:
        st.write(t['pay_stripe_desc'])
        st.link_button(f"{t['btn_stripe']} (€129.00 EUR / 4 Monate)", STRIPE_URL_EUR, use_container_width=True)

    # แท็บ THB
    with tab_map["THB"]:
        st.write(f"{t['pay_thb_desc']} ยอดชำระ: **฿5,090 บาท** (สิทธิ์ 4 เดือนเต็ม)")
        qr_code_url = f"https://promptpay.io/{PROMPTPAY_ID}/5090.png"
        col_q, col_s = st.columns([1, 1])
        with col_q:
            st.image(qr_code_url, caption=f"PromptPay ID: {PROMPTPAY_ID}", width=220)
        with col_s:
            st.file_uploader(t['upload_slip'], type=["jpg", "png", "pdf"])
            if st.button(t['btn_slip']):
                st.info(t['slip_ok'])
else:
    st.info(t['legal_lock'])
