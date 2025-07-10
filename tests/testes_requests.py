import requests, time
import pandas as pd

from fastapi.responses import StreamingResponse
from io import BytesIO


# BASE_URL = "http://127.0.0.1:8000"
BASE_URL = "https://apiplan-qw64.onrender.com"



def pesquisa():

    payload = {
    "config_planograma": 
        {
            "CODPLANOGRAMA": "PLANOGRAMA-MARS",
            "GDL_QTDE": 8,
            "GDL_LARGURA": 120,
            "GDL_PRATELEIRA": 5,
            "GDL_ALTURA": 40,
            "CAO-PETISCO": 10,
            "CAO-UMIDO": 15,
            "CAO-SECO": 20,
            "GATO-PETISCO": 10,
            "GATO-UMIDO": 10,
            "GATO-SECO": 15
        }
    ,
    "itens_produtos": [
        {
            "tipo": "CAO",
            "grupo": "PETISCO",
            "fabricante": "MARS",
            "marca": "PEDIGREE",
            "participacao": 0.3444,
            "cor_rgb": [
                240,
                153,
                24
            ],
            "largura": 10,
            "frentes_min": 2,
            "ordem": 12
        },
        {
            "tipo": "CAO",
            "grupo": "PETISCO",
            "fabricante": "KELCO",
            "marca": "KELDOG",
            "participacao": 0.2961,
            "cor_rgb": [
                254,
                250,
                91
            ],
            "largura": 10,
            "frentes_min": 1,
            "ordem": 60
        },
        {
            "tipo": "CAO",
            "grupo": "PETISCO",
            "fabricante": "NESS",
            "marca": "BISTEQUITOS",
            "participacao": 0.1934,
            "cor_rgb": [
                37,
                211,
                102
            ],
            "largura": 10,
            "frentes_min": 1,
            "ordem": 6
        },
        {
            "tipo": "CAO",
            "grupo": "PETISCO",
            "fabricante": "GRUPO RACOES REIS",
            "marca": "BAW WAW",
            "participacao": 0.1718,
            "cor_rgb": [
                239,
                194,
                13
            ],
            "largura": 10,
            "frentes_min": 1,
            "ordem": 7
        },
        {
            "tipo": "CAO",
            "grupo": "PETISCO",
            "fabricante": "NESTLE",
            "marca": "DOG CHOW",
            "participacao": 0.01443,
            "cor_rgb": [
                64,
                158,
                26
            ],
            "largura": 10,
            "frentes_min": 1,
            "ordem": 13
        },
        {
            "tipo": "CAO",
            "grupo": "UMIDO",
            "fabricante": "MARS",
            "marca": "PEDIGREE",
            "participacao": 0.636,
            "cor_rgb": [
                240,
                153,
                24
            ],
            "largura": 10,
            "frentes_min": 2,
            "ordem": 12
        },
        {
            "tipo": "CAO",
            "grupo": "UMIDO",
            "fabricante": "NESTLE",
            "marca": "DOG CHOW",
            "participacao": 0.266,
            "cor_rgb": [
                64,
                158,
                26
            ],
            "largura": 10,
            "frentes_min": 1,
            "ordem": 13
        },
        {
            "tipo": "CAO",
            "grupo": "UMIDO",
            "fabricante": "MARS",
            "marca": "CHAMP",
            "participacao": 0.0588,
            "cor_rgb": [
                255,
                102,
                0
            ],
            "largura": 10,
            "frentes_min": 2,
            "ordem": 57
        },
        {
            "tipo": "CAO",
            "grupo": "UMIDO",
            "fabricante": "BRF",
            "marca": "BALANCE",
            "participacao": 0.0391,
            "cor_rgb": [
                24,
                198,
                189
            ],
            "largura": 10,
            "frentes_min": 1,
            "ordem": 15
        },
        {
            "tipo": "CAO",
            "grupo": "SECO",
            "fabricante": "MARS",
            "marca": "PEDIGREE",
            "participacao": 0.6342,
            "cor_rgb": [
                240,
                153,
                24
            ],
            "largura": 10,
            "frentes_min": 2,
            "ordem": 12
        },
        {
            "tipo": "CAO",
            "grupo": "SECO",
            "fabricante": "NESTLE",
            "marca": "DOG CHOW",
            "participacao": 0.0675,
            "cor_rgb": [
                64,
                158,
                26
            ],
            "largura": 10,
            "frentes_min": 1,
            "ordem": 13
        },
        {
            "tipo": "CAO",
            "grupo": "SECO",
            "fabricante": "BRF",
            "marca": "BALANCE",
            "participacao": 0.1074,
            "cor_rgb": [
                24,
                198,
                189
            ],
            "largura": 10,
            "frentes_min": 1,
            "ordem": 15
        },
        {
            "tipo": "CAO",
            "grupo": "SECO",
            "fabricante": "NESTLE",
            "marca": "ALPO",
            "participacao": 0.1909,
            "cor_rgb": [
                239,
                67,
                33
            ],
            "largura": 10,
            "frentes_min": 1,
            "ordem": 59
        },
        {
            "tipo": "GATO",
            "grupo": "PETISCO",
            "fabricante": "MARS",
            "marca": "DREAMIES",
            "participacao": 0.4771,
            "cor_rgb": [
                64,
                61,
                233
            ],
            "largura": 10,
            "frentes_min": 2,
            "ordem": 2
        },
        {
            "tipo": "GATO",
            "grupo": "PETISCO",
            "fabricante": "MARS",
            "marca": "WHISKAS",
            "participacao": 0.2102,
            "cor_rgb": [
                165,
                24,
                144
            ],
            "largura": 10,
            "frentes_min": 2,
            "ordem": 10
        },
        {
            "tipo": "GATO",
            "grupo": "PETISCO",
            "fabricante": "KELCO",
            "marca": "KEL CAT",
            "participacao": 0.1135,
            "cor_rgb": [
                255,
                255,
                255
            ],
            "largura": 10,
            "frentes_min": 1,
            "ordem": 999
        },
        {
            "tipo": "GATO",
            "grupo": "PETISCO",
            "fabricante": "NESTLE",
            "marca": "FRISKIES",
            "participacao": 0.1992,
            "cor_rgb": [
                251,
                203,
                13
            ],
            "largura": 10,
            "frentes_min": 1,
            "ordem": 11
        },
        {
            "tipo": "GATO",
            "grupo": "UMIDO",
            "fabricante": "MARS",
            "marca": "WHISKAS",
            "participacao": 0.4894,
            "cor_rgb": [
                165,
                24,
                144
            ],
            "largura": 10,
            "frentes_min": 2,
            "ordem": 10
        },
        {
            "tipo": "GATO",
            "grupo": "UMIDO",
            "fabricante": "BRF",
            "marca": "BALANCE",
            "participacao": 0.0411,
            "cor_rgb": [
                24,
                198,
                189
            ],
            "largura": 10,
            "frentes_min": 1,
            "ordem": 13
        },
        {
            "tipo": "GATO",
            "grupo": "UMIDO",
            "fabricante": "MARS",
            "marca": "KITEKAT",
            "participacao": 0.0724,
            "cor_rgb": [
                109,
                189,
                70
            ],
            "largura": 10,
            "frentes_min": 2,
            "ordem": 47
        },
        {
            "tipo": "GATO",
            "grupo": "UMIDO",
            "fabricante": "NESTLE",
            "marca": "FRISKIES",
            "participacao": 0.3971,
            "cor_rgb": [
                251,
                203,
                13
            ],
            "largura": 10,
            "frentes_min": 1,
            "ordem": 11
        },
        {
            "tipo": "GATO",
            "grupo": "SECO",
            "fabricante": "MARS",
            "marca": "WHISKAS",
            "participacao": 0.5468,
            "cor_rgb": [
                165,
                24,
                144
            ],
            "largura": 10,
            "frentes_min": 2,
            "ordem": 10
        },
        {
            "tipo": "GATO",
            "grupo": "SECO",
            "fabricante": "NESTLE",
            "marca": "FRISKIES",
            "participacao": 0.4037,
            "cor_rgb": [
                254,
                150,
                91
            ],
            "largura": 10,
            "frentes_min": 1,
            "ordem": 11
        },
        {
            "tipo": "GATO",
            "grupo": "SECO",
            "fabricante": "MARS",
            "marca": "KITEKAT",
            "participacao": 0.0496,
            "cor_rgb": [
                251,
                203,
                13
            ],
            "largura": 10,
            "frentes_min": 2,
            "ordem": 47
        }
    ]
}

    # Headers com autenticação
    headers = {
        
        "Content-Type": "application/json"
    }

    # Fazendo a requisição POST
    response = requests.post(f"{BASE_URL}/gc", json=payload, headers=headers)

    
    with open("saida_planograma.pdf", "wb") as f:
        f.write(response.content)

    print("Arquivo PDF salvo como 'saida_planograma.pdf'")

    # print(response.content)


pesquisa()
