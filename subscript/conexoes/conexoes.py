import asyncio
import random

CONTA_SEM_COTA = False

# 1. FUNÇÕES DE BUSCA E NAVEGAÇÃO DE PÁGINAS

# Varre a página de busca atual e extrai os links limpos dos perfis
async def buscar_perfis(page):
    cards = await page.locator("div[role='listitem']").all()
    urls = []
    
    for card in cards:
        # Verifica se o convite já está pendente para esta pessoa
        seletor_texto = card.locator("text=/Pendente/i")
        seletor_css = card.locator("a[aria-label*='Pendente']")
        botao_pendente = seletor_texto.or_(seletor_css).first

        if await botao_pendente.is_visible():
            print("[~] Perfil pulado na busca: Convite já está pendente.")
            continue

        # Fluxo normal
        link = card.locator("a[href*='/in/']").first
        if await link.count() > 0:
            href = await link.get_attribute("href")
            if href:
                url_limpa = href.split("?")[0].strip()
                # Evita links genéricos e duplicados
                if url_limpa not in ["https://www.linkedin.com/in/", "https://www.linkedin.com/in//"] and url_limpa not in urls:
                    urls.append(url_limpa)
                    
    return urls

# Tenta clicar no botão Avançar para mudar de página na busca
async def proxima_pagina(page):
    try:
        seletor_botao = ("button[data-testid='pagination-controls-next-button-visible'], ""button:has-text('Próxima'), ""button[aria-label='Avançar']")
        botao_avancar = page.locator(seletor_botao).first

        if await botao_avancar.count() > 0 and await botao_avancar.is_visible():
            print("[+] Avançando para a próxima página de resultados...")
            
            # Executa o clique simulando o scroll até ele se necessário
            await page.wait_for_load_state("domcontentloaded")
            await botao_avancar.scroll_into_view_if_needed()
            await botao_avancar.evaluate("el => el.click()")
            
            # Aguarda a nova página carregar
            await page.wait_for_load_state("domcontentloaded")
            await asyncio.sleep(random.uniform(4, 7))
            return True

        print("[-] Botão de próxima página não está disponível (fim dos resultados).")
        return False
    except Exception as e:
        print(f"[-] Não foi possível avançar a página: {e}")
        return False

# 2. FUNÇÕES DE INTERAÇÃO COM O PERFIL Acessa a URL do perfil e simula o tempo de leitura humana
async def visitar_perfil(page, url):
    print(f"\n[->] Acessando perfil: {url}")
    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
    
    tempo_leitura = random.uniform(6.0, 10.0)
    print(f"[i] Simulando leitura do perfil por {tempo_leitura:.2f} segundos...")
    await asyncio.sleep(tempo_leitura)

# Tenta clicar no botão Conectar diretamente na capa do perfil.
async def clicar_conectar(page):
    botao = page.locator("a[href*='/custom-invite/']").filter(has_text="Conectar").first
    if await botao.is_visible():
        print("[+] Botão 'Conectar' encontrado diretamente na capa. Clicando...")
        await botao.evaluate("el => el.click()")
        return True
    return False

# Abre o menu "Mais" e tenta seguir e depois conectar por lá
async def conectar_pelo_menu(page):
    # 1. PASSO ANTECIPADO: Verifica se o botão "Seguir" já está escancarado na capa
    botao_seguir_capa = page.locator("button[aria-label^='Seguir'], button:has-text('Seguir')").first
    
    if await botao_seguir_capa.is_visible():
        print("[+] Botão 'Seguir' encontrado diretamente na capa! Seguindo antes...")
        try:
            await botao_seguir_capa.scroll_into_view_if_needed()
            await botao_seguir_capa.click(timeout=3000)
            print("[✓] Botão 'Seguir' clicado na capa!")
        except:
            await botao_seguir_capa.evaluate("el => el.click()")
            print("[✓] Botão 'Seguir' clicado na capa (via fallback)!")
            
        print("[i] Recarregando o perfil para estabilizar os novos botões...")
        await page.reload(wait_until="domcontentloaded")
        await asyncio.sleep(3.5)

    # Procura o botão 'Mais' (...) para podermos caçar o Conectar oculto
    botao_mais = page.locator("button[aria-label='Mais']").first
    if not await botao_mais.is_visible():
        print("[-] Botão 'Mais' (...) não está visível neste perfil.")
        return False

    print("[i] Abrindo menu 'Mais'...")
    try:
        await botao_mais.scroll_into_view_if_needed()
        # um timeout curto de 5s para se o menu falhar ele ir rapido pro plano B
        await botao_mais.click(timeout=5000) 
        await asyncio.sleep(2.5)
    except Exception as e:
        print(f"[~] Falha ao abrir o menu 'Mais' ({e}). Tentando clique via evaluate...")
        try:
            await botao_mais.evaluate("el => el.click()")
            await asyncio.sleep(2.5)
        except:
            return False
    
    # Tenta Seguir primeiro, se a opção estiver disponível
    opcao_seguir = page.locator("div[role='menuitem']").filter(has_text="Seguir").first
    if await opcao_seguir.is_visible():
        print("[+] Opção 'Seguir' encontrada. Seguindo...")
        await opcao_seguir.click()
        print("[✓] Seguido com sucesso!")
        await asyncio.sleep(2.5)

        # Reabre o menu caso tenha fechado após o Seguir
        if await botao_mais.is_visible():
            await botao_mais.click()
            await asyncio.sleep(2)

    # Tenta achar o Conectar dentro do menu flutuante
    conectar = page.locator("[role='menuitem']").filter(has_text="Conectar").first
    if await conectar.is_visible():
        print("[+] Botão 'Conectar' encontrado dentro do menu 'Mais'. Clicando...")
        await conectar.click()
        return True
    
    print("[-] Não encontrou a opção 'Conectar' dentro do menu 'Mais'.")
    return False

# 3. GERENCIAMENTO DE POP-UPS E CONVITES, Gerencia o envio do convite tratando pop-ups com ou sem nota.
async def enviar_convite(page, frases):
    global CONTA_SEM_COTA
    print("[i] Aguardando o LinkedIn abrir os botões do pop-up...")
    
    try:
        botoes_alvo = page.locator("button[aria-label='Adicionar nota'], button[aria-label='Enviar sem nota'], button[aria-label='Enviar convite']").first
        await botoes_alvo.wait_for(state="visible", timeout=8000)
    except:
        print("[~] Pop-up falhou ao carregar ou formato desconhecido. Cancelando...")
        await page.keyboard.press("Escape")
        return False

    botao_adicionar_nota = page.locator("button[aria-label='Adicionar nota']").first
    botao_enviar_sem_nota = page.locator("button[aria-label='Enviar sem nota']").first
    
    # ATALHO INTELIGENTE: Se já sabemos que não tem cota, envia direto sem nota
    if CONTA_SEM_COTA and await botao_enviar_sem_nota.is_visible():
        print("[!] Memória ativa: Sem cota nesta sessão. Clicando direto em 'Enviar sem nota'...")
        await botao_enviar_sem_nota.evaluate("el => el.click()")
        return True

    # Caso 1: Tem opção de Adicionar Nota
    if await botao_adicionar_nota.is_visible():
        print("[+] Clicando em 'Adicionar nota'...")
        await botao_adicionar_nota.evaluate("el => el.click()")
        await asyncio.sleep(2.5)

        # Seletores de verificação de bloqueio
        aviso_limite_premium = page.locator("text=/Experimente Premium/i")
        tem_cotas = page.locator("text=/convite personalizado/i")
        aviso_cota_mensal = page.locator("text=/Você usou sua cota mensal/i")
        aviso_premium_vantagem = page.locator("text=/você quiser com Premium/i")

        # --- SUB-CASO A: Se a tela de bloqueio do Premium aparecer ---
        if await aviso_cota_mensal.is_visible() or await aviso_premium_vantagem.is_visible():
            print("[!] Bloqueio de cota detectado! Ativando modo 'Apenas Sem Nota'...")
            CONTA_SEM_COTA = True

            print("[+] Fechando oferta do Premium com ESC...")
            await page.keyboard.press("Escape")
            await asyncio.sleep(1.5)

            # Se o ESC apenas fechou o aviso e manteve o pop-up de trás:
            if await botao_enviar_sem_nota.is_visible():
                print("[+] Clicando em 'Enviar sem nota'...")
                await botao_enviar_sem_nota.evaluate("el => el.click()")
                return True
            
            print("[~] O aviso fechou o convite por completo. Indo para o próximo perfil já com a flag de 'Sem Nota' ativa.")
            return False
        
        # --- SUB-CASO B: Se o campo de texto abriu normalmente ---
        elif await page.locator("#custom-message").is_visible():
            
            # Verifica se caiu no outro bloqueio alternativo (Cota Semanal do Grátis)
            if await aviso_limite_premium.is_visible() and not (await tem_cotas.is_visible()):
                print("[!] Sem cota semanal para nota. Fechando caixa de texto...")
                await page.keyboard.press("Escape") 
                await asyncio.sleep(1.5)
                
                if await botao_enviar_sem_nota.is_visible():
                    print("[+] Enviando sem nota após fechar o aviso...")
                    await botao_enviar_sem_nota.evaluate("el => el.click()")
                    return True
                return False
                
            # FLUXO PERFEITO: Tem cota livre! Escreve e envia
            else:
                print("[+] Cotas disponíveis! Digitando mensagem...")
                msg_sorteada = random.choice(frases)
                await page.locator("#custom-message").fill(msg_sorteada)
                await asyncio.sleep(random.uniform(2, 4))

                print("[+] Clicando em Enviar convite...")
                botao_enviar_convite = page.locator("button[aria-label='Enviar convite']").first
                if await botao_enviar_convite.is_visible():
                    await botao_enviar_convite.evaluate("el => el.click()")
                    return True
                
    # Caso 2: Só aceita envio Direto/Sem Nota original
    elif await botao_enviar_sem_nota.is_visible():
        print("[!] Pop-up apenas com opção de enviar direto. Enviando...")
        await botao_enviar_sem_nota.evaluate("el => el.click()")
        return True

    # Fallback definitivo
    print("[-] Formato de pop-up inesperado. Fechando para não travar...")
    await page.keyboard.press("Escape")
    return False

# Controla o fluxo do perfil individual. Se der qualquer erro, ele captura e retorna Falso para pular pro proximo
async def processar_perfil(page, url, frases):
    try:
        await visitar_perfil(page, url)
        
        # 1. FORÇA IR PELO MENU PRIMEIRO (Para garantir que vai Seguir e tentar o conectar interno)
        clicou = await conectar_pelo_menu(page)
        
        # 2. Se o menu não resolveu nada (ou não achou o conectar lá dentro), tenta a capa como plano B
        if not clicou:
            print("[i] Menu 'Mais' não encontrou Conectar. Tentando botão direto da capa...")
            clicou = await clicar_conectar(page)

        # Se nenhum botão de conectar foi clicado, encerra o perfil atual
        if not clicou:
            print("[-] Não foi possível encontrar opção para conectar com este perfil.")
            return False

        # Tenta manipular o modal e enviar o convite final
        sucesso_envio = await enviar_convite(page, frases)
        return sucesso_envio

    except Exception as e:
        # SER TIVER QUALQUER ERRO: Imprime o erro, limpa a tela fechando modais e pula
        print(f"[-] Erro crítico ao processar o perfil {url}: {e}. Pulando...")
        await page.keyboard.press("Escape")
        return False

# FLUXO PRINCIPAL CAHAMADA PELO MAIN
async def adicionar(page, busca, limite, frases):
    print(f"\n[+] Iniciando buscas para: {busca} (Limite: {limite})")
    url_busca = f"https://www.linkedin.com/search/results/people/?keywords={busca.replace(' ', '%20')}"
    
    await page.goto(url_busca, wait_until="domcontentloaded", timeout=20000)
    await asyncio.sleep(random.uniform(4, 10))

    conexoes_feitas = 0
    pagina_atual = 1

    while conexoes_feitas < limite:
        perfis = await buscar_perfis(page)
        print(f"[i] Encontrados {len(perfis)} perfis na página {pagina_atual}.")

        if not perfis:
            print("[-] Nenhum perfil encontrado nesta página. Tentando avançar...")
            avancou = await proxima_pagina(page)

            if not avancou:
                print("[-] Não foi possível avançar a página de busca. Encerrando essa área.")
                break
            pagina_atual += 1
            url_busca = page.url
            continue

        for perfil in perfis:
            if conexoes_feitas >= limite:
                break

            # Processa o perfil de forma isolada e segura
            sucesso = await processar_perfil(page, perfil, frases)

            if sucesso:
                conexoes_feitas += 1
                print(f"[Sucesso] {conexoes_feitas}/{limite} convites processados.")
                
                # Resguardo de tempo humano entre ações com sucesso
                aguardo = random.uniform(20, 40)
                print(f"[i] Aguardando {aguardo:.1f}s antes do próximo perfil...")
                await asyncio.sleep(aguardo)
            else:
                # Se falhou ou deu erro, apenas aguarda um tempo curto de segurança antes do próximo
                await asyncio.sleep(random.uniform(2, 4))

        # Se ainda precisa de conexões, volta para os resultados e avança a página
        if conexoes_feitas < limite:
            try:
                print(f"[+] Retornando para os resultados da busca para ir para a próxima página...")
                await page.goto(url_busca, wait_until="domcontentloaded", timeout=20000)
                await asyncio.sleep(random.uniform(3, 5))
                
                avancou = await proxima_pagina(page)
                if not avancou:
                    print("[-] Fim das páginas disponíveis no LinkedIn.")
                    break

                pagina_atual += 1
                url_busca = page.url
            except Exception as e:
                print(f"[-] Erro ao tentar retornar à lista de busca: {e}")
                break

    print(f"[✓] Fim da automação para a busca: {busca}. Total feito: {conexoes_feitas}/{limite}\n")

# Função chamada pelo main.py
async def conexoes(page, limite, areas, frases):
    limite_por_area = limite // len(areas)
    for area in areas:
        await adicionar(page, area, limite_por_area, frases)
        print("\n[Vapor] Concluído para esta área. Aguardando intervalo de transição...")
        await asyncio.sleep(random.uniform(15, 30))