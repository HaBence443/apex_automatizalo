import json
import time
import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def load_config(path="config.json"):
    """Konfiguráció betöltése JSON fájlból."""
    if not os.path.exists(path):
        # Alapértelmezett config létrehozása, ha nem létezik
        default = {
            "apex_url": "https://oracleapex.com/ords/r/apex/workspace-sign-in/oracle-apex-sign-in",
            "workspace": "halmaibenceworkspace",
            "username": "HALMAIB.21D@ACSJSZKI.HU",
            "password": "Jelszo123.",
            "zip_files": [
                "./apexFajlok/wireframe.zip",
                # "/path/to/app2.zip"
            ],
            "headless": False,
            "wait_timeout": 30
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2, ensure_ascii=False)
        print(f"Létrehoztam egy minta config fájlt: {path}")
        print("Töltsd ki az adatokkal, majd futtasd újra a scriptet.")
        sys.exit(0)

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def make_driver(headless=False):
    """Chrome driver inicializálása."""
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(options=opts)


def login(driver, wait, cfg):
    """Bejelentkezés az APEX workspace-be."""
    driver.get(cfg["apex_url"])

    # print("Meg van nyitva")
    # APEX login mezők (a name attribútumok stabilak a Builder login oldalon)
    # Ezt a sort en commenteltem ki
    # wait.until(EC.presence_of_element_located((By.ID, "p_flow_id")))

    workspace = driver.find_element(By.ID, "F4550_P1_COMPANY")
    workspace.clear()
    workspace.send_keys(cfg["workspace"])

    username = driver.find_element(By.ID, "F4550_P1_USERNAME")
    username.clear()
    username.send_keys(cfg["username"])

    password = driver.find_element(By.ID, "F4550_P1_PASSWORD")
    password.clear()
    password.send_keys(cfg["password"])

    driver.find_element(By.ID, "B232005500580944564").click()
    
    # Ezt a sort en commenteltem ki
    # wait.until(EC.url_contains("wwv_flow"))
    print("Bejelentkezés sikeres.")


def import_application(driver, wait, cfg, zip_path):
    """Egyetlen alkalmazás importálása."""
    print(f"\n--- Import indítása: {os.path.basename(zip_path)} ---")

    # Navigálás az Import oldalra (Application Builder > Import)
    # Az URL felépítése instance-függő lehet, ezért a felületi navigációt használjuk
    # Az eredeti sor:
    # driver.get(cfg["apex_url"].rstrip("/") + "/wwv_flow_imp.import")
    #driver.find_element(By.CSS_SELECTOR, '[data-icon="app-builder"]').click()
    driver.find_element(By.CSS_SELECTOR, '[title="App Builder"]').click()    
    driver.find_element(By.CSS_SELECTOR, '[data-icon="app-builder-import-app"]').click()

    # Fájl feltöltés
    file_input = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
    )
    file_input.send_keys(os.path.abspath(zip_path))
    print("  Fájl kiválasztva.")

    # "Next" gomb az 1. lépés után
    click_next(driver, wait, "B45314626525446194")
    print("  1. lépés kész (fájl feltöltve).")

    # 2. lépés: Install (a feltöltött fájl megerősítése / telepítés)
    click_next(driver, wait, "B47638615358532853")
    print("  2. lépés kész.")

    # 3. lépés: Install Application megerősítés
    # Itt általában egy "Install Application" / "Next" gomb van
    # click_install(driver, wait)
    
    print(f"  Import befejezve: {os.path.basename(zip_path)}")
    #driver.find_element(By.CSS_SELECTOR, '[title="App Builder"]').click()    

def click_next(driver, wait, searchedId):
    """A 'Next' gomb megkeresése és kattintása (több lehetséges szelektor)."""
    selectors = [
        (By.ID, searchedId), #Ezt a sort én adtam meg,
        (By.CSS_SELECTOR, "button[value='Next']"),
        (By.XPATH, "//button[normalize-space()='Next']"),
        (By.XPATH, "//a[normalize-space()='Next']"),
        (By.CSS_SELECTOR, "input[value='Next']"),
    ]
    btn = find_first(driver, wait, selectors)
    btn.click()
    time.sleep(1.5)  # várakozás az oldal frissülésére


def click_install(driver, wait):
    """Az 'Install' / 'Install Application' gomb kezelése."""
    selectors = [
        (By.ID, "B47638615358532853"), #Ezt a sort én adtam meg,
        (By.XPATH, "//button[contains(normalize-space(),'Import Application')]"),
        (By.XPATH, "//a[contains(normalize-space(),'Import Application')]"),
        (By.CSS_SELECTOR, "button[value='Import Application']"),
        (By.CSS_SELECTOR, "input[value='Import Application']")
    ]
    btn = find_first(driver, wait, selectors)
    btn.click()
    time.sleep(3)


def find_first(driver, wait, selectors):
    """Az első működő szelektor visszaadása a listából."""
    last_err = None
    for by, sel in selectors:
        try:
            return wait.until(EC.element_to_be_clickable((by, sel)))
        except TimeoutException as e:
            last_err = e
            continue
    raise NoSuchElementException(
        f"Egyik szelektor sem talált kattintható elemet: {selectors}"
    )


def main():
    cfg = load_config()
    driver = make_driver(cfg.get("headless", False))
    wait = WebDriverWait(driver, cfg.get("wait_timeout", 30))

    try:
        login(driver, wait, cfg)
        print("Sikeres bejelentkezes")
        for zip_path in cfg["zip_files"]:
            print(zip_path)
            
            if not os.path.exists(zip_path):
                print(f"FIGYELEM: a fájl nem található, kihagyom: {zip_path}")
                continue
            try:
                print("Az importalas kezdetet veszi")
                import_application(driver, wait, cfg, zip_path)
            except Exception as e:
                print(f"HIBA az import során ({zip_path}): {e}")
                # Folytatjuk a következő fájllal
                continue

        print("\nMinden import feldolgozva.")
        driver.quit()

    finally:
        if not cfg.get("headless", False):
            input("\nNyomj Enter-t a böngésző bezárásához...")
        driver.quit()


if __name__ == "__main__":
    main()