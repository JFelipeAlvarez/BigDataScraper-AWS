import pytest
from unittest.mock import Mock, call
import datetime
from descargar import descargar_y_subir

def test_successful_download_and_upload(mocker):
    """Prueba que se descarguen y suban correctamente 10 páginas"""
    # Configurar mocks
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "contenido html"
    
    mocker.patch('requests.get', return_value=mock_response)
    mock_s3 = mocker.patch('boto3.client')
    mock_datetime = mocker.patch('datetime.datetime')
    mock_datetime.now.return_value.strftime.return_value = "2024-01-01"
    
    descargar_y_subir()
    
    # Verificar subidas a S3 (nueva forma)
    s3_instance = mock_s3.return_value
    expected_calls = [
        call.upload_file(
            f"/tmp/pagina-{i}-2024-01-01.html",
            "landing-casas-2024",
            f"pagina-{i}-2024-01-01.html"
        ) for i in range(1, 11)
    ]
    
    # Verificar cada llamada individualmente
    for i in range(1, 11):
        s3_instance.upload_file.assert_any_call(
            f"/tmp/pagina-{i}-2024-01-01.html",
            "landing-casas-2024",
            f"pagina-{i}-2024-01-01.html"
        )

def test_handle_failed_request(mocker):
    """Prueba el manejo de respuestas fallidas"""
    # Configurar mock de respuesta fallida
    mock_response = Mock()
    mock_response.status_code = 404
    
    mocker.patch('requests.get', return_value=mock_response)
    mock_s3 = mocker.patch('boto3.client')
    
    descargar_y_subir()
    
    # Verificar que no se subió nada a S3
    mock_s3.return_value.upload_file.assert_not_called()

def test_s3_object_naming(mocker):
    """Prueba el formato correcto de los nombres en S3"""
    # Configurar mocks
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "contenido"
    
    mocker.patch('requests.get', return_value=mock_response)
    mock_s3 = mocker.patch('boto3.client')
    mock_datetime = mocker.patch('datetime.datetime')
    mock_datetime.now.return_value.strftime.return_value = "2023-12-31"
    
    descargar_y_subir()
    
    # Obtener el cliente S3 mockeado
    s3_client = mock_s3.return_value
    
    # Verificar que al menos la primera página tiene el formato correcto
    s3_client.upload_file.assert_any_call(
        "/tmp/pagina-1-2023-12-31.html",
        "landing-casas-2024",
        "pagina-1-2023-12-31.html"
    )
    
    # Verificar que alguna llamada contiene el formato esperado
    expected_call = call.upload_file(
        "/tmp/pagina-1-2023-12-31.html",
        "landing-casas-2024",
        "pagina-1-2023-12-31.html"
    )
    
    assert expected_call in s3_client.upload_file.mock_calls, \
        "No se encontró el formato correcto en las llamadas a S3"
        
        