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
        "dimensions": {"width": 1.20, "height": 2
