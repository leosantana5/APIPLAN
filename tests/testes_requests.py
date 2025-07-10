import requests, time
import pandas as pd

from fastapi.responses import StreamingResponse
from io import BytesIO


BASE_URL = "http://127.0.0.1:8000"



def pesquisa():
    # Corpo da requisição
    # payload = {
    #     "documento": cpf_cnpj,
    #     "id_card":id_card
    # }

    payload = {
        "config_planograma": {
            "CODPLANOGRAMA": "PLANOGRAMA-MARS",
            "GDL_QTDE": 13,
            "GDL_LARGURA": 100,
            "GDL_PRATELEIRA": 8,
            "GDL_ALTURA": 40,
            "CAO-PETISCO": 10,
            "CAO-UMIDO": 15,
            "CAO-SECO": 20,
            "GATO-PETISCO": 10,
            "GATO-UMIDO": 10,
            "GATO-SECO": 15
        },
        "itens_produtos": [
            {
            "tipo": "CAO",
            "grupo": "SECO",
            "marca": "PEDIGREE",
            "fabricante": "MARS",
            "participacao": 0.45,
            "cor_rgb": "255,0,0"
            },
            {
            "tipo": "CAO",
            "grupo": "UMIDO",
            "marca": "CESAR",
            "fabricante": "MARS",
            "participacao": 0.55,
            "cor_rgb": "0,255,0"
            }
            # // ... outros produtos
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
