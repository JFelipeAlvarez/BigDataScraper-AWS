import requests
import boto3
import datetime

BUCKET_NAME = "landing-casas-2024"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}



def descargar_y_subir():
    for i in range(1, 11):
        HTML_URL = f"https://casas.mitula.com.co/find?page={i}&operationType=sell&propertyType=mitula_studio_apartment&geoId=mitula-CO-poblacion-0000014156"
        response = requests.get(HTML_URL, headers=headers)   
        if response.status_code == 200:
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            OBJECT_NAME = f"pagina-{i}-{today}.html"  
            temp_file = f"/tmp/{OBJECT_NAME}"
            with open(temp_file, "w", encoding="utf-8") as file:
                file.write(response.text)
            s3_client = boto3.client("s3")
            s3_client.upload_file(temp_file, BUCKET_NAME, OBJECT_NAME)
            print(f"Archivo subido a S3: s3://{BUCKET_NAME}/{OBJECT_NAME}")
        else:
            print(f"Error al descargar la página: {response.status_code}")


def app(event, context):
    descargar_y_subir()
    return {}