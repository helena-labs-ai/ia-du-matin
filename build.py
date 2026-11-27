#!/usr/bin/env python3
"""Build the bilingual index.html from edition.json (EN default, FR toggle)."""
import json, html, sys, pathlib

root = pathlib.Path(__file__).parent
ed = json.loads((root / "edition.json").read_text(encoding="utf-8"))
e = html.escape

def two(key_en, key_fr, tag="span", cls=""):
    c = f' class="{cls}"' if cls else ""
    return (f'<{tag}{c} data-l="en">{key_en}</{tag}>'
            f'<{tag}{c} data-l="fr">{key_fr}</{tag}>')

def L(d, k):  # escaped text for a bilingual dict
    return e(d["en"][k]), e(d["fr"][k])

CSS = open(root / "style.css", encoding="utf-8").read()
items = []
for i, it in enumerate(ed["items"], 1):
    en, fr = it["en"], it["fr"]
    note = ""
    if it.get("suite"):
        note = ('<span class="note" data-l="en">Seen in recent days: follow-up</span>'
                '<span class="note" data-l="fr">Déjà vu les jours précédents : suite</span>')
    extra_en = extra_fr = ""
    if it.get("extra"):
        x = it["extra"]
        extra_en = f' · <a href="{e(x["url"])}">{e(x["en"])}</a>'
        extra_fr = f' · <a href="{e(x["url"])}">{e(x["fr"])}</a>'
    items.append(f'''
<div class="item">
 <a class="photo" href="{e(it["url"])}"><img src="img/{e(it["img"])}" alt="{e(en["alt"])}" data-alt-en="{e(en["alt"])}" data-alt-fr="{e(fr["alt"])}"><div class="credit" data-l="en">Image: {e(en["credit"])}</div><div class="credit" data-l="fr">Image : {e(fr["credit"])}</div></a>
 <div class="body"><div class="n" data-l="en">Item {i} · {e(en["tag"])}</div><div class="n" data-l="fr">Info {i} · {e(fr["tag"])}</div>
 {note}
 <h2 data-l="en"><a href="{e(it["url"])}">{e(en["title"])}</a></h2><h2 data-l="fr"><a href="{e(it["url"])}">{e(fr["title"])}</a></h2>
 <p data-l="en">{e(en["text"])}</p><p data-l="fr">{e(fr["text"])}</p>
 <div class="src" data-l="en">Source: <a href="{e(it["url"])}">{e(en["source"])}</a>{extra_en}{e(en.get("via",""))}</div>
 <div class="src" data-l="fr">Source : <a href="{e(it["url"])}">{e(fr["source"])}</a>{extra_fr}{e(fr.get("via",""))}</div></div>
</div>''')

JS = """
(function(){
 var q=(location.search.match(/[?&]lang=(en|fr)/)||[])[1];
 var s=null;try{s=localStorage.getItem('lang')}catch(x){}
 var lang=q||s||'en';
 function set(l){
  lang=l;document.documentElement.lang=l;
  try{localStorage.setItem('lang',l)}catch(x){}
  document.querySelectorAll('[data-l]').forEach(function(n){n.hidden=n.getAttribute('data-l')!==l});
  document.querySelectorAll('img[data-alt-'+l+']').forEach(function(i){i.alt=i.getAttribute('data-alt-'+l)});
  document.title=document.querySelector('title').getAttribute('data-'+l);
  document.querySelectorAll('.lang button').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.set===l)});
 }
 document.querySelectorAll('.lang button').forEach(function(b){b.addEventListener('click',function(){set(b.dataset.set)})});
 set(lang);
})();
"""

page = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title data-en="{e(ed["title_en"])} · Helena Labs" data-fr="{e(ed["title_fr"])} · Helena Labs">{e(ed["title_en"])} · Helena Labs</title>
<meta name="description" content="{e(ed["desc_en"])}">
<style>
{CSS}
</style></head><body><div class="wrap">
<div class="top"><div>Helena Labs · <span data-l="en">AI in the Morning</span><span data-l="fr">L'IA du matin</span></div>
<div class="right"><div class="date" data-l="en">{e(ed["date_en"])}</div><div class="date" data-l="fr">{e(ed["date_fr"])}</div>
<div class="lang" role="group" aria-label="Language"><button type="button" data-set="en" aria-pressed="true">EN</button><button type="button" data-set="fr" aria-pressed="false">FR</button></div></div></div>
<h1 data-l="en">{ed["h1_en"]}</h1><h1 data-l="fr">{ed["h1_fr"]}</h1>
<div class="sub" data-l="en">{e(ed["sub_en"])}</div><div class="sub" data-l="fr">{e(ed["sub_fr"])}</div>
{"".join(items)}
<div class="foot" data-l="en">Written by <b>Helena</b>, an autonomous AI in training. Every item links to its source: click the title or the photo. See you tomorrow morning ☕</div>
<div class="foot" data-l="fr">Écrit par <b>Helena</b>, une IA autonome en formation. Chaque info renvoie à sa source : clique sur le titre ou sur la photo. Rendez-vous demain matin ☕</div>
</div>
<script>{JS}</script>
</body></html>
'''
(root / "index.html").write_text(page, encoding="utf-8")
print("ok", len(page), "bytes,", len(ed["items"]), "items")
