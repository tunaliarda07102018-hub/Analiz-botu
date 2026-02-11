import streamlit as st
import yfinance as yf
import pandas_ta as ta

st.set_page_config(page_title="Otomatik Borsa Robotu", layout="wide")

st.title("🤖 Yapay Zeka Destekli Hisse Analizör")

# Kullanıcıdan hisse kodunu al (BIST için sonuna .IS eklenmeli)
hisse_adi = st.sidebar.text_input("Hisse Kodu (Örn: THYAO, BESTE)", "THYAO").upper()
ticker_symbol = f"{hisse_adi}.IS"

try:
    # 1. Verileri Çek
    hisse = yf.Ticker(ticker_symbol)
    df = hisse.history(period="1y") # 1 yıllık veri
    info = hisse.info

    if df.empty:
        st.error("Hisse verisi bulunamadı. Kodu doğru girdiğinizden emin olun.")
    else:
        # 2. Teknik Göstergeleri Hesapla
        df['MA200'] = ta.sma(df['Close'], length=200)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        son_fiyat = df['Close'].iloc[-1]
        son_rsi = df['RSI'].iloc[-1]
        ma200_degeri = df['MA200'].iloc[-1] if not df['MA200'].isna().all() else 0
        
        # 3. El Değiştirme Oranı (Tahmini)
        gunluk_hacim = df['Volume'].iloc[-1]
        # Yahoo Finance her hissenin dolaşımdaki payını vermeyebilir, yoksa 1 kabul et
        dolasimdaki_pay = info.get('floatShares', 1) 
        edo = (gunluk_hacim / dolasimdaki_pay) * 100 if dolasimdaki_pay > 1 else 0

        # --- ARAYÜZ ---
        col1, col2, col3 = st.columns(3)
        col1.metric("Son Fiyat", f"{son_fiyat:.2f} TL")
        col2.metric("RSI (14)", f"{son_rsi:.1f}")
        col3.metric("Tahmini El Değiştirme", f"%{edo:.2f}")

        st.divider()

        # 4. KARAR MEKANİZMASI (Sinyaller)
        if son_fiyat > ma200_degeri and ma200_degeri != 0:
            st.success(f"🟢 **BOĞA PİYASASI:** {hisse_adi} yükseliş trendinde.")
        elif ma200_degeri == 0:
            st.info("ℹ️ Hisse çok yeni olduğu için uzun vadeli trend (MA200) hesaplanamıyor.")
        else:
            st.error(f"🔴 **AYI PİYASASI:** {hisse_adi} düşüş trendinde.")

        # Risk Uyarısı
        if edo > 20:
            st.warning(f"⚠️ **DİKKAT:** El değiştirme oranı (%{edo:.2f}) yüksek! Kar satışları gelebilir.")

        # Grafik
        st.line_chart(df['Close'])

except Exception as e:
    st.write(f"Bir hata oluştu: {e}")
