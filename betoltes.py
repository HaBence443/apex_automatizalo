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

def list_files(folder_path):
    return [os.path.join(folder_path, f).replace(os.sep, '/') for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f))]

def load_config(path="config.json"):
    if not os.path.exists(path):
        print("A kód első futtatásánál meg kell adnod pár adatot.")
        print("Ha az adatok közül bármelyik változik két futás közt akkor töröld ki a config.json fájlt.")
        print("Az adatok megadásánál törekedj arra, hogy pontos adatokat adjál meg.")
        print("Miután megadtad a szükséges adatokat, inditsd el újra a kódot.")
        
        apexUrl = input("Add meg a workspace-d bejelentkezési oldalának linkjét: ")
        workspace = input("Add meg a workspace-d nevét: ")
        username = input("Add meg a felhasználónevedet: ")
        password = input("Add meg a jelszavadat: ")
        filePaths = list_files(input("Add meg a fájlokat tartalmazó mappa elérési útvonalát: "))
        
        default = {
            "apex_url": apexUrl,
            "workspace": workspace,
            "username": username,
            "password": password,
            "zip_files": filePaths,
            "headless": False,
            "wait_timeout": 30
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2, ensure_ascii=False)
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
    driver.get(cfg["apex_url"])

    #workspace
    workspace = driver.find_element(By.ID, "F4550_P1_COMPANY")
    workspace.clear()
    workspace.send_keys(cfg["workspace"])

    #felhasznalonev
    username = driver.find_element(By.ID, "F4550_P1_USERNAME")
    username.clear()
    username.send_keys(cfg["username"])

    #jelszo
    password = driver.find_element(By.ID, "F4550_P1_PASSWORD")
    password.clear()
    password.send_keys(cfg["password"])

    #bejelentkezo gomb
    driver.find_element(By.ID, "B232005500580944564").click()
    
    print("Bejelentkezés sikeres.")


def import_application(driver, wait, cfg, zip_path):
    print(f"\n--- Import indítása: {os.path.basename(zip_path)} ---")

    #menu gombok
    driver.find_element(By.CSS_SELECTOR, '[title="App Builder"]').click()    
    driver.find_element(By.CSS_SELECTOR, '[data-icon="app-builder-import-app"]').click()

    file_input = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
    )
    file_input.send_keys(os.path.abspath(zip_path))
    print("  Fájl kiválasztva.")

    driver.find_element(By.ID, "B45314626525446194").click()
    print("  1. lépés kész (fájl feltöltve).")

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1.5)
    driver.find_element(By.ID, "B47638615358532853").click()
    print("  2. lépés kész.")
    print(f"  Import befejezve: {os.path.basename(zip_path)}")  


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
                continue

        print("\nMinden import feldolgozva.")
        driver.quit()

    finally:
        if not cfg.get("headless", False):
            input("\nNyomj Enter-t a böngésző bezárásához...")
        driver.quit()


if __name__ == "__main__":
    main()