"""Verificaciones del Cap. 3 (2026-10-11): IC bootstrap en HIBA, bootstrap por imagen frente a por lesión
(Swin − ConvNeXt) y corrección de Holm sobre statistical_tests_les.json. Ver
docs/resul/verificaciones_cap03_resul_20261011.md. 100% local; correr desde Codigo/.
"""
import sys, json
import numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\Facu\1\Facultad\Tesina-cap03\Codigo")
sys.path.insert(0, r"C:\Users\Facu\1\Facultad\Tesina-cap03\Codigo\scripts")
import statistical_tests as st
R="outputs/results/"
# 8a HIBA
for name,f in [("Swin t06_les_cwnone","swin_tiny_sweep_t06_les_cwnone_hiba_predictions_hiba.json"),
               ("ConvNeXt t02_les_cwnone","convnext_tiny_sweep_t02_les_cwnone_hiba_predictions_hiba.json")]:
    d=json.load(open(R+f)); yt,yp=d["y_true"],d["y_pred"]
    print("8a",name,"n=",len(yt),"classes present",sorted(set(yt)))
    for m in ["sens_macro","accuracy","f1_macro"]:
        print("   ",m, [round(x,4) for x in st.bootstrap_ci(yt,yp,st.METRICS[m],2000,42)])
# check hiba re-run HAM preds == winner preds
for a,b in [("swin_tiny_sweep_t06_les_cwnone_hiba_predictions.json","swin_tiny_sweep_t06_les_cwnone_predictions.json"),
            ("convnext_tiny_sweep_t02_les_cwnone_hiba_predictions.json","convnext_tiny_sweep_t02_les_cwnone_predictions.json")]:
    A=json.load(open(R+a)); B=json.load(open(R+b))
    pa=dict(zip(A["image_ids"],A["y_pred"])); pb=dict(zip(B["image_ids"],B["y_pred"]))
    print("same HAM preds", a[:30], sum(pa[i]==pb[i] for i in pb), "/", len(pb))
# 8b
S=json.load(open(R+"swin_tiny_sweep_t06_les_cwnone_predictions.json"))
C=json.load(open(R+"convnext_tiny_sweep_t02_les_cwnone_predictions.json"))
ids=S["image_ids"]; posC={i:k for k,i in enumerate(C["image_ids"])}
yt=np.array(S["y_true"]); pa=np.array(S["y_pred"]); pb=np.array(C["y_pred"])[[posC[i] for i in ids]]
assert (np.array(C["y_true"])[[posC[i] for i in ids]]==yt).all()
meta=pd.read_csv("data/raw/HAM10000/HAM10000_metadata").set_index("image_id")
les=meta.loc[ids,"lesion_id"].values
print("8b n_img",len(ids),"n_les",len(set(les)))
for m in ["f1_macro","sens_macro","accuracy"]:
    fn=st.METRICS[m]
    print(" image-level",m,[round(x,4) for x in st.paired_bootstrap_diff(yt,pa,pb,fn,2000,42)])
    # lesion block bootstrap
    ul=np.unique(les); groups=[np.where(les==l)[0] for l in ul]
    rng=np.random.default_rng(42); diffs=np.empty(2000)
    for b in range(2000):
        pick=rng.integers(0,len(ul),len(ul))
        idx=np.concatenate([groups[k] for k in pick])
        diffs[b]=fn(yt[idx],pa[idx])-fn(yt[idx],pb[idx])
    lo,hi=np.percentile(diffs,[2.5,97.5]); p=2*min((diffs<=0).mean(),(diffs>=0).mean())
    print(" lesion-block",m,round(fn(yt,pa)-fn(yt,pb),4),round(lo,4),round(hi,4),round(min(p,1),4))
# 8c Holm
d=json.load(open(R+"statistical_tests_les.json"))
def holm(ps,alpha=0.05):
    items=sorted(ps.items(), key=lambda kv: kv[1]); m=len(items); rej={}; stop=False
    for k,(name,p) in enumerate(items):
        if not stop and p <= alpha/(m-k): rej[name]=True
        else: stop=True; rej[name]=False
    return rej
for test,key in [("mcnemar","p_value"),("wilcoxon_perclass","p_value")]:
    ps={k:v[key] for k,v in d[test].items()}
    raw={k:p<0.05 for k,p in ps.items()}; h=holm(ps)
    print("8c",test,"n",len(ps),"raw sig",sum(raw.values()),"holm sig",sum(h.values()))
    for k in ps:
        if raw[k]!=h[k]: print("   cambia:",k,ps[k])
    for k,p in sorted(ps.items(), key=lambda kv: kv[1]): print("     ",k,f"{p:.3g}",raw[k],h[k])
