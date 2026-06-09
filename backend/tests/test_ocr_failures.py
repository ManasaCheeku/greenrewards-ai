import os
import tempfile
import io
import pytest
from services import ai_verifier


def test_empty_ocr_returns_low_confidence(monkeypatch, tmp_path):
    # monkeypatch OCR to return empty string
    monkeypatch.setattr(ai_verifier, 'ocr_extract_text', lambda path: '')
    # create empty temp file
    fp = tmp_path / "empty.jpg"
    fp.write_bytes(b"")
    res = ai_verifier.verify_proof(str(fp), 'travel')
    assert 'confidence' in res
    assert res['confidence'] <= 0.9


def test_corrupted_upload(monkeypatch, tmp_path):
    # corrupted: OCR returns gibberish
    monkeypatch.setattr(ai_verifier, 'ocr_extract_text', lambda path: '\x00\x01\xff')
    fp = tmp_path / 'corrupt.jpg'
    fp.write_bytes(b"not an image")
    res = ai_verifier.verify_proof(str(fp), 'food')
    assert 'detected_action' in res
    assert isinstance(res['confidence'], float)


def test_low_confidence_detect_food(monkeypatch, tmp_path):
    monkeypatch.setattr(ai_verifier, 'ocr_extract_text', lambda path: 'some random text without keywords')
    fp = tmp_path / 'meal.jpg'
    fp.write_bytes(b"meal")
    res = ai_verifier.verify_proof(str(fp), 'food')
    assert res['confidence'] <= 0.5 or res['detected_action'] in ['non-vegetarian', 'organic']


def test_invalid_file_format_handled(tmp_path):
    fp = tmp_path / 'file.txt'
    fp.write_text('plain text not an image')
    res = ai_verifier.verify_proof(str(fp), 'waste')
    # Should classify or return default without raising
    assert 'detected_action' in res
