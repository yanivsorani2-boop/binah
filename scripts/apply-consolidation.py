import json, os, re

plan = json.load(open('.cluster-plan.json'))
redirect_block = "\n# === v6 cluster consolidation ===\n"
deleted = 0; redirected = 0; imgs_deleted = 0

for cname, info in plan.items():
    canonical = info['canonical']
    for orphan in info['redirects']:
        redirect_block += f'\n[[redirects]]\n  from = "/articles/{orphan}"\n  to = "/articles/{canonical}"\n  status = 301\n  force = true\n'
        # delete HTML file
        p = f"articles/{orphan}.html"
        if os.path.exists(p):
            os.remove(p)
            deleted += 1
        # delete OG images
        for ext in ['jpg','webp','avif']:
            ip = f"images/og/{orphan}.{ext}"
            if os.path.exists(ip):
                os.remove(ip)
                imgs_deleted += 1
        redirected += 1

# append to netlify.toml
nt = open('netlify.toml').read()
if 'v6 cluster consolidation' not in nt:
    with open('netlify.toml','a') as f:
        f.write(redirect_block)

# rebuild sitemap.xml - remove orphan URLs
sm = open('sitemap.xml').read()
for cname, info in plan.items():
    for orphan in info['redirects']:
        pattern = r'\s*<url>\s*<loc>[^<]*' + re.escape(orphan) + r'[^<]*</loc>[\s\S]*?</url>'
        sm = re.sub(pattern, '', sm)
# clean up extra blank lines
sm = re.sub(r'\n{3,}', '\n\n', sm)
open('sitemap.xml','w').write(sm)

# count remaining sitemap entries
remaining = len(re.findall(r'<loc>[^<]+/articles/2026-', sm))
print(f"Sitemap: {remaining} auto articles remaining (target: 17)")

# remove cards from index.html
home = open('index.html').read()
removed_cards = 0
for cname, info in plan.items():
    for orphan in info['redirects']:
        new_home = re.sub(r'<article[^>]*>(?:(?!</article>).)*?' + re.escape(orphan) + r'(?:(?!</article>).)*?</article>\s*', '', home, flags=re.DOTALL)
        if new_home != home:
            removed_cards += 1
            home = new_home
open('index.html','w').write(home)

# also from category pages
for cat in os.listdir('categories'):
    if not cat.endswith('.html'): continue
    p = f"categories/{cat}"
    h = open(p).read()
    orig = h
    for cname, info in plan.items():
        for orphan in info['redirects']:
            h = re.sub(r'<article[^>]*>(?:(?!</article>).)*?' + re.escape(orphan) + r'(?:(?!</article>).)*?</article>\s*', '', h, flags=re.DOTALL)
    if h != orig:
        open(p,'w').write(h)

# also archive.html
if os.path.exists('archive.html'):
    h = open('archive.html').read()
    for cname, info in plan.items():
        for orphan in info['redirects']:
            h = re.sub(r'<article[^>]*>(?:(?!</article>).)*?' + re.escape(orphan) + r'(?:(?!</article>).)*?</article>\s*', '', h, flags=re.DOTALL)
    open('archive.html','w').write(h)

# also data/articles-archive.json
if os.path.exists('data/articles-archive.json'):
    aj = json.load(open('data/articles-archive.json'))
    all_orphans = set()
    for info in plan.values():
        all_orphans.update(info['redirects'])
    if isinstance(aj, list):
        aj = [a for a in aj if a.get('slug','') not in all_orphans and a.get('href','').replace('/articles/','').replace('.html','') not in all_orphans]
        json.dump(aj, open('data/articles-archive.json','w'), ensure_ascii=False, indent=2)

# also feed.xml
if os.path.exists('feed.xml'):
    feed = open('feed.xml').read()
    for cname, info in plan.items():
        for orphan in info['redirects']:
            feed = re.sub(r'\s*<item>[\s\S]*?' + re.escape(orphan) + r'[\s\S]*?</item>', '', feed)
    open('feed.xml','w').write(feed)

print(f"Deleted HTML: {deleted}, Images deleted: {imgs_deleted}")
print(f"Redirects added to netlify.toml: {redirected}")
print(f"Cards removed from homepage: {removed_cards}")
