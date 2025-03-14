import boto3
import csv
import datetime
from bs4 import BeautifulSoup



s3_client = boto3.client("s3")
BUCKET_DESTINO = "casas-final2024"


def app(event, context):
    bucket_origen = event["Records"][0]["s3"]["bucket"]["name"]
    archivo_html = event["Records"][0]["s3"]["object"]["key"]
    print(f"Procesando archivo: {archivo_html} desde {bucket_origen}")
    
    response = s3_client.get_object(Bucket=bucket_origen, Key=archivo_html)
    contenido_html = response["Body"].read().decode("utf-8")
    
    soup = BeautifulSoup(contenido_html, "html.parser")
    
    casas = []


    for card in soup.find_all("a", class_="listing listing-card"):
        data = {
            "FechaDescarga": datetime.datetime.now().strftime("%Y-%m-%d"), 
            "Barrio": card.get("data-location"),
            "Valor": card.get("data-price"),
            "NumHabitaciones": card.get("data-rooms"),
            "NumBanos": card.find("p", {"data-test": "bathrooms"}).get("content") if card.find("p", {"data-test": "bathrooms"}) else None,
            "mts2": card.get("data-floorarea"),
        }
        casas.append(data)
    
    fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d")
    name_file = archivo_html.replace(".html", "")
    nombre_csv = f"{name_file}.csv"
    ruta_csv = f"/tmp/{nombre_csv}"  

    
    with open(ruta_csv, "w", newline="", encoding="utf-8-sig") as csvfile:
        campos = ['FechaDescarga', 'Barrio', 'Valor', 'NumHabitaciones', 'NumBanos', 'mts2']
        writer = csv.DictWriter(csvfile, fieldnames=campos, delimiter=';')
        
        writer.writeheader()
        writer.writerows(casas)

    
    s3_client.upload_file(ruta_csv, BUCKET_DESTINO, f"{fecha_hoy}/{nombre_csv}")

    print(f"Archivo CSV subido: s3://{BUCKET_DESTINO}/{fecha_hoy}/{nombre_csv}")
    
    return {}
    