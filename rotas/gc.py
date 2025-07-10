# from fastapi import APIRouter, Request, Depends
# from fastapi.responses import JSONResponse
# import json
# import re
# from .planograma import *
# from io import StringIO

# from fastapi.responses import StreamingResponse
# from io import BytesIO

# router = APIRouter()

# @router.post("/gc")
# async def validar_gc(
#     request: Request
# ):
#     body = await request.json()
#     cgc_input = str(body.get("documento")).strip()

#     gerar_planograma()


#     dados = {
#         "CODPLANOGRAMA": "PLANOGRAMA-MARS",
#         "GDL_QTDE": 13,
#         "GDL_LARGURA": 100,
#         "GDL_PRATELEIRA": 5,
#         "GDL_ALTURA": 40,
#         "CAO-PETISCO": 10,
#         "CAO-UMIDO": 15,
#         "CAO-SECO": 20,
#         "GATO-PETISCO": 10,
#         "GATO-UMIDO": 10,
#         "GATO-SECO": 15
#     }

#     # config_dados = pd.DataFrame([dados])

#     if not cgc_input:
#         return JSONResponse(
#             status_code=400,
#             content={
#                 "success": False,
#                 "message": "Campo 'documento' é obrigatório.",
#                 "data": []
#             }
#         )
    
#         # Validar e formatar o CPF ou CNPJ

#     # gerar_planograma(config_dados, config_dados)
    
#     return JSONResponse(
#             status_code=200,
#             content={
#                 "success": True,
#                 "message": "Dados Válidados.",
#                 "data": [dados]
#             }
#         )


# @router.post("/gc")
# async def gerar_planograma_via_json(request: Request):
#     body = await request.json()

#     config_dict = body.get("config_planograma")
#     produtos_list = body.get("itens_produtos")

#     if not config_dict or not produtos_list:
#         return JSONResponse(
#             status_code=400,
#             content={"success": False, "message": "Dados 'config_planograma' e 'itens_produtos' são obrigatórios."}
#         )

#     # Criar os DataFrames diretamente
#     config_df = pd.DataFrame([config_dict])
#     produtos_df = pd.DataFrame(produtos_list)

#     # Simular leitura dos CSVs
    
#     buffer_config = StringIO()
#     buffer_produtos = StringIO()
#     config_df.to_csv(buffer_config, index=False)
#     produtos_df.to_csv(buffer_produtos, index=False, sep=';')

#     # Posicionar o cursor no início para leitura via pd.read_csv
#     buffer_config.seek(0)
#     buffer_produtos.seek(0)

#     # Substituir as leituras de arquivo nos seus métodos:
#     # pd.read_csv("config_planograma.csv") -> pd.read_csv(buffer_config)
#     # pd.read_csv("Itens_produtos.csv") -> pd.read_csv(buffer_produtos)

#     # Dica: você pode passar os DataFrames diretamente para `gerar_planograma()` se quiser modularizar
#     try:
#         # salvar temporariamente como workaround se não for modularizado
#         config_df.to_csv("config_planograma.csv", index=False)
#         produtos_df.to_csv("Itens_produtos.csv", index=False, sep=';')

#         gerar_planograma(config_df, produtos_df)
#     except SystemExit:
#         return JSONResponse(
#             status_code=500,
#             content={"success": False, "message": "Erro ao gerar planograma."}
#         )

#     return JSONResponse(
#         status_code=200,
#         content={"success": True, "message": "Planograma gerado com sucesso."}
#     )


from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, JSONResponse
import pandas as pd
from io import BytesIO
from .planograma import gerar_planograma

router = APIRouter()

@router.post("/gc")
async def gerar_planograma_via_json(request: Request):
    try:
        body = await request.json()

        config_dict = body.get("config_planograma")
        produtos_list = body.get("itens_produtos")

        if not config_dict or not produtos_list:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Campos 'config_planograma' e 'itens_produtos' são obrigatórios."}
            )

        config_df = pd.DataFrame([config_dict])
        produtos_df = pd.DataFrame(produtos_list)

        # Gera o PDF em memória
        pdf_buffer: BytesIO = gerar_planograma(config_df, produtos_df)

        # Retorna como download
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=planograma.pdf"}
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Erro ao gerar planograma: {str(e)}"}
        )
