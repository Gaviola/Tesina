"""Verificaciones del Cap. 3 (2026-10-11): IC bootstrap de los VLM ajustados (verosimilitud y CoT) en HAM10000.
Ver docs/resul/verificaciones_cap03_resul_20261011.md. 100% local; correr desde Codigo/.
"""
import sys, json
sys.path.insert(0, r"C:\Users\Facu\1\Facultad\Tesina-cap03\Codigo"); sys.path.insert(0, r"C:\Users\Facu\1\Facultad\Tesina-cap03\Codigo\scripts")
import statistical_tests as st
R="outputs/results/"
for f in ["llava_med/v1/llava_med_likelihood_predictions.json","llava_med/v1/llava_med_cot_predictions.json",
          "llava_med/v2/llava_med_likelihood_finetuned_predictions.json","llava_med/v2/llava_med_cot_finetuned_predictions.json",
          "mini_vlm/v1/mini_vlm_likelihood_predictions.json","mini_vlm/v1/mini_vlm_cot_predictions.json",
          "mini_vlm/v2/mini_vlm_likelihood_finetuned_predictions.json","mini_vlm/v2/mini_vlm_cot_finetuned_predictions.json"]:
    d=json.load(open(R+f)); out=[]
    for m in ["accuracy","sens_macro"]:
        p,lo,hi=st.bootstrap_ci(d["y_true"],d["y_pred"],st.METRICS[m],2000,42); out.append(f"{m} {p:.3f} [{lo:.3f},{hi:.3f}]")
    print(f.split('/')[-1].replace('_predictions.json',''), f.split('/')[1], " | ".join(out))
