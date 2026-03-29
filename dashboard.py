"""
Influencer Factory — Web Dashboard (Streamlit)
Oluşturulan verileri ve personaları Excel estetiğinde görselleştiren araç.
Kullanım: streamlit run dashboard.py
"""
import streamlit as st
import pandas as pd
import json
from pathlib import Path

st.set_page_config(
    page_title="Influencer Factory Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Estetik CSS Ayarları
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.15rem;
        font-weight: 600;
        color: #E0E0E0;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] [data-testid="stMarkdownContainer"] p {
        color: #D6336C; /* bright_magenta vibe */
    }
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏭 AI Influencer Factory Dashboard")
st.markdown("Personaları ve output verilerinizi yönetebileceğiniz, rahat okunabilir bir arayüz.")
st.divider()

tab1, tab2, tab3 = st.tabs(["🎭 Sanatçı Profilleri", "🚀 Sosyal Medya Çıktıları", "🌐 Web İçerikleri"])

# ─── 1. PERSONA TABLOSU ──────────────────────────────────────────────
with tab1:
    st.subheader("Mevcut Personalar")
    personas_dir = Path("personas")
    persona_data = []

    if personas_dir.exists():
        for entry in sorted(personas_dir.iterdir()):
            if entry.is_dir() and (entry / "seed.json").exists():
                try:
                    with open(entry / "seed.json", "r", encoding="utf-8") as f:
                        seed = json.load(f)
                    
                    has_cache = (entry / "persona.json").exists()
                    img_dir = entry / "images"
                    
                    # Say resimleri
                    extensions = ["*.jpg", "*.jpeg", "*.png", "*.webp"]
                    img_count = sum(1 for ext in extensions for _ in img_dir.glob(ext)) if img_dir.exists() else 0

                    music_dict = seed.get("music") or {}
                    content_dict = seed.get("content") or {}
                    genre = music_dict.get("genre") or content_dict.get("niche") or seed.get("profession", "Bilinmiyor")

                    persona_data.append({
                        "Klasör": entry.name,
                        "Sahne Adı": seed.get("stage_name", seed.get("name", entry.name)),
                        "Meslek / Tür": genre,
                        "Kişilik Notları (Özet)": seed.get("personality_hints", "")[:60] + "...",
                        "Görsel Havuzu": f"{img_count} Fotoğraf",
                        "AI Persona Belleği": "✅ Mevcut" if has_cache else "❌ Yok"
                    })
                except Exception as e:
                    st.error(f"Hata okunurken: {entry.name} - {e}")
    
    if persona_data:
        df_personas = pd.DataFrame(persona_data)
        st.dataframe(df_personas, use_container_width=True, hide_index=True)
    else:
        st.info("Kayıtlı sanatçı/persona bulunamadı.")


# ─── 2. SOSYAL MEDYA ÇIKTILARI ───────────────────────────────────────
with tab2:
    st.subheader("Üretilen İçerik Paketleri")
    output_dir = Path("output")
    if output_dir.exists():
        # output içindeki sadece dizinleri (web_content hariç) al
        plan_dirs = [d for d in output_dir.iterdir() if d.is_dir() and d.name != "web_content"]
        
        if plan_dirs:
            plan_dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)
            dir_names = [d.name for d in plan_dirs]
            
            selected_dir = st.selectbox("İncelemek istediğiniz içerik paketini seçin:", dir_names)
            
            if selected_dir:
                selected_path = output_dir / selected_dir
                md_files = sorted(selected_path.glob("*.md"))
                json_files = sorted(selected_path.glob("*.json"))
                
                if md_files or json_files:
                    st.divider()
                    
                    if json_files:
                        st.markdown("### 📊 Veri Tabloları (JSON)")
                        for j_file in json_files:
                            try:
                                with open(j_file, "r", encoding="utf-8") as f:
                                    j_data = json.load(f)
                                    
                                if isinstance(j_data, dict):
                                    v_prompts = j_data.get("visual_prompts", [])
                                    if v_prompts:
                                        st.caption(f"🎨 Görsel Promptları ({len(v_prompts)})")
                                        st.dataframe(pd.DataFrame(v_prompts), use_container_width=True)
                                        
                                    vid_prompts = j_data.get("video_prompts", [])
                                    if vid_prompts:
                                        st.caption(f"🎬 Video Promptları ({len(vid_prompts)})")
                                        st.dataframe(pd.DataFrame(vid_prompts), use_container_width=True)
                                        
                                    caps = j_data.get("captions", [])
                                    if caps:
                                        st.caption(f"✍️ Captions & Metinler ({len(caps)})")
                                        st.dataframe(pd.DataFrame(caps), use_container_width=True)
                            except Exception as e:
                                st.warning(f"JSON verisi işlenemedi: {e}")
                                
                    if md_files:
                        st.markdown("### 📄 Raporlar ve Metinler")
                        md_tabs = st.tabs([f.name.replace(".md", "").replace("_", " ") for f in md_files])
                        for t, m_file in zip(md_tabs, md_files):
                            with t:
                                with open(m_file, "r", encoding="utf-8") as f:
                                    st.markdown(f.read())
                else:
                    st.warning("Bu paket içinde MD veya JSON dosyası bulunamadı.")
        else:
            st.info("Henüz sosyal medya içerik paketi üretilmemiş veya bulunamıyor.")
    else:
        st.info("output klasörü henüz oluşturulmamış.")


# ─── 3. WEB İÇERİKLERİ ──────────────────────────────────────────────
with tab3:
    st.subheader("🌐 Web İçerikleri (JSON Datagrid)")
    web_dir = Path("output/web_content")
    
    if web_dir.exists():
        json_files = list(web_dir.glob("*.json"))
        
        if json_files:
            json_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            web_file_names = [f.name for f in json_files]
            
            selected_web_json = st.selectbox("İncelemek istediğiniz web içerik verisini (JSON) seçin:", web_file_names)
            
            if selected_web_json:
                with open(web_dir / selected_web_json, "r", encoding="utf-8") as f:
                    web_data = json.load(f)
                
                st.write(f"**Sanatçı:** {web_data.get('artist_name')} | **Dil:** {web_data.get('language')} | **Tarih:** {web_data.get('generated_at')}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 📖 Biography Snapshot'ları")
                    bios = web_data.get("biographies", [])
                    if bios:
                        df_bio = pd.DataFrame(bios)
                        # Sütunları düzenle
                        df_bio = df_bio[["date", "content", "image_prompt", "word_count"]]
                        st.dataframe(df_bio, use_container_width=True, hide_index=True)
                    else:
                        st.caption("Veri yok.")
                        
                with col2:
                    st.markdown("### 📔 Portrait Günlükleri")
                    ports = web_data.get("portraits", [])
                    if ports:
                        df_port = pd.DataFrame(ports)
                        df_port = df_port[["date", "mood_tag", "content", "image_prompt"]]
                        st.dataframe(df_port, use_container_width=True, hide_index=True)
                    else:
                        st.caption("Veri yok.")
                        
                st.markdown("### 📝 Pinned & Loose Notes")
                notes = web_data.get("notes", [])
                if notes:
                    df_notes = pd.DataFrame(notes)
                    st.dataframe(df_notes, use_container_width=True, hide_index=True)
                
        else:
            st.info("Henüz web içerik JSON çıktısı üretilmemiş.")
    else:
        st.info("output/web_content klasörü bulunamadı.")
