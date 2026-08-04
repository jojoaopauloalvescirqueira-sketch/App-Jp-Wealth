// ============ GRÁFICOS · CROMO PADRÃO DE TERMINAL ============
// Convenções de gráfico financeiro compartilhadas pelos 6 SVGs do sistema:
// eixo Y à DIREITA, gridlines pontilhadas, área preenchida sob a linha, caixa
// de cotação corrente no eixo e bloco de estatísticas no canto superior.
// É só desenho — nenhuma destas funções calcula valor, todas recebem prontos.
const CH = {
  // Margens padrão: eixo à direita, então L encolhe e R cresce.
  L:10, R:62, T:14, B:22,

  // Gridlines horizontais pontilhadas + rótulos do eixo à direita.
  gridY(W,L,R,Y,vals,fmt){
    return vals.map(v=>{
      const y=+Y(v).toFixed(1);
      return `<line x1="${L}" x2="${W-R}" y1="${y}" y2="${y}" stroke="var(--line)" stroke-dasharray="1 3"/>`
           + `<text x="${W-R+5}" y="${(y+3).toFixed(1)}" font-size="8.5" fill="var(--ink-faint)">${fmt(v)}</text>`;
    }).join('');
  },

  // Caixa de cotação corrente colada no eixo direito, em vídeo invertido.
  callout(W,R,y,txt,color){
    const w=Math.max(28, String(txt).length*5.2+8);
    return `<g><rect x="${W-R+2}" y="${(y-6).toFixed(1)}" width="${w.toFixed(1)}" height="12" fill="${color}"/>`
         + `<text x="${W-R+5}" y="${(y+3).toFixed(1)}" font-size="8.5" font-weight="700" fill="var(--bg)">${esc(txt)}</text></g>`;
  },

  // Bloco de estatísticas no canto superior esquerdo: marcador, rótulo, valor.
  // rows = [{mark:'□', label:'Último', value:'$10.240', color:'var(--f1)'}]
  stats(L,T,rows,width){
    const w=width||150;
    return `<g font-size="8.5">` + rows.map((r,i)=>{
      const y=T+9+i*10;
      return `<text x="${L+3}" y="${y}" fill="${r.color||'var(--ink-faint)'}">${r.mark||'·'}</text>`
           + `<text x="${L+13}" y="${y}" fill="var(--ink-dim)">${esc(r.label)}</text>`
           + `<text x="${L+w}" y="${y}" text-anchor="end" fill="${r.color||'var(--data-num)'}" font-weight="700">${esc(r.value)}</text>`;
    }).join('') + `</g>`;
  },

  // Fecha um path de linha contra uma baseline, produzindo a área preenchida.
  area(path,x0,x1,yBase){
    return `${path} L${(+x1).toFixed(1)} ${(+yBase).toFixed(1)} L${(+x0).toFixed(1)} ${(+yBase).toFixed(1)} Z`;
  },

  // Linha de limite horizontal rotulada (MDD, alarme, piso).
  limit(W,L,R,y,label,color){
    return `<line x1="${L}" x2="${W-R}" y1="${(+y).toFixed(1)}" y2="${(+y).toFixed(1)}" stroke="${color}" stroke-dasharray="4 3" opacity=".9"/>`
         + `<text x="${W-R-4}" y="${(+y-3).toFixed(1)}" text-anchor="end" font-size="8.5" fill="${color}">${esc(label)}</text>`;
  },

  // Régua de ticks igualmente espaçados entre min e max.
  ticks(min,max,n){ return Array.from({length:n+1},(_,i)=>min+(max-min)*i/n); }
};
