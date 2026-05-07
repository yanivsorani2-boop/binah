import os, re, json
from collections import defaultdict

CLUSTERS = {
    'compare-flagship-models': r'^compare-.*(claude.*gemini|gemini.*claude|claude.*gpt|gpt.*claude|gemini.*gpt|gpt.*gemini)',
    'compare-models-general': r'^compare-(?!.*claude.*gemini|.*gemini.*claude)',
    'guide-chatgpt-mastery': r'^guide-.*chatgpt',
    'guide-prompts-engineering': r'^guide-.*prompt',
    'guide-ai-tools-overview': r'^guide-.*ai-tools',
    'guide-weekly-ai-roundup': r'^guide-weekly',
    'tools-coding-comparison': r'^tools-.*coding',
    'tools-video-comparison': r'^tools-.*video',
    'tools-writing-comparison': r'^tools-.*writing',
    'tools-comprehensive-comparison': r'^tools-(ai-tools|best)(?!.*coding|.*video|.*writing)',
    'tools-weekly-roundup': r'^tools-weekly',
    'business-ai-roi-israel': r'^business-(?!weekly)',
    'business-weekly-roundup': r'^business-weekly',
    'hebrew-ai-tools-review': r'^hebrew-(?!weekly)',
    'hebrew-weekly-roundup': r'^hebrew-weekly',
    'ai-agents-enterprise': r'^ai-agents',
}

clusters = defaultdict(list)
for f in sorted(os.listdir('articles')):
    if not f.startswith('2026-') or not f.endswith('.html'): continue
    slug = f[:-5]
    topic = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', slug)
    matched = False
    for cname, pattern in CLUSTERS.items():
        if re.match(pattern, topic):
            clusters[cname].append(slug)
            matched = True; break
    if not matched: clusters['misc'].append(slug)

def word_count(slug):
    try:
        h = open(f"articles/{slug}.html").read()
        m = re.search(r'<main.*?</main>', h, re.DOTALL)
        if not m: return 0
        t = re.sub(r'<[^>]+>', ' ', re.sub(r'<script.*?</script>|<style.*?</style>', '', m.group(), flags=re.DOTALL))
        return len(t.split())
    except: return 0

result = {}
for cname, slugs in clusters.items():
    if not slugs: continue
    ranked = sorted(slugs, key=lambda s: (s[:10], word_count(s)), reverse=True)
    result[cname] = {'canonical': ranked[0], 'redirects': ranked[1:], 'count': len(slugs), 'topic_he': ''}

with open('.cluster-plan.json','w') as f: json.dump(result, f, ensure_ascii=False, indent=2)
print(f"Clusters: {len(result)}, total articles: {sum(c['count'] for c in result.values())}, redirects: {sum(len(c['redirects']) for c in result.values())}")
for cname, info in result.items():
    print(f"  {cname}: {info['count']} -> {info['canonical']}")
