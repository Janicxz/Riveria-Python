import requests
import json
import time

def hae_data(sivu):
    """
    Hakee PRH:n avoimen datan API:sta (v3) ohjelmistoalalla toimivien yritysten tiedot ja palauttaa valitun sivun tiedot.
    Args:
        sivu (int): Sivu jolta haetaan yritysten tiedot.
    Returns:
        (dict): Palauttaa yritysten tiedot.
    """
    vuodesta_lahtien = 1990
    API_URL = f"https://avoindata.prh.fi/opendata-ytj-api/v3/companies?mainBusinessLine=ohjelmisto&registrationDateStart={vuodesta_lahtien}-01-01&page={sivu}"
    print(f"Haetaan sivun {sivu} tietoja")
    response = requests.get(API_URL)
    data = response.json()
    if response.status_code == 200 and response.text:
        return data
    elif response.status_code == 429:
        print("Liikaa pyyntöjä, odotetaan hetki ja yritetään uudelleen..")
        time.sleep(10)
        hae_data(sivu)
    else:
        print(f"Tietoja ei löytynyt osoitteesta {API_URL}")
        return None

def hae_osoitetiedot(yritys_tiedot):
    """
        Palauttaa yrityksen osoite- ja yhteystiedot.
    """
    osoite = ""
    postinumero = ""
    postitoimipaikka = ""
    yhteystiedot = ""

    if "website" in yritys_tiedot:
        if "url" in yritys_tiedot["website"]:
            yhteystiedot = yritys_tiedot["website"]["url"]

    if len(yritys_tiedot["addresses"]) > 0:
        if "street" in yritys_tiedot["addresses"][0]:
            osoite = yritys_tiedot["addresses"][0]["street"] + " "
            if "buildingNumber" in yritys_tiedot["addresses"][0]:
                osoite = osoite + yritys_tiedot["addresses"][0]["buildingNumber"] + " "
            if "apartmentIdSuffix" in yritys_tiedot["addresses"][0]:
                if yritys_tiedot["addresses"][0]["apartmentIdSuffix"] != "":
                    osoite = osoite + yritys_tiedot["addresses"][0]["apartmentIdSuffix"] + " "
            if "apartmentNumber" in yritys_tiedot["addresses"][0]:
                if yritys_tiedot["addresses"][0]["apartmentNumber"] != "":
                    osoite = osoite + yritys_tiedot["addresses"][0]["apartmentNumber"]
        elif "freeAddressLine" in yritys_tiedot["addresses"][0]:
            osoite = yritys_tiedot["addresses"][0]["freeAddressLine"]

        if "postCode" in yritys_tiedot["addresses"][0]:
            postinumero = yritys_tiedot["addresses"][0]["postCode"]
        if len(yritys_tiedot["addresses"][0]["postOffices"]) > 0:
            if "city" in yritys_tiedot["addresses"][0]["postOffices"][0]:
                postitoimipaikka = yritys_tiedot["addresses"][0]["postOffices"][0]["city"]
    return (osoite, postinumero, postitoimipaikka, yhteystiedot)

kaikki_tiedot = []
def lisaa_yrityksen_tiedot(yritys):
    """
        Lisää yrityksen tiedot kaikki_tiedot listaan.
    """
    ytunnus = yritys["businessId"]["value"]
    osoite, postinumero, postitoimipaikka, yhteystiedot = hae_osoitetiedot(yritys)
    lakkaamispaiva = ""

    if "endDate" in yritys:
        lakkaamispaiva = yritys["endDate"]

    tiedot = {
        "Y_tunnus": ytunnus,
        "Rekisterointi_pvm": yritys["registrationDate"],
        "Lakkaamispaiva": lakkaamispaiva,
        #"Viimeksimuokattu": yritys_tiedot["lastModified"],
        "Nimi": yritys["names"][0]["name"],
        "Toimiala": yritys["mainBusinessLine"]["descriptions"][0]["description"],
        "Yritysmuoto": yritys["companyForms"][0]["descriptions"][2]["description"],
        "Osoite": osoite,
        "Postinumero": postinumero,
        "Postitoimipaikka": postitoimipaikka,
        "Yhteystiedot": yhteystiedot

    }
    kaikki_tiedot.append(tiedot)

def main():
    """
        Hakee ohjelmistoalalla toimivien yritysten tiedot PRH:n avoindata API:sta, käsittelee ja tallentaa ne ohjelmistoalanyritykset.json tiedostoon.
    """
    alku_vuosi = 1990
    sivu = 1
    sivujen_maara = 0
    API_URL = f"https://avoindata.prh.fi/opendata-ytj-api/v3/companies?mainBusinessLine=ohjelmisto&registrationDateStart={alku_vuosi}-01-01&page={sivu}"
    data = hae_data(sivu)

    sivujen_maara = data["totalResults"]//100
    print(f"Sivuja yhteensä: {sivujen_maara}")
    while (sivu <= sivujen_maara):
        data = hae_data(sivu)
        yritysten_maara = len(data["companies"])
        yrityksia_lisatty = 1
        for yritys in data["companies"]:
            ytunnus = yritys["businessId"]["value"]
            print(f"Lisätään yrityksen {ytunnus} tiedot. ({yrityksia_lisatty}/{yritysten_maara}) sivu ({sivu}/{sivujen_maara})")
            lisaa_yrityksen_tiedot(yritys)
            yrityksia_lisatty += 1
        sivu += 1

    filename = f"ohjelmistoalanyritykset.json"
    with open(filename, "w") as json_file:
        json.dump(kaikki_tiedot, json_file)
        print(f"Tallennettu: {filename}")

if __name__ == "__main__":
    main()