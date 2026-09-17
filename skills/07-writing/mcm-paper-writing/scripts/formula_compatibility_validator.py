"""Conservative Markdown math lint; never claims conversion or UI editability."""
import argparse
import json
import re
from pathlib import Path

COMMANDS = set('frac sqrt sum prod int sin cos tan exp ln log min max left right mathbf boldsymbol mathrm operatorname text hat bar tilde vec overline underline begin end alpha beta gamma delta epsilon varepsilon zeta eta theta vartheta iota kappa lambda mu nu xi pi rho sigma tau upsilon phi varphi chi psi omega Gamma Delta Theta Lambda Xi Pi Sigma Upsilon Phi Psi Omega le leq ge geq ne neq approx sim simeq equiv in notin subset subseteq supset supseteq times cdot div pm mp infty partial nabla ell forall exists to rightarrow mapsto ldots cdots vdots ddots lbrace rbrace langle rangle vert Vert lvert rvert lVert rVert bmod mod lim arg det sup inf limits nolimits'.split())
ENVS = {'aligned','cases','matrix','pmatrix','bmatrix','Bmatrix','vmatrix','Vmatrix'}

def strip_code(text):
    text = re.sub(r'(?ms)^\s*(`{3,}|~{3,})[^\n]*\n.*?^\s*\1\s*$', '', text)
    return re.sub(r'`[^`\n]*`', '', text)

def extract_math(text):
    text = strip_code(text)
    tokens = list(re.finditer(r'(?<!\\)\$\$|(?<!\\)\$', text))
    blocks, errors = [], []
    opening = None
    for token in tokens:
        if opening is None:
            opening = token
        elif token.group() != opening.group():
            errors.append('Mismatched inline/display delimiter')
        else:
            body = text[opening.end():token.start()]
            blocks.append(body)
            if opening.group() == '$' and (not body or body != body.strip() or '\n' in body):
                errors.append('Inline math must be nonempty with no adjacent whitespace/newline')
            opening = None
    if opening is not None:
        errors.append('Unclosed math delimiter')
    return blocks, errors

def audit_formula(text):
    source = strip_code(text)
    blocks, errors = extract_math(text)
    findings = []
    def add(code, status, message):
        findings.append(dict(code=code,status=status,message=message))
    if re.search(r'<\s*/?\s*(?:m:)?oMath', source, re.I):
        add('RAW_OMML_IN_MARKDOWN','FAIL','Raw OMML is forbidden in canonical Markdown')
    if re.search(r'!\[[^\]]*(?:公式|equation|formula)[^\]]*\]|!\[[^\]]*\]\([^)]*(?:equation|formula|[/\\]eq[_-])', source, re.I):
        add('FORMULA_AS_IMAGE','FAIL','Suspected formula image: CRITICAL pending semantic review')
    if re.search(r'\\(?:newcommand|renewcommand|def|usepackage|input|include)\b', source):
        add('UNSUPPORTED_LATEX_MACROS','FAIL','Custom macros/packages/raw TeX are not allowed without conversion evidence')
    for body in blocks:
        depth=0
        for b in re.findall(r'(?<!\\)[{}]',body):
            depth += 1 if b=='{' else -1
            if depth<0: errors.append('Unexpected closing brace')
        if depth: errors.append('Unbalanced braces')
        stack=[]
        for kind,env in re.findall(r'\\(begin|end)\{([^}]+)\}',body):
            if env not in ENVS: add('UNSUPPORTED_LATEX_MACROS','WARNING',f'Environment requires conversion test: {env}')
            if kind=='begin': stack.append(env)
            elif not stack or stack.pop()!=env: errors.append('Environment mismatch')
        if stack: errors.append('Unclosed environment')
        if len(re.findall(r'\\left\b',body)) != len(re.findall(r'\\right\b',body)):
            errors.append('Unpaired left/right delimiters')
        for command in sorted(set(re.findall(r'\\([A-Za-z]+)',body))-COMMANDS):
            add('NUMBERING_CONVERSION_TEST_REQUIRED' if command=='tag' else 'UNSUPPORTED_LATEX_MACROS','WARNING',f'Needs exact converter test: \\{command}')
    for error in sorted(set(errors)): add('FORMULA_SYNTAX_VALID','FAIL',error)
    return {'math_count':len(blocks),'findings':findings,
            'static_status':'FAIL' if any(x['status']=='FAIL' for x in findings) else 'WARNING' if findings else 'PASS',
            'word_native_equation': 'NOT_VERIFIED', 'image_semantic_review':'REQUIRED'}

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('markdown',type=Path)
    args=parser.parse_args(); result=audit_formula(args.markdown.read_text(encoding='utf-8'))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(result['static_status']=='FAIL')
