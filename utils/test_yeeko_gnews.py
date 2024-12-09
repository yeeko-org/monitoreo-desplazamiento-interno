

def test_yeeko_gnews():
    from utils.yeeko_gnews import YeekoGoogleNews
    gn = YeekoGoogleNews("es", "MX")
    # final_query = ("(desplazados OR desplazada OR desplazado OR desplazaron OR "
    #                "desplazadas) AND (México OR Zacatecas OR Tlaxcala OR "
    #                "Aguascalientes OR Colima OR Guanajuato)")
    final_query = ("(desplazados OR desplazada OR desplazado OR desplazaron OR "
                   "desplazadas) AND (México OR Zacatecas OR Tlaxcala OR "
                   "Aguascalientes OR Colima OR Guanajuato){{DATE}} "
                   "-colombia -gaza -líbano -israel -hamas -siria -haití")
    # negatives = [
    #     "colombia", "gaza", "líbano", "israel", "hamas", "siria", "haití"]
    # search_kwargs = {"when": "2d", "negative_words": negatives}
    search_kwargs = {"when": "2d"}
    links = gn.search(final_query, helper=False, **search_kwargs)


def test_prompt():
    from utils.open_ai import JsonRequestOpenAI
    user_prompt = (
        "290: NOTIVER (www.notiver.com\n"
        "291: Minuto Neuquen (www.minutoneuquen.com)\n"
        "292: #LA17 CONECTANDO A LA PATAGONIA (lu17.com)\n"
        "296: Clarín (www.clarin.com)\n"
        "298: Nou Diari (www.noudiari.es)\n"
        "299: A24.com (www.a24.com)\n"
        "300: El Día de Gualeguaychú (www.eldiaonline.com)\n"
        "301: El Chorrillero (elchorrillero.com)\n"
        "302: El Mañana de Reynosa (www.elmanana.com)\n"
        "303: Galiciapress (www.galiciapress.es)\n"
        "305: Real Madrid (www.realmadrid.com)\n"
        "306: Diari Més (www.diarimes.com)\n"
        "307: Diario InfoBierzo | Noticias del Bierzo, León, CyL y España (www.infobierzo.com)\n"
        "308: HaceInstantes (www.haceinstantes.com)\n"
        "310: CatalunyaPress (www.catalunyapress.es)\n"
        "311: Radio Sudamericana (www.radiosudamericana.com)\n")

    origin_request = JsonRequestOpenAI(
        "source/prompt_origin.txt")

    origin_response = origin_request.send_prompt(user_prompt)

