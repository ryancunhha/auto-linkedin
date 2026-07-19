# Automação LinkedIn (Python + Playwright)

Uma solução automatizada, modular, inteligente e altamente resiliente desenvolvida em Python para gerenciar e expandir sua presença no LinkedIn de forma orgânica.

---

## Escopo do Projeto & Funcionalidades

O sistema é totalmente modular. Suas etapas são centralizadas e acionadas por um script principal (`main.py`), permitindo ativar ou desativar recursos pelas configurações:

*   **Módulo 1: Aquecimento & Engajamento Automático (Feed)**  
    *   Simula navegação humana rolando o feed inicial através de comandos nativos do navegador (`window.scrollBy`).
    *   Sorteia uma meta diária aleatória de curtidas para quebrar padrões mecânicos de comportamento.
    *   Filtros inteligentes para ignorar posts patrocinados (anúncios) e proteção anti-descurtir (valida o estado da reação atual antes de interagir).
*   **Módulo 2: Expansão de Networking (Conexões)**  
    *   Busca automatizada por palavras-chave segmentadas por áreas de interesse.
    *   Lógica híbrida de interação: detecta se o perfil possui o botão "Seguir" exposto ou se o "Conectar" está oculto no menu "Mais" (...), adaptando o clique em tempo real.
    *   Envio inteligente de notas personalizadas (sorteadas de um banco de frases).
    *   **Memória Ativa de Cotas:** Caso o LinkedIn exiba o bloqueio de convites personalizados (Premium/Limite Semanal), o script memoriza o estado da sessão e passa a enviar os próximos convites automaticamente "Sem Nota", impedindo a interrupção do fluxo.
*   **Módulo 3: Gestão de Comunidade Ativa (Convites Recebidos)**  
    *   Varredura na aba de redes para aceitar conexões pendentes de forma automatizada.
*   **Módulo 4: Automação de Presença & Conteúdo** *[Em Planejamento]*  
    *   Agendamento de postagens, suporte a mídias, enquetes e textos para dias estratégicos.

---

## Gerenciamento de Riscos & Blindagem

Para proteger o perfil contra as rígidas diretrizes do LinkedIn, a automação aplica técnicas avançadas de emulação humana:

*   **Aleatoriedade Humana Completa:** Prazos de leitura de perfis, tempo de visualização de posts no feed e intervalos pós-conexão utilizam delays flutuantes e dinâmicos (`random.uniform`).
*   **Cliques e Rolagens Nativas:** Uso de métodos como `.click()` nativo e `.scroll_into_view_if_needed()` em vez de injeções brutas de JavaScript, forçando o navegador a disparar os eventos reais dos frameworks do LinkedIn.
*   **Resiliência Baseada em Fallbacks:** Caso o motor do Playwright sofra interceptação de ponteiro (camadas visuais ocultas do LinkedIn bloqueando o mouse), o robô aciona automaticamente um clique via `evaluate` como plano B, garantindo autonomia de 100% sem travamentos.
*   **Mecanismo Anti-Crash no DOM:** Estruturas de tratamento de erro individuais (`try/except`) isolam falhas em perfis específicos. Se um perfil quebrar ou mudar de layout, o robô limpa a tela com a tecla `Escape` e avança para o próximo alvo.

---

## Arquitetura do Projeto

O projeto adota uma arquitetura limpa, facilitando a escalabilidade do código:

*   `main.py`: Arquivo centralizador que gerencia as flags de ativação e parâmetros globais.
*   `session.json`: Arquivo gerado localmente contendo os tokens e cookies de autenticação salvos.
*   `subscript/`: Pasta que isola as responsabilidades de cada etapa do robô.
    *   `login/login.py`: Gerenciamento e validação de autenticação.
    *   `feeds/curtir.py`: Lógica de aquecimento de conta e curtidas no feed.
    *   `conexoes/conexoes.py`: Lógica de busca de alvos, navegação de páginas e envio de convites.
    *   `convites/convites.py`: Módulo de aceitação de solicitações recebidas.
*   `.gitignore`: Proteção estrita de dados sensíveis (oculta arquivos `.json` de sessão e pastas de cache do Python).

---

## Como executar o Projeto

1. Instale a biblioteca do Playwright e seus navegadores dependentes:
```bash
pip install playwright
playwright install
```
Execute o script principal:

```bash 
python main.py
```

> ⚠️ **Nota Importante:** Na primeira execução, o navegador abrirá no modo visível para que você faça o login manual na sua conta do LinkedIn. Os cookies serão salvos localmente de forma criptografada no seu computador e as próximas execuções rodarão direto na conta em segundo plano.
> 
> Se for clonar este repositório para fazer seu próprio modelo, tenha **cuidado com o `.gitignore`** para nunca expor seus dados de sessão publicamente!
