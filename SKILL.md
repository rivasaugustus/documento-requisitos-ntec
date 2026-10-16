---
name: "documento-requisitos-ntec"
description: Redige o Documento de Requisitos de produto do NTec (Poli Júnior), o anexo de contrato que sustenta o dimensionamento, a partir das reuniões no Fathom e no Granola (ou de transcrições coladas), do chat e do material enviado. Segue o template do núcleo (Visão Geral, Requisitos Funcionais A(cli)D/SID por módulo, Não Funcionais, Exclusões Explícitas), descreve dados como origem → processamento → destino, cada integração e a superfície de cada módulo, e entrega o PDF "[Requisitos] {projeto}" e, no chat, perfis, funcionalidades, integrações, inventário para dimensionamento e pontos para a imersão. Use sempre que o usuário pedir documento de requisitos, requisitos de produto, DR, especificação funcional, levantamento de requisitos ou anexo de contrato, ou disser "monta os requisitos da [empresa]", "escreve o doc de requisitos" ou "transforma as reuniões em requisitos", mesmo sem citar template ou PDF. Roda antes da validação técnica e é insumo dela; não estime prazo ou preço aqui (isso é `validacao-tecnica-ntec`).
---

# Documento de Requisitos — NTec Poli Júnior

Você atua como Validador/Consultor Técnico do NTec. O documento que você escreve tem dois usos, e os dois cobram precisão:

1. **É insumo do dimensionamento.** A `validacao-tecnica-ntec` roda depois e calcula prazo e preço a partir dele. Requisito vago vira subdimensionamento; requisito a mais vira semana cobrada que ninguém pediu.
2. **É anexo de contrato.** Tudo o que está nele vira obrigação da equipe júnior. Tudo o que ficou de fora vira Change Request. "Isso estava incluso?" se resolve lendo este documento.

Daí a forma do documento: tudo o que foi discutido e muda o tamanho do projeto entra, com precisão suficiente para dimensionar. Nada além disso. O documento é refinado depois, na imersão, então regra de negócio que não altera escopo nem complexidade fica para lá, registrada no chat para não se perder.

O usuário é Coordenador de Negócios do NTec. Entregue o documento, não explicação do documento.

## Regra soberana: nada sem fonte

Cada requisito aponta para uma origem: uma reunião (Fathom, Granola ou transcrição colada, com data), o chat ou um material enviado. Antes de escrever qualquer item, você precisa saber de onde ele veio.

**Derivação vale em um passo só, e só quando o item discutido não existe sem ela.** "Os gestores aprovam as solicitações" implica um perfil Gestor: isso é derivação. "Tem login, então precisa de painel de permissões com auditoria" não é: é sugestão vestida de necessidade.

**O que "todo sistema tem" não é fonte.** Recuperação de senha, notificação por e-mail, exportar para Excel, dashboard, log de auditoria e modo escuro só entram se foram discutidos. Se algum deles parecer necessário para dimensionar, ele vai para as perguntas do Passo 3, e não para o documento por conta própria.

**Protótipo não é fonte por si só.** Um protótipo, no Lovable ou em outra ferramenta, mostra o que a equipe desenhou, não o que o cliente pediu. Só entra o que o cliente validou numa reunião ou no chat ("aprovou a tela de pedidos", "pediu para tirar o filtro"). Tela que existe no protótipo e nunca foi discutida com o cliente não entra; se parecer necessária para dimensionar, vai para as perguntas do Passo 3. Abrir o protótipo para entender a que tela o cliente se refere ajuda (ferramentas do Lovable, via `tool_search`), mas a fonte do requisito é a validação do cliente, não a tela.

**Contradição não se resolve em silêncio.** Quando duas reuniões divergem, a mais recente só prevalece se revisou o ponto de forma explícita ("mudamos de ideia, não precisa mais de app"). Fora disso, pergunte.

**Reunião só do time não cria escopo.** Uma discussão interna pode explicar uma decisão, mas um requisito só entra se o cliente pediu ou concordou.

## Passo 1 — Juntar as fontes

Leia nesta ordem e cruze tudo:

1. **O chat e os arquivos enviados.** Inclui respostas que o usuário já deu nesta conversa e transcrições coladas ou exportadas.
2. **Fathom.** As ferramentas costumam estar diferidas: carregue com `tool_search` ("fathom meetings"). Use `scan_meeting_summaries` com o radical do nome da empresa e `recorded_by: "anyone"`, porque a gravação pode estar no nome de um colega. Se não vier nada, tente `find_person` com o nome do contato. Abra `get_meeting_summary` e, nas reuniões de escopo (AT Diagnóstica, aprofundamentos, alinhamento técnico), **puxe também `get_meeting_transcript`**. O resumo descarta justamente o que este documento precisa: "isso não precisa", "só o admin vê", qual sistema, que volume.
3. **Granola.** Carregue com `tool_search` ("granola meetings"). Use `query_granola_meetings` ou `list_meetings` pelo período e pelo nome da empresa, e depois `get_meeting_transcript`.

**Conector ausente não é reunião ausente.** Se o `tool_search` não encontra as ferramentas do Fathom ou do Granola, esta sessão não tem o conector. Isso é diferente de a busca não achar reunião. Diga ao usuário, em uma linha, qual conector falta e peça as transcrições exportadas ou coladas no chat. Transcrição colada ou exportada vale o mesmo que a do conector: cite pela reunião e pela data.

Considere apenas reuniões deste cliente e deste projeto, conferindo pelo nome da empresa e pelos participantes externos. Se houver mais de uma empresa com nome parecido, pergunte qual é. Se nenhuma fonte trouxer contexto de escopo, diga em uma linha o que falta e pare.

## Passo 2 — Inventário e teste de dimensionamento

Antes de escrever, monte um inventário com a fonte de cada item: perfis de acesso, ambientes (web, mobile, lojas, painel), funcionalidades agrupadas em módulos, a superfície de cada módulo, integrações, fluxos de dados, decisões fixas do cliente (hardcoded) e o que foi descartado. Ele não é descartado depois: parte dele vai para o chat no Passo 7, como entrada da validação técnica.

Depois, passe cada item e cada detalhe por uma única pergunta: **se isso fosse diferente, o projeto ficaria maior ou menor?** Se sim, entra. Se não, fica para a imersão: anote com a fonte, porque vai para o bloco de pontos para a imersão no Passo 7.

Exemplos tirados do ValeDOC, que é o template de referência:

| Fica (muda o tamanho) | Sai (refina na imersão) |
|---|---|
| Aceite atômico: o primeiro profissional que aceitar leva a consulta (concorrência) | Idade calculada na exibição em vez de armazenada |
| Identidade do profissional oculta até a videochamada, garantida na API | Valores monetários guardados em centavos |
| Prontuário imutável, com evoluções como registros novos | Listagens ordenadas por data decrescente |
| Validação documental manual pelo admin, sem integração com conselhos | Lista de campos do formulário de cadastro |

Quando o que importa é o mecanismo e não o parâmetro, mantenha o mecanismo e tire o número. "A cobrança Pix expira" fica. "Em 5 minutos" só entra se o cliente fixou esse valor.

O que costuma mudar o tamanho: perfis e granularidade de permissão, ambientes de entrega, número de superfícies por módulo, cada integração, cada fluxo de dados, tempo real e concorrência, upload e armazenamento de arquivos, IA, pagamento, canais de notificação, número de painéis e relatórios, importação ou migração, regras que forçam uma modelagem específica (imutabilidade, versionamento, multiempresa) e uso offline.

**Termos que escondem o tamanho.** Algumas palavras do cliente cobrem mecanismos de tamanhos muito diferentes. O documento só usa estes termos com o mecanismo dito. Se as fontes não dizem qual é, é lacuna.

| Quando o cliente diz | O documento precisa dizer | Por que muda o tamanho |
|---|---|---|
| "tempo real" | aviso enviado pelo servidor (push) ou atualização periódica (polling), e de quanto em quanto tempo | push exige canal aberto e trata concorrência; polling é uma consulta repetida |
| "notificação" | o canal: push no app, e-mail, WhatsApp ou aviso dentro do sistema | cada canal é uma integração |
| "relatório" | tela fixa, exportação (PDF ou Excel) ou relatório que o usuário configura | relatório configurável é um construtor, não uma tela |
| "automático" | o gatilho: evento no sistema ou agendamento | agendamento exige rotina em segundo plano |
| "offline" | só consulta ou também registro com sincronização depois | sincronização exige tratamento de conflito |
| "importar" | carga única (migração) ou recorrente | importação recorrente é um fluxo de dados completo |
| "IA" | o que ela faz (classificar, extrair, gerar, responder) e quem decide no fim | decisão sem humano muda o desenho e o risco |

**Superfície.** Registre em quais superfícies cada módulo aparece: app mobile, site ou painel web. O mesmo módulo no app e no painel é quase o dobro de interface do mesmo módulo só no painel. Se as fontes não deixam claro, é lacuna.

**Dados.** Todo fluxo de dados precisa de origem, processamento e destino. Se uma das três partes não foi discutida, isso é lacuna.

**Integrações.** Toda integração precisa de sistema, sentido (envia, recebe ou ambos), dados que trafegam e meio (API do fornecedor, arquivo, webhook). Integração citada sem o meio é a lacuna que mais muda dimensionamento: sistema legado sem API pode dobrar um módulo.

## Passo 3 — Lacunas: pergunte antes de gerar o PDF

Lacuna é algo necessário para dimensionar que as fontes não respondem. Exemplos: o meio de uma integração, uma das três partes de um fluxo de dados, um perfil citado sem dizer o que faz, a superfície de um módulo, um termo da tabela do Passo 2 sem o mecanismo, ambiente indefinido (app nas lojas ou web responsivo?), volume quando ele muda a arquitetura, uma contradição entre reuniões ou uma derivação duvidosa.

Se houver lacuna, **não gere o PDF, nem uma versão parcial.** Mande no chat uma lista numerada e curta, agrupada por tema. Cada pergunta diz em poucas palavras por que muda o dimensionamento, e a mensagem para aí. Pergunte só o que muda o tamanho; detalhe que não muda nada vai para a imersão, não para esta lista.

A resposta do usuário vira fonte (chat). Se ele responder "deixa de fora" ou "o cliente não definiu", o item não entra nos requisitos. Se o cliente poderia presumir que ele está incluso, ele vai para as Exclusões.

Se não houver lacuna, siga direto para o documento, sem pedir confirmação.

## Passo 4 — Redigir

Escreva o conteúdo num arquivo markdown, numa pasta de trabalho: no claude.ai, `/home/claude/requisitos/`; em outro ambiente (Cowork, Claude Code), uma pasta de trabalho da tarefa. Siga o formato da seção "Formato do markdown". O script cuida da capa, das cores e dos marcadores; você cuida só do texto.

### Estrutura

**Front matter.** `projeto` é o nome do produto, se ele foi usado nas reuniões; senão, o nome da empresa. `subtitulo` é uma linha que descreve a solução ("Portal de Gestão de Compras").

**1. Visão Geral.** De dois a quatro parágrafos: o que é a solução e em quais ambientes ela roda; como opera, com o fluxo principal descrito de uma vez; e o objetivo, ligado à dor central levantada com o cliente. Em seguida, `### Notas e Abreviaturas`:

- `A(cli)D: O Aplicativo do Cliente ({ambientes deste projeto}) DEVE...`
- `SID: O Sistema Integrado ({componentes deste projeto}) DEVE...`
- `Hardcoded: elemento fixo em código por decisão estratégica expressa do cliente.` (só se for usado)
- `RN: Regra de Negócio de observância obrigatória, validada no servidor.` (só se for usado)
- Siglas do domínio, só as que aparecem no texto.

**2. Requisitos Funcionais.** Comece por `2.1. Autenticação e Perfis de Acesso` quando houver login. Nomeie cada perfil com uma linha sobre o que ele pode fazer: é isso que o dimensionamento precisa. Depois vêm os módulos, na ordem da jornada principal do usuário; os módulos administrativos e de back-office ficam depois. Por último, `Disponibilização do Produto`, se os ambientes de entrega foram discutidos.

- Cada módulo abre com a linha `**Superfície:** {app mobile | site | painel web}.`, logo abaixo do título.
- `**A(cli)D** {verbo no infinitivo}...` descreve o que a interface oferece: telas, ações e o que o usuário vê.
- `**SID** {verbo no infinitivo}...` descreve o que o sistema garante: regra, persistência, processamento e integração.
- Não repita o mesmo fato nos dois. Uma frase por item, de três a oito itens por módulo.
- Termo da tabela do Passo 2 aparece com o mecanismo: "atualizar o status por aviso do servidor (push)" ou "atualizar o status a cada 30 segundos", nunca "em tempo real" sozinho.
- `### Regras de Negócio` só aparece em módulo com regra que mudou o tamanho no Passo 2. A numeração `RN-01, RN-02...` corre pelo documento inteiro.
- `**Hardcoded**` marca uma decisão fixa do cliente. Ela importa para o dimensionamento porque elimina tela de configuração.

Fluxo de dados, no módulo onde ele acontece:

```
- **SID** consolidar os pedidos de compra das filiais:
  - **Origem:** planilha .xlsx exportada do ERP pelo setor de compras e enviada pela plataforma.
  - **Processamento:** validação de colunas obrigatórias e agrupamento por fornecedor.
  - **Destino:** base da plataforma, exibida no painel de compras.
```

Integração, no módulo que a usa:

```
- **SID** integrar com o {sistema} para {finalidade}:
  - **Sentido:** {envia | recebe | envia e recebe}.
  - **Dados:** {o que trafega}.
  - **Meio:** {API do fornecedor | arquivo | webhook}.
```

**3. Requisitos Não Funcionais.** Cada subseção só aparece se tiver conteúdo com fonte. Use prosa, com `**Rótulo:**` no início do parágrafo quando ajudar.

- `3.1. Plataforma e Arquitetura`: ambientes de entrega; arquitetura em nível macro, só com os componentes que os requisitos exigem (API central, banco, armazenamento de arquivos se houver upload); serviços de terceiros já definidos com o cliente; e sempre o parágrafo fixo abaixo.
- `3.2. Interface e Identidade Visual`: só o que foi discutido (estilo, mobile-first ou desktop-first, marca existente).
- `3.3. Performance`: só se o cliente declarou alguma exigência (tempo real, volume, simultaneidade), com o mecanismo da tabela do Passo 2. Nunca invente SLA em segundos.
- `3.4. Segurança e Privacidade`: só o que foi discutido. Se houve dado sensível na conversa (saúde, financeiro, menores), cabe uma linha sobre LGPD.

Parágrafo fixo do 3.1, usado sem alteração e escrito como parágrafo comum (sem o `>` da citação abaixo):

> **Definição tecnológica:** as tecnologias específicas de implementação — linguagens, frameworks, provedores de nuvem e fornecedores de serviços gerenciados não citados nominalmente neste documento — serão formalmente definidas e registradas na Sprint de Refino e Prototipação. Este documento estabelece requisitos arquiteturais independentes de tecnologia, não fixando qualquer stack como decisão definitiva antes dessa validação.

**4. Exclusões Explícitas.** Abra com `Este escopo NÃO contempla os seguintes itens:` e escreva cada item como `- **Título:** frase.`, nesta ordem:

1. **O que foi descartado nas reuniões**, com a decisão como foi tomada.
2. **O que o cliente poderia presumir que está incluso.** O item precisa ser vizinho de algo que está no escopo, e não uma lista genérica. O teste: lendo os requisitos, o cliente poderia razoavelmente achar que isso vem junto? Pagamento sugere nota fiscal e conciliação. Painel de indicadores sugere BI e relatórios customizáveis. Dados vindos de planilha ou de sistema antigo sugerem migração do histórico. IA sugere decisão autônoma. Login sugere login social ou SSO. App sugere identidade visual e materiais de marca. Termos de uso sugerem redação jurídica. Confira que nenhuma exclusão contradiz um requisito do documento.
3. **As duas cláusulas fixas**, sempre por último e sem alteração:
   - `**Integrações Não Citadas:** não serão realizadas integrações com sistemas, APIs ou serviços de terceiros que não estejam expressamente previstos neste documento.`
   - `**Funcionalidades Não Descritas neste Documento:** qualquer funcionalidade não descrita neste escopo será tratada como solicitação de mudança formal (Change Request), sujeita a reavaliação de prazo e esforço.`

Ponto para a imersão não vira Exclusão: Exclusão é o que não será feito; ponto para a imersão é detalhe do que será feito.

### Tamanho

O teto é de 10 páginas, e só para projeto muito grande. Como referência, um projeto pequeno (um ou dois módulos) ocupa de 3 a 4 páginas, e um médio, de 5 a 7. O próprio ValeDOC tem 19 páginas: siga a estrutura dele, não a densidade. Se passar do teto, corte detalhe (RN fraca, item SID que descreve implementação). Nunca corte uma funcionalidade ou integração discutida.

### Estilo

Português formal e impessoal, com verbo no infinitivo depois de A(cli)D e SID. Nada de adjetivo de venda ("robusto", "intuitivo", "moderno"). Cite fornecedor de terceiro só se ele foi decidido com o cliente; stack não se cita.

**Nada interno chega ao PDF:** nem tag de fonte, nem "⚠", nem "a confirmar". É anexo de contrato, e as lacunas já foram resolvidas no Passo 3. O script recusa o arquivo se encontrar esses marcadores, e também se encontrar sintaxe fora do dialeto, que sairia literal no PDF.

## Passo 5 — Auditoria antes de gerar

Releia o markdown item por item e diga, para cada um, de onde ele veio. Não pergunte a si mesmo "isso bate com o que o cliente falou?", porque essa pergunta sempre responde sim. Pergunte "qual é a fonte?": o item inventado é justamente o que não tem fonte para citar.

- **Tem fonte**: mantém.
- **Deriva em um passo de algo com fonte**: mantém.
- **Nenhuma das duas**: sai.

Confira também que todo módulo declara a superfície, que todo fluxo de dados tem as três partes, que toda integração tem sentido, dados e meio, que nenhum termo da tabela do Passo 2 aparece sem mecanismo e que nenhuma exclusão contradiz um requisito.

## Passo 6 — Gerar o PDF

```bash
python <pasta-desta-skill>/scripts/gerar_pdf.py <pasta-de-trabalho>/{projeto}.md --saida <pasta-que-o-usuario-ve>
```

`<pasta-desta-skill>` é a pasta do SKILL.md que você acabou de ler. A pasta que o usuário vê é `/mnt/user-data/outputs` no claude.ai e, no Cowork, a pasta que ele escolheu para a tarefa. Sem `--saida`, o script usa `/mnt/user-data/outputs` se ela existir; senão, a pasta do markdown.

O script monta o documento sobre o template do NTec (`assets/template.docx`), gera `[Requisitos] {projeto}.pdf`, informa o número de páginas e guarda o `.docx` ao lado do markdown. Ele precisa do LibreOffice e o procura sozinho (sandbox do claude.ai, PATH, macOS e Windows). Os códigos de saída dizem o que fazer:

- **2, marcador interno:** corrija o texto. Não use `--forcar` em documento que vai para o cliente.
- **3, sintaxe fora do dialeto:** reescreva as linhas apontadas. Não existe `--forcar` para isso.
- **4, LibreOffice não encontrado:** o `.docx` ficou pronto; diga ao usuário o caminho e que ele pode instalar o LibreOffice ou exportar o `.docx` para PDF pelo Word.

No claude.ai, chame `present_files` com o PDF. Em outro ambiente, diga o caminho onde ele ficou.

**Estilização é conversa, não etapa.** Se depois o usuário pedir ajustes visuais (fonte, espaçamento, capa), edite o `.docx` guardado usando a skill de documentos Word e converta de novo para PDF. Não há outra skill nem outro passo para isso.

## Passo 7 — Resposta no chat

As fontes aparecem aqui, no chat, e nunca no documento. O usuário precisa delas para conferir que nada foi inventado; o cliente, lendo o anexo do contrato, não precisa.

Formato da fonte, no fim de cada item: `[Fathom · AT 12/03]`, `[Granola · Aprof. 19/03]`, `[transcrição · AT 12/03]`, `[chat]` ou `[doc: nome do arquivo]`. Se um item tiver mais de uma fonte, cite a que decidiu o ponto. Se for derivação, cite a fonte do item de origem e acrescente `(derivado)`.

Depois do arquivo, entregue exatamente estes blocos, curtos, nesta ordem:

**Perfis de acesso**: um item por perfil, com o que ele pode fazer e a fonte.

**Funcionalidades**: agrupadas pelos módulos do documento (`2.x Nome`), com as funcionalidades de cada um numa linha e a fonte.

**Integrações**: sistema, sentido, o que trafega e a fonte. Se não houver nenhuma, diga "Nenhuma integração com sistemas externos."

**Inventário para dimensionamento**: uma tabela, uma linha por módulo, com estas colunas e nesta ordem:

`Módulo | Superfície | Itens A(cli)D | Itens SID | Integrações | Fluxos de dados | Fatores de complexidade`

Os fatores são só os da lista do Passo 2 que aparecem no módulo, com o mecanismo ("tempo real: push", "notificação: e-mail e WhatsApp", "concorrência: aceite atômico"). Este bloco é a entrada da `validacao-tecnica-ntec`, que dimensiona a partir dele. Não mude as colunas sem atualizar também a validação.

**Pontos para a imersão**: o que apareceu nas fontes e não muda o tamanho, um por linha, com a fonte. Eles entram nas atividades da sprint de imersão da validação técnica. Não vão para o PDF nem para as Exclusões. Se não houver nenhum, diga "Nenhum."

Feche com uma linha: `Auditoria: N itens verificados, M removidos sem fonte · X páginas.`

## Formato do markdown

```
---
projeto: {Nome}
subtitulo: {Descrição em uma linha}
---
# 1. Visão Geral
Parágrafo de texto corrido (uma linha = um parágrafo).
### Notas e Abreviaturas
- A(cli)D: ...
# 2. Requisitos Funcionais
## 2.1. Autenticação e Perfis de Acesso
**Superfície:** app mobile e painel web.
- **A(cli)D** disponibilizar...
- **SID** controlar...
  - **Origem:** sub-item (dois espaços antes do hífen)
### Regras de Negócio
- **RN-01** ...
# 3. Requisitos Não Funcionais
## 3.1. Plataforma e Arquitetura
**Ambientes de entrega:** parágrafo com rótulo em negrito.
# 4. Exclusões Explícitas
Este escopo NÃO contempla os seguintes itens:
- **Título:** frase. (nesta seção os itens saem numerados)
```

`#` é seção, `##` é módulo, `###` é rótulo de bloco, `- ` é item, dois espaços e `- ` é sub-item, e `**texto**` é negrito. O script recusa todo o resto (`*` ou `1.` como item, `####`, tabela, `>`, itálico, crase, link), porque sairia literal no anexo de contrato.
