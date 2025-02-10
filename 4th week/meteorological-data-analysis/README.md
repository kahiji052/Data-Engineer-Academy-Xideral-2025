# Análisis Meteorológico con AWS y Machine Learning

## 📌 Objetivo del Proyecto
El propósito de este repositorio es mostrar la manera en que se obtuvieron y analizaron los datos meteorológicos (para este caso, se eligió la Avenida Paseo de la Reforma en la Ciudad de México) utilizando la API de **Open-Meteor**, aplicando un proceso ETL mediante Python desde Amazon Web Services (AWS) y finalmente desarrollando un modelo de aprendizaje automático para evaluar patrones climáticos.

En sí, espero que esta documentación pueda ser una guía en el paso a paso para quienes deseen replicarlo o tomarlo como base para otro tipo de proyectos.

## 1. Obtención de los Datos
Desde **Google Colab** se utilizó la API de Open-Meteor para extraer información meteorológica diaria. Los parámetros de interés fueron los siguientes en un período de 2020 a 2024:

- **Temperatura máxima** (`temperature_2m_max`)
- **Temperatura mínima** (`temperature_2m_min`)
- **Temperatura media** (`temperature_2m_mean`)
- **Precipitación total** (`rain_sum`)
- **Horas de precipitación** (`precipitation_hours`)
- **Velocidad máxima del viento a 10m** (`wind_speed_10m_max`)
- **Radiación solar acumulada** (`shortwave_radiation_sum`)

Debido a que estos datos serán usados desde AWS, dentro del notebook se realiza la conversión del DataFrame a CSV para poder subirlo al bucket. El notebook se encuentra dentro de este repositorio bajo el nombre: [fetch_data_&_upload_to_S3.ipynb](https://github.com/kahiji052/Data-Engineer-Academy-Xideral-2025/blob/main/4th%20week/meteorological-data-analysis/fetch_data_%26_upload_to_S3.ipynb)

🚨 **NOTA:** *en este caso no se instaló AWS CLI, lo considero opcional debido a que mediante las variables de entorno (Secrets) definí las llaves de acceso al igual que el nombre del bucket.*

En la siguiente captura de pantalla se visualiza el archivo cargado al bucket definido desde el notebook.
![image](https://github.com/user-attachments/assets/4113cd0d-2a63-4d72-84ee-178ad6d365a9)


## 2. Proceso ETL en AWS
### Creación de Función Lambda
Antes de este paso y para evitar confusiones, es importante crear un rol para la función con los permisos para S3 y CloudWatch. El nombre en mi caso fue `lambda_weather_data`.
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": [
        "arn:aws:s3:::<bucket-name>/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```
En la creación de la función sólo asigné el nombre y escogí la versión más reciente de Python (3.13), el resto se quedó por defecto.
![image](https://github.com/user-attachments/assets/3b79c572-2820-41a1-a91c-0f2d4362937b)

Una vez creada, también es importante agregar un Layer. Para este caso, sólo fue necesario pandas y la configuración fue la siguiente.
![image](https://github.com/user-attachments/assets/af1fab6d-e0f7-4211-81f9-062973ff19bc)

Mi interés es automatizar lo más que se pueda, idealmente todo. Con el notebook anterior, el trigger para la función Lambda será un evento S3, específicamente el tipo de evento que se activa cuando un archivo con prefijo `weather_` es subido (PUT) al bucket. Descarga el archivo, lo limpia eliminando las filas duplicadas y valores nulos, luego sube el archivo procesado (con el prefijo processed_) nuevamente al bucket. De manera que para este punto ya se tiene el csv original y el procesado.

El código de la función en lambda también se encuentra dentro del repositorio llamado [lambda_function.py](https://github.com/kahiji052/Data-Engineer-Academy-Xideral-2025/blob/main/4th%20week/meteorological-data-analysis/lamda_function.py)

![image](https://github.com/user-attachments/assets/053c1513-dafb-48ff-974e-a419edeb2069)

### Creación de Crawler para catalogar los datos
El Crawler detecta en automático el esquema de los datos meteorológicos (al momento de su creación, es importante crear una base de datos nueva para que los esquemas sean cargados ahí). En este caso, se creó una tabla y adjunto el esquema.
![image](https://github.com/user-attachments/assets/9487a482-af2d-4ba7-9e50-729af49c1785)
![image](https://github.com/user-attachments/assets/dda254f5-de76-481b-b5fc-90ac33eb8abc)


### Glue Job para transformar los datos (Visual ETL)
AWS Glue Job permite realizar transformaciones en los datos a través de una interfaz visual. El job quedó de la siguiente manera, a continuación explico cada nodo:

![image](https://github.com/user-attachments/assets/46764ad1-f522-448e-8b5a-a21aafb7f316)

- **Data Source:** se escogió el archivo procesado por la función lambda.
- **Transform - Change Schema:** se modificó la columna fecha para que tenga el tipo `DATE`. El resto de las columnas, al tener un valor decimal, se convirtieron a `FLOAT`.
- **Tranform - Identifier:** se generó un campo id único para cada registro.
- **Data Target:** una vez que los datos se han transformado de la manera deseada, se suben al bucket.

El archivo con los datos transformados tendrá un nombre predefinido por AWS como se ve aquí:
![image](https://github.com/user-attachments/assets/6879ed00-fad7-4c7c-bb12-6694fec3e2f0)

Y el archivo csv se encuentra aquí: [transformed_weather_data.csv](https://github.com/kahiji052/Data-Engineer-Academy-Xideral-2025/tree/main/4th%20week/meteorological-data-analysis/transformed_weather_data.csv)


## 3. Análisis Exploratorio de Datos (EDA)
Para todas las variables se implementó la transformación de datos de manera binaria y en multiclase, a pesar de que se eligió `Radiation_Class` como la variable objetivo para el modelo de Machine Learning, se realizaron las transformaciones en todas para facilitar el entrenamiento del modelo mediante categorías.

- **Lluvia** (1- lluvia, 0 - no lluvia)
- **Radiación** (2 - alta radiación, 1 - radiación moderada, 0 - baja radiación)
- **Viento** (2 - vientos fuertes, 1 - viento con ráfagas leves, 0 - sin viento)
- **Temperatura** (2 - Alta, 1 - Moderada, 0 - Baja)

Para realizar la exploración se implementó:
- **Histograma:** para ver la distribución de las variables.
- **Gráficos de Caja:** para identifican valores atípicos (y así evitar distorsiones en el modelo).
- **Matriz de correlación:** verificar las variables que están relacionadas entre sí.

Adicional, se hizo la gráfica para ver la temperatura más dominante entre el 2020 a 2024. Para el caso de Reforma fue moderada como se ve en la siguiente imagen.

![image](https://github.com/user-attachments/assets/a867ac3e-0585-4b1d-99a0-6ac83e6380c2)


## 4. Preprocesamiento de Datos
Se aplicaron técnicas de escalado para normalizar las variables numéricas, lo que mejora el rendimiento de los modelos de Machine Learning. En este caso, se utilizaron los siguientes escaladores:
- MinMaxScaler: Escala las variables a un rango de 0 a 1.
- StandardScaler: Escala las variables para que tengan una media de 0 y una desviación estándar de 1.

## 5. Implementación de Modelo de Aprendizaje Automático
Se implementó el modelo `Random Forest` para la predicción de la variable objetivo `Radiation_Class`, fue entrenado utilizando el conjunto de datos preprocesado y se utilizaron estas métricas :
- Precisión: fracción de predicciones correctas sobre el total de predicciones.
- Exactitud: proporción de predicciones positivas correctas sobre todas las predicciones positivas.
- Sensibilidad: capacidad del modelo para identificar correctamente los casos positivos (en este caso, las clases de radiación alta).


![image](https://github.com/user-attachments/assets/9bb260d3-922e-4bae-8b66-c5d52960bbdf)


## 6. Conclusiones
Principalmente, con este proyecto consolidé y apliqué los conocimientos adquiridos en el transcurso de la academia. La implementación del pipeline ETL utilizando AWS permitió automatizar el proceso de la adquisición y limpieza de los datos proporcionados de la API. Y queda la posibilidad de implementar otro tipo de modelos, o en todo caso, ir probando diferentes variables objetivo; dado que para este caso, Random Forest permitió evaluar la precisión del modelo de predicción con una presición del 79%, lo cual no es tan alto pero quizá pudo influir que en el caso de lluvias acumuladas la mayoría fue 0.
