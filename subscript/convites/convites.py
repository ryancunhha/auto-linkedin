import asyncio
import random
import re

async def analisar_convites(page, limite):
    print(f"\n[+] Iniciando Módulo de Análise de Convites (Limite: {limite})")
    
    # Navega até a página de convites
    url_convites = "https://www.linkedin.com/mynetwork"
    print(f"[i] Acessando: {url_convites}")
    await page.goto(url_convites)
    
    # Aguarda o carregamento
    await asyncio.sleep(random.uniform(4, 6))
    
    # Buscaremos os botões e "Aceitar"
    botoes_aceitar = page.get_by_role("button", name=re.compile(r"^Aceitar convite"))
    
    total_convites = await botoes_aceitar.count()
    print(f"[i] Total de convites detectados na tela: {total_convites}")
    
    if total_convites == 0:
        print("[!] Nenhum convite pendente encontrado para analisar.")
        return

    # Limita a quantidade
    analisar_qtd = min(total_convites, limite)
    
    print("\n" + "="*50)
    print(f"PROCESSANDO: {analisar_qtd} CONVITES")
    print("="*50)
    
    for i in range(analisar_qtd):
        btn_aceitar = botoes_aceitar.first
        
        # ACEITA QUALQUER COISA NA LISTA
        try:
            print(f"[->] Aceitando convites...")
            await btn_aceitar.click()
        except Exception as e:
            print(f"[-] Falha no botão de aceitar: {e}")

        print("-" * 50)

        if i < analisar_qtd - 1:
            tempo_espera = random.uniform(3.5, 6.0)
            print(f"[i] Aguardando {tempo_espera:.2f} segundos antes do próximo convite...")
            await asyncio.sleep(tempo_espera)
        
print("[✓] Fim da análise de convites.\n")