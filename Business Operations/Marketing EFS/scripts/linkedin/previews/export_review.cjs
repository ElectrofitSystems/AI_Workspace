const runtimeModules = require('node:path').join(require('node:os').homedir(), '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules');
const {chromium} = require(require.resolve('playwright', {paths: [__dirname, runtimeModules]}));
const {pathToFileURL} = require('node:url');
const fs = require('node:fs');
const path = require('node:path');
const outputDir = path.resolve(__dirname, '../../../output/Linkedin/posts');
(async()=>{
  const browser=await chromium.launch({headless:true,channel:'msedge'});
  const page=await browser.newPage({viewport:{width:736,height:4000}});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(pathToFileURL(path.resolve(outputDir,'previews/review.html')).href);
  const frame=page.frameLocator('iframe');
  const main=page.frames().find(f=>f!==page.mainFrame());
  await frame.locator('.li-post').first().waitFor();
  const posts=JSON.parse(fs.readFileSync(path.resolve(outputDir,'selection.json'),'utf8'));
  const stamp=new Intl.DateTimeFormat('sv-SE',{timeZone:'Europe/Rome'}).format(new Date()).replaceAll('-','')+'-'+require('node:crypto').randomUUID().slice(0,8);
  const dir=path.resolve(outputDir,'reviews',stamp);fs.mkdirSync(dir,{recursive:true});
  const files=[];
  for(let i=0;i<posts.length;i++){
    const p=posts[i];const version=i===0?'editorial-v02':'editorial-v01';const prefix=p.id+'-'+version+'-'+stamp;
    const article=frame.locator('.li-post').nth(i);
    const btn=article.locator('.li-expand');
    const text=await article.locator('.li-copy').textContent();
    if(text!==p.body.commentary)throw Error('Exact copy mismatch '+p.id);
    const loaded=await article.locator('img').evaluateAll(xs=>xs.every(x=>x.complete&&x.naturalWidth>0));
    if(!loaded)throw Error('Image load failure');
    for(const mode of ['full','feed']){
      const desired=mode==='full';
      if((await btn.getAttribute('aria-expanded')==='true')!==desired)await btn.click();
      const height=await main.evaluate(()=>document.documentElement.scrollHeight);
      await page.setViewportSize({width:736,height:height+64});
      await page.locator('iframe').evaluate((el,h)=>{el.style.height=h+'px';},height);
      const name=prefix+'-linkedin-'+mode+'.png';
      await article.screenshot({path:path.join(dir,name)});
      files.push({post_id:p.id,editorial_version:version,kind:mode,name,path:path.join(dir,name),mime:'image/png'});
    }
    const name=prefix+'-copy.md';fs.writeFileSync(path.join(dir,name),p.body.commentary+'\n','utf8');
    files.push({post_id:p.id,editorial_version:version,kind:'copy',name,path:path.join(dir,name),mime:'text/markdown'});
    const media=path.resolve(__dirname, '../../../input/Media/Pictures', p.body.media.file);
    const mediaName=prefix+'-original-media'+path.extname(media);
    fs.copyFileSync(media,path.join(dir,mediaName));
    files.push({post_id:p.id,editorial_version:version,kind:'media',name:mediaName,path:path.join(dir,mediaName),mime:p.body.media.mime});
    p.review_fingerprint=require('node:crypto').createHash('sha256').update(JSON.stringify({post_id:p.id,copy:p.body.commentary,media_sha256:p.body.media.sha256,destination:'https://www.linkedin.com/company/efitsys/',slot:null})).digest('hex');
  }
  if(errors.length)throw Error(errors.join('; '));
  const result={stamp,directory:dir,posts,files};
  fs.writeFileSync(path.join(dir,'package.json'),JSON.stringify(result,null,2));
  console.log(JSON.stringify(result));await browser.close();
})().catch(e=>{console.error(e.message);process.exit(1)});
