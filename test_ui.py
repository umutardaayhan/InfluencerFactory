from prompt_toolkit.application import Application
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import Frame, TextArea
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style

def _ask_master_prompt_fullscreen(initial_text="") -> str:
    header = Window(
        height=1,
        content=FormattedTextControl(
            " ✍️  MASTER PROMPT EKRANI | Max 5000 Karakter | Kaydet & Çık: ESC ardından ENTER"
        ),
        style="class:header"
    )

    text_area = TextArea(
        text=initial_text,
        multiline=True,
        scrollbar=True,
        focus_on_click=True,
        style="class:textarea"
    )

    frame = Frame(
        body=text_area,
        title="Persona Detayları (Açıklama veya Resim Analizi Sonucu)",
        style="class:frame"
    )

    layout = Layout(HSplit([header, frame]))

    kb = KeyBindings()

    @kb.add("escape", "enter")
    def _(event):
        content = text_area.text
        if len(content) > 5000:
            content = content[:5000]
        event.app.exit(result=content)
        
    @kb.add("c-c")
    def _(event):
        event.app.exit(result="")

    style = Style([
        ("header", "fg:#ffffff bg:#800080 bold"),
        ("frame", "fg:#00ffff"),
        ("textarea", "bg:#111111 fg:#ffffff"),
    ])

    app = Application(
        layout=layout,
        key_bindings=kb,
        style=style,
        full_screen=True,
        mouse_support=True,
    )
    result = app.run()
    return result or ""

if __name__ == "__main__":
    print("UI is ready")
