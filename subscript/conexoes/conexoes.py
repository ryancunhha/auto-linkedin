import asyncio
import random

FRASES = [
    "Olá, tudo bem? Vi seu perfil e gostaria de conectar para acompanhar seu trabalho. Um abraço!",
    "Olá! Achei muito interessante seu perfil e gostaria de adicionar à minha rede de contatos.",
    "Tudo bem? Gostaria de nos conectar por aqui para acompanhar a novidades da área!"
]

async def adicionar(page, busca, limite):
    print(f"\n[+] Iniciando buscas para: {busca} (Limite: {limite})")
    url_busca = f"https://www.linkedin.com/search/results/people/?keywords={busca.replace(' ', '%20')}"
    await page.goto(url_busca)
    await page.wait_for_load_state("networkidle")
    await asyncio.sleep(random.uniform(4, 6))

    conexoes_feitas = 0
    while conexoes_feitas < limite:
        botoes_conectar = await page.locator("[componentkey*='ConnectButtonstate']").all()

        if not botoes_conectar:
            print("[-] Nenhum botão Conectar encontrado. Avançando página...")
            try:
                await page.get_by_label("Avançar").click()
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(random.uniform(4, 7))
                continue
            except:
                print("[-] Não foi possível avançar a página.")
                break

        for botao in botoes_conectar:
            if conexoes_feitas >= limite:
                break
            try:
                await botao.click()
                await asyncio.sleep(random.uniform(2, 3))

                botao_adicionar_nota = page.get_by_role("button", name="Adicionar nota")
                botao_enviar_sem_nota = page.get_by_role("button", name="Enviar sem nota")
                
                if await botao_adicionar_nota.is_visible():
                    print("[+] Pop-up 1 detectado. Clicando em 'Adicionar nota'...")
                    await botao_adicionar_nota.click()
                    await asyncio.sleep(2)

                    aviso_limite_premium = page.get_by_text("Experimente Premium")
                    tem_cotas = page.get_by_text("convites personalizados este mês")

                    if await aviso_limite_premium.is_visible() and not (await tem_cotas.is_visible()):
                        print("[!] Limite de notas detectado no Pop-up 2. Cancelando e enviando sem nota...")
                        await page.get_by_role("button", name="Cancelar a inclusão da nota").click()
                        await asyncio.sleep(1.5)
                        await page.get_by_role("button", name="Enviar sem nota").click()
                    else:
                        print("[+] Cotas disponíveis! Escolhendo uma mensagem aleatória...")
                        
                        # LOGICA DE SORTEIO
                        msg_sorteada = random.choice(FRASES)
                        
                        await page.locator("#custom-message").fill(msg_sorteada)
                        await asyncio.sleep(random.uniform(2, 4))

                        print("[+] Clicando em Enviar convite...")
                        await page.get_by_label("Enviar convite").click()
                
                elif await botao_enviar_sem_nota.is_visible():
                    print("[!] Pop-up direto sem opção de nota. Enviando direto...")
                    await botao_enviar_sem_nota.click()
                else:
                    print("[~] Convite enviado direto no clique.")

                conexoes_feitas += 1
                print(f"[Sucesso] {conexoes_feitas}/{limite} convites processados para {busca}")
                
                await asyncio.sleep(random.uniform(30, 60))
                
            except Exception as e:
                print(f"[-] Ocorreu um erro com este perfil: {e}")
                botao_fechar = page.get_by_label("Fechar", exact=True)
                if await botao_fechar.is_visible():
                    await botao_fechar.click()
                continue

        if conexoes_feitas < limite:
            try:
                print("[+] Mudando para próxima página de resultados...")
                await page.get_by_label("Avançar").click()
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(random.uniform(4, 7))
            except:
                break

async def conexoes(page, limite, areas):
    limite_por_area = limite // len(areas)
    for area in areas:
        await adicionar(page, area, limite_por_area)
        print("\n[Vapor] Aguardando intervalo...")
        await asyncio.sleep(random.uniform(10, 20))