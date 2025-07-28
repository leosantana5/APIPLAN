from fastapi import APIRouter, Request, Response
from fastapi.responses import StreamingResponse, JSONResponse
import pandas as pd
from io import BytesIO
from .planograma import gerar_planograma_teste
import base64


router = APIRouter()

@router.post("/gc")
async def gerar_pdf_teste_hello_world():
    try:
        buffer = BytesIO()

        # Cria PDF em memória com "Hello World"
        with PdfPages(buffer) as pdf:
            fig, ax = plt.subplots(figsize=(8.27, 11.69))  # A4
            ax.text(0.5, 0.5, 'Hello World', fontsize=30, ha='center', va='center')
            ax.axis('off')
            pdf.savefig(fig)
            plt.close(fig)

        buffer.seek(0)
        pdf_bytes = buffer.getvalue()
        pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")

        return JSONResponse(content={"pdf_base64": pdf_b64})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
