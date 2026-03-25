"""
Influencer Factory — Web Content Writer Testleri (v2)

agents/web_content_writer.py modülü için birim testleri.
Yeni model yapısına göre güncellenmiştir:
  - WebBiography: date, image_prompt, content, word_count
  - WebPortrait: date, mood_tag, content, word_count

LLM API çağrısı olmadan çalışır.

Çalıştırma:
    python -m pytest tests/test_web_content.py -v
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from datetime import datetime

from core.models import WebBiography, WebPortrait, WebContentPackage


# ─── WebBiography Model Tests ─────────────────────────────────

class TestWebBiographyModel:
    """WebBiography (tarihli enstante) model doğrulama testleri."""

    def test_valid_biography_snapshot(self):
        bio = WebBiography(
            date="November 14, 2022",
            image_prompt="A cold, sparse rehearsal room. A single standing lamp casts amber light on sheet music. Winter dark outside the window.",
            content="She sat at the piano for two hours without playing a single note. The sheet music had been there for three weeks. She turned it face-down.",
            word_count=30,
        )
        assert bio.date == "November 14, 2022"
        assert "lamp" in bio.image_prompt
        assert bio.word_count == 30

    def test_image_prompt_present(self):
        """image_prompt boş olmamalı."""
        bio = WebBiography(
            date="March 3, 2021",
            image_prompt="Candlelight. An empty corner table. The sound of rain.",
            content="She ordered a coffee she did not drink.",
            word_count=8,
        )
        assert len(bio.image_prompt) > 0

    def test_biography_requires_date(self):
        """date eksikliğinde hata fırlatılmalı."""
        with pytest.raises(Exception):
            WebBiography(
                image_prompt="A room.",
                content="She waited.",
                word_count=2,
            )

    def test_biography_requires_content(self):
        """content eksikliğinde hata fırlatılmalı."""
        with pytest.raises(Exception):
            WebBiography(
                date="January 1, 2023",
                image_prompt="A hallway.",
                word_count=0,
            )

    def test_no_variant_field(self):
        """Eski 'variant' alanı artık modelde olmamalı (yeni yapı)."""
        bio = WebBiography(
            date="July 7, 2022",
            image_prompt="Fog over water at dusk.",
            content="She had been on the train for four hours and still had not opened her notebook.",
            word_count=18,
        )
        assert not hasattr(bio, "variant")
        assert not hasattr(bio, "tone_tags")


# ─── WebPortrait Model Tests ───────────────────────────────────

class TestWebPortraitModel:
    """WebPortrait (günlük alıntısı) model doğrulama testleri."""

    def test_valid_diary_entry(self):
        portrait = WebPortrait(
            date="October 3, 2023",
            mood_tag="still",
            content="I left the window open all afternoon. The curtain moved, but nothing came in. I watched it for a long time.",
            word_count=22,
        )
        assert portrait.mood_tag == "still"
        assert "I" in portrait.content  # birinci şahıs
        assert portrait.date == "October 3, 2023"

    def test_restless_mood(self):
        portrait = WebPortrait(
            date="February 17, 2024",
            mood_tag="restless",
            content="I made tea and forgot it on the counter. Three times. The same thought keeps arriving and I keep putting it down elsewhere.",
            word_count=27,
        )
        assert portrait.mood_tag == "restless"

    def test_hollow_mood(self):
        portrait = WebPortrait(
            date="August 29, 2022",
            mood_tag="hollow",
            content="The session ended at 4. I sat in the parking lot for a while. It was finished. That's all.",
            word_count=20,
        )
        assert portrait.mood_tag == "hollow"

    def test_portrait_requires_mood_tag(self):
        """mood_tag eksikliğinde hata fırlatılmalı."""
        with pytest.raises(Exception):
            WebPortrait(
                date="January 1, 2023",
                content="I sat by the window.",
                word_count=5,
            )

    def test_no_creative_angle_field(self):
        """Eski 'creative_angle' alanı artık modelde olmamalı."""
        portrait = WebPortrait(
            date="May 10, 2023",
            mood_tag="still",
            content="The day passed without event.",
            word_count=5,
        )
        assert not hasattr(portrait, "creative_angle")
        assert not hasattr(portrait, "variant")


# ─── WebContentPackage Tests ───────────────────────────────────

class TestWebContentPackageModel:
    """WebContentPackage paket model doğrulama testleri."""

    def _make_biographies(self):
        return [
            WebBiography(
                date=f"Month {i}, 202{i}",
                image_prompt=f"A dark room. Scene {i}.",
                content=f"A moment from period {i}.",
                word_count=5,
            )
            for i in range(1, 4)
        ]

    def _make_portraits(self):
        moods = ["still", "restless", "hollow"]
        return [
            WebPortrait(
                date=f"Month {i}, 202{i}",
                mood_tag=moods[i - 1],
                content=f"I was here. Moment {i}.",
                word_count=5,
            )
            for i in range(1, 4)
        ]

    def test_full_package_creation(self):
        package = WebContentPackage(
            artist_name="Scarlett Noire",
            biographies=self._make_biographies(),
            portraits=self._make_portraits(),
            language="English",
            generated_at=datetime.now().isoformat(),
            model_used="gemini-2.5-flash",
        )
        assert package.artist_name == "Scarlett Noire"
        assert len(package.biographies) == 3
        assert len(package.portraits) == 3

    def test_package_default_language(self):
        package = WebContentPackage(
            artist_name="Scarlett Noire",
            biographies=self._make_biographies(),
            portraits=self._make_portraits(),
            generated_at=datetime.now().isoformat(),
            model_used="gemini-2.5-flash",
        )
        assert package.language == "English"

    def test_package_serialization(self):
        package = WebContentPackage(
            artist_name="Scarlett Noire",
            biographies=self._make_biographies(),
            portraits=self._make_portraits(),
            generated_at=datetime.now().isoformat(),
            model_used="gemini-2.5-flash",
        )
        data = package.model_dump()
        assert isinstance(data, dict)
        assert "biographies" in data and "portraits" in data
        assert len(data["biographies"]) == 3
        # Yeni alanlar mevcut
        assert "date" in data["biographies"][0]
        assert "image_prompt" in data["biographies"][0]
        assert "mood_tag" in data["portraits"][0]

    def test_biography_has_no_variant_in_serialized(self):
        """Serileştirilmiş JSON'da eski 'variant' alanı olmamalı."""
        package = WebContentPackage(
            artist_name="Scarlett Noire",
            biographies=self._make_biographies(),
            portraits=self._make_portraits(),
            generated_at=datetime.now().isoformat(),
            model_used="gemini-2.5-flash",
        )
        data = package.model_dump()
        assert "variant" not in data["biographies"][0]
        assert "tone_tags" not in data["biographies"][0]
        assert "creative_angle" not in data["portraits"][0]


# ─── Persona Loading Tests ─────────────────────────────────────

class TestPersonaLoading:
    PERSONA_DIR = str(Path(__file__).parent.parent / "personas" / "scarlett_noire")

    def test_persona_dir_exists(self):
        assert Path(self.PERSONA_DIR).exists()

    def test_persona_json_exists(self):
        assert (Path(self.PERSONA_DIR) / "persona.json").exists()

    def test_seed_json_exists(self):
        assert (Path(self.PERSONA_DIR) / "seed.json").exists()

    def test_load_cached_persona(self):
        from core.persona_loader import load_cached_persona
        persona = load_cached_persona(self.PERSONA_DIR)
        assert persona is not None
        assert persona.stage_name == "Scarlett Noire"

    def test_persona_has_biography(self):
        from core.persona_loader import load_cached_persona
        persona = load_cached_persona(self.PERSONA_DIR)
        assert persona is not None
        assert len(persona.biography) > 0

    def test_load_seed(self):
        from core.persona_loader import load_seed
        seed = load_seed(self.PERSONA_DIR)
        assert isinstance(seed, dict)
        assert "name" in seed


# ─── Prompt Builder Tests ──────────────────────────────────────

class TestPromptBuilders:
    """Biography ve portrait prompt oluşturucuların doğruluğunu test eder."""

    SAMPLE_CTX = {
        "stage_name": "Scarlett Noire",
        "age": 25,
        "biography_base": "A musician weaving gothic narratives.",
        "tone": "Calm, measured, melancholic but comforting.",
        "speaking_style": "Well-structured, evocative, lyrical.",
        "catchphrases": ["May your shadows be deep.", "Listen closely."],
        "visual_references": "Gothic Rock, Dark Cabaret, Cinematic Noir.",
        "fashion_style": "Dark neo-gothic, Victorian, lace and leather.",
        "color_palette": "Jet Black, Platinum Blonde, Crimson Red",
        "music_genre": "Dark Pop, Gothic Pop",
        "personality_hints": "Never ironic, always restrained.",
        "extra_notes": "No romance, no sexuality.",
        "content_niche": "Quiet observation, memory.",
    }

    def test_biography_prompt_returns_tuple(self):
        from agents.web_content_writer import _build_biography_prompt, _BIO_DIRECTIVES
        sys_p, human_p = _build_biography_prompt(self.SAMPLE_CTX, _BIO_DIRECTIVES[0], "English")
        assert isinstance(sys_p, str) and len(sys_p) > 50
        assert isinstance(human_p, str) and len(human_p) > 50

    def test_biography_system_prompt_has_persona(self):
        from agents.web_content_writer import _build_biography_prompt, _BIO_DIRECTIVES
        sys_p, _ = _build_biography_prompt(self.SAMPLE_CTX, _BIO_DIRECTIVES[0], "English")
        assert "Scarlett Noire" in sys_p

    def test_biography_prompt_asks_for_json(self):
        """Biography prompt'u JSON döndürmesini talep etmeli."""
        from agents.web_content_writer import _build_biography_prompt, _BIO_DIRECTIVES
        _, human_p = _build_biography_prompt(self.SAMPLE_CTX, _BIO_DIRECTIVES[1], "English")
        assert "json" in human_p.lower() or "JSON" in human_p

    def test_biography_prompt_forbids_physical_detail(self):
        """Image prompt'un aşırı fiziksel betimleme yapmayacağına dair yönerge olmalı."""
        from agents.web_content_writer import _build_biography_prompt, _BIO_DIRECTIVES
        _, human_p = _build_biography_prompt(self.SAMPLE_CTX, _BIO_DIRECTIVES[0], "English")
        assert "physical" in human_p.lower() or "face" in human_p.lower() or "eye color" in human_p.lower()

    def test_biography_prompt_has_three_directives(self):
        """3 farklı direktif mevcut olmalı."""
        from agents.web_content_writer import _BIO_DIRECTIVES
        assert len(_BIO_DIRECTIVES) == 3
        moods = [d["mood"] for d in _BIO_DIRECTIVES]
        # Hepsi farklı olmalı
        assert len(set(moods)) == 3

    def test_portrait_prompt_returns_tuple(self):
        from agents.web_content_writer import _build_portrait_prompt, _PORTRAIT_DIRECTIVES
        sys_p, human_p = _build_portrait_prompt(self.SAMPLE_CTX, _PORTRAIT_DIRECTIVES[0], "English")
        assert isinstance(sys_p, str) and len(sys_p) > 50
        assert isinstance(human_p, str) and len(human_p) > 50

    def test_portrait_prompt_asks_for_first_person(self):
        """Portrait prompt'u birinci şahıs talep etmeli."""
        from agents.web_content_writer import _build_portrait_prompt, _PORTRAIT_DIRECTIVES
        sys_p, _ = _build_portrait_prompt(self.SAMPLE_CTX, _PORTRAIT_DIRECTIVES[0], "English")
        assert "First person" in sys_p or "first person" in sys_p

    def test_portrait_prompt_asks_for_json(self):
        from agents.web_content_writer import _build_portrait_prompt, _PORTRAIT_DIRECTIVES
        _, human_p = _build_portrait_prompt(self.SAMPLE_CTX, _PORTRAIT_DIRECTIVES[1], "English")
        assert "json" in human_p.lower() or "JSON" in human_p

    def test_portrait_has_three_directives(self):
        from agents.web_content_writer import _PORTRAIT_DIRECTIVES
        assert len(_PORTRAIT_DIRECTIVES) == 3
        mood_tags = [d["mood_tag"] for d in _PORTRAIT_DIRECTIVES]
        assert set(mood_tags) == {"still", "restless", "hollow"}

    def test_language_passed_to_biography_system(self):
        from agents.web_content_writer import _build_biography_prompt, _BIO_DIRECTIVES
        sys_p, _ = _build_biography_prompt(self.SAMPLE_CTX, _BIO_DIRECTIVES[0], "Turkish")
        assert "Turkish" in sys_p

    def test_language_passed_to_portrait_system(self):
        from agents.web_content_writer import _build_portrait_prompt, _PORTRAIT_DIRECTIVES
        sys_p, _ = _build_portrait_prompt(self.SAMPLE_CTX, _PORTRAIT_DIRECTIVES[0], "Turkish")
        assert "Turkish" in sys_p

    def test_biography_forbidden_rules_in_system(self):
        from agents.web_content_writer import _build_biography_prompt, _BIO_DIRECTIVES
        sys_p, _ = _build_biography_prompt(self.SAMPLE_CTX, _BIO_DIRECTIVES[0], "English")
        assert "FORBIDDEN" in sys_p

    def test_portrait_forbidden_rules_in_system(self):
        from agents.web_content_writer import _build_portrait_prompt, _PORTRAIT_DIRECTIVES
        sys_p, _ = _build_portrait_prompt(self.SAMPLE_CTX, _PORTRAIT_DIRECTIVES[0], "English")
        assert "FORBIDDEN" in sys_p


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
