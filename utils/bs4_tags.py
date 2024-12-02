

def get_content_text_rick(url: str, title: str = None) -> tuple:
    import requests
    from bs4 import BeautifulSoup
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, "html.parser")
    body = soup.body
    if title not in body.get_text():
        title = None

    excluded_tags = [
        'script', 'style', 'noscript', 'svg', 'button', 'input',
        'textarea', 'select', 'option', 'form', 'fieldset', 'canvas',
        'nav', 'aside', 'address', 'map', 'area',
        'legend', 'iframe', 'embed', 'object', 'param', 'video', 'audio']
    for excluded_tag in excluded_tags:
        for tag in body.find_all(excluded_tag):
            tag.decompose()
    main_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']
    begin_title = not bool(title)
    for tag in body.find_all():
        tag_text = tag.get_text(strip=True)
        if not tag_text and tag.name not in main_tags:
            tag.decompose()
        if not begin_title:
            direct_text = tag.string
            if direct_text and title in direct_text:
                begin_title = True
        if not begin_title:
            if title not in tag_text:
                tag.decompose()

    allowed_attrs = ['class', 'id', 'href', 'src', 'alt', 'title']
    # new_body = BeautifulSoup('', 'html.parser')
    for tag in body.find_all():
        relevant_attrs = {
            key: value for key, value in tag.attrs.items()
            if key in allowed_attrs
        }
        tag.attrs = relevant_attrs
    # print("Body3:", body.prettify())
    new_html = body.prettify()
    return new_html, body.get_text(separator="\n")
