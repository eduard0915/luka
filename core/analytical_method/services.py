"""Servicios de lógica de negocio para la construcción de ecuaciones de cálculo.

Contiene la construcción de ecuaciones LaTeX a partir de relaciones de cálculo
(AnalyticalMethodCalculateRelation), compartida por las vistas de detalle de
métodos analíticos y de productos.
"""


def _build_leaf_latex(cr):
    """Construye el LaTeX de un término hoja (relación, relación-add, volumen, factor o muestra)."""
    parts_rel = []
    if cr.analytical_method_calculate:
        term = f"\\text{{{cr.analytical_method_calculate.calculate_description}}}"
        if cr.analytical_method_calculate.unit_measure_calculate:
            term += f" \\text{{ ({cr.analytical_method_calculate.unit_measure_calculate})}}"
        parts_rel.append(term)
    if cr.calculate_relation_related:
        term = f"\\text{{{cr.calculate_relation_related.calculate_description_relation}}}"
        if cr.calculate_relation_related.unit_measure_calculate:
            term += f" \\text{{ ({cr.calculate_relation_related.unit_measure_calculate})}}"
        parts_rel.append(term)
    if cr.volumen_std:
        if cr.subtract_blank:
            parts_rel.append(f"\\left({cr.volumen_std} - \\text{{Blanco}}\\right)")
        else:
            parts_rel.append(f"\\text{{{cr.volumen_std}}}")
    if cr.factor:
        parts_rel.append(str(cr.factor))
    if cr.sample_quantity:
        parts_rel.append(f"\\text{{{cr.sample_quantity}}}")
    return " \\times ".join(parts_rel)


def _combine_terms(pairs):
    """Combina una lista de pares (operation, latex) aplicando sumas y restas con paréntesis.

    Un término con operation 'add' o 'subtract' se agrupa con el término anterior
    en un paréntesis; el resto se encadena multiplicativamente.
    """
    chain = []
    for operation, latex in pairs:
        if operation in ('add', 'subtract') and chain:
            prev = chain.pop()
            symbol = '+' if operation == 'add' else '-'
            chain.append(f"\\left({prev} {symbol} {latex}\\right)")
        else:
            chain.append(latex)
    return chain


def _term_latex(cr, children_map):
    """Retorna el LaTeX de un término; si tiene hijos, renderiza el grupo entre paréntesis."""
    if children_map.get(cr.id):
        inner = _build_group_latex(children_map[cr.id], children_map)
        return f"\\left({inner}\\right)" if inner else ""
    return _build_leaf_latex(cr)


def _build_group_latex(terms, children_map):
    """Combina términos hermanos (mismo padre) respetando operation y position.

    Los términos con position 'Denominador' u operation 'divide' van al denominador;
    los de operation 'add'/'subtract' se agrupan con el término anterior.
    """
    num_pairs = []
    den_pairs = []
    for cr in terms:
        latex = _term_latex(cr, children_map)
        if not latex:
            continue
        if cr.operation == 'divide':
            den_pairs.append((None, latex))
        elif cr.position == 'Denominador':
            den_pairs.append((cr.operation, latex))
        else:
            num_pairs.append((cr.operation, latex))
    str_num = " \\times ".join(_combine_terms(num_pairs)) if num_pairs else "1"
    str_den = " \\times ".join(_combine_terms(den_pairs))
    if str_den:
        return f"\\frac{{{str_num}}}{{{str_den}}}"
    return str_num


def _build_relation_equation(relations):
    """Construye la ecuación LaTeX a partir de un conjunto de relaciones de cálculo.

    Soporta operaciones (+, −, ×, ÷) y sub-expresiones anidadas mediante los
    campos operation y parent de cada relación. Las relaciones sin operation ni
    parent generan la misma ecuación multiplicativa de siempre.

    Retorna None si no existe una descripción de cálculo entre las relaciones.
    """
    # Orden cronológico ascendente: la operación de cada término (+/−) se aplica
    # sobre el término creado inmediatamente antes dentro de su grupo. Para las
    # ecuaciones planas (solo × y ÷) el orden es matemáticamente equivalente.
    relations = sorted(list(relations), key=lambda cr: cr.date_creation)
    relation_ids = {cr.id for cr in relations}
    children_map = {}
    roots = []
    rel_desc = ""
    rel_unit = ""

    for cr in relations:
        if cr.calculate_description_relation:
            rel_desc = cr.calculate_description_relation
            rel_unit = cr.unit_measure_calculate
        if cr.parent_id and cr.parent_id in relation_ids:
            children_map.setdefault(cr.parent_id, []).append(cr)
        else:
            roots.append(cr)

    if not rel_desc:
        return None

    num_pairs = []
    den_pairs = []
    gen_terms_rel = []
    for cr in roots:
        latex = _term_latex(cr, children_map)
        if not latex:
            continue
        if cr.operation == 'divide':
            den_pairs.append((None, latex))
        elif cr.position == 'Numerador':
            num_pairs.append((cr.operation, latex))
        elif cr.position == 'Denominador':
            den_pairs.append((cr.operation, latex))
        elif cr.position == 'General':
            gen_terms_rel.append(latex)

    str_num_rel = " \\times ".join(_combine_terms(num_pairs)) if num_pairs else "1"
    str_den_rel = " \\times ".join(_combine_terms(den_pairs))
    str_gen_rel = f" \\times {' \\times '.join(gen_terms_rel)}" if gen_terms_rel else ""

    label_rel = f"\\text{{{rel_desc}}}"
    if rel_unit:
        label_rel += f" \\text{{ ({rel_unit})}}"
    if str_den_rel:
        return f"{label_rel} = \\frac{{{str_num_rel}}}{{{str_den_rel}}}{str_gen_rel}"
    return f"{label_rel} = {str_num_rel}{str_gen_rel}"
