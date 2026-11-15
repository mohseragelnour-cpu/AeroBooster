const fs=require("fs");
let h=fs.readFileSync("ui.html","utf8");
const inj=(tag,file)=>{const c=fs.readFileSync(file,"utf8").replace(/<\/script/gi,"<\\/script"); h=h.replace(`<script>/*${tag}*/</script>`,()=>`<script>\n${c}\n</script>`);};
inj("ENGINE","engine.js");inj("SCENARIOS","scenarios.js");inj("GEOM","geom.js");inj("APP","app.js");
fs.mkdirSync("dist",{recursive:true});fs.writeFileSync("dist/index.html",h);console.log("bytes",h.length);
