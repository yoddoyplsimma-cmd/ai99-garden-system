import streamlit as st
import urllib.parse
import time
from datetime import datetime
import os

# ==============================================================================
# SECTION 1: GLOBAL CONFIGURATION, HEADERS & MULTI-CURRENCY ENGINE
# ==============================================================================
AMAZON_AFFILIATE_TAG = "ybcai99garden-20"
ACCESS_PERIOD_DAYS = 120  # สิทธิ์เข้าถึงระบบ 4 เดือนเต็ม (1 ไตรมาส)

# ท่อชำระเงินจริงสำหรับ Seasonal Access Pass
STRIPE_URL_USD = "https://buy.stripe.com/your_actual_stripe_link_usd"
STRIPE_URL_EUR = "https://buy.stripe.com/your_actual_stripe_link_eur"
PROMPTPAY_ID = "0812345678"  # PromptPay ID บัญชีพี่ยอด CEO

# โครงสร้างราคาและอัตราแปลงสกุลเงินคงที่ (Fixed Production Rates)
PRICING_CONFIG = {
    "USD": {
        "symbol": "$",
        "rate": 139.95,
        "format": "$139.95",
        "multiplier": 1.0,
        "label": "USD ($139.95) - US & International"
    },
    "EUR": {
        "symbol": "€",
        "rate": 129.00,
        "format": "€129.00",
        "multiplier": 0.9217,
        "label": "EUR (€129.00) - European Union"
    },
    "THB": {
        "symbol": "฿",
        "rate": 5090.00,
        "format": "5,090 บาท",
        "multiplier": 36.37,
        "label": "THB (฿5,090) - Thai PromptPay"
    }
}

LANG_TO_CURR = {
    "TH": "THB",
    "EN": "USD",
    "DE": "EUR"
}

st.set_page_config(
    page_title="AI 99 Garden Design",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling ปรับ UI ให้อ่านง่าย คมชัดทั้ง Light และ Dark Mode
st.markdown("""
<style>
    /* บังคับสีพื้นหลังและการ์ดให้อ่านออก 100% */
    .main-title { 
        font-size: 2.2rem; 
        font-weight: 800; 
        color: #10B981 !important; 
        margin-bottom: 4px; 
    }
    .sub-title { 
        font-size: 1.05rem; 
        color: #94A3B8 !important; 
        margin-bottom: 24px; 
    }
    .app-card { 
        background-color: #1E293B; 
        border: 1px solid #334155; 
        border-radius: 12px; 
        padding: 20px; 
        margin-bottom: 16px; 
        color: #F8FAFC !important;
    }
    .spec-tag { 
        background-color: #0F172A; 
        color: #38BDF8 !important; 
        font-weight: 700; 
        padding: 6px 14px; 
        border-radius: 8px; 
        font-size: 0.88rem; 
        margin-right: 8px; 
        border: 1px solid #1E293B;
        display: inline-block;
    }
    .legal-box { 
        background-color: #1E293B; 
        border-left: 5px solid #F59E0B; 
        border-top: 1px solid #334155;
        border-right: 1px solid #334155;
        border-bottom: 1px solid #334155;
        padding: 18px; 
        border-radius: 8px; 
        margin: 20px 0px; 
        font-size: 0.95rem; 
        color: #E2E8F0 !important;
        line-height: 1.6;
    }
    .bom-row {
        background: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 10px;
        align-items: center;
    }
    /* Infinite Image Carousel */
    .carousel-track-container {
        overflow: hidden;
        width: 100%;
        border-radius: 12px;
        margin-top: 14px;
        border: 1px solid #334155;
        background: #0F172A;
        padding: 8px 0;
    }
    .carousel-track {
        display: flex;
        width: calc(200px * 8);
        animation: scroll-left 20s linear infinite;
    }
    .carousel-track:hover {
        animation-play-state: paused;
    }
    .carousel-slide {
        width: 200px;
        padding: 6px;
        flex-shrink: 0;
    }
    .carousel-slide img {
        width: 100%;
        height: 130px;
        object-fit: cover;
        border-radius: 8px;
        border: 1px solid #334155;
    }
    @keyframes scroll-left {
        0% { transform: translateX(0); }
        100% { transform: translateX(calc(-200px * 4)); }
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# SECTION 2: LOCALIZATION (TH / EN / DE)
# ==============================================================================
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
        "ask_placeholder": "สอบถามขนาด สเปก หรือวิธีสั่งซื้อ...",
        "btn_send": "ส่งคำถาม",
        "step1_title": "1. เลือกสไตล์สวนและใส่ภาพพื้นที่",
        "style_label": "เลือกสไตล์สวนมาตรฐานที่คำนวณโครงสร้างแล้ว:",
        "dim_title": "📌 สเปกมิติมาตรฐาน (Standard Space Dimensions)",
        "dim_w": "ความกว้าง", "dim_h": "ความสูง", "dim_d": "ความลึก", "meter": "เมตร",
        "category_txt": "หมวดหมู่", "arch_name": "ชื่อสถาปัตยกรรม",
        "scan_header": "📷 อัปโหลดหรือสแกนภาพมุมบ้านของคุณ",
        "scan_desc": "อัปโหลดภาพมุมระเบียงหรือห้อง เพื่อให้ระบบจัดวางชุดอุปกรณ์ลงในพื้นที่ได้อย่างแม่นยำ",
        "cam_choice": ["📁 อัปโหลดรูปภาพ (Upload File)", "📷 ถ่ายภาพสด (Live Camera)"],
        "cam_prompt": "เปิดกล้องเพื่อถ่ายภาพมุมที่ต้องการจัดวาง",
        "upload_prompt": "เลือกไฟล์ภาพสวน/ระเบียง (JPG, PNG)",
        "step2_title": "2. ปรับแต่งทรงกระถางและดูชุดอุปกรณ์ (BOM)",
        "pot_shape_label": "เลือกรูปทรงกระถาง / รางปลูก:",
        "pot_shapes": [
            "รางยาวมินิมอล (Rectangular Trough)", 
            "ทรงกระบอกโมเดิร์น (Cylinder Modern)", 
            "สี่เหลี่ยมลูกบาศก์ (Square Cube)", 
            "ทรงกลมคลาสสิก (Round Classic)"
        ],
        "pot_color_label": "เลือกโทนสีและเนื้อวัสดุ:",
        "pot_colors": [
            "ดำด้านลอฟท์ (Matte Black)", 
            "ขาวคลีนมินิมอล (Matte White)", 
            "เทาคอนกรีตโมเดิร์น (Concrete Grey)", 
            "ดินเผาธรรมชาติ (Terracotta)"
        ],
        "bom_title": "📦 ตารางรายการอุปกรณ์ในเซ็ต (Bill of Materials)",
        "col_name": "รายการอุปกรณ์",
        "col_qty": "จำนวน",
        "col_price": "ราคาแปลง",
        "col_link": "สั่งซื้อ",
        "est_price": "ราคาเฉลี่ย", 
        "btn_amazon": "Amazon ↗",
        "step3_title": "ราคารวมอุปกรณ์โดยประมาณ:",
        "amazon_note": "* ราคาสินค้าจริงขึ้นอยู่กับผู้ขายบน Amazon ณ วันที่ทำรายการ",
        "btn_buy_all": "🛒 สั่งซื้ออุปกรณ์ชุดนี้ทั้งหมดบน Amazon (One-Click)",
        "legal_title": "⚖️ ข้อตกลงสิทธิ์การใช้งาน Seasonal Access Pass",
        "legal_rule1": f"- สิทธิ์เข้าถึงแบบแปลนและระบบคำนวณสถาปัตยกรรม <b>{ACCESS_PERIOD_DAYS} วัน (4 เดือนเต็ม)</b>",
        "legal_rule2": "- หมดอายุอัตโนมัติ ไม่มีการเรียกเก็บเงินซ้ำซ้อน",
        "legal_rule3": "- สิทธิ์ใช้งานระบบถือเป็นสินทรัพย์ดิจิทัลเสร็จสมบูรณ์ทันที มีผลผูกพันตามกฎหมาย",
        "legal_notice": "ℹ️ ทำเครื่องหมายยอมรับข้อตกลง 2 ข้อด้านล่าง เพื่อเปิดท่อชำระเงินสำหรับสิทธิ์ 120 วัน",
        "chk1_txt": "1. ยอมรับข้อตกลงและนโยบายทรัพย์สินทางปัญญาของ AI99",
        "chk2_txt": "2. ยืนยันสละสิทธิ์การขอคืนเงินทุกกรณี 100% หลังเข้าถึงระบบ",
        "legal_unlock": "✅ ยืนยันข้อกำหนดเรียบร้อย ปลดล็อกระบบชำระเงินแล้ว",
        "legal_lock": "กรุณาติ๊กยอมรับเงื่อนไข 2 ข้อด้านบน เพื่อปลดล็อกช่องทางการชำระเงิน",
        "pay_usd_tab": "💳 บัตรเครดิตสากล (USD)", 
        "pay_eur_tab": "💶 บัตรเครดิตยุโรป (EUR)", 
        "pay_thb_tab": "📱 สแกน QR พร้อมเพย์ (THB)",
        "pay_stripe_desc": "ชำระผ่านระบบความปลอดภัย Stripe สากล",
        "btn_stripe": "🚀 ปลดล็อกสิทธิ์ 4 เดือน",
        "pay_thb_desc": "สแกน QR Code พร้อมเพย์ ชำระตรงเข้าบัญชี",
        "upload_slip": "แนบสลิปโอนเงินเพื่อปลดล็อกสิทธิ์ใช้งาน:",
        "btn_slip": "ยืนยันการส่งสลิป",
        "slip_ok": "ระบบได้รับข้อมูลสลิปเรียบร้อยแล้ว กำลังตรวจสอบเปิดสิทธิ์การใช้งานครับ"
    },
    "EN": {
        "title": "🌿 AI 99 Garden Design",
        "subtitle": "Precision Area Computation • Modular Shapes & Colors • Complete Kit Sourcing",
        "sidebar_guide": "🤖 Assistant Guide (AI Guide)",
        "sidebar_safety": "Safety Logic Protocol: Zero-Hallucination Guard",
        "quick_questions": "Frequently Asked Questions:",
        "btn_how": "🚩 How to Use",
        "btn_dim": "📐 Check Dimensions",
        "btn_pot": "🪴 Customize Pots",
        "btn_pass": "⏳ 4-Month Pass",
        "ask_input_label": "Ask AI Guide:",
        "ask_placeholder": "Inquire dimensions, BOM specs, or orders...",
        "btn_send": "Send Inquiry",
        "step1_title": "1. Select Architecture & Upload Photo",
        "style_label": "Engineered Standard Archetypes:",
        "dim_title": "📌 Standard Specifications & Dimensions",
        "dim_w": "Width", "dim_h": "Height", "dim_d": "Depth", "meter": "m",
        "category_txt": "Category", "arch_name": "Architecture Title",
        "scan_header": "📷 Upload or Scan Space Image",
        "scan_desc": "Provide a photo of your balcony or room corner for accurate spatial computation.",
        "cam_choice": ["📁 Upload File", "📷 Live Camera"],
        "cam_prompt": "Scan your balcony or room with camera",
        "upload_prompt": "Select room/balcony photo (JPG, PNG)",
        "step2_title": "2. Customize Shape, Color & Materials (BOM)",
        "pot_shape_label": "Select Planter Style / Shape:",
        "pot_shapes": ["Rectangular Trough", "Cylinder Modern", "Square Cube", "Round Classic"],
        "pot_color_label": "Select Material Texture & Color:",
        "pot_colors": ["Matte Black Loft", "Matte White Minimal", "Concrete Grey Modern", "Terracotta Natural"],
        "bom_title": "📦 Bill of Materials (BOM Dataset)",
        "col_name": "Item Description",
        "col_qty": "Qty",
        "col_price": "Converted Price",
        "col_link": "Source",
        "est_price": "Unit Price", 
        "btn_amazon": "Amazon ↗",
        "step3_title": "Estimated Equipment Total:",
        "amazon_note": "* Live prices subject to vendor listings on Amazon at checkout.",
        "btn_buy_all": "🛒 Order Full Kit on Amazon (One-Click)",
        "legal_title": "⚖️ Seasonal Access Pass Terms of Service",
        "legal_rule1": f"- Grants full blueprint and dimensional access for <b>{ACCESS_PERIOD_DAYS} days (4 Months)</b>",
        "legal_rule2": "- Automatically ends without recurring charges.",
        "legal_rule3": "- System access is deemed complete upon delivery of digital assets.",
        "legal_notice": "ℹ️ Accept both terms below to unlock 120-day pass checkout.",
        "chk1_txt": "1. I accept the AI99 Terms of Service and Intellectual Property Policy.",
        "chk2_txt": "2. I acknowledge and agree to 100% Strict Non-Refundable Policy upon digital delivery.",
        "legal_unlock": "✅ Terms accepted. Checkout is unlocked.",
        "legal_lock": "Please confirm both checkboxes to unlock the payment gateway.",
        "pay_usd_tab": "💳 International Card (USD)", 
        "pay_eur_tab": "💶 European Card (EUR)", 
        "pay_thb_tab": "📱 PromptPay QR (THB)",
        "pay_stripe_desc": "Secure checkout powered by Stripe Global.",
        "btn_stripe": "🚀 Unlock 4-Month Access",
        "pay_thb_desc": "Scan PromptPay QR for direct local transfer.",
        "upload_slip": "Upload bank transfer confirmation slip:",
        "btn_slip": "Submit Transfer Slip",
        "slip_ok": "Slip received. Activating your seasonal account now."
    },
    "DE": {
        "title": "🌿 AI99 Intelligentes Garten-Raumplanungssystem",
        "subtitle": "Präzise Raumberechnung • Individuelle Formen & Farben • Vollständiges Ausrüstungsset",
        "sidebar_guide": "🤖 Systemassistent (AI Guide)",
        "sidebar_safety": "Sicherheitskontrolle: Zero-Hallucination Guard",
        "quick_questions": "Häufige Fragen:",
        "btn_how": "🚩 Anleitung",
        "btn_dim": "📐 Maße prüfen",
        "btn_pot": "🪴 Gefäße anpassen",
        "btn_pass": "⏳ 4-Monats-Pass",
        "ask_input_label": "Frage an den AI-Guide:",
        "ask_placeholder": "Maße, Stückliste oder Bestellung anfragen...",
        "btn_send": "Frage senden",
        "step1_title": "1. Stil wählen & Raumbild erfassen",
        "style_label": "Berechnete Standard-Architekturmodelle:",
        "dim_title": "📌 Standardspezifikationen & Abmessungen",
        "dim_w": "Breite", "dim_h": "Höhe", "dim_d": "Tiefe", "meter": "m",
        "category_txt": "Kategorie", "arch_name": "Architektur-Titel",
        "scan_header": "📷 Raumbild hochladen oder aufnehmen",
        "scan_desc": "Erfassen Sie Ihren Balkon oder Raum für präzise Maßberechnungen.",
        "cam_choice": ["📁 Datei-Upload", "📷 Live-Kamera"],
        "cam_prompt": "Balkon oder Raumecke scannen",
        "upload_prompt": "Raumbild auswählen (JPG, PNG)",
        "step2_title": "2. Formen, Farben & Stückliste anpassen (BOM)",
        "pot_shape_label": "Pflanzgefäß-Form auswählen:",
        "pot_shapes": ["Rechteckiger Trog (Minimal)", "Zylinder Modern", "Würfel (Square)", "Runder Topf (Klassisch)"],
        "pot_color_label": "Farbton & Textur auswählen:",
        "pot_colors": ["Mattschwarz Loft", "Mattweiß Minimal", "Betongrau Modern", "Terrakotta Natur"],
        "bom_title": "📦 Stückliste der Ausrüstung (Bill of Materials)",
        "col_name": "Artikelname",
        "col_qty": "Menge",
        "col_price": "Preis",
        "col_link": "Kauf",
        "est_price": "Einzelpreis", 
        "btn_amazon": "Amazon ↗",
        "step3_title": "Geschätzte Gesamtkosten:",
        "amazon_note": "* Tatsächliche Preise hängen vom jeweiligen Amazon-Händler ab.",
        "btn_buy_all": "🛒 Gesamte Ausrüstung mit einem Klick auf Amazon bestellen",
        "legal_title": "⚖️ Nutzungsbedingungen für Seasonal Access Pass",
        "legal_rule1": f"- Gültig für vollen Zugriff auf Baupläne für <b>{ACCESS_PERIOD_DAYS} Tage (4 Monate)</b>",
        "legal_rule2": "- Endet automatisch nach 120 Tagen ohne Folgekosten.",
        "legal_rule3": "- Der Systemzugang gilt als vollständige digitale Bereitstellung.",
        "legal_notice": "ℹ️ Bitte bestätigen Sie beide Felder für die Freischaltung.",
        "chk1_txt": "1. Ich akzeptiere die AI99-Nutzungsbedingungen und Richtlinien.",
        "chk2_txt": "2. Ich bestätige den 100%igen Verzicht auf Rückerstattung nach Bereitstellung.",
        "legal_unlock": "✅ Bedingungen akzeptiert. Zahlung freigeschaltet.",
        "legal_lock": "Bitte bestätigen Sie die Pflichtfelder zur Zahlungsfreigabe.",
        "pay_usd_tab": "💳 Internationale Karte (USD)", 
        "pay_eur_tab": "💶 Europäische Karte (EUR)", 
        "pay_thb_tab": "📱 PromptPay QR (THB)",
        "pay_stripe_desc": "Sicher über Stripe bezahlen.",
        "btn_stripe": "🚀 4-Monats-Zugang freischalten",
        "pay_thb_desc": "PromptPay QR für Überweisung scannen.",
        "upload_slip": "Zahlungsbeleg hochladen:",
        "btn_slip": "Beleg übermitteln",
        "slip_ok": "Beleg empfangen. Der Zugang wird unverzüglich aktiviert."
    }
}

# ==============================================================================
# SECTION 3: MASTER ARCHITECTURAL CATALOG
# ==============================================================================
CATALOG = {
    "STYLE-BAL-01": {
        "title_th": "สวนผักสลัดแนวตั้งระเบียงคอนโด (Verdant Balcony Kit)",
        "title_en": "Minimalist Vertical Balcony Salad Kit",
        "title_de": "Minimalistischer Vertikaler Balkon-Salatgarten",
        "category": "Balcony Micro-Space",
        "dimensions": {"width": 1.20, "height": 2.00, "depth": 0.45},
        "default_items": [
            {"id": "rack", "name": "โครงชั้นวางกัลวาไนซ์ 4-5 ชั้น ทรง Slim", "name_en": "Slim Galvanized 5-Tier Rack", "name_de": "Schlankes 5-Etagen-Regal Verzinkt", "qty": 1, "price_usd": 45.0, "search": "vertical garden wall planter rack outdoor"},
            {"id": "planter", "name": "รางปลูกผักสลัด Food-grade ทน UV", "name_en": "Food-grade UV Resistant Planter Box", "name_de": "UV-beständiger Pflanzkasten", "qty": 4, "price_usd": 8.0, "search": "rectangular planter box UV resistant"},
            {"id": "drip", "name": "ชุดระบบน้ำหยดอัตโนมัติ Micro-drip", "name_en": "Automatic Micro-Drip Irrigation Kit", "name_de": "Automatisches Micro-Drip Bewässerungsset", "qty": 1, "price_usd": 18.5, "search": "automatic micro drip irrigation kit balcony"},
            {"id": "soil", "name": "ดินปลูกสูตรมินิมอลระบายน้ำไว (50L)", "name_en": "Organic Lightweight Potting Mix (50L)", "name_de": "Organische Pflanzerde leicht (50L)", "qty": 2, "price_usd": 12.0, "search": "organic potting mix perlite lightweight"}
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
            {"id": "humidifier", "name": "เครื่องพ่นหมอก Ultrasonic + เซนเซอร์", "name_en": "Ultrasonic Mist Maker + Sensor", "name_de": "Ultraschall-Vernebler mit Sensor", "qty": 1, "price_usd": 28.0, "search": "ultrasonic mist maker with humidity controller"},
            {"id": "spores", "name": "ก้อนเชื้อเห็ดพรีเมียม (Oyster/Lion's Mane)", "name_en": "Organic Mushroom Grow Kit Substrate", "name_de": "Bio-Pilzzucht Substratblöcke", "qty": 4, "price_usd": 6.5, "search": "organic mushroom grow kit lion mane oyster"},
            {"id": "light", "name": "ไฟ LED Bar 5W สเปกตรัมขาว", "name_en": "5W White Spectrum LED Grow Bar", "name_de": "5W Weißspektrum LED-Leiste", "qty": 1, "price_usd": 14.0, "search": "small indoor led grow light bar for plants"}
        ]
    },
    "STYLE-IND-01": {
        "title_th": "ชั้นวางไม้และไฟปลูกในห้องรับแขก (Living Plant Shelf)",
        "title_en": "Living Room Aesthetic Greenery Stand",
        "title_de": "Ästhetisches Wohnzimmer-Pflanzenregal",
        "category": "Indoor Greenery",
        "dimensions": {"width": 1.00, "height": 1.60, "depth": 0.35},
        "default_items": [
            {"id": "wood_rack", "name": "ชั้นวางไม้โครงเหล็กนอร์ดิก 4 ชั้น", "name_en": "4-Tier Nordic Metal Wood Plant Stand", "name_de": "4-stufiges Metall-Holz-Pflanzenregal", "qty": 1, "price_usd": 62.0, "search": "tiered plant stand indoor metal wood tall"},
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

# ==============================================================================
# SECTION 4: SECURITY LAYER
# ==============================================================================
def secure_ai_guide(user_query, active_style_data, lang="TH"):
    dim = active_style_data["dimensions"]
    title = active_style_data["title_th"] if lang == "TH" else (active_style_data["title_de"] if lang == "DE" else active_style_data["title_en"])
    q = user_query.lower()
    
    if any(w in q for w in ["วิธีใช้", "how", "anleitung"]):
        return "🚩 1. เลือกสไตล์สวน 2. อัปโหลดภาพพื้นที่ 3. ปรับขนาดชิ้นส่วนและสั่งซื้อบน Amazon"
    elif any(w in q for w in ["ขนาด", "dim", "size", "maße"]):
        return f"📐 {title}: กว้าง {dim['width']}ม. x สูง {dim['height']}ม. x ลึก {dim['depth']}ม."
    else:
        return f"🌿 AI Guide พร้อมให้คำปรึกษาสไตล์ {title} ปรับอุปกรณ์ในสเต็ป 2 ได้ทันทีครับ"

# ==============================================================================
# SECTION 5: SIDEBAR
# ==============================================================================
if "user_lang" not in st.session_state:
    st.session_state.user_lang = "TH"
if "user_curr" not in st.session_state:
    st.session_state.user_curr = "THB"

def on_lang_change():
    st.session_state.user_curr = LANG_TO_CURR[st.session_state.user_lang]

with st.sidebar:
    st.markdown("### 🌐 ภาษา / Language")
    st.radio("Language:", ["TH", "EN", "DE"], key="user_lang", on_change=on_lang_change, horizontal=True, label_visibility="collapsed")
    t = I18N[st.session_state.user_lang]

    st.markdown("---")
    st.markdown("### 💱 สกุลเงิน / Currency")
    st.radio("Currency:", list(PRICING_CONFIG.keys()), key="user_curr", format_func=lambda x: PRICING_CONFIG[x]["label"], label_visibility="collapsed")
    curr = PRICING_CONFIG[st.session_state.user_curr]

    st.markdown("---")
    st.markdown(f"### {t['sidebar_guide']}")
    st.caption(t['sidebar_safety'])
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        ask_how = st.button(t['btn_how'], use_container_width=True)
    with col_b2:
        ask_dim = st.button(t['btn_dim'], use_container_width=True)
        
    if "guide_msg" not in st.session_state:
        st.session_state.guide_msg = "AI99 Ready. Select your design and customize anytime."

    active_style_for_guide = CATALOG["STYLE-BAL-01"]
    if ask_how:
        st.session_state.guide_msg = secure_ai_guide("วิธีใช้", active_style_for_guide, st.session_state.user_lang)
    elif ask_dim:
        st.session_state.guide_msg = secure_ai_guide("ขนาด", active_style_for_guide, st.session_state.user_lang)

    st.info(st.session_state.guide_msg)
    st.markdown("---")
    st.caption(f"Affiliate Tag: `{AMAZON_AFFILIATE_TAG}`")

# ==============================================================================
# SECTION 6: WORKSPACE HEADER
# ==============================================================================
st.markdown(f"<div class='main-title'>{t['title']}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='sub-title'>{t['subtitle']}</div>", unsafe_allow_html=True)

# ==============================================================================
# SECTION 7: STEP 1 - ARCHITECTURE & CAROUSEL
# ==============================================================================
st.markdown(f"### {t['step1_title']}")

style_keys = list(CATALOG.keys())
selected_key = st.selectbox(
    t['style_label'],
    style_keys,
    format_func=lambda x: f"{CATALOG[x]['category']} - {CATALOG[x]['title_th'] if st.session_state.user_lang=='TH' else (CATALOG[x]['title_de'] if st.session_state.user_lang=='DE' else CATALOG[x]['title_en'])}"
)

current_style = CATALOG[selected_key]
dim = current_style["dimensions"]
style_disp_title = current_style["title_th"] if st.session_state.user_lang == "TH" else (
    current_style["title_de"] if st.session_state.user_lang == "DE" else current_style["title_en"]
)

col1, col2 = st.columns([1, 1], gap="medium")

IMG_BALCONY = "https://lh3.googleusercontent.com/d/1y3A2kCG-JhqbysqN6e0M5aG4iiG3HRdD"
IMG_MUSHROOM = "https://lh3.googleusercontent.com/d/1xcOBnsLuCZBM7gVe8XURQqrlnP7-R-pO"
IMG_INDOOR = "https://lh3.googleusercontent.com/d/1-8q8l4pGELAYp0_tn6Z387aq9XclS_3p"
IMG_TRELLIS = "https://lh3.googleusercontent.com/d/1AjZgaGwLXlwB7neIQLvUmLmYR3-b3YJF"

CAROUSEL_HTML = f"""
<div class="carousel-track-container">
    <div class="carousel-track">
        <div class="carousel-slide"><img src="{IMG_BALCONY}"></div>
        <div class="carousel-slide"><img src="{IMG_MUSHROOM}"></div>
        <div class="carousel-slide"><img src="{IMG_INDOOR}"></div>
        <div class="carousel-slide"><img src="{IMG_TRELLIS}"></div>
        <div class="carousel-slide"><img src="{IMG_BALCONY}"></div>
        <div class="carousel-slide"><img src="{IMG_MUSHROOM}"></div>
        <div class="carousel-slide"><img src="{IMG_INDOOR}"></div>
        <div class="carousel-slide"><img src="{IMG_TRELLIS}"></div>
    </div>
</div>
"""

with col1:
    st.markdown(f"""
    <div class='app-card'>
        <h4 style='color: #F8FAFC; margin-top:0;'>{t['dim_title']}</h4>
        <div style='margin-bottom: 12px;'>
            <span class='spec-tag'>{t['dim_w']}: {dim['width']} {t['meter']}</span>
            <span class='spec-tag'>{t['dim_h']}: {dim['height']} {t['meter']}</span>
            <span class='spec-tag'>{t['dim_d']}: {dim['depth']} {t['meter']}</span>
        </div>
        <p style='margin: 0; color: #94A3B8; font-size: 0.92rem; line-height: 1.6;'>
            <b>{t['category_txt']}:</b> {current_style['category']}<br>
            <b>{t['arch_name']}:</b> {style_disp_title}
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(CAROUSEL_HTML, unsafe_allow_html=True)

with col2:
    st.markdown(f"#### {t['scan_header']}")
    st.caption(t['scan_desc'])
    # ตั้งตัวเลือกเริ่มต้นเป็น Upload เพื่อป้องกันจอดำกินพื้นที่
    cam_mode = st.radio("Camera Option:", t['cam_choice'], index=0, horizontal=True, label_visibility="collapsed")
    if cam_mode == t['cam_choice'][1]:
        st.camera_input(t['cam_prompt'])
    else:
        st.file_uploader(t['upload_prompt'], type=["jpg", "png", "jpeg"])

st.markdown("---")

# ==============================================================================
# SECTION 8: STEP 2 - INTERACTIVE BOM CONFIGURATOR
# ==============================================================================
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

# ส่วนแสดงรายการอุปกรณ์พร้อมกรอบชัดเจน
for item in current_style["default_items"]:
    item_id = f"{selected_key}_{item['id']}"
    if item_id not in st.session_state.quantities:
        st.session_state.quantities[item_id] = item["qty"]

    item_name = item["name"] if st.session_state.user_lang == "TH" else (
        item["name_de"] if st.session_state.user_lang == "DE" else item["name_en"]
    )
    if item["id"] in ["planter", "pots", "hook_pots"]:
        item_name = f"{item_name} [{pot_shape.split(' ')[0]} - {pot_color.split(' ')[0]}]"
    
    unit_price = item["price_usd"] * curr["multiplier"]
    
    with st.container():
        c_name, c_qty, c_price, c_aff = st.columns([5, 2, 2, 3])
        with c_name:
            st.markdown(f"**{item_name}**")
            st.caption(f"{t['est_price']}: {curr['symbol']}{unit_price:,.2f}")
        with c_qty:
            qty = st.number_input(
                f"Qty_{item_id}", 
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
            st.markdown(f"**{curr['symbol']}{subtotal_converted:,.2f}**")
        with c_aff:
            query = f"{item['search']} {pot_color.split(' ')[0]}"
            st.link_button(t['btn_amazon'], get_amazon_link(query), use_container_width=True)

st.markdown("---")

# ==============================================================================
# SECTION 9: STEP 3 - TOTAL CHECKOUT, LEGAL CONSENT & PAYMENT
# ==============================================================================
col_sum, col_buy = st.columns([1, 1])
total_converted = total_estimated_base * curr["multiplier"]

with col_sum:
    st.markdown(f"### {t['step3_title']} `{curr['symbol']}{total_converted:,.2f}`")
    st.caption(t['amazon_note'])

with col_buy:
    search_all = f"{current_style['category']} {pot_color.split(' ')[0]}"
    st.link_button(t['btn_buy_all'], get_amazon_link(search_all), use_container_width=True)

st.markdown(f"""
<div class='legal-box'>
    <b>{t['legal_title']} ({curr['format']} / {ACCESS_PERIOD_DAYS} Days):</b><br>
    {t['legal_rule1']}<br>
    {t['legal_rule2']}<br>
    {t['legal_rule3']}
</div>
""", unsafe_allow_html=True)

st.info(t['legal_notice'])

chk1 = st.checkbox(t['chk1_txt'])
chk2 = st.checkbox(t['chk2_txt'])

if chk1 and chk2:
    st.success(t['legal_unlock'])
    
    if st.session_state.user_lang == "TH":
        tab1, tab2, tab3 = st.tabs([f"{t['pay_thb_tab']} - ฿5,090", f"{t['pay_usd_tab']} - $139.95", f"{t['pay_eur_tab']} - €129.00"])
        active_order = ["THB", "USD", "EUR"]
    elif st.session_state.user_lang == "DE":
        tab1, tab2, tab3 = st.tabs([f"{t['pay_eur_tab']} - €129.00", f"{t['pay_usd_tab']} - $139.95", f"{t['pay_thb_tab']} - ฿5,090"])
        active_order = ["EUR", "USD", "THB"]
    else:
        tab1, tab2, tab3 = st.tabs([f"{t['pay_usd_tab']} - $139.95", f"{t['pay_eur_tab']} - €129.00", f"{t['pay_thb_tab']} - ฿5,090"])
        active_order = ["USD", "EUR", "THB"]

    tab_map = {active_order[0]: tab1, active_order[1]: tab2, active_order[2]: tab3}

    with tab_map["USD"]:
        st.write(t['pay_stripe_desc'])
        st.link_button(f"{t['btn_stripe']} ($139.95 USD)", STRIPE_URL_USD, use_container_width=True)

    with tab_map["EUR"]:
        st.write(t['pay_stripe_desc'])
        st.link_button(f"{t['btn_stripe']} (€129.00 EUR)", STRIPE_URL_EUR, use_container_width=True)

    with tab_map["THB"]:
        st.write(f"{t['pay_thb_desc']} ยอดชำระ: **฿5,090 บาท**")
        qr_code_url = f"https://promptpay.io/{PROMPTPAY_ID}/5090.png"
        col_q, col_s = st.columns([1, 1])
        with col_q:
            st.image(qr_code_url, caption=f"PromptPay ID: {PROMPTPAY_ID}", width=230)
        with col_s:
            st.file_uploader(t['upload_slip'], type=["jpg", "png", "pdf"])
            if st.button(t['btn_slip']):
                st.info(t['slip_ok'])
else:
    st.warning(t['legal_lock'])
