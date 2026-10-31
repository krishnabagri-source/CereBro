import { mkdir, readFile, rename, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { seedProfiles, type Learner } from '../src/engine';

export type Store = { learners: Learner[]; active: number; subject: string };
const defaults=():Store=>({learners:seedProfiles(),active:0,subject:'algebra'});

export async function loadStore(filePath:string):Promise<Store>{
  try {
    const parsed=JSON.parse(await readFile(filePath,'utf8')) as Partial<Store>;
    if(!Array.isArray(parsed.learners)||parsed.learners.length<2||!Number.isInteger(parsed.active)||typeof parsed.subject!=='string')return defaults();
    return parsed as Store;
  } catch { return defaults(); }
}
export async function saveStore(filePath:string,store:Store):Promise<void>{
  await mkdir(path.dirname(filePath),{recursive:true});
  const temp=`${filePath}.tmp`;
  await writeFile(temp,JSON.stringify(store,null,2),'utf8');
  await rename(temp,filePath);
}
