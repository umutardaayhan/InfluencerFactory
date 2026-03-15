---
name: cli-ux-design
description: Rich ve InquirerPy ile terminal UI/UX tasarımı. Gothic/Dark tema, ASCII art, progress bar, panel hizalama ve estetiğin zirvesi. CLI arayüz oluşturma veya iyileştirme yapılırken kullanılır.
---

# CLI UX Design — Terminal UI Tasarımı

## Ne Zaman Kullanılır
- Yeni CLI menü öğeleri eklenirken
- Rich Panel/Progress bar hizalama sorunları çözülürken
- Terminal estetiğini iyileştirirken
- InquirerPy prompt'ları tasarlanırken

## Teknoloji Stack'i

| Kütüphane | Kullanım |
|-----------|----------|
| `rich` | Panel, Progress, Console, Markdown rendering |
| `InquirerPy` | İnteraktif select, confirm, text prompt'ları |
| `Align` | Panel ve metin ortalama |

## Estetik Standartları

### Renk Paleti (Gothic/Dark Tema)
```python
# Başlıklar ve vurgular
"bold bright_magenta"    # Parlak mor — AI çıktıları
"bold bright_cyan"       # Parlak mavi — progress/spinner
"bright_green"           # Yeşil — başarı mesajları
"bold red"               # Kırmızı — hata mesajları
"dim"                    # Soluk — alt bilgiler, ipuçları
"bright_yellow"          # Sarı — uyarılar
```

### Panel Kuralları
```python
from rich.panel import Panel
from rich.align import Align

# ✅ DOĞRU: Ortalanmış, genişlemeyen panel
console.print(Align.center(
    Panel(content, border_style="magenta", expand=False)
))

# ❌ YANLIŞ: Expand=True veya Align olmadan
console.print(Panel(content))  # Tam ekran genişler, çirkin görünür
```

### Progress Bar
```python
from rich.progress import Progress, SpinnerColumn, TextColumn

with Progress(
    SpinnerColumn("dots", style="bright_cyan"),
    TextColumn("[bright_cyan]İşlem yapılıyor...[/bright_cyan]"),
    console=console,
) as progress:
    task = progress.add_task("Görev", total=None)
    # ... iş yap ...
    progress.update(task, completed=1)
```

## InquirerPy Kullanım Standartları

### Select Menü
```python
from InquirerPy import inquirer

choice = inquirer.select(
    message="Ne yapmak istersin?",
    choices=[
        {"name": "🎨 Tekil Görsel Üret", "value": "image_gen"},
        {"name": "📅 İçerik Takvimi Oluştur", "value": "pipeline"},
        {"name": "🚪 Çıkış", "value": "exit"},
    ],
    pointer="❯",
    qmark="🎭",
).execute()
```

### Confirm Prompt
```python
proceed = inquirer.confirm(
    message="Bu prompt harika görünüyor! Nano Banana 2 ile çizilmesini ister misin?",
    default=True,
    qmark="🍌"
).execute()
```

### Text Input
```python
user_input = inquirer.text(
    message="Fikrini yaz:",
    qmark="💡",
    validate=lambda x: len(x) > 0,
    invalid_message="Boş geçilemez!"
).execute()
```

## ASCII Art & Başlık Kuralları

### Banner Stili
- `pyfiglet` veya hardcoded ASCII art kullan
- Renklendirme: `[bright_magenta]` veya `[bright_cyan]`
- Center alignment: `Align.center()` ile ortala
- Her banner altına `[dim]` ile versiyon/slogan ekle

### Hata Mesajları — Tiyatral Stil
```python
# ❌ Robotik (YASAK)
print("İşlem başarısız oldu.")

# ✅ Tiyatral (DOĞRU)
console.print("[bold red]🚨 Perde düştü! API sahne arkasında bir sorunla karşılaştı.[/bold red]")
```

## Hizalama Sorunları Çözüm Rehberi

| Sorun | Çözüm |
|-------|-------|
| Panel tam ekran genişliyor | `expand=False` ekle |
| ASCII art kayıyor | `Align.center()` ile sarmala |
| Progress bar üst satıra binme | `console=console` parametresini ver |
| Emoji hizalama bozukluğu | Monospace font kontrol, `\u200b` zero-width kullan |
