import streamlit as st
import urllib.parse
import time
from datetime import datetime
import os

# ==============================================================================
# SECTION 1: GLOBAL CONFIGURATION, HEADERS & MULTI-CURRENCY ENGINE
# ==============================================================================
AMAZON_AFFILIATE_TAG = "ybcai99garden-20"
ACCESS_PERIOD_DAYS = 120

STRIPE_URL_USD = "https://buy.stripe.com/your_actual_stripe_link_usd"
STRIPE_URL_EUR = "https://buy.stripe.com/your_actual_stripe_link_eur"
PROMPTPAY_ID = "0800838340"

REGISTERED_MEMBERS = {
    "0800838340": "999999",
    "080-083-8340": "999999",
    "080 083 8340": "999999",
    "+49151234567": "772109"
}

PRICING_CONFIG = {
    "USD": {"symbol": "$", "rate": 139.95, "format": "$139.95", "multiplier": 1.0, "label": "USD ($139.95) - US & International"},
    "EUR": {"symbol": "€", "rate": 129.00, "format": "€129.00", "multiplier": 0.9217, "label": "EUR (€129.00) - European Union"},
    "THB": {"symbol": "฿", "rate": 5090.00, "format": "5,090 บาท", "multiplier": 36.37, "label": "THB (฿5,090) - Thai PromptPay"}
}

LANG_TO_CURR = {"TH": "THB", "EN": "USD", "DE": "EUR"}

st.set_page_config(
    page_title="AI 99 Garden Design",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<head>
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
</head>
<style>
    .stApp { 
        background-color: #0E1117; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #FFFFFF !important;
    }
    .hero-container {
        background: linear-gradient(135deg, #064E3B 0%, #0F172A 100%);
        border: 1px solid #10B981;
        border-radius: 16px;
        padding: 26px 24px;
        margin-bottom: 22px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.4);
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #34D399 !important;
        margin-bottom: 6px;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #E2E8F0 !important;
        line-height: 1.6;
        margin-bottom: 10px;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(16, 185, 129, 0.2);
        color: #6EE7B7 !important;
        border: 1px solid #10B981;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .display-card { 
        background-color: #1E293B; 
        border: 1px solid #334155; 
        border-radius: 14px; 
        padding: 16px; 
        margin-bottom: 14px; 
        box-shadow: 0 4px 14px rgba(0,0,0,0.2);
        color: #FFFFFF !important;
    }
    .spec-tag { 
        background-color: #0F172A; 
        color: #38BDF8 !important; 
        font-weight: 700; 
        padding: 5px 12px; 
        border-radius: 8px; 
        font-size: 0.85rem; 
        margin-right: 6px; 
        border: 1px solid #334155;
        display: inline-block;
    }
    .fixed-img-container {
        width: 100%;
        height: 320px;
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #334155;
        background: #020617;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .fixed-img-container img {
        width: 100%;
        height: 100%;
        object-fit: cover !important;
    }
    .bom-header-bar {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 10px 14px;
        font-weight: 700;
        color: #38BDF8 !important;
        font-size: 0.92rem;
        margin-bottom: 8px;
    }
    .lock-box {
        background: rgba(30, 41, 59, 0.8);
        border: 2px dashed #EF4444;
        border-radius: 12px;
        padding: 26px;
        text-align: center;
        margin: 18px 0;
    }
    .legal-box { 
        background-color: #1E293B; 
        border-left: 5px solid #F59E0B; 
        border-top: 1px solid #334155;
        border-right: 1px solid #334155;
        border-bottom: 1px solid #334155;
        padding: 18px; 
        border-radius: 10px; 
        margin: 18px 0px; 
        font-size: 0.95rem; 
        color: #E2E8F0 !important;
        line-height: 1.6;
    }
    .guide-bubble { 
        background-color: #1E293B; 
        border-left: 4px solid #10B981; 
        border-top: 1px solid #334155;
        border-right: 1px solid #334155;
        border-bottom: 1px solid #334155;
        padding: 14px; 
        border-radius: 8px; 
        margin-bottom: 12px; 
        font-size: 0.92rem; 
        color: #F8FAFC !important;
        line-height: 1.5;
    }
    .legal-footer {
        background-color: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 22px;
        margin-top: 36px;
        margin-bottom: 20px;
        font-size: 0.86rem;
        color: #94A3B8 !important;
        line-height: 1.7;
    }
    .legal-footer-links a {
        color: #38BDF8 !important;
        text-decoration: none;
        margin-right: 18px;
        font-weight: 600;
    }
    div[data-testid="stMarkdownContainer"] p, 
    div[data-testid="stMarkdownContainer"] span,
    div[data-testid="stMarkdownContainer"] b {
        color: #F8FAFC !important;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# SECTION 2: LOCALIZATION (TH / EN / DE)
# ==============================================================================
I18N = {
    "TH": {
        "hero_badge": "🌿 สถาปัตยกรรมจัดสวนพื้นที่จำกัดอัจฉริยะ",
        "hero_title": "เนรมิตพื้นที่สวนในฝัน สู่ความจริงด้วย AI99",
        "hero_desc": "คำนวณสัดส่วนพื้นที่ระเบียงและมุมห้องจริงอย่างแม่นยำ พร้อมแปลนจัดวางชุดอุปกรณ์และตารางสั่งซื้อครบวงจรในที่เดียว",
        "top_mode_label": "สถานะการใช้งานระบบ:",
        "top_modes": ["👤 ผู้เยี่ยมชม / สั่งซื้อสิทธิ์ใหม่", "🔑 สมาชิกเดิมเข้าสู่ระบบ (Login)"],
        "login_title": "🔑 ยืนยันตัวตนสมาชิก AI99 (Phone + Access PIN)",
        "login_prompt": "หมายเลขโทรศัพท์ที่ลงทะเบียน:",
        "login_pin_prompt": "รหัสผ่านลับ Access PIN (6 หลัก):",
        "login_btn": "🚀 ปลดล็อกเข้าใช้งานระบบเต็มรูปแบบ",
        "login_success": "ยืนยันตัวตนสำเร็จ! ปลดล็อกตาราง Master BOM เรียบร้อยแล้ว",
        "login_fail": "หมายเลขโทรศัพท์หรือรหัส PIN ไม่ถูกต้อง",
        "logout_btn": "ออกจากระบบ",
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
        "step1_title": "1. เลือกสไตล์สวนต้นแบบ & เทียบกับมุมห้องจริงของคุณ",
        "style_label": "เลือกสไตล์สวนมาตรฐานที่ผ่านการคำนวณโครงสร้างแล้ว:",
        "model_screen_title": "🖼️ ภาพต้นแบบสไตล์ที่เลือก (Architecture Blueprint)",
        "user_screen_title": "📷 ภาพพื้นที่มุมบ้านจริงของคุณ (Your Space Upload)",
        "dim_title": "📌 สเปกมิติมาตรฐานของพื้นที่",
        "dim_w": "กว้าง",
        "dim_h": "สูง",
        "dim_d": "ลึก",
        "meter": "ม.",
        "category_txt": "หมวดหมู่",
        "arch_name": "ชื่อสถาปัตยกรรม",
        "scan_desc": "อัปโหลดภาพมุมห้องหรือระเบียงจริงเพื่อดูการจัดวาง (รองรับ JPG, PNG)",
        "upload_prompt": "เลือกไฟล์ภาพมุมบ้านของคุณ",
        "confirm_ai_btn": "⚡ ส่งภาพเข้าสู่ 3-Core AI เพื่อคำนวณมิติและจับคู่ชิ้นส่วน",
        "ai_result_title": "✨ ภาพผลลัพธ์การจัดวางเสมือนจริง (AI Rendered Concept):",
        "step2_title": "2. ปรับแต่งรูปทรงกระถาง สี และดูรายการอุปกรณ์ (Interactive Customizer)",
        "bom_locked_msg": "🔒 **ส่วนตาราง Master BOM และ
