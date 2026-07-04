# Automação LinkedIn (Python + Playwright)

Uma solução automatizada, modular e inteligente desenvolvida em Python para gerenciar o LinkedIn.

---

## Escopo do Projeto & Funcionalidades

O sistema é dividido em etapas independentes acionados por um script central (`main.py`):

*   **Módulo 1: Expansão de Networking**
    *   Busca automatizada por palavras-chave.
    *   Envio inteligente de notas personalizadas (sorteadas em frases de um banco de dados).
    *   *Fallback das notas* automático: se as cotas de notas da conta gratuita esgotarem, o script envia o convite sem nota para não interromper o fluxo.
*   **Módulo 2: Candidatura Simplificada (Easy Apply)** *[Em Desenvolvimento]*
    *   Filtro inteligente focado em vagas de nível Júnior.
*   **Módulo 3: Automação de Presença & Conteúdo** *[Em Planejamento]*
    *   Postagens agendadas para dias estratégicos.
    *   Suporte a enquetes, mídias e textos.
*   **Módulo 4: Gestão de Comunidade Ativa** *[Em Desenvolvimento]*
    *   Aceite automático de convites e conexões recebidas.

---

## Gerenciamento de Riscos

Para proteger o perfil, a automação simula o comportamento real de um usuário através de mecanismos de segurança:

*   **Aleatoriedade Humana:** Uso da biblioteca `random` do Python para criar intervalos dinâmicos.
*   **Controle de Cota:** Divisão exata do limite diário caso múltiplas áreas sejam sorteadas.
*   **Tratamento de Erros:** Estruturas de `try/except` impedem o script de travar caso o LinkedIn mude algum elemento da interface.

---

## Arquitetura do Projeto

O projeto adota uma arquitetura limpa, facilitando a manutenção e a escalabilidade:

*   `main.py`: Arquivo centralizador do fluxo.
*   `subscript/`: Pasta que contém os submódulos de execução separados por responsabilidade.
    *   `login/login.py`: Gerenciamento de autenticação.
    *   `conexoes/conexoes.py`: Lógica de busca de alvos e envio automatizado de convites.
*   `.gitignore`: Proteção estrita de dados sensíveis (oculta arquivos `.json` de sessão e pastas de cache do Python).

---

## Como executar o Projeto

1. Instale a biblioteca do Playwright:
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
