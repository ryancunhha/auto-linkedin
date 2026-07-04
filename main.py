import asyncio
from playwright.async_api import async_playwright

from subscript.login.login import login
from subscript.conexoes.conexoes import conexoes

SESSION_FILE = "linkedin_session.json"
LIMITE_DIARIO = 5
AREAS_DE_BUSCA = ["desenvolvedor"]

async def main():
    login_sucesso = await login(SESSION_FILE)
    
    if not login_sucesso:
        print("[-] Não foi possível prosseguir sem o login. Encerrando.")
        return

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(SESSION_FILE, headless=False)
        page = context.pages[0] if context.pages else await context.new_page()
        
        print("\n[+] Iniciando Módulo 1: Adicionar Pessoas e Enviar Mensagens...")
        await conexoes(page, LIMITE_DIARIO, AREAS_DE_BUSCA)
        
        await context.close()
        print("\n[✓] Todas as automações do dia foram concluídas!")

if __name__ == "__main__":
    asyncio.run(main())