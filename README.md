# Monitoreo de Desplazamiento Interna

El proyecto es un scraper de noticias enfocado en la búsqueda de noticias sobre desplazamiento forzado interno

Las consultas son muy personalizables, por lo que puede buscar cualquier tema que se pueda encontrar en Google News.

Utiliza una búsqueda de contenido basada en etiquetas. El modelo SourceMethod sirve para declarar las etiquetas esperadas en el contenido para la extracción de datos.

# Flujo de Trabajo:

El modelo SearchQuery declara la consulta a buscar con un intervalo de tiempo. Al guardarse, genera automáticamente registros del modelo Link por cada noticia encontrada.
![image](https://github.com/yeeko-org/monitoreo-de-desaparicion-interna/assets/2782352/6bed8998-b42a-40ea-a1f5-ae194424e30e)


Se deben registrar SourceMethod con las etiquetas esperadas.
![image](https://github.com/yeeko-org/monitoreo-de-desaparicion-interna/assets/2782352/bc03d855-b41e-4a71-b60d-0e3979c0f996)


Seleccionando un grupo de Links, se puede usar uno de los SourceMethod que se considere adecuado para realizar el scraping. El administrador de Django está configurado para ayudar con una selección visual.
![image](https://github.com/yeeko-org/monitoreo-de-desaparicion-interna/assets/2782352/f66ea421-d881-4c65-b70e-1b8a8ca15fc8)
![image](https://github.com/yeeko-org/monitoreo-de-desaparicion-interna/assets/2782352/f2c061af-2e62-4859-8eb9-92330062bac1)


SourceMethod genera los registros News a partir de los Links seleccionados.
![image](https://github.com/yeeko-org/monitoreo-de-desaparicion-interna/assets/2782352/1976f99e-0d19-46dd-8a4b-17c746d0274d)

# Instalacion

La instalacion de la libreria pygooglenews puede causar problemas, se recomienda instalar individualmente sin dependencias:

    pip install pygooglenews --no-deps
