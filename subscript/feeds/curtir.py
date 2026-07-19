import asyncio
import random

async def curtir_feed(page, limite_curtidas=3):
    # Sorteia um número aleatório entre 1 e o limite definido
    meta_curtidas = random.randint(1, max(1, limite_curtidas))
    
    print(f"\n[+] Iniciando Módulo de Engajamento (Feed Inicial)")
    print(f"[i] Meta sorteada para hoje: {meta_curtidas} curtidas (Limite máximo configurado: {limite_curtidas})")
    
    url_feed = "https://www.linkedin.com/feed/"
    print(f"[i] Acessando: {url_feed}")
    
    try:
        await page.goto(url_feed, wait_until="domcontentloaded", timeout=25000)
        print("[i] Aguardando a estrutura da página estabilizar...")
        
        # --- NOVA ESPERA ESTRUTURAL (IMUNE A MUDANÇAS DE CLASSES DE POSTS) ---
        estrutura_global = ".global-nav, .share-box-feed-entry__trigger, main"
        await page.locator(estrutura_global).first.wait_for(state="visible", timeout=12000)
        
        # Dá um respiro humano de 4 segundos para os primeiros posts carregarem o HTML de reação no fundo
        await asyncio.sleep(4)
        
    except Exception as e:
        print(f"[-] A estrutura da página demorou muito para responder: {e}")
        return False
        
    curtidas_feitas = 0
    posts_analisados = 0
    max_tentativas = meta_curtidas * 6  

    print(f"[i] Buscando posts para interagir... (Meta: {meta_curtidas} curtidas)")

    while curtidas_feitas < meta_curtidas and posts_analisados < max_tentativas:
        posts_analisados += 1
        
        # Rolagem via Javascript força a descida da página e faz o LinkedIn carregar conteúdo
        distancia_scroll = random.randint(450, 750)
        await page.evaluate(f"window.scrollBy(0, {distancia_scroll});")
        await asyncio.sleep(random.uniform(2.5, 4.0))

        # Procura os botões de reação DIRETOS na tela inteira (Mapeia o botão independente de qual classe o post usa)
        seletor_botoes = "button[aria-label^='Situação do botão de reação:'], button[aria-label*='botão de reação']"
        botoes_reacao = await page.locator(seletor_botoes).all()

        if not botoes_reacao:
            print("[~] Nenhum botão de reação visível nesta área do feed. Rolando mais...")
            continue

        # Seleciona um botão aleatório dos primeiros que apareceram para simular desinteresse mecânico
        limite_selecao = min(len(botoes_reacao), 3)
        btn_alvo = random.choice(botoes_reacao[:limite_selecao])

        try:
            # Captura o label de acessibilidade para fazer a checagem anti-descurtir
            label_atual = await btn_alvo.get_attribute("aria-label") or ""
            
            # PROTEÇÃO: Se você já reagiu (ex: "Gostei"), pula para o próximo post
            if "nenhuma reação" not in label_atual:
                print("[~] Post pulado: Você já reagiu a este conteúdo anteriormente.")
                continue
            
            # --- FILTRO ADICIONAL: Verifica se o botão não pertence a um anúncio patrocinado ---
            container_pai = btn_alvo.locator("xpath=./ancestor::div[contains(@class, 'feed') or @data-urn]").first
            if await container_pai.count() > 0:
                anuncio = container_pai.locator("text=/Patrocinado|Promoted/i").first
                if await anuncio.is_visible():
                    print("[~] Post patrocinado detectado. Pulando curtida...")
                    continue

            # FLUXO NORMAL
            await btn_alvo.scroll_into_view_if_needed()
            await asyncio.sleep(1.5)
            
            # Tenta o clique real do mouse, caindo para evaluate se houver sobreposição de layout
            try:
                await btn_alvo.click(timeout=3000)
            except:
                await btn_alvo.evaluate("el => el.click()")
                
            curtidas_feitas += 1
            print(f"[✓] Post {curtidas_feitas}/{meta_curtidas} curtido com sucesso!")

            # Simula o tempo de leitura humana
            tempo_leitura = random.uniform(6.0, 12.0)
            print(f"[i] Simulando leitura humana do post por {tempo_leitura:.1f}s...")
            await asyncio.sleep(tempo_leitura)

        except Exception as e:
            continue

    print(f"[✓] Fim do Módulo de Engajamento. Total de likes enviados hoje: {curtidas_feitas}\n")
    return True