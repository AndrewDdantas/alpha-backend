from fastapi import APIRouter

from app.api.v1.endpoints import pessoas, auth, rotas, empresas, diarias, veiculos, alocacoes, presencas, relatorios, pontos_onibus, relatorios_extras

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
api_router.include_router(pessoas.router, prefix="/pessoas", tags=["Pessoas"])
api_router.include_router(rotas.router, prefix="/rotas", tags=["Rotas de Fretados"])
api_router.include_router(empresas.router, prefix="/empresas", tags=["Empresas"])
api_router.include_router(diarias.router, prefix="/diarias", tags=["Diárias"])
api_router.include_router(veiculos.router, prefix="/veiculos", tags=["Veículos"])
api_router.include_router(alocacoes.router, prefix="/alocacoes", tags=["Alocações"])
api_router.include_router(presencas.router, prefix="/presencas", tags=["Presenças"])
api_router.include_router(relatorios.router, prefix="/relatorios", tags=["Relatórios"])
api_router.include_router(relatorios_extras.router, prefix="/relatorios", tags=["Relatórios Extras"])
api_router.include_router(pontos_onibus.router, prefix="/pontos-onibus", tags=["Pontos de Ônibus"])






