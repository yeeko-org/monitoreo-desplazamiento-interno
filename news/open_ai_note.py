from utils.open_ai import JsonRequestOpenAI


class NoteOpenAI(JsonRequestOpenAI):
    def __init__(self):
        super().__init__()
        self.first_example = """
            El Consejo de Ministros aprueba “permisos climáticos” para evitar desplazamientos durante catástrofes | Economía | EL PAÍS\n_\n_\n_\n_\nSeleccione:\n- - -\nEspaña\nAmérica\nMéxico\nColombia\nChile\nArgentina\nUS \nEspañol\nUS English\nEconomía\nsuscríbete\nH\nHOLA\nIniciar sesión\nEconomía\nMercados\nVivienda\nFormación\nMis derechos\nNegocios\nCinco Días\nRetina\nÚltimas noticias\nTRABAJO\nEl Consejo de Ministros aprueba “permisos climáticos” para evitar desplazamientos durante catástrofes\nTrabajo refuerza este derecho de los empleados, que podrán faltar hasta cuatro días “prorrogables hasta que desaparezcan las circunstancias” sin perder salario. Los comités podrán acordar el 
            parón de la actividad durante alertas\nLa vicepresidenta segunda y ministra de Trabajo, Yolanda Díaz, interviene este miércoles en el Congreso.\nEduardo Parra  (Europa Press)\nEmilio Sánchez Hidalgo\nMadrid - \n28 nov 2024 - 07:33\nCET\nWhatsapp\nFacebook\nTwitter\nLinkedin\nBluesky\nCopiar enlace\nComentarios\nEl Consejo de Ministros ha aprobado este jueves un \nnuevo paquete de políticas\n para atender a los afectados por la dana, que ha 
            causado \nmás de 200 muertos\n en la provincia de Valencia. Entre ellas hay varias medidas de carácter laboral, pensadas para trascender más allá de esta catástrofe. Destaca lo que el Ministerio de Trabajo cataloga como “permisos climáticos”, una modificación legislativa de los permisos remunerados en el Estatuto de los Trabajadores. Con ellos, el Gobierno pretende reforzar el derecho de los empleados a no acudir a su puesto durante catástrofes. Además, los representantes de los trabajadores podrán acordar el parón de la actividad durante alertas y se obligará a que \nlos convenios contengan medidas preventivas específicas.\nEstos permisos se han incluido en un tercer real decreto de medidas para afrontar las consecuencias de la DANA, valorado en 2.274 millones de euros, que incluye ayudas directas a fondo perdido de hasta 10.000 euros para la compra de vehículos y líneas de 
            apoyo para la reconstrucción del tejido productivo de las zonas afectadas.
        """
        self.first_response = {
            "title": "El Consejo de Ministros aprueba 'permisos climáticos' para proteger a empleados durante catástrofes",
            "subtitle": "Los empleados podrán faltar hasta cuatro días prorrogables sin perder salario; los convenios laborales incluirán medidas preventivas para alertas climáticas.",
            "content": "El Consejo de Ministros ha aprobado un nuevo paquete de políticas destinadas a atender a los afectados por la reciente DANA (depresión aislada en niveles altos), que ha provocado más de 200 muertos en la provincia de Valencia. Entre las medidas aprobadas, se incluyen los llamados 'permisos climáticos', una modificación legislativa en el Estatuto de los Trabajadores que permitirá a los empleados ausentarse de sus puestos de trabajo hasta por cuatro días, prorrogables, sin perder su salario, en situaciones de catástrofes naturales. Además, los comités de empresa podrán acordar el cese de actividades laborales durante alertas climáticas, y los convenios colectivos deberán incluir disposiciones específicas para prevenir riesgos asociados a fenómenos meteorológicos extremos. Estas medidas forman parte de un tercer real decreto para mitigar las consecuencias de la DANA, con una inversión de 2.274 millones de euros. Este decreto también contempla ayudas directas de hasta 10.000 euros para la compra de vehículos y programas de apoyo para la reconstrucción económica de las zonas más afectadas."
        }
        self.prompt = """
            The following text is a news article, extracted from a website, so in addition to the news article, it can contain additional information. Extract the exact information and organize it in a JSON structure. The JSON must include three main keys: "title", "subtitle" and "content" and omit everything that is not related to the content.

            1. **Title**: The concise title of the main topic of the text.
            2. **Subtitle**: Check if the text also contains a subtitle. If not, omit this information.
            3. **Content**: Analyze how much of the text is part of the news article based on the title.
        """
