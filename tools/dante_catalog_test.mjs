// Approved contract: BRIEF-DANTE-20261024 + CHG-JPW-DANTE-{PRODUCT,CONTROLS}.
// DOM-free catalog proof; browser navigation and financial persistence need their own suites.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
const root = path.resolve(import.meta.dirname, '..');
const source = process.argv[2] || path.join(root, 'src/js/40-app/26-learning-catalog.js');
const context = {window:{}};
vm.runInNewContext(fs.readFileSync(source, 'utf8'), context, {filename:source});
const catalog = context.window.JPWLearningCatalog;
const owners = new Map();
for (const track of catalog.tracks) for (const lesson of track.steps) {
  assert(!owners.has(lesson.id), 'duplicate lesson '+lesson.id);
  owners.set(lesson.id, track.id);
}
const legacy = {
  basics:'home menu location help local-state progress',
  'personal-finance':'overview budget income expense debts comparison scenarios',
  forex:'accounts context performance operation history accounting planning reserves',
  research:'forex pivots stocks-br stocks-global reits others',
  tools:'calendar nocuda genetrix normative',
  alladin:'start instruments assets accounts cashAccounts ledger balances positions',
  general:'notes notes-save settings-general settings-account settings-appearance settings-interface settings-editor settings-statute settings-parameters settings-tool-params settings-tool-check settings-forex-consolidated settings-educational settings-probability-lab settings-storage settings-about backup session'
};
let legacyCount=0;
for (const [owner,suffixes] of Object.entries(legacy)) for (const suffix of suffixes.split(' ')) {
  const id=owner+'-'+suffix;if(id==='tools-nocuda')assert(!owners.has(id),'retired lesson absent from visible tracks');else assert.equal(owners.get(id),owner,'legacy owner '+id);legacyCount++;
}
assert.equal(legacyCount,57);
assert.deepEqual(JSON.parse(JSON.stringify(catalog.retiredSteps)),[{id:'tools-nocuda',trackId:'tools',replacementId:'tools-genetrix'}],'retired compatibility identities are separate from visible lessons');
for(const [owner,suffixes] of Object.entries(legacy)) {
  const expected=suffixes.split(' ').map(s=>owner+'-'+s).filter(id=>id!=='tools-nocuda');
  const actual=catalog.tracks.find(t=>t.id===owner).steps;
  assert.equal(actual[0].id,expected[0],'legacy start '+owner);
  assert.deepEqual(Array.from(actual,s=>s.id).filter(id=>expected.includes(id)),expected,'relative legacy order '+owner);
}
assert.equal(catalog.version,1,'catalogVersion remains compatible');
assert(Array.isArray(catalog.journey),'continuous journey is required');
assert.deepEqual(Array.from(catalog.journey,c=>c.id),['basics','research','planning','forex','personal-finance','tools','alladin','general']);
const journeyIds=[];
for (const chapter of catalog.journey) {
  assert(chapter.title&&chapter.stepIds.length,'chapter requires title and lessons');
  for (const id of chapter.stepIds) {assert(owners.has(id),'journey references real ID '+id);journeyIds.push(id);}
}
assert.equal(new Set(journeyIds).size,journeyIds.length,'journey never duplicates a lesson');
assert.equal(journeyIds.length,owners.size,'each lesson occurs exactly once');
const planning=catalog.journey.find(c=>c.id==='planning');
assert.equal(planning.module,'planning');
assert(planning.stepIds.includes('forex-planning'));
assert(!catalog.journey.find(c=>c.id==='forex').stepIds.includes('forex-planning'));
const lessons=catalog.tracks.flatMap(t=>t.steps);
assert.equal(lessons.find(s=>s.id==='forex-planning').availabilityModule,'planning');
for(const lesson of lessons){
  assert(Array.isArray(lesson.speech)&&lesson.speech.length,'editorial speech '+lesson.id);
  for(const speech of lesson.speech){
    assert.equal(typeof speech,'string');assert(speech.trim());
    assert(speech.length<=280,'short balloon '+lesson.id);
    assert((speech.match(/[.!?](?:\s|$)/g)||[]).length<=2,'two sentences per balloon '+lesson.id);
    assert(!/<[^>]+>/.test(speech),'plain text '+lesson.id);
  }
  assert(lesson.anchor&&typeof lesson.anchor==='string','anchor '+lesson.id);
  if(lesson.practice)assert(['budget','notes'].includes(lesson.practice),'only existing observers');
  if(lesson.kind==='action')assert(['menu','help','notes','session'].includes(lesson.action),'only existing action observers');
}
for(const id of ['planning-form','planning-consolidated','planning-monthly','tools-agenda','tools-markets','tools-calendar-coverage','general-notifications']) {
  const lesson=lessons.find(s=>s.id===id);assert(lesson,'real capability coverage '+id);
  assert.equal(lesson.kind,'read');assert(!lesson.practice,'no unsupported practice '+id);
}
const taskContracts={
  'planning-form':[/Criar nova conta|criar.*conta/i,/mês.*ano|ano.*mês/i,/capital.*aporte/i,/perfil/i,/custo.*renda/i,/previsão.*marcos|marcos.*previsão/i,/Revisar/i,/Confirmar/i,/Cancelar/i,/indeterminado/i],
  'planning-monthly':[/conta.*mês/i,/Percentual.*USD|percentual.*dólares/i,/zero.*ausência|ausência.*zero/i,/Confirmar registro/i,/fechamentos.*reconferência/i,/aporte.*reais/i,/saque.*opciona/i,/Finalizado = Sim/i,/Salvar resultado e revisar fechamento/i,/Confirmar fechamento/i,/anterior pendente/i,/indeterminado/i],
  'tools-agenda':[/Novo/i,/Tipo.*Título/i,/Data/i,/Dia inteiro/i,/Horário inicial.*final/i,/Fuso/i,/inexistente.*ambíguo/i,/Salvar/i,/Registro salvo na agenda/i,/Atualizar revisão/i,/indeterminado/i,/Editar/i,/Concluir/i,/Excluir registro/i,/Cancelar/i]
};
for(const [id,requirements] of Object.entries(taskContracts)){
  const lesson=lessons.find(s=>s.id===id),text=lesson.speech.join(' ');
  let previousPhase=-1;
  for(const requirement of requirements){
    assert(requirement.test(text),'complete task semantics '+id+': '+requirement);
    const phase=lesson.speech.findIndex(line=>requirement.test(line));
    assert(phase>=previousPhase,'task phase order '+id+': '+requirement);previousPhase=phase;
  }
  assert.equal(lesson.speechAnchors?.length,lesson.speech.length,'one control anchor per speech '+id);
  for(const selector of lesson.speechAnchors)assert(typeof selector==='string'&&selector.trim(),'real speech control '+id);
  assert(Array.isArray(lesson.followHosts)&&lesson.followHosts.length,'concrete task hosts '+id);
  assert(lesson.followHosts.every(selector=>!/(?:reset|restart|archive|annul|data-pl-submit=\"read|history|print)/.test(selector)),'no unrelated task hosts '+id);
}
const allowedHosts={
  'planning-form':[
    '#planning dialog[data-pl-submit="configure-choice"]','#planning dialog[data-pl-submit="create"]','#planning dialog[data-pl-submit="edit"]',
    '#planning:has(dialog[data-pl-submit="create"][open],dialog[data-pl-submit="edit"][open]) dialog[data-pl-subdialog="profiles"]',
    '#planning:has(dialog[data-pl-submit="create"][open],dialog[data-pl-submit="edit"][open]) dialog[data-pl-subdialog="stop"]'
  ],
  'planning-monthly':['#planning dialog[data-pl-submit="result"]','#planning dialog[data-pl-submit="contribution"]','#planning dialog[data-pl-submit="withdrawal"]','#planning dialog[data-pl-submit="finalize"]','#planning dialog[data-pl-inline-guard]'],
  'tools-agenda':['#calendarDialog','#execEcal .calendar-form','#calendarDialog .calendar-form']
};
for(const [id,hosts] of Object.entries(allowedHosts))assert.deepEqual(Array.from(lessons.find(s=>s.id===id).followHosts),hosts,'restricted concrete hosts '+id);
const planningUI=fs.readFileSync(path.join(root,'src/js/30-accounting/06-planning/03-ui.js'),'utf8');
const agendaUI=fs.readFileSync(path.join(root,'src/js/40-app/19-calendar-agenda.js'),'utf8');
for(const token of ['pl-native-ano','pl-native-forecastArea','pl-native-lifeSummary','pl-native-dreamSummary','data-pl-native-review','data-pl-native-success','plInlineEditor','data-pl-inline-review','plInlineGuard','data-pl-closure-result','closure-save-result','closure-previous','confirmFlows'])assert(planningUI.includes(token),'real Planning source hook '+token);
for(const token of ['calendarDialog','calendar-form','calendar-form-ambiguities','startAtChoice','endAtChoice','refresh-revision','confirm-remove','cancel-form','calendarComplete'])assert(agendaUI.includes(token),'real Agenda source hook '+token);
assert.equal(lessons.find(s=>s.id==='tools-markets').anchor,'#marketHoursTool','real existing section anchor');
assert(Object.isFrozen(catalog)&&Object.isFrozen(catalog.journey)&&Object.isFrozen(lessons[0].speech),'immutable catalog');
console.log(JSON.stringify({result:'PASS',legacyIds:legacyCount,lessons:lessons.length,chapters:catalog.journey.length,checks:'ownership, unique complete journey, planning availability, short speech, safe observers, coverage, complete task phases, per-speech anchors, restricted hosts, source hooks, immutable'},null,2));
