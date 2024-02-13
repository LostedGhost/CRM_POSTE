def generate_code(prefixe_table, lenght_table):
    code_final = prefixe_table + '{:05d}'.format(lenght_table)
    return code_final.upper()
    