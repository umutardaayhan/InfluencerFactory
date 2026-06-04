"""
Influencer Factory — Web Content Writer Testleri (v3)

agents/web_content_writer.py modülü için birim testleri.
Güncel model yapısı:
  - WebBiography: date, image_prompt, content, word_count
  - WebPortrait:  date, mood_tag, image_prompt, content, word_count
  - WebNote:      content, is_pinned, word_count
  - WebContentPackage: biographies, portraits, notes

LLM API çağrısı olmadan çalışır.

Çalıştırma:
    python -m pytest tests/test_web_content.py -v
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from datetime import datetime

from core.models import WebBiography, WebPortrait, WebNote, WebContentPackage


# ─── WebBiography Model Tests ─────────────────────────────────


class TestWebBiographyModel:
    """WebBiography (tarihli enstante) model doğrulama testleri."""

    def test_valid_biography_snapshot(self):
        bio = WebBiography(
            date="November 14, 2022",
            image_prompt="A cold, sparse rehearsal room. A single standing lamp casts amber light. Winter dark outside.",
            content="I sat at the piano for two hours without playing a single note. The sheet music had been there for three weeks.",
            word_count=24,
        )
        assert bio.date == "November 14, 2022"
        assert "lamp" in bio.image_prompt
        assert bio.word_count == 24

    def test_image_prompt_present(self):
        bio = WebBiography(
            date="March 3, 2021",
            image_prompt="Candlelight. An empty corner table. Rain.",
            content="I ordered a coffee I did not drink.",
            word_count=8,
        )
        assert len(bio.image_prompt) > 0

    def test_biography_requires_date(self):
        with pytest.raises(Exception):
            WebBiography(image_prompt="A room.", content="I waited.", word_count=2)

    def test_biography_requires_content(self):
        with pytest.raises(Exception):
            WebBiography(
                date="January 1, 2023", image_prompt="A hallway.", word_count=0
            )

    def test_no_variant_field(self):
        bio = WebBiography(
            date="July 7, 2022",
            image_prompt="Fog over water at dusk.",
            content="I had been on the train for four hours.",
            word_count=10,
        )
        assert not hasattr(bio, "variant")
        assert not hasattr(bio, "tone_tags")


# ─── WebPortrait Model Tests ───────────────────────────────────


class TestWebPortraitModel:
    """WebPortrait (günlük alıntısı + image_prompt) model testleri."""

    def _make_portrait(self, mood="still"):
        return WebPortrait(
            date="October 3, 2023",
            title="The Weight of Silence",
            mood_tag=mood,
            image_prompt="The person in the reference images provided* sits near a dark window, a long coat draped over her shoulders.",
            content="I left the window open all afternoon. The curtain moved, but nothing came in.",
            word_count=16,
        )

    def test_valid_diary_entry_with_image_prompt(self):
        portrait = self._make_portrait()
        assert portrait.mood_tag == "still"
        assert "I" in portrait.content
        assert "reference images provided" in portrait.image_prompt
        assert portrait.date == "October 3, 2023"

    def test_portrait_has_image_prompt_field(self):
        """image_prompt alanı artık WebPortrait'te mevcut olmalı."""
        portrait = self._make_portrait("restless")
        assert hasattr(portrait, "image_prompt")
        assert len(portrait.image_prompt) > 0

    def test_portrait_requires_mood_tag(self):
        with pytest.raises(Exception):
            WebPortrait(
                date="January 1, 2023",
                image_prompt="A room.",
                content="I sat by the window.",
                word_count=5,
            )

    def test_portrait_requires_image_prompt(self):
        with pytest.raises(Exception):
            WebPortrait(
                date="January 1, 2023",
                mood_tag="still",
                content="I sat by the window.",
                word_count=5,
            )

    def test_no_creative_angle_field(self):
        portrait = self._make_portrait()
        assert not hasattr(portrait, "creative_angle")
        assert not hasattr(portrait, "variant")

    def test_all_mood_tags(self):
        for mood in ["still", "restless", "hollow"]:
            portrait = self._make_portrait(mood)
            assert portrait.mood_tag == mood


# ─── WebNote Model Tests ───────────────────────────────────────


class TestWebNoteModel:
    """WebNote (kısa vurucu günlük notu) model testleri."""

    def test_valid_pinned_note(self):
        note = WebNote(
            content="The cold does not arrive. It simply becomes apparent.",
            is_pinned=True,
            word_count=9,
        )
        assert note.is_pinned is True
        assert len(note.content) > 0

    def test_valid_unpinned_note(self):
        note = WebNote(
            content="I left the door slightly open. No one came through.",
            is_pinned=False,
            word_count=11,
        )
        assert note.is_pinned is False

    def test_note_requires_content(self):
        with pytest.raises(Exception):
            WebNote(is_pinned=True, word_count=0)

    def test_note_requires_is_pinned(self):
        with pytest.raises(Exception):
            WebNote(content="A note.", word_count=2)

    def test_note_word_count(self):
        note = WebNote(content="One. Two. Three.", is_pinned=False, word_count=3)
        assert note.word_count == 3

    def test_pinned_note_bool_type(self):
        note = WebNote(content="Something.", is_pinned=True, word_count=1)
        assert isinstance(note.is_pinned, bool)


# ─── WebContentPackage Tests ───────────────────────────────────


class TestWebContentPackageModel:
    """WebContentPackage paket model doğrulama testleri."""

    def _make_biographies(self):
        return [
            WebBiography(
                date=f"Month {i}, 202{i}",
                image_prompt=f"A dark room. Scene {i}.",
                content=f"I was there. Moment {i}.",
                word_count=5,
            )
            for i in range(1, 4)
        ]

    def _make_portraits(self):
        moods = ["still", "restless", "hollow"]
        titles = ["Silent Hours", "Sleepless Corridors", "After the Record"]
        return [
            WebPortrait(
                date=f"Month {i}, 202{i}",
                title=titles[i - 1],
                mood_tag=moods[i - 1],
                image_prompt=f"The person in the reference images provided* stands in scene {i}.",
                content=f"I was here. Moment {i}.",
                word_count=5,
            )
            for i in range(1, 4)
        ]

    def _make_notes(self):
        return [
            WebNote(content="A quiet observation.", is_pinned=False, word_count=3),
            WebNote(
                content="The most striking one — heavier.", is_pinned=True, word_count=6
            ),
            WebNote(content="Another understated note.", is_pinned=False, word_count=3),
        ]

    def test_full_package_creation(self):
        package = WebContentPackage(
            artist_name="Scarlett Noire",
            biographies=self._make_biographies(),
            portraits=self._make_portraits(),
            notes=self._make_notes(),
            language="English",
            generated_at=datetime.now().isoformat(),
            model_used="gemini-2.5-flash",
        )
        assert package.artist_name == "Scarlett Noire"
        assert len(package.biographies) == 3
        assert len(package.portraits) == 3
        assert len(package.notes) == 3

    def test_package_requires_notes(self):
        """notes alanı zorunlu olmalı."""
        with pytest.raises(Exception):
            WebContentPackage(
                artist_name="Scarlett Noire",
                biographies=self._make_biographies(),
                portraits=self._make_portraits(),
                generated_at=datetime.now().isoformat(),
                model_used="gemini-2.5-flash",
            )

    def test_exactly_one_pinned_note(self):
        package = WebContentPackage(
            artist_name="Scarlett Noire",
            biographies=self._make_biographies(),
            portraits=self._make_portraits(),
            notes=self._make_notes(),
            generated_at=datetime.now().isoformat(),
            model_used="gemini-2.5-flash",
        )
        pinned = [n for n in package.notes if n.is_pinned]
        assert len(pinned) == 1

    def test_package_serialization(self):
        package = WebContentPackage(
            artist_name="Scarlett Noire",
            biographies=self._make_biographies(),
            portraits=self._make_portraits(),
            notes=self._make_notes(),
            generated_at=datetime.now().isoformat(),
            model_used="gemini-2.5-flash",
        )
        data = package.model_dump()
        assert "biographies" in data
        assert "portraits" in data
        assert "notes" in data
        # Portrait'te image_prompt olmalı
        assert "image_prompt" in data["portraits"][0]
        # Note'ta is_pinned olmalı
        assert "is_pinned" in data["notes"][0]

    def test_biography_has_no_variant_in_serialized(self):
        package = WebContentPackage(
            artist_name="Scarlett Noire",
            biographies=self._make_biographies(),
            portraits=self._make_portraits(),
            notes=self._make_notes(),
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
    """Biography, portrait ve notes prompt oluşturucuların testleri."""

    SAMPLE_CTX = {
        "stage_name": "Scarlett Noire",
        "age": 29,
        "birth_year": 1997,
        "career_start_year": 2015,
        "career_peak_year": 2025,
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

    # ── Biography ────────────────────────────────────────────────

    def test_biography_prompt_returns_tuple(self):
        from agents.web_content_writer import _build_biography_prompt, _BIO_DIRECTIVES

        sys_p, human_p = _build_biography_prompt(
            self.SAMPLE_CTX, _BIO_DIRECTIVES[0], "English"
        )
        assert isinstance(sys_p, str) and len(sys_p) > 50
        assert isinstance(human_p, str) and len(human_p) > 50

    def test_biography_system_prompt_has_persona(self):
        from agents.web_content_writer import _build_biography_prompt, _BIO_DIRECTIVES

        sys_p, _ = _build_biography_prompt(
            self.SAMPLE_CTX, _BIO_DIRECTIVES[0], "English"
        )
        assert "Scarlett Noire" in sys_p

    def test_biography_prompt_asks_for_json(self):
        from agents.web_content_writer import _build_biography_prompt, _BIO_DIRECTIVES

        _, human_p = _build_biography_prompt(
            self.SAMPLE_CTX, _BIO_DIRECTIVES[1], "English"
        )
        assert "json" in human_p.lower() or "JSON" in human_p

    def test_biography_prompt_forbids_physical_detail(self):
        from agents.web_content_writer import _build_biography_prompt, _BIO_DIRECTIVES

        _, human_p = _build_biography_prompt(
            self.SAMPLE_CTX, _BIO_DIRECTIVES[0], "English"
        )
        assert (
            "physical" in human_p.lower()
            or "face" in human_p.lower()
            or "eye color" in human_p.lower()
        )

    def test_biography_has_three_directives(self):
        from agents.web_content_writer import _BIO_DIRECTIVES

        assert len(_BIO_DIRECTIVES) == 3
        moods = [d["mood"] for d in _BIO_DIRECTIVES]
        assert len(set(moods)) == 3

    def test_biography_chronology_constraint_in_system(self):
        from agents.web_content_writer import _build_biography_prompt, _BIO_DIRECTIVES

        sys_p, _ = _build_biography_prompt(
            self.SAMPLE_CTX, _BIO_DIRECTIVES[0], "English"
        )
        assert "1997" in sys_p
        assert "2015" in sys_p
        assert "CHRONOLOGY" in sys_p or "born" in sys_p.lower()

    def test_biography_date_range_in_human_prompt(self):
        from agents.web_content_writer import _build_biography_prompt, _BIO_DIRECTIVES

        _, human_p = _build_biography_prompt(
            self.SAMPLE_CTX, _BIO_DIRECTIVES[1], "English"
        )
        assert "2015" in human_p
        assert "2025" in human_p
        assert "1997" in human_p

    def test_biography_image_prompt_has_reference_marker(self):
        from agents.web_content_writer import _build_biography_prompt, _BIO_DIRECTIVES

        _, human_p = _build_biography_prompt(
            self.SAMPLE_CTX, _BIO_DIRECTIVES[0], "English"
        )
        assert "reference images provided" in human_p.lower()

    def test_biography_content_is_first_person(self):
        from agents.web_content_writer import _build_biography_prompt, _BIO_DIRECTIVES

        _, human_p = _build_biography_prompt(
            self.SAMPLE_CTX, _BIO_DIRECTIVES[0], "English"
        )
        assert "FIRST PERSON" in human_p or "first person" in human_p.lower()

    def test_biography_image_prompt_clothing_rule(self):
        from agents.web_content_writer import _build_biography_prompt, _BIO_DIRECTIVES

        _, human_p = _build_biography_prompt(
            self.SAMPLE_CTX, _BIO_DIRECTIVES[1], "English"
        )
        assert "CLOTHING" in human_p or "clothing" in human_p.lower()

    def test_biography_image_prompt_no_visible_text_rule(self):
        from agents.web_content_writer import _build_biography_prompt, _BIO_DIRECTIVES

        _, human_p = _build_biography_prompt(
            self.SAMPLE_CTX, _BIO_DIRECTIVES[2], "English"
        )
        assert (
            "TEXT" in human_p
            or "legible" in human_p.lower()
            or "readable" in human_p.lower()
        )

    def test_biography_forbidden_rules_in_system(self):
        from agents.web_content_writer import _build_biography_prompt, _BIO_DIRECTIVES

        sys_p, _ = _build_biography_prompt(
            self.SAMPLE_CTX, _BIO_DIRECTIVES[0], "English"
        )
        assert "FORBIDDEN" in sys_p

    def test_language_passed_to_biography_system(self):
        from agents.web_content_writer import _build_biography_prompt, _BIO_DIRECTIVES

        sys_p, _ = _build_biography_prompt(
            self.SAMPLE_CTX, _BIO_DIRECTIVES[0], "Turkish"
        )
        assert "Turkish" in sys_p

    # ── Portrait ─────────────────────────────────────────────────

    def test_portrait_prompt_returns_tuple(self):
        from agents.web_content_writer import (
            _build_portrait_prompt,
            _PORTRAIT_DIRECTIVES,
        )

        sys_p, human_p = _build_portrait_prompt(
            self.SAMPLE_CTX, _PORTRAIT_DIRECTIVES[0], "English"
        )
        assert isinstance(sys_p, str) and len(sys_p) > 50
        assert isinstance(human_p, str) and len(human_p) > 50

    def test_portrait_prompt_asks_for_first_person(self):
        from agents.web_content_writer import (
            _build_portrait_prompt,
            _PORTRAIT_DIRECTIVES,
        )

        sys_p, _ = _build_portrait_prompt(
            self.SAMPLE_CTX, _PORTRAIT_DIRECTIVES[0], "English"
        )
        assert "First person" in sys_p or "first person" in sys_p

    def test_portrait_prompt_asks_for_json(self):
        from agents.web_content_writer import (
            _build_portrait_prompt,
            _PORTRAIT_DIRECTIVES,
        )

        _, human_p = _build_portrait_prompt(
            self.SAMPLE_CTX, _PORTRAIT_DIRECTIVES[1], "English"
        )
        assert "json" in human_p.lower() or "JSON" in human_p

    def test_portrait_prompt_has_image_prompt_section(self):
        """Portrait prompt artık IMAGE_PROMPT talep etmeli."""
        from agents.web_content_writer import (
            _build_portrait_prompt,
            _PORTRAIT_DIRECTIVES,
        )

        _, human_p = _build_portrait_prompt(
            self.SAMPLE_CTX, _PORTRAIT_DIRECTIVES[0], "English"
        )
        assert "IMAGE_PROMPT" in human_p or "image_prompt" in human_p.lower()

    def test_portrait_image_prompt_reference_marker(self):
        """Portrait image prompt da referans ibaresi içermeli."""
        from agents.web_content_writer import (
            _build_portrait_prompt,
            _PORTRAIT_DIRECTIVES,
        )

        _, human_p = _build_portrait_prompt(
            self.SAMPLE_CTX, _PORTRAIT_DIRECTIVES[0], "English"
        )
        assert "reference images provided" in human_p.lower()

    def test_portrait_image_prompt_clothing_rule(self):
        from agents.web_content_writer import (
            _build_portrait_prompt,
            _PORTRAIT_DIRECTIVES,
        )

        _, human_p = _build_portrait_prompt(
            self.SAMPLE_CTX, _PORTRAIT_DIRECTIVES[1], "English"
        )
        assert "CLOTHING" in human_p or "clothing" in human_p.lower()

    def test_portrait_image_prompt_no_visible_text_rule(self):
        from agents.web_content_writer import (
            _build_portrait_prompt,
            _PORTRAIT_DIRECTIVES,
        )

        _, human_p = _build_portrait_prompt(
            self.SAMPLE_CTX, _PORTRAIT_DIRECTIVES[2], "English"
        )
        assert (
            "TEXT" in human_p
            or "legible" in human_p.lower()
            or "readable" in human_p.lower()
        )

    def test_portrait_json_schema_has_image_prompt(self):
        """Portrait JSON örneğinde image_prompt alanı olmalı."""
        from agents.web_content_writer import (
            _build_portrait_prompt,
            _PORTRAIT_DIRECTIVES,
        )

        _, human_p = _build_portrait_prompt(
            self.SAMPLE_CTX, _PORTRAIT_DIRECTIVES[0], "English"
        )
        assert '"image_prompt"' in human_p

    def test_portrait_has_three_directives(self):
        from agents.web_content_writer import _PORTRAIT_DIRECTIVES

        assert len(_PORTRAIT_DIRECTIVES) == 3
        mood_tags = [d["mood_tag"] for d in _PORTRAIT_DIRECTIVES]
        assert set(mood_tags) == {"still", "restless", "hollow"}

    def test_portrait_chronology_constraint_in_system(self):
        from agents.web_content_writer import (
            _build_portrait_prompt,
            _PORTRAIT_DIRECTIVES,
        )

        sys_p, _ = _build_portrait_prompt(
            self.SAMPLE_CTX, _PORTRAIT_DIRECTIVES[0], "English"
        )
        assert "1997" in sys_p
        assert "2015" in sys_p
        assert "CHRONOLOGY" in sys_p or "born" in sys_p.lower()

    def test_portrait_date_range_in_human_prompt(self):
        from agents.web_content_writer import (
            _build_portrait_prompt,
            _PORTRAIT_DIRECTIVES,
        )

        _, human_p = _build_portrait_prompt(
            self.SAMPLE_CTX, _PORTRAIT_DIRECTIVES[1], "English"
        )
        assert "2015" in human_p
        assert "2025" in human_p
        assert "1997" in human_p

    def test_language_passed_to_portrait_system(self):
        from agents.web_content_writer import (
            _build_portrait_prompt,
            _PORTRAIT_DIRECTIVES,
        )

        sys_p, _ = _build_portrait_prompt(
            self.SAMPLE_CTX, _PORTRAIT_DIRECTIVES[0], "Turkish"
        )
        assert "Turkish" in sys_p

    def test_portrait_forbidden_rules_in_system(self):
        from agents.web_content_writer import (
            _build_portrait_prompt,
            _PORTRAIT_DIRECTIVES,
        )

        sys_p, _ = _build_portrait_prompt(
            self.SAMPLE_CTX, _PORTRAIT_DIRECTIVES[0], "English"
        )
        assert "FORBIDDEN" in sys_p

    # ── Notes ────────────────────────────────────────────────────

    def test_notes_prompt_returns_tuple(self):
        from agents.web_content_writer import _build_notes_prompt

        sys_p, human_p = _build_notes_prompt(self.SAMPLE_CTX, "English")
        assert isinstance(sys_p, str) and len(sys_p) > 50
        assert isinstance(human_p, str) and len(human_p) > 50

    def test_notes_prompt_asks_for_json(self):
        from agents.web_content_writer import _build_notes_prompt

        _, human_p = _build_notes_prompt(self.SAMPLE_CTX, "English")
        assert "json" in human_p.lower() or "JSON" in human_p

    def test_notes_prompt_requests_exactly_3_notes(self):
        from agents.web_content_writer import _build_notes_prompt

        _, human_p = _build_notes_prompt(self.SAMPLE_CTX, "English")
        assert "3" in human_p or "three" in human_p.lower()

    def test_notes_prompt_requires_one_pinned(self):
        from agents.web_content_writer import _build_notes_prompt

        _, human_p = _build_notes_prompt(self.SAMPLE_CTX, "English")
        assert "is_pinned" in human_p
        assert "ONE" in human_p or "one" in human_p.lower()

    def test_notes_prompt_forbidden_rules_in_system(self):
        from agents.web_content_writer import _build_notes_prompt

        sys_p, _ = _build_notes_prompt(self.SAMPLE_CTX, "English")
        assert "FORBIDDEN" in sys_p

    def test_notes_language_passed_to_system(self):
        from agents.web_content_writer import _build_notes_prompt

        sys_p, _ = _build_notes_prompt(self.SAMPLE_CTX, "Turkish")
        assert "Turkish" in sys_p

    def test_notes_json_schema_has_notes_array(self):
        from agents.web_content_writer import _build_notes_prompt

        _, human_p = _build_notes_prompt(self.SAMPLE_CTX, "English")
        assert '"notes"' in human_p


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
