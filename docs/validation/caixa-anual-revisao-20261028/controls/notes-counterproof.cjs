'use strict';
const fs=require('node:fs'),path=require('node:path');
const original=fs.readFileSync;
const target=path.resolve('src/js/40-app/14-mvp-notes.js');
const alias=process.env.CAIXA_ALIAS;
if(!['management','contab'].includes(alias))throw Error('Choose the exact alias');
let applied=0;
fs.readFileSync=function(file,...args){
  let value=original.call(this,file,...args);
  if(typeof file==='string'&&path.resolve(file)===target&&typeof value==='string'){
    const from=alias+":'Gerenciamento · Caixa Anual'";
    const to=alias+":'Gerenciamento · Contabilidade'";
    if(value.split(from).length!==2)throw Error('Expected one exact label');
    value=value.replace(from,to);applied++;
  }
  return value;
};
process.on('exit',()=>console.error(JSON.stringify({counterproof:alias,sourceReadMutations:applied,diskUnchanged:true})));
