wpl = tuple(i for i in range(14, 30))
wph = tuple(i for i in range(30, 50))
wps = tuple(i for i in range(90, 120))

def rl(row):
    if row == 0:
        return 'rs(2)'
    return wpl[row]

def rh(row):
    if row == 3:
        return 'rl(0)'
    return wph[row]

def rs(row):
    return wps[row]

eval_locals = {
    'l': rl,
    'h': rh,
    's': rs,
    'rl': rl,
    'rh': rh,
    'rs': rs,
}

def evalExpression(value):
    result = eval(str(value), {}, eval_locals)
    if isinstance(result, (int, float, bool)):
        return result
    else:
        return evalExpression(result)
    
res = evalExpression('rh(3)')
print(res)