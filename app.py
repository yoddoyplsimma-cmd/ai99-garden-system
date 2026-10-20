import streamlit as st
import urllib.parse
import time
from datetime import datetime
import os

# ==============================================================================
# SECTION 1: GLOBAL CONFIGURATION, PWA HEADERS & MULTI-CURRENCY ENGINE
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

# แผนผังผูกภาษาเข้ากับสกุลเงินอัตโนมัติ (Language to Default Currency Mapping)
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

# Custom Styling สไตล์มินิมอลโมเดิร์น + แถบภาพวิ่งอัตโนมัติคลีนๆ ไร้ตัวหนังสือบดบัง (Clean Infinite Flow)
st.markdown("""
<head>
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
</head>
<style>
    .stApp { 
        background-color: #FAFAFA; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .main-title { 
        font-size: 2.2rem; 
        font-weight: 800; 
        color: #1B4D3E; 
        margin-bottom: 2px; 
        letter-spacing: -0.5px;
    }
    .sub-title { 
        font-size: 1.05rem; 
        color: #64748B; 
        margin-bottom: 24px; 
    }
    .white-card { 
        background-color: #FFFFFF; 
        border: 1px solid #E2E8F0; 
        border-radius: 14px; 
        padding: 22px; 
        margin-bottom: 16px; 
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }
    .spec-tag { 
        background-color: #F1F5F9; 
        color: #0F172A; 
        font-weight: 700; 
        padding: 6px 14px; 
        border-radius: 8px; 
        font-size: 0.88rem; 
        margin-right: 8px; 
        border: 1px solid #E2E8F0;
        display: inline-block;
    }
    .legal-box { 
        background-color: #FFFFFF; 
        border-left: 5px solid #F59E0B; 
        border-top: 1px solid #E2E8F0;
        border-right: 1px solid #E2E8F0;
        border-bottom: 1px solid #E2E8F0;
        padding: 20px; 
        border-radius: 10px; 
        margin: 20px 0px; 
        font-size: 0.95rem; 
        color: #334155;
        line-height: 1.6;
    }
    .guide-bubble { 
        background-color: #FFFFFF; 
        border-left: 4px solid #10B981; 
        border-top: 1px solid #E2E8F0;
        border-right: 1px solid #E2E8F0;
        border-bottom: 1px solid #E2E8F0;
        padding: 14px; 
        border-radius: 8px; 
        margin-bottom: 12px; 
        font-size: 0.92rem; 
        color: #1E293B;
        line-height: 1.5;
    }
    /* Infinite Pure Image Carousel Styling */
    .carousel-track-container {
        overflow: hidden;
        width: 100%;
        border-radius: 14px;
        margin-top: 18px;
        border: 1px solid #E2E8F0;
        background: #FFFFFF;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        padding: 6px 0;
    }
    .carousel-track {
        display: flex;
        width: calc(240px * 8);
        animation: scroll-left 24s linear infinite;
    }
    .carousel-track:hover {
        animation-play-state: paused;
    }
    .carousel-slide {
        width: 240px;
        padding: 8px;
        box-sizing: border-box;
        flex-shrink: 0;
    }
    .carousel-slide img {
        width: 100%;
        height: 160px;
        object-fit: cover;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .carousel-slide img:hover {
        transform: scale(1.04);
        box-shadow: 0 6px 14px rgba(0,0,0,0.08);
    }
    @keyframes scroll-left {
        0% { transform: translateX(0); }
        100% { transform: translateX(calc(-240px * 4)); }
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# SECTION 2: COMPREHENSIVE TRILINGUAL LOCALIZATION (TH / EN / DE)
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
        "step1_title": "1. เลือกสไตล์สวนที่ต้องการจัดวาง",
        "style_label": "รูปแบบสไตล์มาตรฐานที่ผ่านการคำนวณโครงสร้างแล้ว:",
        "dim_title": "📌 สเปกมิติมาตรฐานของพื้นที่ (Standard Space Dimensions)",
        "dim_w": "ความกว้าง", "dim_h": "ความสูง", "dim_d": "ความลึก", "meter": "เมตร",
        "category_txt": "ประเภทหมวดหมู่", "arch_name": "ชื่อสถาปัตยกรรม",
        "scan_header": "📷 สแกนหรืออัปโหลดภาพพื้นที่จริงของคุณ",
        "scan_desc": "บันทึกภาพมุมระเบียง ห้อง หรือสวน เพื่อให้ระบบนำไปคำนวณสัดส่วนและจัดวางชุดอุปกรณ์ลงในพื้นที่ได้อย่างแม่นยำ (รองรับไฟล์ JPG, PNG หรือเปิดกล้องสด)",
        "cam_choice": ["เปิดกล้องสด (Camera)", "อัปโหลดรูปภาพ (Upload)"],
        "cam_prompt": "สแกนมุมระเบียงหรือห้องที่ต้องการจัดวาง",
        "upload_prompt": "เลือกไฟล์ภาพพื้นที่มุมบ้าน (JPG, PNG)",
        "step2_title": "2. ปรับแต่งรูปทรง สี และจำนวนอุปกรณ์ (Interactive Customizer)",
        "pot_shape_label": "เลือกรูปทรงกระถาง / รางปลูก (Planter Style):",
        "pot_shapes": [
            "รางยาวมินิมอล (Rectangular Trough)", 
            "ทรงกระบอกโมเดิร์น (Cylinder Modern)", 
            "สี่เหลี่ยมลูกบาศก์ (Square Cube)", 
            "ทรงกลมคลาสสิก (Round Classic)"
        ],
        "pot_color_label": "เลือกโทนสีและเนื้อวัสดุ (Color & Texture):",
        "pot_colors": [
            "ดำด้านลอฟท์ (Matte Black)", 
            "ขาวคลีนมินิมอล (Matte White)", 
            "เทาคอนกรีตโมเดิร์น (Concrete Grey)", 
            "ดินเผาธรรมชาติ (Terracotta)"
        ],
        "bom_title": "📦 ตารางรายการอุปกรณ์ในเซ็ต (Bill of Materials)",
        "col_name": "รายการอุปกรณ์",
        "col_qty": "จำนวน (ชิ้น)",
        "col_price": "ราคาแปลง",
        "col_link": "สั่งซื้อผ่านระบบ",
        "est_price": "ประมาณการชิ้นละ", 
        "btn_amazon": "ดูบน Amazon ↗",
        "step3_title": "ราคารวมอุปกรณ์โดยประมาณ:",
        "amazon_note": "ราคาสินค้าจริงขึ้นอยู่กับผู้ขายบน Amazon ณ วันที่ทำการสั่งซื้อ",
        "btn_buy_all": "🛒 สั่งซื้ออุปกรณ์ชุดนี้ทั้งหมดบน Amazon (One-Click)",
        "legal_title": "⚖️ ข้อตกลงสิทธิ์การใช้งาน Seasonal Access Pass",
        "legal_rule1": f"- สิทธิ์นี้ครอบคลุมการเข้าถึงไฟล์พิมพ์เขียว แผนผังระบบ และการคำนวณสเปกสถาปัตยกรรมเป็นเวลา <b>{ACCESS_PERIOD_DAYS} วัน (4 เดือนเต็ม)</b>",
        "legal_rule2": "- เมื่อครบกำหนด 4 เดือน สิทธิ์จะสิ้นสุดลงโดยอัตโนมัติ ไม่มีการต่ออายุหรือเรียกเก็บเงินซ้ำซ้อน",
        "legal_rule3": "- การเข้าถึงระบบถือเป็นการส่งมอบสินทรัพย์ดิจิทัลเสร็จสมบูรณ์ทันที มีผลผูกพันตามกฎหมายธุรกรรมอิเล็กทรอนิกส์",
        "legal_notice": "ℹ️ **คำชี้แจงก่อนชำระเงิน:** โปรดตรวจสอบและทำเครื่องหมายยอมรับข้อตกลงทั้ง 2 ข้อด้านล่าง เพื่อปลดล็อกช่องทางการชำระเงินสำหรับสิทธิ์การใช้งาน Seasonal Access Pass (120 วันเต็ม)",
        "chk1_txt": "1. ข้าพเจ้ายอมรับข้อตกลงการให้บริการ และนโยบายทรัพย์สินทางปัญญาของ AI99 (รับทราบว่าแบบแปลนและพิมพ์เขียวเป็นลิขสิทธิ์เฉพาะ)",
        "chk2_txt": "2. ข้าพเจ้ายืนยันสละสิทธิ์การขอคืนเงินทุกกรณี 100% หลังเข้าถึงระบบ (เนื่องจากระบบจะส่งมอบสินทรัพย์ดิจิทัลและพิมพ์เขียวให้ทันทีหลังการชำระเงิน)",
        "legal_unlock": "✅ ยืนยันข้อกำหนดครบถ้วน ปลดล็อกท่อชำระเงินสิทธิ์ 4 เดือนเรียบร้อยแล้ว",
        "legal_lock": "กรุณาทำเครื่องหมายติ๊กถูกที่ช่องสี่เหลี่ยม 2 จุดด้านบนให้ครบ เพื่อปลดล็อกระบบชำระเงิน",
        "pay_usd_tab": "💳 บัตรเครดิต/เดบิตสากล (USD)", 
        "pay_eur_tab": "💶 บัตรเครดิตยุโรป (EUR)", 
        "pay_thb_tab": "📱 สแกน QR พร้อมเพย์ (THB)",
        "pay_stripe_desc": "ชำระค่าบริการ Seasonal Pass 4 เดือน ผ่านระบบ Stripe มาตรฐานความปลอดภัยระดับโลก",
        "btn_stripe": "🚀 ปลดล็อกสิทธิ์ 4 เดือน",
        "pay_thb_desc": "สแกน QR Code พร้อมเพย์ ชำระตรงเข้าบัญชี",
        "upload_slip": "แนบสลิปโอนเงินเพื่อปลดล็อกสิทธิ์ใช้งาน:",
        "btn_slip": "ยืนยันการส่งสลิปโอนเงิน",
        "slip_ok": "ระบบได้รับข้อมูลสลิปเรียบร้อยแล้ว กำลังดำเนินการตรวจสอบเปิดสิทธิ์การใช้งาน 4 เดือนครับ"
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
        "step1_title": "1. Select Desired Garden Architecture",
        "style_label": "Engineered Standard Archetypes:",
        "dim_title": "📌 Standard Specifications & Dimensions",
        "dim_w": "Width", "dim_h": "Height", "dim_d": "Depth", "meter": "m",
        "category_txt": "Category", "arch_name": "Architecture Title",
        "scan_header": "📷 Scan or Upload Your Actual Space",
        "scan_desc": "Capture or upload your balcony, room, or garden corner for accurate dimensional computation and equipment fit (Supports JPG, PNG, or Live Camera).",
        "cam_choice": ["Live Camera", "File Upload"],
        "cam_prompt": "Scan your balcony or indoor room corner",
        "upload_prompt": "Upload space image file (JPG, PNG)",
        "step2_title": "2. Customize Shape, Color & Quantities (BOM Configurator)",
        "pot_shape_label": "Select Planter Style / Shape:",
        "pot_shapes": [
            "Rectangular Trough", 
            "Cylinder Modern", 
            "Square Cube", 
            "Round Classic"
        ],
        "pot_color_label": "Select Material Texture & Color:",
        "pot_colors": [
            "Matte Black Loft", 
            "Matte White Minimal", 
            "Concrete Grey Modern", 
            "Terracotta Natural"
        ],
        "bom_title": "📦 Bill of Materials (BOM Dataset)",
        "col_name": "Equipment Name",
        "col_qty": "Quantity",
        "col_price": "Converted Price",
        "col_link": "Amazon Sourcing",
        "est_price": "Est. Unit Price", 
        "btn_amazon": "View on Amazon ↗",
        "step3_title": "Estimated Equipment Total:",
        "amazon_note": "Actual pricing depends on live vendor listings on Amazon at checkout.",
        "btn_buy_all": "🛒 Order Full Equipment Kit on Amazon (One-Click)",
        "legal_title": "⚖️ Seasonal Access Pass Terms of Service",
        "legal_rule1": f"- Grants full access to blueprints, architectural specs, and dimensional layouts for <b>{ACCESS_PERIOD_DAYS} days (Full 4-Month Quarter)</b>",
        "legal_rule2": "- Automatically terminates after 120 days without hidden recurring charges.",
        "legal_rule3": "- System access constitutes immediate and final delivery of digital assets with binding legal enforcement.",
        "legal_notice": "ℹ️ **Pre-Payment Notice:** Please review and accept both mandatory conditions below to unlock the payment gateway for your 120-Day Seasonal Access Pass.",
        "chk1_txt": "1. I accept the AI99 Terms of Service and Intellectual Property Policy (Acknowledging that all blueprints and spatial designs are proprietary assets).",
        "chk2_txt": "2. I acknowledge and agree to the 100% Strict Non-Refundable Policy once access is granted (Digital architectural assets and blueprints are delivered immediately upon payment).",
        "legal_unlock": "✅ Terms accepted. Payment gateway for the 4-month pass is unlocked.",
        "legal_lock": "Please accept both mandatory checkboxes above to unlock payment checkout.",
        "pay_usd_tab": "💳 International Card (USD)", 
        "pay_eur_tab": "💶 European Card (EUR)", 
        "pay_thb_tab": "📱 PromptPay QR (THB)",
        "pay_stripe_desc": "Pay 4-Month Seasonal Pass via secure Stripe international gateway.",
        "btn_stripe": "🚀 Unlock 4-Month Access",
        "pay_thb_desc": "Scan PromptPay QR for direct local transfer.",
        "upload_slip": "Upload bank transfer confirmation slip:",
        "btn_slip": "Submit Transfer Slip",
        "slip_ok": "Slip received. Activating your 4-month seasonal account now."
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
        "step1_title": "1. Gewünschten Gartenstil auswählen",
        "style_label": "Berechnete Standard-Architekturmodelle:",
        "dim_title": "📌 Standardspezifikationen & Abmessungen",
        "dim_w": "Breite", "dim_h": "Höhe", "dim_d": "Tiefe", "meter": "m",
        "category_txt": "Kategorie", "arch_name": "Architektur-Titel",
        "scan_header": "📷 Scannen oder Hochladen Ihres Raumbildes",
        "scan_desc": "Erfassen oder laden Sie Ihren Balkon, Raum oder Gartenbereich hoch, um präzise Maßberechnungen und Platzierungen zu ermöglichen (Unterstützt JPG, PNG oder Live-Kamera).",
        "cam_choice": ["Live-Kamera", "Datei-Upload"],
        "cam_prompt": "Balkon oder Raumecke scannen",
        "upload_prompt": "Raumbild auswählen (JPG, PNG)",
        "step2_title": "2. Formen, Farben & Stückzahlen anpassen (BOM-Konfigurator)",
        "pot_shape_label": "Pflanzgefäß-Form auswählen:",
        "pot_shapes": [
            "Rechteckiger Trog (Minimal)", 
            "Zylinder Modern", 
            "Würfel (Square)", 
            "Runder Topf (Klassisch)"
        ],
        "pot_color_label": "Farbton & Textur auswählen:",
        "pot_colors": [
            "Mattschwarz Loft", 
            "Mattweiß Minimal", 
            "Betongrau Modern", 
            "Terrakotta Natur"
        ],
        "bom_title": "📦 Stückliste der Ausrüstung (Bill of Materials)",
        "col_name": "Artikelname",
        "col_qty": "Menge",
        "col_price": "Umgerechneter Preis",
        "col_link": "Amazon-Beschaffung",
        "est_price": "Geschätzter Einzelpreis", 
        "btn_amazon": "Auf Amazon ansehen ↗",
        "step3_title": "Geschätzte Gesamtkosten der Ausrüstung:",
        "amazon_note": "Tatsächliche Preise hängen vom jeweiligen Amazon-Händler ab.",
        "btn_buy_all": "🛒 Gesamte Ausrüstung mit einem Klick auf Amazon bestellen",
        "legal_title": "⚖️ Nutzungsbedingungen für den Seasonal Access Pass",
        "legal_rule1": f"- Gültig für vollständigen Zugriff auf Baupläne und Raumspezifikationen für <b>{ACCESS_PERIOD_DAYS} Tage (4 volle Monate)</b>",
        "legal_rule2": "- Endet automatisch nach 120 Tagen ohne Folgekosten oder automatische Verlängerung.",
        "legal_rule3": "- Der Systemzugang gilt als vollständige digitale Bereitstellung und ist rechtlich bindend.",
        "legal_notice": "ℹ️ **Hinweis vor der Zahlung:** Bitte bestätigen Sie beide untenstehenden Pflichtfelder, um die Zahlungskanäle für Ihren 120-Tage Seasonal Access Pass freizuschalten.",
        "chk1_txt": "1. Ich akzeptiere die AI99-Nutzungsbedingungen und die Richtlinien zum geistigen Eigentum (Anerkennung der urheberrechtlich geschützten Baupläne).",
        "chk2_txt": "2. Ich bestätige den 100%igen Verzicht auf Rückerstattung nach Bereitstellung des Zugangs (Digitale Architektur-Assets und Baupläne werden nach der Zahlung sofort freigeschaltet).",
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

# ==============================================================================
# SECTION 3: MASTER ARCHITECTURAL CATALOG (FULL BOM DATASET - 4 MODELS)
# ==============================================================================
CATALOG = {
    "STYLE-BAL-01": {
        "title_th": "สวนผักสลัดแนวตั้งระเบียงคอนโด (Verdant Balcony Kit)",
        "title_en": "Minimalist Vertical Balcony Salad Kit",
        "title_de": "Minimalistischer Vertikaler Balkon-Salatgarten",
        "category": "Balcony Micro-Space",
        "dimensions": {"width": 1.20, "height": 2.00, "depth": 0.45},
        "description_th": "ชุดปลูกผักสลัดและพืชครัวแนวตั้ง สำหรับระเบียงขนาดกะทัดรัด พร้อมระบบน้ำหยดอัตโนมัติ",
        "description_en": "Vertical salad greens and culinary herb kit engineered for compact balconies with micro-irrigation.",
        "description_de": "Vertikales Salatanbau-Set für kompakte Balkone inklusive automatischer Tropfbewässerung.",
        "default_items": [
            {
                "id": "rack", 
                "name": "โครงชั้นวางกัลวาไนซ์ 4-5 ชั้น ทรง Slim", 
                "name_en": "Slim Galvanized 5-Tier Rack", 
                "name_de": "Schlankes 5-Etagen-Regal Verzinkt", 
                "qty": 1, 
                "price_usd": 45.0, 
                "search": "vertical garden wall planter rack outdoor"
            },
            {
                "id": "planter", 
                "name": "รางปลูกผักสลัด Food-grade ทน UV", 
                "name_en": "Food-grade UV Resistant Planter Box", 
                "name_de": "UV-beständiger Pflanzkasten Lebensmittelqualität", 
                "qty": 4, 
                "price_usd": 8.0, 
                "search": "rectangular planter box UV resistant"
            },
            {
                "id": "drip", 
                "name": "ชุดระบบน้ำหยดอัตโนมัติ Micro-drip", 
                "name_en": "Automatic Micro-Drip Irrigation Kit", 
                "name_de": "Automatisches Micro-Drip Bewässerungsset", 
                "qty": 1, 
                "price_usd": 18.5, 
                "search": "automatic micro drip irrigation kit balcony"
            },
            {
                "id": "soil", 
                "name": "ดินปลูกสูตรมินิมอลระบายน้ำไว (50L)", 
                "name_en": "Organic Lightweight Potting Mix (50L)", 
                "name_de": "Organische Pflanzerde leicht durchlässig (50L)", 
                "qty": 2, 
                "price_usd": 12.0, 
                "search": "organic potting mix perlite lightweight"
            }
        ]
    },
    "STYLE-MSH-01": {
        "title_th": "สมาร์ทฟังกิพอด ตู้เห็ดในร่มกินได้ (Smart Fungi Pod)",
        "title_en": "Indoor Micro Mushroom Chamber",
        "title_de": "Smarte Indoor-Pilzzuchtkammer",
        "category": "Mushroom Chamber",
        "dimensions": {"width": 0.50, "height": 0.70, "depth": 0.40},
        "description_th": "ตู้เพาะเห็ดนางรมและเห็ดหัวลิงอัจฉริยะ คุมความชื้นด้วยอัลตราโซนิก สะอาด ปลอดเชื้อ",
        "description_en": "Precision humidity-controlled indoor fruiting chamber for gourmet oyster and lion's mane mushrooms.",
        "description_de": "Präzisionsgesteuerte Feuchtigkeitskammer für Speisepilze im Innenbereich.",
        "default_items": [
            {
                "id": "chamber", 
                "name": "ตู้โหลแก้ว/อะคริลิก คุมความชื้นมินิมอล", 
                "name_en": "Humidity Controlled Chamber Tent", 
                "name_de": "Feuchtigkeitsgesteuerte Zuchtkammer", 
                "qty": 1, 
                "price_usd": 55.0, 
                "search": "mushroom fruiting chamber grow tent"
            },
            {
                "id": "humidifier", 
                "name": "เครื่องพ่นหมอก Ultrasonic + เซนเซอร์", 
                "name_en": "Ultrasonic Mist Maker + Sensor", 
                "name_de": "Ultraschall-Vernebler mit Feuchtigkeitssensor", 
                "qty": 1, 
                "price_usd": 28.0, 
                "search": "ultrasonic mist maker with humidity controller"
            },
            {
                "id": "spores", 
                "name": "ก้อนเชื้อเห็ดพรีเมียม (Oyster/Lion's Mane)", 
                "name_en": "Organic Mushroom Grow Kit Substrate", 
                "name_de": "Bio-Pilzzucht Substratblöcke", 
                "qty": 4, 
                "price_usd": 6.5, 
                "search": "organic mushroom grow kit lion mane oyster"
            },
            {
                "id": "light", 
                "name": "ไฟ LED Bar 5W สเปกตรัมขาว", 
                "name_en": "5W White Spectrum LED Grow Bar", 
                "name_de": "5W Weißspektrum LED-Wachstumsleiste", 
                "qty": 1, 
                "price_usd": 14.0, 
                "search": "small indoor led grow light bar for plants"
            }
        ]
    },
    "STYLE-IND-01": {
        "title_th": "ชั้นวางไม้และไฟปลูกในห้องรับแขก (Living Plant Shelf)",
        "title_en": "Living Room Aesthetic Greenery Stand",
        "title_de": "Ästhetisches Wohnzimmer-Pflanzenregal",
        "category": "Indoor Greenery",
        "dimensions": {"width": 1.00, "height": 1.60, "depth": 0.35},
        "description_th": "ชั้นวางไม้โครงเหล็กสไตล์นอร์ดิก พร้อมไฟปลูกซ่อนใต้ชั้น สำหรับมุมพักผ่อนในห้องนั่งเล่น",
        "description_en": "Nordic steel-wood tiered shelving unit with concealed full-spectrum under-shelf grow lights.",
        "description_de": "Nordisches Holz-Metall-Stufenregal mit integrierten Full-Spectrum Pflanzenleuchten.",
        "default_items": [
            {
                "id": "wood_rack", 
                "name": "ชั้นวางไม้โครงเหล็กนอร์ดิก 4 ชั้น", 
                "name_en": "4-Tier Nordic Metal Wood Plant Stand", 
                "name_de": "4-stufiges Nordisches Metall-Holz-Pflanzenregal", 
                "qty": 1, 
                "price_usd": 62.0, 
                "search": "tiered plant stand indoor metal wood tall"
            },
            {
                "id": "grow_light", 
                "name": "ไฟ Grow Light ซ่อนใต้ชั้น Full Spectrum", 
                "name_en": "Under-shelf Full Spectrum Grow Lights", 
                "name_de": "Full-Spectrum Unterbau-Pflanzenleuchten", 
                "qty": 3, 
                "price_usd": 15.0, 
                "search": "under shelf grow lights full spectrum warm white"
            },
            {
                "id": "pots", 
                "name": "กระถางเซรามิกมินิมอลพร้อมจานรอง", 
                "name_en": "Modern Ceramic Pots with Saucers", 
                "name_de": "Moderne Keramiktöpfe mit Untersetzern", 
                "qty": 6, 
                "price_usd": 7.0, 
                "search": "ceramic plant pots with drainage hole saucer modern"
            }
        ]
    },
    "STYLE-FYD-01": {
        "title_th": "แผงสวนแนวตั้งระแนงหน้าบ้าน (Front Entrance Green Wall)",
        "title_en": "Front Yard Compact Trellis System",
        "title_de": "Kompaktes Vorgarten-Spaliersystem",
        "category": "Front Yard",
        "dimensions": {"width": 1.80, "height": 1.80, "depth": 0.50},
        "description_th": "แผงระแนงเหล็กโมดูลาร์กันสนิมพร้อมกระถางแขวนระบบล็อค สำหรับตกแต่งผนังหน้าบ้านและโรงรถ",
        "description_en": "Heavy-duty rustproof freestanding modular trellis with hook-lock self-watering planters.",
        "description_de": "Rostfreies modulares Standspalier mit selbstbewässernden Hängepflanzkübeln.",
        "default_items": [
            {
                "id": "trellis", 
                "name": "แผงระแนงเหล็กโมดูลาร์ตั้งพื้น พ่นกันสนิม", 
                "name_en": "Freestanding Modular Garden Trellis", 
                "name_de": "Freistehendes Modulares Gartenspalier", 
                "qty": 1, 
                "price_usd": 78.0, 
                "search": "freestanding garden trellis wall panel metal"
            },
            {
                "id": "hook_pots", 
                "name": "กระถางแขวนระบบ Hook Lock เก็บน้ำสำรอง", 
                "name_en": "Hook Lock Self-Watering Hanging Pots", 
                "name_de": "Selbstbewässernde Hängepflanzkübel mit Haken", 
                "qty": 12, 
                "price_usd": 4.5, 
                "search": "hanging wall planter pots self watering hook"
            },
            {
                "id": "timer_drip", 
                "name": "ระบบน้ำหยด PE พร้อมไทม์เมอร์ก๊อกน้ำ", 
                "name_en": "Faucet Hose Timer + Drip Kit", 
                "name_de": "Wasserhahn-Timer mit Tropfbewässerung", 
                "qty": 1, 
                "price_usd": 24.0, 
                "search": "outdoor faucet hose timer with drip distribution tubing"
            }
        ]
    }
}

def get_amazon_link(keyword):
    """สร้าง URL ค้นหาสินค้าบน Amazon พร้อม Affiliate Tag ประจำระบบ"""
    encoded = urllib.parse.quote_plus(keyword)
    return f"https://www.amazon.com/s?k={encoded}&tag={AMAZON_AFFILIATE_TAG}"

# ==============================================================================
# SECTION 4: SECURITY LAYER & ZERO-HALLUCINATION AI TOUR GUIDE
# ==============================================================================
def secure_ai_guide(user_query, active_style_data, lang="TH"):
    """
    ป้อมคุมตรรกะความปลอดภัย สกัด Prompt Injection / Anti-Spam / Rate-limiting
    และตอบเฉพาะข้อมูลในขอบเขตสถาปัตยกรรมจัดสวน AI99
    """
    now = time.time()
    if "last_request_time" not in st.session_state:
        st.session_state.last_request_time = 0
        st.session_state.req_count = 0

    if now - st.session_state.last_request_time < 1.5:
        st.session_state.req_count += 1
        if st.session_state.req_count > 4:
            if lang == "TH":
                return "⚠️ ระบบตรวจพบคำขอถี่เกินไป กรุณารอสักครู่เพื่อความปลอดภัยครับ"
            elif lang == "DE":
                return "⚠️ Zu viele Anfragen in kurzer Zeit. Bitte warten Sie einen Moment."
            else:
                return "⚠️ Too many requests. Please wait a moment for security verification."
    else:
        st.session_state.req_count = 0

    st.session_state.last_request_time = now

    blacklist = ["ignore previous", "hack", "api key", "password", "system prompt", "database", "token", "root", "script"]
    if any(b in user_query.lower() for b in blacklist):
        if lang == "TH":
            return "🛡️ ขออภัยครับ ระบบอนุญาตให้สอบถามเฉพาะข้อมูลสถาปัตยกรรมจัดสวนในหน้านี้เท่านั้น"
        elif lang == "DE":
            return "🛡️ Zugriff verweigert: Nur Anfragen zur Gartenarchitektur erlaubt."
        else:
            return "🛡️ Access restricted: Queries are strictly confined to spatial garden architecture."

    q = user_query.lower()
    title = active_style_data["title_th"] if lang == "TH" else (
        active_style_data["title_de"] if lang == "DE" else active_style_data["title_en"]
    )
    dim = active_style_data["dimensions"]

    if any(w in q for w in ["วิธีใช้", "ทำยังไง", "ทัวร์", "start", "how", "anleitung"]):
        if lang == "TH":
            return "🚩 **ขั้นตอนง่ายๆ 3 สเต็ป:**\n1. เลือกสไตล์สวนด้านบน แล้วเปิดกล้องถ่ายมุมห้องจริง\n2. เลื่อนลงมาปรับแต่งทรงกระถาง สี และจำนวนชิ้นในตาราง\n3. กดสั่งซื้ออุปกรณ์ผ่าน Amazon หรือปลดล็อกพิมพ์เขียว 4 เดือนที่ปุ่มด้านล่างครับ"
        elif lang == "DE":
            return "🚩 **3 einfache Schritte:**\n1. Stil oben wählen und Raum mit Kamera scannen.\n2. Gefäßform, Farbe und Stückzahlen anpassen.\n3. Ausrüstung über Amazon bestellen oder 4-Monats-Bauplan freischalten."
        else:
            return "🚩 **3 Quick Steps:**\n1. Select style and scan space.\n2. Customize planter forms and quantities.\n3. Order kit via Amazon or unlock the 4-Month Seasonal Blueprint below."

    elif any(w in q for w in ["ขนาด", "พื้นที่", "กว้าง", "dim", "size", "fläche", "maße"]):
        return f"📐 **{title}** -> กว้าง {dim['width']} ม. x สูง {dim['height']} ม. x ลึก {dim['depth']} ม."

    elif any(w in q for w in ["กระถาง", "สลับ", "เปลี่ยน", "pot", "planter", "topf"]):
        if lang == "TH":
            return "💡 ปรับทรงกระถางและสีได้ในสเต็ป 2 ลิงก์ค้นหา Amazon จะปรับตรงรุ่นให้อัตโนมัติครับ"
        elif lang == "DE":
            return "💡 Passen Sie Gefäßform und Farbe in Schritt 2 an. Amazon-Links aktualisieren sich automatisch."
        else:
            return "💡 Adjust planter forms in Step 2. Amazon catalog search queries will update dynamically."

    elif any(w in q for w in ["อายุ", "4 เดือน", "ราคา", "pass", "price", "preis"]):
        return f"💳 Seasonal Pass: $139.95 USD / €129.00 EUR / ฿5,090 THB ({ACCESS_PERIOD_DAYS} Days full access)"

    else:
        if lang == "TH":
            return f"🌿 AI ไกด์พร้อมช่วยเหลือครับ สำหรับสไตล์ **{title}** สามารถปรับแต่งอุปกรณ์ได้ที่ตารางด้านล่างเลยครับ"
        elif lang == "DE":
            return f"🌿 AI-Guide bereit. Für **{title}** können Sie die Ausrüstung unten anpassen."
        else:
            return f"🌿 AI Guide standing by. Configure individual BOM units for **{title}** below."

# ==============================================================================
# SECTION 5: STATE MANAGEMENT & DYNAMIC SIDEBAR CONTROLLER
# ==============================================================================
if "user_lang" not in st.session_state:
    st.session_state.user_lang = "TH"
if "user_curr" not in st.session_state:
    st.session_state.user_curr = "THB"

def on_lang_change():
    """เมื่อผู้ใช้เปลี่ยนภาษา ให้สลับสกุลเงินตามความเหมาะสมอัตโนมัติ"""
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
        st.session_state.guide_msg = "AI99 Ready. Select your design and customize anytime."

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
    st.caption(f"Affiliate Associate Tag: `{AMAZON_AFFILIATE_TAG}`")
    st.caption(f"Active Sync Engine: **{selected_lang} ➔ {selected_currency_key}**")

# ==============================================================================
# SECTION 6: WORKSPACE HEADER
# ==============================================================================
st.markdown(f"<div class='main-title'>{t['title']}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='sub-title'>{t['subtitle']}</div>", unsafe_allow_html=True)

# ==============================================================================
# SECTION 7: STEP 1 - ARCHITECTURE SELECTION & PURE FLOWING CAROUSEL
# ==============================================================================
st.markdown(f"### {t['step1_title']}")

def get_style_title(k, lang):
    item = CATALOG[k]
    if lang == "TH":
        return f"{item['category']} - {item['title_th']}"
    elif lang == "DE":
        return f"{item['category']} - {item['title_de']}"
    else:
        return f"{item['category']} - {item['title_en']}"

style_keys = list(CATALOG.keys())
selected_key = st.selectbox(
    t['style_label'],
    style_keys,
    format_func=lambda x: get_style_title(x, selected_lang)
)

current_style = CATALOG[selected_key]
dim = current_style["dimensions"]
style_disp_title = current_style["title_th"] if selected_lang == "TH" else (
    current_style["title_de"] if selected_lang == "DE" else current_style["title_en"]
)

col1, col2 = st.columns([1, 1])

# ชุดรูปภาพ 4 แนวตรงรุ่น 100% จากโฟลเดอร์ 'รวม' ใน Google Drive ของพี่ยอด
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
    <div class='white-card'>
        <h4 style='color: #0F172A; margin-top:0;'>{t['dim_title']}</h4>
        <div style='margin-bottom: 12px;'>
            <span class='spec-tag'>{t['dim_w']}: {dim['width']} {t['meter']}</span>
            <span class='spec-tag'>{t['dim_h']}: {dim['height']} {t['meter']}</span>
            <span class='spec-tag'>{t['dim_d']}: {dim['depth']} {t['meter']}</span>
        </div>
        <p style='margin: 0; color: #475569; font-size: 0.92rem; line-height: 1.6;'>
            <b>{t['category_txt']}:</b> {current_style['category']}<br>
            <b>{t['arch_name']}:</b> {style_disp_title}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(CAROUSEL_HTML, unsafe_allow_html=True)

with col2:
    st.markdown(f"#### {t['scan_header']}")
    st.caption(t['scan_desc'])
    cam_mode = st.radio("Camera Option:", t['cam_choice'], horizontal=True, label_visibility="collapsed")
    if cam_mode == t['cam_choice'][0]:
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

header_c1, header_c2, header_c3, header_c4 = st.columns([4, 2, 2, 3])
with header_c1:
    st.write(f"**{t['col_name']}**")
with header_c2:
    st.write(f"**{t['col_qty']}**")
with header_c3:
    st.write(f"**{t['col_price']}**")
with header_c4:
    st.write(f"**{t['col_link']}**")

for item in current_style["default_items"]:
    item_id = f"{selected_key}_{item['id']}"
    if item_id not in st.session_state.quantities:
        st.session_state.quantities[item_id] = item["qty"]

    c_name, c_qty, c_price, c_aff = st.columns([4, 2, 2, 3])
    
    with c_name:
        item_name = item["name"] if selected_lang == "TH" else (
            item["name_de"] if selected_lang == "DE" else item["name_en"]
        )
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

# ==============================================================================
# SECTION 9: STEP 3 - TOTAL CHECKOUT, LEGAL CONSENT & PAYMENT CHANNELS
# ==============================================================================
col_sum, col_buy = st.columns([1, 1])
total_converted = total_estimated_base * curr["multiplier"]

with col_sum:
    st.markdown(f"### {t['step3_title']} `{curr['symbol']}{total_converted:,.2f}`")
    st.caption(t['amazon_note'])

with col_buy:
    search_all = f"{current_style['category']} {pot_color.split(' ')[0]}"
    st.link_button(t['btn_buy_all'], get_amazon_link(search_all), use_container_width=True)

# บล็อกเงื่อนไขทางกฎหมาย 120 วัน (Strict Non-Refundable)
st.markdown(f"""
<div class='legal-box'>
    <b>{t['legal_title']} ({curr['format']} / {ACCESS_PERIOD_DAYS} Days):</b><br>
    {t['legal_rule1']}<br>
    {t['legal_rule2']}<br>
    {t['legal_rule3']}
</div>
""", unsafe_allow_html=True)

# คำชี้แจงนำหน้า 2 ปุ่มมหัศจรรย์
st.info(t['legal_notice'])

chk1 = st.checkbox(t['chk1_txt'])
chk2 = st.checkbox(t['chk2_txt'])

if chk1 and chk2:
    st.success(t['legal_unlock'])
    
    # เรียงลำดับแท็บชำระเงินให้ตรงกับภาษาที่เลือกอัตโนมัติ
    if selected_lang == "TH":
        tab1, tab2, tab3 = st.tabs([
            f"{t['pay_thb_tab']} - ฿5,090", 
            f"{t['pay_usd_tab']} - $139.95", 
            f"{t['pay_eur_tab']} - €129.00"
        ])
        active_tab_order = ["THB", "USD", "EUR"]
    elif selected_lang == "DE":
        tab1, tab2, tab3 = st.tabs([
            f"{t['pay_eur_tab']} - €129.00", 
            f"{t['pay_usd_tab']} - $139.95", 
            f"{t['pay_thb_tab']} - ฿5,090"
        ])
        active_tab_order = ["EUR", "USD", "THB"]
    else:
        tab1, tab2, tab3 = st.tabs([
            f"{t['pay_usd_tab']} - $139.95", 
            f"{t['pay_eur_tab']} - €129.00", 
            f"{t['pay_thb_tab']} - ฿5,090"
        ])
        active_tab_order = ["USD", "EUR", "THB"]

    tab_map = {
        active_tab_order[0]: tab1, 
        active_tab_order[1]: tab2, 
        active_tab_order[2]: tab3
    }

    with tab_map["USD"]:
        st.write(t['pay_stripe_desc'])
        st.link_button(
            f"{t['btn_stripe']} ($139.95 USD / 4 Months)", 
            STRIPE_URL_USD, 
            use_container_width=True
        )

    with tab_map["EUR"]:
        st.write(t['pay_stripe_desc'])
        st.link_button(
            f"{t['btn_stripe']} (€129.00 EUR / 4 Monate)", 
            STRIPE_URL_EUR, 
            use_container_width=True
        )

    with tab_map["THB"]:
        st.write(f"{t['pay_thb_desc']} ยอดชำระ: **฿5,090 บาท** (สิทธิ์ 4 เดือนเต็ม)")
        qr_code_url = f"https://promptpay.io/{PROMPTPAY_ID}/5090.png"
        col_q, col_s = st.columns([1, 1])
        with col_q:
            st.image(qr_code_url, caption=f"PromptPay ID: {PROMPTPAY_ID}", width=230)
        with col_s:
            st.file_uploader(t['upload_slip'], type=["jpg", "png", "pdf"])
            if st.button(t['btn_slip']):
                st.info(t['slip_ok'])
else:
    st.info(t['legal_lock'])
