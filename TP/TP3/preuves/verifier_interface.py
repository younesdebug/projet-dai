"""Vérifications manuelles automatisées du TP, avec le navigateur Edge local."""
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "preuves"
PYTHON = ROOT / ".venv/Scripts/python.exe"
ENV = dict(os.environ, PATH=str(PYTHON.parent) + os.pathsep + os.environ["PATH"], PYTHONUTF8="1")
ENV["PYTHONUNBUFFERED"] = "1"
FLAGS = subprocess.CREATE_NO_WINDOW


def start(args, name):
    log = (OUT / f"{name}.log").open("w", encoding="utf-8")
    return subprocess.Popen(args, cwd=ROOT, env=ENV, stdout=log, stderr=log, creationflags=FLAGS)


def stop(process):
    subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True)


def visit(page):
    for _ in range(60):
        try:
            page.goto("http://127.0.0.1:8511", wait_until="domcontentloaded")
            page.get_by_text(re.compile("MaintAI · prédiction de panne|ModuleNotFoundError")).first.wait_for(timeout=10000)
            time.sleep(2)
            return
        except Exception:
            time.sleep(1)
    raise RuntimeError("Streamlit inaccessible")


def save(page, name):
    page.screenshot(path=str(OUT / f"{name}.png"), full_page=True)
    (OUT / f"{name}.txt").write_text(page.locator("body").inner_text(), encoding="utf-8")


def main():
    phase = sys.argv[1]
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1700})
        if phase == "initial":
            for label, command in [("initial-cli", [str(PYTHON.parent / "streamlit.exe")]),
                                   ("initial-module", [str(PYTHON), "-m", "streamlit"])]:
                server = start(command + ["run", "ui/app.py", "--server.port=8511", "--server.headless=true", "--server.address=127.0.0.1", "--browser.gatherUsageStats=false"], label)
                try:
                    visit(page)
                    save(page, label)
                finally:
                    stop(server)
                    time.sleep(2)
        else:
            server = start([str(PYTHON), "-m", "streamlit", "run", "ui/app.py", "--server.port=8511", "--server.headless=true", "--server.address=127.0.0.1", "--browser.gatherUsageStats=false"], phase + "-streamlit")
            try:
                visit(page)
                counts = {}
                def count(label):
                    time.sleep(2)
                    counts[label] = (OUT / (phase + "-streamlit.log")).read_text(encoding="utf-8").count("relance")
                count("initial")
                page.get_by_role("combobox").click()
                page.get_by_role("option", name="vibration_mm_s", exact=True).click()
                time.sleep(3)
                save(page, phase + "-donnees-vibration")
                count("apres_selectbox")
                if phase == "relance":
                    page.get_by_role("tab", name="Prédiction").click()
                    page.get_by_role("slider", name="Température (°C)").press("ArrowRight")
                    count("apres_curseur_dans_formulaire")
                    page.get_by_role("button", name="Prédire", exact=True).click()
                    count("apres_soumission")
                    (OUT / "relances.json").write_text(json.dumps(counts, indent=2), encoding="utf-8")
                if phase == "final":
                    api = start([str(PYTHON), "-m", "uvicorn", "maintai.api.main:app", "--env-file", ".env", "--host", "127.0.0.1", "--port", "8011"], "final-api")
                    try:
                        time.sleep(5)
                        page.get_by_role("tab", name="Prédiction").click()
                        page.get_by_label("URL de l'API", exact=True).fill("http://127.0.0.1:8011")
                        page.get_by_label("URL de l'API", exact=True).press("Enter")
                        time.sleep(2)
                        key = next(line.split("=", 1)[1] for line in (ROOT / ".env").read_text().splitlines() if line.startswith("MAINTAI_API_KEY="))
                        page.get_by_label("Clé API", exact=True).fill(key)
                        page.get_by_label("Clé API", exact=True).press("Enter")
                        time.sleep(2)
                        page.get_by_role("button", name="Prédire", exact=True).click()
                        page.get_by_text("ALERTE : risque de panne élevé.", exact=True).wait_for(timeout=20000)
                        save(page, "final-bonne-cle")
                        page.get_by_label("Clé API", exact=True).fill("fausse-cle")
                        page.get_by_label("Clé API", exact=True).press("Enter")
                        time.sleep(2)
                        page.get_by_role("button", name="Prédire", exact=True).click()
                        page.get_by_text("Erreur 401 : Clé API absente ou invalide", exact=True).wait_for(timeout=20000)
                        save(page, "final-mauvaise-cle")
                        page.get_by_label("Clé API", exact=True).fill(key)
                        page.get_by_label("Clé API", exact=True).press("Enter")
                        time.sleep(2)
                        page.get_by_role("slider", name="Température (°C)").press("Home")
                        page.get_by_role("button", name="Prédire", exact=True).click()
                        page.get_by_text("NORMAL : risque de panne faible.", exact=True).wait_for(timeout=20000)
                        save(page, "final-normal")
                        stop(api)
                        time.sleep(2)
                        page.get_by_role("button", name="Prédire", exact=True).click()
                        page.get_by_text("API injoignable : vérifiez son adresse et que le serveur est démarré.", exact=True).wait_for(timeout=20000)
                        save(page, "final-api-arretee")
                    finally:
                        stop(api)
            finally:
                stop(server)
        browser.close()


if __name__ == "__main__":
    main()
