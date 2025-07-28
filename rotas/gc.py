from fastapi import APIRouter, Request, Response
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
       # return StreamingResponse(
       #     pdf_buffer,
       #     media_type="application/pdf",
        #    headers={"Content-Disposition": "attachment; filename=planograma.pdf"}
        #)
        pdf_bytes = pdf_buffer.getvalue()
        print(f"📄 Tamanho do PDF gerado: {len(pdf_bytes)} bytes")
        print("📊 config_df:")
        print(config_df)
        
        print("📊 produtos_df:")
        print(produtos_df)
        pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")
        #return Response(
        #    content=pdf_b64,
        #    media_type="application/pdf"
        #)
        return JSONResponse(
            content={
                "success": True,
                "message": "PDF gerado com sucesso",
                "pdf_base64": pdf_b64
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Erro ao gerar planograma: {str(e)}"}
        )
