"""Validate internal pre-draft architecture, not scientific merit or page quotas."""
import argparse
import json
from pathlib import Path
import jsonschema

def validate_plan(plan):
    schema=json.loads((Path(__file__).resolve().parents[1]/'references/paper_page_plan.schema.json').read_text())
    errors=[e.message for e in jsonschema.Draft202012Validator(schema).iter_errors(plan)]
    if errors: return errors
    target=plan['target_total_pages']; lo,hi=plan['target_range']
    if not 0<lo<=target<=hi<=plan['official_page_limit']:
        errors.append('Range/target must be ordered and within configured limit')
    sections=plan['section_page_budget'].values()
    if abs(sum(x['planned_pages'] for x in sections)-target)>0.05:
        errors.append('Section budgets must sum to target')
    for field,total in [('planned_figures','major_figure_plan'),('planned_tables','major_table_plan')]:
        ids=[v for s in sections for v in s[field]]
        if len(set(ids))!=len(ids) or len(ids)!=plan[total]: errors.append(f'{field}: duplicate IDs or inconsistent total')
    expected=plan['subproblem_count']>=3 or plan['model_stage_count']>=3 or plan['multiple_models'] or plan['cross_subproblem_dependency']
    if expected and not plan['framework_figure_expected'] and not plan.get('framework_waiver','').strip():
        errors.append('Complex architecture requires framework or substantive waiver')
    if plan['framework_figure_expected'] and plan.get('framework_figure_id') not in [v for s in sections for v in s['planned_figures']]:
        errors.append('Expected framework must be in visual plan')
    return errors

def page_review(pages, target=25, soft_range=(23,27), official_limit=30, official_count=None):
    if pages is None: return 'NOT_RENDERED'
    if (pages if official_count is None else official_count)>official_limit: return 'PAGE_LIMIT_VIOLATION'
    if soft_range[0]<=pages<=soft_range[1]: return 'IDEAL'
    if pages>soft_range[1]: return 'NEAR_LIMIT'
    if pages<soft_range[0]-3: return 'CONTENT_GAP_REVIEW_REQUIRED'
    return 'SHORT_BUT_ACCEPTABLE'

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('plan',type=Path); a=p.parse_args()
    errors=validate_plan(json.loads(a.plan.read_text(encoding='utf-8')))
    print(json.dumps({'status':'FAIL' if errors else 'PASS','errors':errors},ensure_ascii=False,indent=2))
    raise SystemExit(bool(errors))
