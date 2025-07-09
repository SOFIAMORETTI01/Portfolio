def main():
            # Libraries
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.common.by import By
            from webdriver_manager.chrome import ChromeDriverManager
            import pandas as pd
            import time

            options = webdriver.ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

            # URL only for Capital Federal
            url = "https://www.argenprop.com/departamentos/alquiler/capital-federal"
            driver.get(url)
            time.sleep(4)

            resultados = []
            pagina = 1

            while pagina <= 20:
                print(f"🔍 Scrapeando página {pagina}")
                cards = driver.find_elements(By.CLASS_NAME, "listing__item")

                if not cards:
                    print("⚠️ No se encontraron publicaciones en esta página. Se detiene.")
                    break

                for card in cards:
                    titulo = precio_raw = expensas_raw = ubicacion = superficie = estado = ambientes = banios = antiguedad = ""
                    moneda = ""

                    try:
                        titulo_completo = card.find_element(By.CLASS_NAME, "card__title--primary").text
                        titulo = titulo_completo.replace("Departamento en Alquiler en ", "").strip()
                    except:
                        pass

                    try:
                        precio_raw = card.find_element(By.CLASS_NAME, "card__price").text
                        moneda = "USD" if "USD" in precio_raw.upper() else "ARS"
                        precio_solo = precio_raw.split("+")[0]
                        precio_limpio = (
                            precio_solo.replace("USD", "")
                            .replace("$", "")
                            .replace(".", "")
                            .replace(",", "")
                            .strip()
                        )
                        precio = int(precio_limpio) if precio_limpio.isdigit() else ""
                    except:
                        precio = ""
                        moneda = ""

                    try:
                        expensas_raw = card.find_element(By.CLASS_NAME, "card__expenses").text
                    except:
                        if "+" in precio_raw:
                            expensas_raw = precio_raw.split("+")[1]
                        else:
                            expensas_raw = ""

                    try:
                        expensas_num = (
                            expensas_raw.replace("expensas", "")
                            .replace("$", "")
                            .replace(".", "")
                            .replace(",", "")
                            .strip()
                        )
                        expensas = int(''.join(filter(str.isdigit, expensas_num))) if expensas_num else ""
                    except:
                        expensas = ""

                    try:
                        ubicacion_raw = card.find_element(By.CLASS_NAME, "card__address").text
                        if "*RESERVADO*" in ubicacion_raw.upper():
                            ubicacion = ubicacion_raw.replace("*RESERVADO*", "").strip()
                        elif "*EN NEGOCIACION*" in ubicacion_raw.upper():
                            ubicacion = ubicacion_raw.replace("*EN NEGOCIACION*", "").strip()
                        else:
                            ubicacion = ubicacion_raw
                    except:
                        pass

                    try:
                        features = card.find_element(By.CLASS_NAME, "card__main-features").text.split("\n")
                        for item in features:
                            if "m²" in item:
                                superficie = item.lower()
                                superficie = superficie.replace("m²", "").replace("cubie", "").replace("cubierta", "")
                                superficie = superficie.replace(",", ".").strip()
                                superficie = ''.join(c for c in superficie if c.isdigit() or c == '.')
                                try:
                                    superficie = float(superficie)
                                except:
                                    superficie = ""
                            elif "ambiente" in item:
                                if "3 amb" in item:
                                    ambientes = "2 dorm."
                                elif "2 amb" in item:
                                    ambientes = "1 dorm."
                                elif "1 amb" in item:
                                    ambientes = "1 dorm."
                                else:
                                    ambientes = item
                            elif "dorm" in item:
                                ambientes = item
                            elif "baño" in item:
                                banios = ''.join(filter(str.isdigit, item))
                            elif "año" in item:
                                antiguedad = ''.join(filter(str.isdigit, item))
                            else:
                                estado = item
                    except:
                        pass

                    resultados.append({
                        "Título": titulo,
                        "Precio": precio,
                        "Moneda": moneda,
                        "Expensas": expensas,
                        "Ubicación": ubicacion,
                        "Superficie": superficie,
                        "Estado": estado,
                        "Ambientes": ambientes,
                        "Baños": banios,
                        "Antigüedad": antiguedad,
                    })

                try:
                    siguiente = driver.find_element(By.XPATH, "//a[@aria-label='Siguiente']")
                    driver.execute_script("arguments[0].click();", siguiente)
                    time.sleep(4)
                    pagina += 1
                except:
                    print("🚫 No se pudo encontrar el botón de siguiente página.")
                    break

            driver.quit()

            # DataFrame creation
            df = pd.DataFrame(resultados)

            # Neighborhood unification
            def unificar_barrio(titulo):
                titulo = titulo.lower()
                if "caballito" in titulo:
                    return "Caballito"
                elif "palermo" in titulo:
                    return "Palermo"
                elif "belgrano" in titulo:
                    return "Belgrano"
                elif "flores" in titulo:
                    return "Flores"
                elif "villa crespo" in titulo:
                    return "Villa Crespo"
                elif "almagro" in titulo:
                    return "Almagro"
                elif "recoleta" in titulo:
                    return "Recoleta"
                elif "barrio norte" in titulo:
                    return "Barrio Norte"
                elif "boedo" in titulo:
                    return "Boedo"
                elif "monserrat" in titulo:
                    return "Monserrat"
                elif "once" in titulo:
                    return "Once"
                elif "san telmo" in titulo:
                    return "San Telmo"
                elif "san cristobal" in titulo:
                    return "San Cristóbal"
                elif "retiro" in titulo or "catalinas" in titulo:
                    return "Retiro"
                elif "congreso" in titulo:
                    return "Congreso"
                elif "constitucion" in titulo:
                    return "Constitución"
                elif "paternal" in titulo:
                    return "La Paternal"
                elif "nuñez" in titulo:
                    return "Nuñez"
                elif "villa urquiza" in titulo:
                    return "Villa Urquiza"
                elif "villa devoto" in titulo:
                    return "Villa Devoto"
                elif "villa del parque" in titulo:
                    return "Villa del Parque"
                elif "villa luro" in titulo:
                    return "Villa Luro"
                elif "villa santa rita" in titulo:
                    return "Villa Santa Rita"
                elif "villa general mitre" in titulo:
                    return "Villa Gral. Mitre"
                elif "Catalinas" in titulo:
                    return "Retiro"
                else:
                    return titulo.title().split(",")[0]

            df["Barrio"] = df["Título"].apply(unificar_barrio)

            # CSV creation
            df.to_csv("scrape_argenprop.csv", index=False, encoding="utf-8-sig")
            print(f"✅ Archivo generado con {len(df)} publicaciones.")

if __name__ == "__main__":
    main()

