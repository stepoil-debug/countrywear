const crypto = require('crypto');
const REPO = process.env.GITHUB_REPO || 'stepoil-debug/countrywear';
const BRANCH = process.env.GITHUB_BRANCH || 'main';
const TOKEN = process.env.GITHUB_TOKEN;
const SESSION_SECRET = process.env.SESSION_SECRET;
const ADMIN_USER = process.env.ADMIN_USER || 'admin';
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD;
function response(statusCode, body){return {statusCode,headers:{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','Access-Control-Allow-Origin':'*','Access-Control-Allow-Headers':'Content-Type, Authorization','Access-Control-Allow-Methods':'GET,PUT,POST,DELETE,OPTIONS'},body:JSON.stringify(body)}}
function safeEqual(a,b){const ah=crypto.createHash('sha256').update(String(a||'')).digest();const bh=crypto.createHash('sha256').update(String(b||'')).digest();return crypto.timingSafeEqual(ah,bh)}
function sign(payload){if(!SESSION_SECRET)throw new Error('SESSION_SECRET não configurado');const raw=Buffer.from(JSON.stringify(payload)).toString('base64url');const sig=crypto.createHmac('sha256',SESSION_SECRET).update(raw).digest('base64url');return `${raw}.${sig}`}
function verify(token){if(!token||!SESSION_SECRET)return false;const [raw,sig]=token.split('.');if(!raw||!sig)return false;const expected=crypto.createHmac('sha256',SESSION_SECRET).update(raw).digest('base64url');if(!safeEqual(sig,expected))return false;try{const p=JSON.parse(Buffer.from(raw,'base64url').toString('utf8'));return p.exp>Date.now()?p:false}catch{return false}}
function requireAuth(event){const header=event.headers.authorization||event.headers.Authorization||'';return verify(header.replace(/^Bearer\s+/i,''))}
async function gh(path, options={}){if(!TOKEN)throw new Error('GITHUB_TOKEN não configurado');const r=await fetch(`https://api.github.com/repos/${REPO}${path}`,{...options,headers:{Accept:'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28',Authorization:`Bearer ${TOKEN}`,'User-Agent':'lr-countrywear-admin',...(options.headers||{})}});if(r.status===204)return null;const data=await r.json().catch(()=>({}));if(!r.ok)throw new Error(data.message||`GitHub ${r.status}`);return data}
async function readFile(path){const data=await gh(`/contents/${encodePath(path)}?ref=${encodeURIComponent(BRANCH)}`);return {sha:data.sha,content:Buffer.from(data.content,'base64').toString('utf8')}}
async function writeText(path,content,message){let sha;try{sha=(await readFile(path)).sha}catch(e){if(!String(e.message).includes('Not Found'))throw e}const body={message,content:Buffer.from(content,'utf8').toString('base64'),branch:BRANCH,...(sha?{sha}:{})};return gh(`/contents/${encodePath(path)}`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})}
async function writeBase64(path,base64,message){let sha;try{sha=(await gh(`/contents/${encodePath(path)}?ref=${encodeURIComponent(BRANCH)}`)).sha}catch(e){if(!String(e.message).includes('Not Found'))throw e}return gh(`/contents/${encodePath(path)}`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({message,content:base64,branch:BRANCH,...(sha?{sha}:{})})})}
async function deleteFile(path,message){const data=await gh(`/contents/${encodePath(path)}?ref=${encodeURIComponent(BRANCH)}`);return gh(`/contents/${encodePath(path)}`,{method:'DELETE',headers:{'Content-Type':'application/json'},body:JSON.stringify({message,sha:data.sha,branch:BRANCH})})}
function encodePath(path){return path.split('/').map(encodeURIComponent).join('/')}
module.exports={response,safeEqual,sign,verify,requireAuth,gh,readFile,writeText,writeBase64,deleteFile,ADMIN_USER,ADMIN_PASSWORD};
