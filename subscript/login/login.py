import asyncio
from playwright.async_api import async_playwright

async def login(session_file):
    async with async_playwright() as p:
        # SE JÀ EXISTE
        import os
        if os.path.exists(session_file):
            print("[✓] Sessão do LinkedIn já existe. Pulando etapa de login.")
            return True

        # SE NÃO EXISTIR 
        print("[+] Abrindo o navegador. Faça login na sua conta do LinkedIn...")
        context = await p.chromium.launch_persistent_context(session_file, headless=False)
        page = context.pages[0] if context.pages else await context.new_page()
        
        # PAGINA LOGIN
        await page.goto("https://www.linkedin.com/login")
        
        print("[!] Aguardando você fazer o login...")
        try:
            # 3 minutos de espera
            await page.wait_for_url("https://www.linkedin.com/feed/", timeout=180000)
            print("[✓] Login detectado com sucesso! Os dados foram salvos.")
            await context.close()
            return True
        except Exception:
            print("[-] Tempo esgotado. Tente rodar de novo se não deu tempo de logar.")
            await context.close()
            return False
            
        await context.close()