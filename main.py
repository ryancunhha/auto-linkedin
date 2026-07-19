import asyncio
from playwright.async_api import async_playwright

from subscript.login.login import login
from subscript.conexoes.conexoes import conexoes
from subscript.convites.convites import analisar_convites
from subscript.feeds.curtir import curtir_feed

# GERAL
SESSION_FILE = "session.json"

#  ENGAJAMENTO (Curtidas no Feed)
ATIVO_MODULO_FEED = True
LIMITE_DIARIO_CURTIDAS = 3

# ENVIAR AMIZADE + MENSAGEM PERSORNALIZADO (3 são gratis por mês)
ATIVO_MODULO_1 = False
LIMITE_DIARIO_ENVIO = 5
AREAS_DE_BUSCA = ["desenvolvedor"]
FRASES = [
    "Olá, tudo bem? Vi seu perfil e gostaria de conectar para acompanhar seu trabalho. Um abraço!",
    "Olá! Achei muito interessante seu perfil e gostaria de adicionar à minha rede de contatos.",
    "Tudo bem? Gostaria de nos conectar por aqui para acompanhar a novidades da área!"
]

# ACEITAR CONVITES "Minhas rede"
ATIVO_MODULO_2 = False
LIMITE_DIARIO_ACEITAR = 1

async def main():
    login_sucesso = await login(SESSION_FILE)
    
    if not login_sucesso:
        print("[-] Não foi possível prosseguir sem o login. Encerrando.")
        return

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(SESSION_FILE, headless=False)
        page = context.pages[0] if context.pages else await context.new_page()

        # MÓDULO FEEDS: Aquecimento da conta
        if ATIVO_MODULO_FEED:
            await curtir_feed(page, limite_curtidas=LIMITE_DIARIO_CURTIDAS)
        else:
            print("[*] Módulo Feed/Curtidas desativado.")
        
        # MODULO 1: Conexões
        print("\n[+] Iniciando Módulo 1: Adicionar Pessoas e Enviar Mensagens...")
        if ATIVO_MODULO_1:
            await conexoes(page, LIMITE_DIARIO_ENVIO, AREAS_DE_BUSCA, FRASES)
        else: 
            print("[*] Módulo 1 desativado.")

        # MÓDULO 2: Análise de Convites
        print("\n[+] Iniciando Módulo 2: Analisar Convites Recebidos...")
        if ATIVO_MODULO_2:
            await analisar_convites(page, limite=LIMITE_DIARIO_ACEITAR)
        else: 
            print("[*] Módulo 2 desativado.")
        
        # CONCLUSÃO
        await context.close()
        print("\n[✓] Todas as automações do dia foram concluídas!")

if __name__ == "__main__":
    asyncio.run(main())