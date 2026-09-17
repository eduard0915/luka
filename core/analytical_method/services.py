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
    if cr.volumen_std or cr.standard_base:
        if cr.subtract_blank:
            vol_str = f"\\left({cr.volumen_std or 'mL Gastados'} - \\text{{Blanco}}\\right)"
        else:
            vol_str = f"\\text{{{cr.volumen_std}}}" if cr.volumen_std else ""
        if cr.standard_base:
            vol_str += f" \\times \\text{{[{cr.standard_base}]}}"
        if vol_str:
            parts_rel.append(vol_str)
    if cr.factor:
        parts_rel.append(str(cr.factor))
    if cr.variable:
        parts_rel.append(f"\\text{{{cr.variable}}}")
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


def _format_latex_number(value):
    """Formatea un número para LaTeX eliminando el '.0' de los enteros."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value) if value not in (None, '') else ''
    if number == int(number):
        return str(int(number))
    return str(number)


class GravimetryTermUnit:
    """Unidad de término gravimétrico compatible con los constructores de ecuación.

    Expone los atributos que consumen ``_build_gravimetry_equation`` y
    ``evaluate_gravimetry_terms`` a partir de una fila de AnalyticalMethodCalculate
    o de un GravimetryTerm.
    """
    def __init__(self, term_type, constant_value=None, operation=None,
                 consecutive=None, date_creation=None):
        self.term_type = term_type
        self.constant_value = constant_value
        self.operation = operation
        self.consecutive = consecutive
        self.date_creation = date_creation


def build_gravimetry_data(calcules):
    """Construye el LaTeX del cálculo básico y las unidades de término.

    A partir de las filas de ``AnalyticalMethodCalculate`` del método:
    - El cálculo básico se arma con Peso Bruto, Peso Filtro, Peso de Muestra y
      los factores multiplicadores (filas sin ``term_type``).
    - Los términos constantes son las filas con ``term_type='constant'`` (valor
      en ``factor``).
    - La operación del bloque básico se toma de sus filas (puede ser nula).

    Retorna ``(basic_latex, term_units)``.
    """
    calcules = list(calcules)
    basic_rows = [c for c in calcules
                  if c.gross_weight or c.weight_of_filter or c.sample_quantity]
    gross = next((c for c in basic_rows if c.gross_weight), None)
    wof = next((c for c in basic_rows if c.weight_of_filter), None)
    sq = next((c for c in basic_rows if c.sample_quantity), None)

    basic_latex = ''
    term_units = []

    if gross and wof and sq:
        factors_num = [str(c.factor) for c in calcules
                       if c.factor and c.position == 'Numerador' and not c.term_type]
        factors_den = [str(c.factor) for c in calcules
                       if c.factor and c.position == 'Denominador' and not c.term_type]

        numerator = f"\\left(\\text{{{gross.gross_weight}}}\\right) - \\text{{{wof.weight_of_filter}}}"
        denominator = f"\\text{{{sq.sample_quantity}}}"
        if factors_den:
            denominator += f" \\cdot {' \\cdot '.join(factors_den)}"
        multiplier = f" \\times {' \\cdot '.join(factors_num)}" if factors_num else ""

        basic_latex = f"\\frac{{{numerator}}}{{{denominator}}}{multiplier}"

        operation = next((c.operation for c in basic_rows if c.operation), None)
        consecutive = next((c.consecutive for c in basic_rows if c.consecutive is not None), None)
        date_creation = next((c.date_creation for c in basic_rows if c.date_creation), None)
        term_units.append(GravimetryTermUnit(
            'basic', None, operation, consecutive, date_creation))

    for c in calcules:
        if c.term_type == 'constant' and c.factor is not None:
            term_units.append(GravimetryTermUnit(
                'constant', c.factor, c.operation, c.consecutive, c.date_creation))

    return basic_latex, term_units


def evaluate_gravimetry_terms(basic_value, terms):
    """Evalúa numéricamente la ecuación gravimétrica a partir de sus términos.

    El primer término se toma como base y no aplica su operación; los siguientes
    se combinan con el acumulado mediante suma (+), resta (−), multiplicación (×)
    o división (÷). Un término de tipo 'basic' usa ``basic_value``; los de tipo
    'constant' su valor almacenado.

    Retorna ``None`` cuando no existen términos evaluables. Una división por cero
    deja el acumulado en cero.
    """
    ordered = sorted(terms, key=lambda term: (term.consecutive or 0, term.date_creation))
    values = []
    for term in ordered:
        value = basic_value if term.term_type == 'basic' else term.constant_value
        if value is None:
            continue
        values.append((term.operation, float(value)))

    if not values:
        return None

    result = values[0][1]
    for operation, value in values[1:]:
        if operation == 'add':
            result += value
        elif operation == 'subtract':
            result -= value
        elif operation == 'divide':
            result = result / value if value else 0
        else:
            result *= value
    return result


def _build_gravimetry_equation(basic_latex, terms):
    """Construye el lado derecho de la ecuación gravimétrica a partir de sus términos.

    El primer término se toma como base y no aplica su operación; los términos
    siguientes se combinan con el acumulado mediante suma (+), resta (−),
    multiplicación (×) o división (÷), en el mismo orden (izquierda a derecha)
    con el que ``evaluate_gravimetry_terms`` los evalúa numéricamente. Un término
    de tipo 'basic' usa el LaTeX del cálculo básico de gravimetría; los de tipo
    'constant' su valor numérico.

    Cada término se muestra separado: los términos del cálculo básico se agrupan
    entre paréntesis (incluido cuando son el primer término de una ecuación con
    varios términos), y cuando el acumulado es una suma o resta y se multiplica
    por el siguiente término también se agrupa.

    Retorna una cadena vacía cuando no existen términos válidos.
    """
    ordered = sorted(terms, key=lambda term: (term.consecutive or 0, term.date_creation))
    pieces = []
    for term in ordered:
        if term.term_type == 'basic':
            latex = basic_latex
        else:
            latex = _format_latex_number(term.constant_value)
        if not latex:
            continue
        pieces.append((term.operation, latex, term.term_type == 'basic'))

    if not pieces:
        return ''

    expression = pieces[0][1]
    is_additive = False
    if len(pieces) > 1 and pieces[0][2]:
        expression = f'\\left({expression}\\right)'
    for operation, latex, is_basic in pieces[1:]:
        if is_basic:
            latex = f'\\left({latex}\\right)'
        if operation == 'add':
            expression = f'{expression} + {latex}'
            is_additive = True
        elif operation == 'subtract':
            expression = f'{expression} - {latex}'
            is_additive = True
        elif operation == 'divide':
            expression = f'\\frac{{{expression}}}{{{latex}}}'
            is_additive = False
        else:
            if is_additive:
                expression = f'\\left({expression}\\right)'
            expression = f'{expression} \\times {latex}'
            is_additive = False
    return expression
