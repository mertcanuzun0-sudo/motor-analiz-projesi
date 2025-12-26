import streamlit as st
import math
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. SAYFA KONFİGÜRASYONU VE STİL
# ---------------------------------------------------------
st.set_page_config(
    page_title="EcoMotor Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Özel CSS ile Modern Görünüm
st.markdown("""
<style>
    /* Ana Başlık Stili */
    .main-title {
        font-size: 3rem;
        color: #2E86C1;
        text-align: center;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.2rem;
        color: #566573;
        text-align: center;
        margin-bottom: 30px;
    }
    
    /* Metrik Kartları */
    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    div[data-testid="metric-container"]:hover {
        transform: scale(1.02);
        border-color: #2E86C1;
    }
    
    /* Sekme Stilleri */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f1f3f4;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF;
        border-bottom: 2px solid #2E86C1;
        color: #2E86C1;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. VERİTABANI VE FONKSİYONLAR
# ---------------------------------------------------------
STANDART_VERILER = {
  "2_kutup": {
    "0.75": {"IE3": 80.7}, "1.1": {"IE3": 82.7}, "1.5": {"IE3": 84.2}, "2.2": {"IE3": 85.9},
    "3": {"IE3": 87.1}, "4": {"IE3": 88.1}, "5.5": {"IE3": 89.2}, "7.5": {"IE3": 90.1},
    "11": {"IE3": 91.2}, "15": {"IE3": 91.9}, "18.5": {"IE3": 92.4}, "22": {"IE3": 92.7},
    "30": {"IE3": 93.3}, "37": {"IE3": 93.7}
  },
  "4_kutup": {
    "0.75": {"IE3": 82.5}, "1.1": {"IE3": 84.1}, "1.5": {"IE3": 85.3}, "2.2": {"IE3": 86.7},
    "3": {"IE3": 87.7}, "4": {"IE3": 88.6}, "5.5": {"IE3": 89.6}, "7.5": {"IE3": 90.4},
    "11": {"IE3": 91.4}, "15": {"IE3": 92.1}, "18.5": {"IE3": 92.6}, "22": {"IE3": 93.0},
    "30": {"IE3": 93.6}, "37": {"IE3": 93.9}
  },
  "6_kutup": {
    "0.75": {"IE3": 78.9}, "1.1": {"IE3": 81.0}, "1.5": {"IE3": 82.5}, "2.2": {"IE3": 84.3},
    "3": {"IE3": 85.6}, "4": {"IE3": 86.8}, "5.5": {"IE3": 88.0}, "7.5": {"IE3": 89.1},
    "11": {"IE3": 90.3}, "15": {"IE3": 91.2}
  }
}

HAZIR_MOTORLAR = [
    {"Marka": "GAMAK", "Model": "AGM 90 L 4", "kW": 1.5, "Kutup": 4, "V": 380, "A": 3.5, "Cos": 0.78},
    {"Marka": "GAMAK", "Model": "AGM 112 M 4", "kW": 4.0, "Kutup": 4, "V": 380, "A": 8.4, "Cos": 0.82},
    {"Marka": "VOLT", "Model": "VM 100 L4", "kW": 2.2, "Kutup": 4, "V": 380, "A": 4.9, "Cos": 0.79},
    {"Marka": "SIEMENS", "Model": "1LE1001 11kW", "kW": 11.0, "Kutup": 4, "V": 400, "A": 20.5, "Cos": 0.84},
    {"Marka": "ABB", "Model": "M2BAX 132", "kW": 7.5, "Kutup": 4, "V": 400, "A": 14.7, "Cos": 0.82},
    {"Marka": "WEG", "Model": "W22 5.5kW", "kW": 5.5, "Kutup": 4, "V": 380, "A": 11.0, "Cos": 0.82},
]

if 'analiz_listesi' not in st.session_state:
    st.session_state.analiz_listesi = []

# ---------------------------------------------------------
# 3. HEADER VE SIDEBAR (SOL PANEL)
# ---------------------------------------------------------
st.markdown('<p class="main-title">⚡ EcoMotor Pro</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Endüstriyel Enerji Verimliliği Analiz Platformu</p>', unsafe_allow_html=True)

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3103/3103445.png", width=100)
    st.header("⚙️ Parametreler")
    
    giris_tipi = st.radio("Veri Giriş Yöntemi", ["Hazır Listeden Seç", "Manuel Giriş"], horizontal=True)
    
    secilen_motor = {}
    
    if giris_tipi == "Hazır Listeden Seç":
        markalar = sorted(list(set([m["Marka"] for m in HAZIR_MOTORLAR])))
        sec_marka = st.selectbox("Marka", markalar)
        
        modeller = [m for m in HAZIR_MOTORLAR if m["Marka"] == sec_marka]
        sec_model = st.selectbox("Model", [m["Model"] for m in modeller])
        
        secilen_motor = next(m for m in modeller if m["Model"] == sec_model)
        
        val_kw = float(secilen_motor["kW"])
        val_kutup = int(secilen_motor["Kutup"])
        val_v = float(secilen_motor["V"])
        val_a = float(secilen_motor["A"])
        val_cos = float(secilen_motor["Cos"])
    else:
        val_kw, val_kutup, val_v, val_a, val_cos = 1.5, 4, 380.0, 3.5, 0.88

    with st.expander("🔧 Teknik Detaylar", expanded=True):
        guc_kw = st.number_input("Güç (kW)", value=val_kw, step=0.5)
        kutup = st.selectbox("Kutup Sayısı", [2, 4, 6], index=[2,4,6].index(val_kutup) if val_kutup in [2,4,6] else 1)
        voltaj = st.number_input("Voltaj (V)", value=val_v)
        akim = st.number_input("Akım (A)", value=val_a)
        cos_phi = st.slider("Güç Faktörü (Cosφ)", 0.5, 1.0, val_cos)

    st.markdown("---")
    st.header("💰 İşletme Ayarları")
    calisma_saati = st.number_input("Yıllık Çalışma Saati", value=2500, step=100)
    birim_fiyat = st.number_input("Elektrik Fiyatı (TL/kWh)", value=4.5, step=0.1)
    
    hesapla = st.button("🚀 Analizi Başlat", type="primary", use_container_width=True)

# ---------------------------------------------------------
# 4. HESAPLAMA VE GÖRSELLEŞTİRME
# ---------------------------------------------------------
if hesapla:
    # Temel Hesaplar
    p_giris = math.sqrt(3) * voltaj * akim * cos_phi
    p_cikis = guc_kw * 1000
    mevcut_verim = (p_cikis / p_giris) * 100 if p_giris > 0 else 0
    
    # Referans
    ref_verim = 0
    anahtar_kutup = f"{kutup}_kutup"
    anahtar_kw = str(guc_kw)
    if anahtar_kutup in STANDART_VERILER and anahtar_kw in STANDART_VERILER[anahtar_kutup]:
        ref_verim = STANDART_VERILER[anahtar_kutup][anahtar_kw]["IE3"]
        
    # Tasarruf
    tasarruf_tl = 0
    co2 = 0
    if ref_verim > 0 and mevcut_verim < ref_verim:
        eta_old, eta_new = mevcut_verim/100, ref_verim/100
        tasarruf_kwh = guc_kw * ((1/eta_old) - (1/eta_new)) * calisma_saati
        tasarruf_tl = tasarruf_kwh * birim_fiyat
        co2 = tasarruf_kwh * 0.44

    # --- SEKMELİ YAPI ---
    tab1, tab2, tab3 = st.tabs(["📊 Ana Kontrol Paneli", "📈 Finansal Projeksiyon", "📋 Kayıtlar"])

    with tab1:
        # Üst Metrikler
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Mevcut Verim", f"%{mevcut_verim:.1f}", delta=f"{mevcut_verim-ref_verim:.1f}% Fark" if ref_verim else None)
        c2.metric("Giriş Gücü", f"{p_giris/1000:.2f} kW")
        c3.metric("Yıllık Tüketim", f"{(p_giris/1000)*calisma_saati:,.0f} kWh")
        c4.metric("Potansiyel Kazanç", f"{tasarruf_tl:,.0f} TL", delta_color="normal")

        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            st.subheader("Motor Verimlilik Göstergesi")
            # Gauge Chart (Kadran)
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = mevcut_verim,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Verimlilik (%)"},
                delta = {'reference': ref_verim, 'increasing': {'color': "green"}},
                gauge = {
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': "#2E86C1"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 70], 'color': '#ffcbcb'},
                        {'range': [70, ref_verim], 'color': '#ffffd1'},
                        {'range': [ref_verim, 100], 'color': '#d1ffbd'}],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': ref_verim}}))
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col_right:
            st.subheader("Verim Karşılaştırması")
            df_chart = pd.DataFrame({
                "Tip": ["Mevcut Motor", "IE3 Standart"],
                "Verim": [mevcut_verim, ref_verim]
            })
            fig_bar = px.bar(df_chart, x="Tip", y="Verim", color="Tip", 
                             color_discrete_sequence=["#E74C3C", "#27AE60"], text="Verim")
            fig_bar.update_layout(yaxis_range=[50, 100])
            st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        if tasarruf_tl > 0:
            st.subheader("💰 Yatırım Geri Dönüşü (ROI)")
            
            yeni_motor_fiyati = guc_kw * 4500
            amortisman = yeni_motor_fiyati / tasarruf_tl
            
            col_roi1, col_roi2 = st.columns([3, 1])
            
            with col_roi1:
                years = list(range(1, 6))
                earnings = [tasarruf_tl * y for y in years]
                costs = [yeni_motor_fiyati] * 5
                
                df_roi = pd.DataFrame({"Yıl": years, "Kümülatif Kazanç": earnings, "Maliyet": costs})
                fig_line = px.line(df_roi, x="Yıl", y=["Kümülatif Kazanç", "Maliyet"], 
                                   markers=True, title="5 Yıllık Kazanç Projeksiyonu")
                st.plotly_chart(fig_line, use_container_width=True)
            
            with col_roi2:
                st.success(f"Amortisman Süresi:\n# {amortisman:.1f} Yıl")
                st.info(f"5 Yılda Net Kâr:\n# {(tasarruf_tl*5 - yeni_motor_fiyati):,.0f} TL")
                st.warning(f"Karbon Salınımı:\n# -{co2:.1f} kg")
        else:
            st.info("Bu motor zaten yüksek verimli, değişim gerekmez.")

    with tab3:
        if st.button("📥 Analizi Listeye Kaydet"):
            st.session_state.analiz_listesi.append({
                "Tarih": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
                "Model": secilen_motor.get("Model", "Manuel"),
                "Güç": guc_kw,
                "Mevcut Verim": round(mevcut_verim, 2),
                "Yıllık Kazanç": round(tasarruf_tl, 2)
            })
            st.success("Kaydedildi!")

        if len(st.session_state.analiz_listesi) > 0:
            df_list = pd.DataFrame(st.session_state.analiz_listesi)
            st.dataframe(df_list, use_container_width=True)
            
            csv = df_list.to_csv(index=False).encode('utf-8')
            st.download_button("Excel İndir", csv, "rapor.csv", "text/csv")
        else:
            st.warning("Henüz kayıt yok.")

else:
    st.info("👈 Lütfen sol panelden verileri girip 'Analizi Başlat' butonuna basın.")