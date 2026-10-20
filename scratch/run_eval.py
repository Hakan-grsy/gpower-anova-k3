import json
from src.agent import ClinicalAnovaAgent

with open('agent_evaluation/clinical_questions_tr.json', encoding='utf-8') as f:
    questions = json.load(f)

agent = ClinicalAnovaAgent()
results = []

for q in questions:
    res = agent.consult(q['question'])
    gt = q['ground_truth']
    qid = q['id']
    spec = q['specialty']
    
    family_match = (res['test_family'] == gt['test_family'])
    k_match = (res['parameters']['num_groups'] == gt['num_groups'])
    f_match = (abs(res['parameters']['effect_size_f'] - gt['effect_size_f']) < 1e-4)
    alpha_match = (abs(res['parameters']['alpha'] - gt['alpha']) < 1e-4)
    power_match = (abs(res['parameters']['power'] - gt['power']) < 1e-4)
    n_match = (res['n_total'] == gt['expected_n_total'])
    
    params_match = (k_match and f_match and alpha_match and power_match)
    eval_item = {
        'id': qid,
        'specialty': spec,
        'family_match': family_match,
        'params_match': params_match,
        'n_match': n_match,
        'extracted_params': res['parameters'],
        'expected_n': gt['expected_n_total'],
        'calculated_n': res['n_total'],
        'actual_power': res['actual_power']
    }
    results.append(eval_item)
    print(f"Q{qid} [{spec}]: Family={family_match}, Params={params_match}, N={n_match} (Got {res['n_total']}, Exp {gt['expected_n_total']})")

with open('agent_evaluation/tool_call_logs.json', 'w', encoding='utf-8') as f:
    json.dump(agent.tool_call_logs, f, indent=2, ensure_ascii=False)

print('Tool call logs written successfully! Total tool calls:', len(agent.tool_call_logs))
