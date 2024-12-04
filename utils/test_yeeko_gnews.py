

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
