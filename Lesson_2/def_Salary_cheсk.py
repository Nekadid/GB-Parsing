import re

salary_in = '23/ertgr-234/regtre руб.'

def Salary_check(salary_in):
    pat1 = r'^\d{1,4}'
    pat2 = r'\s.*'
    pat3 = r'(?<=-).*?(?=/)'


    if re.fullmatch(r'\bдо.*', salary_in):
        return {'top_salary': salary_in}
    if re.fullmatch(r'\bот.*', salary_in):
        return {'down_salary': salary_in}
    if re.fullmatch(r'\b\d{1,}.*',salary_in):
        return {'down_salary': f'{re.search(pat1, salary_in)[0]}{re.search(pat2, salary_in)[0]}','top_salary': f'{re.search(pat3, salary_in)[0]}{re.search(pat2, salary_in)[0]}'}

print(Salary_check(salary_in))