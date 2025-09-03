import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# PENGATURAN APLIKASI STREAMLIT
# ==============================================================================

# Atur judul halaman
st.set_page_config(
    page_title="Chatbot Apoteker Gemini",
    layout="centered"
)

# Judul utama aplikasi
st.title("👨🏻‍⚕️ Chatbot Apoteker")
st.markdown("Halo! Saya seorang apoteker. Silakan tanyakan tentang obat yang Anda butuhkan.")

# ==============================================================================
# PENGATURAN API KEY DAN MODEL
# ==============================================================================

# Mengambil API Key dari secrets Streamlit
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.warning("Peringatan: API Key tidak ditemukan. Harap atur GEMINI_API_KEY di `Secrets` Streamlit.")
    st.info("Anda bisa menambahkannya di sidebar 'Manage app' -> 'Secrets' atau di file `.streamlit/secrets.toml`.")
    st.stop() # Hentikan eksekusi jika API Key tidak ada

# Nama model Gemini
MODEL_NAME = 'gemini-1.5-flash'

# ==============================================================================
# FUNGSI UTAMA CHATBOT
# ==============================================================================

# Inisialisasi model dan konfigurasi
try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(
        MODEL_NAME,
        generation_config=genai.types.GenerationConfig(
            temperature=0.4,
            max_output_tokens=500
        )
    )
except Exception as e:
    st.error(f"Kesalahan saat menginisialisasi model: {e}")
    st.stop()

# --- Mengelola Riwayat Chat di Streamlit ---
# Cek apakah riwayat chat sudah ada di session_state
if "messages" not in st.session_state:
    # Jika belum, inisialisasi riwayat chat dengan konteks awal
    st.session_state.messages = [
        {
            "role": "user",
            "parts": ["Kamu adalah seorang apoteker. Tuliskan obat apa yang diinginkan untuk menyembuhkan penyakit anda. Jawaban singkat dan jelas. Tolak pertanyaan selain tentang obat."]
        },
        {
            "role": "model",
            "parts": ["Baik! Saya akan menjawab pertanyaan Anda tentang obat."]
        }
    ]

# Tampilkan pesan dari riwayat chat
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["parts"][0])
    elif message["role"] == "model":
        with st.chat_message("assistant"):
            st.write(message["parts"][0])
    
# Mengelola input pengguna
if user_input := st.chat_input("Tanyakan tentang obat..."):
    # Tambahkan input pengguna ke riwayat chat
    st.session_state.messages.append({"role": "user", "parts": [user_input]})
    
    # Tampilkan input pengguna di UI
    with st.chat_message("user"):
        st.write(user_input)

    # Dapatkan respons dari model
    with st.chat_message("assistant"):
        with st.spinner("Sedang membalas..."):
            try:
                # Inisialisasi sesi chat dengan riwayat yang ada di session_state
                chat = model.start_chat(history=st.session_state.messages)
                response = chat.send_message(user_input, request_options={"timeout": 60})
                
                if response and response.text:
                    st.write(response.text)
                    # Tambahkan respons model ke riwayat chat
                    st.session_state.messages.append({"role": "model", "parts": [response.text]})
                else:
                    st.error("Maaf, saya tidak bisa memberikan balasan.")
            except Exception as e:
                st.error(f"Maaf, terjadi kesalahan saat berkomunikasi dengan Gemini:")
                st.error(f"Detail Error: {e}")
