# jp-wealth-news-feed

Alimentador de dados para o widget **"Notícias de alto impacto · hoje"** do JP
Wealth Risk Terminal. Este repositório contém **apenas dados públicos** de
calendário econômico (Forex Factory) — nenhum dado pessoal ou do terminal.

## Por que este repositório existe

O feed do Forex Factory não permite leitura direta pelo navegador (sem CORS) e
limita ~1 requisição por minuto por IP. O app JP Wealth é 100% client-side, sem
servidor próprio. A GitHub Action deste repositório faz a busca do lado do
servidor a cada 30 minutos e publica o resultado filtrado em
`ff-high-impact.json`, que o GitHub serve com CORS liberado
(`access-control-allow-origin: *`) via `raw.githubusercontent.com`.

## Filtro aplicado

Somente eventos de **impacto Alto** nas moedas **USD, EUR, JPY e GBP** — a
cobertura exata dos mercados operados no terminal: EURUSD, USDJPY, GBPUSD,
S&P 500 e Gold. O restante do calendário é descartado na origem.

## Como publicar (uma única vez)

1. Crie um repositório **público** no GitHub chamado exatamente
   `jp-wealth-news-feed` (o nome faz parte da URL que o widget consome).
2. Copie todo o conteúdo desta pasta para ele (incluindo a pasta oculta
   `.github/`) e publique na branch `main`.
3. Na aba **Actions** do repositório novo, habilite os workflows se o GitHub
   pedir, abra "Atualizar notícias de alto impacto" e clique **Run workflow**
   uma vez para validar.
4. Pronto — o agendamento de 30 min assume a partir daí.

A URL final consumida pelo widget:

```
https://raw.githubusercontent.com/jojoaopauloalvescirqueira-sketch/jp-wealth-news-feed/main/ff-high-impact.json
```

## Manutenção

- **Dado parado?** O GitHub pausa agendamentos após ~60 dias sem atividade no
  repositório. Abra Actions → "Atualizar notícias de alto impacto" → Run
  workflow. O widget do app também denuncia a idade do dado ("atualizado às").
- **Feed fora do ar?** O script nunca sobrescreve o JSON anterior com dado
  inválido — o último dado bom permanece publicado até o feed voltar.
- **Trocar o filtro** (moedas/impacto): editar as constantes no topo de
  `scripts/fetch_news.py`.

## Arquivos

| Arquivo | Papel |
|---|---|
| `ff-high-impact.json` | Saída publicada — o que o widget consome |
| `scripts/fetch_news.py` | Busca, valida e filtra o feed |
| `.github/workflows/update-news.yml` | Agendamento de 30 min + commit condicional |
