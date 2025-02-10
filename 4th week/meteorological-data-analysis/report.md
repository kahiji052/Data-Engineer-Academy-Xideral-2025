# Análisis Meteorológico con AWS y Machine Learning

## Objetivo del Proyecto
El propósito de este repositorio es mostrar la manera en que se obtuvieron y analizaron los datos meteorológicos (para este caso, se eligió la Avenida Paseo de la Reforma en la Ciudad de México) utilizando la API de **Open-Meteor**, aplicando un proceso ETL mediante Python desde Amazon Web Services (AWS) y finalmente desarrollando un modelo de aprendizaje automático para evaluar patrones climáticos.

## 1. Obtención de los Datos
Desde **Google Colab** se utilizó la API de Open-Meteor para extraer información meteorológica diaria. Los parámetros de interés fueron los siguientes en un período de 2020 a 2024:
    • Temperatura máxima (`temperature_2m_max`)
    • Temperatura mínima (`temperature_2m_min`)
    • Temperatura media (`temperature_2m_mean`)
    • Precipitación total (`rain_sum`)
    • Horas de precipitación (`precipitation_hours`)
    • Velocidad máxima del viento a 10m (`wind_speed_10m_max`)
    • Radiación solar acumulada (`shortwave_radiation_sum`)

Debido a que estos datos serán usados desde AWS, dentro del notebook se realiza la conversión del DataFrame a CSV para poder subirlo al bucket. El notebook se encuentra dentro de este repositorio bajo el nombre: [fetch_data_&_upload_to_S3]

⚠️ **Nota**
*En este caso no se instaló AWS CLI, lo cosidero opcional debido a que mediante las variables de entorno (Secrets) definí las llaves de acceso al igual que el nombre del bucket.*
