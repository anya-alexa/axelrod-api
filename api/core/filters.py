from distutils.util import strtobool
import operator


def passes_boolean_filter(strategy, classifier, value):
    if isinstance(value, str):
        filter_value = strtobool(value)
    else:
        filter_value = value

    return strategy.classifier[classifier] == filter_value


def passes_operator_filter(strategy, filter, value, operator):
    if isinstance(value, str):
        filter_value = int(value)
    else:
        filter_value = value

    return operator(strategy.classifier[filter], filter_value)


def passes_filterset(strategy, filterset):
    """
    Parameters
    ----------
        strategy : a descendant class of axelrod.Player
        filterset : dictionary

    Returns
    -------
        boolean
    """
    filter_types = {
        'stochastic': ('boolean', 'stochastic'),
        'long_run_time': ('boolean', 'long_run_time'),
        'manipulates_state': ('boolean', 'stochastic'),
        'manipulates_source': ('boolean', 'stochastic'),
        'inspects_source': ('boolean', 'stochastic'),
        'min_memory_depth': ('gte', 'memory_depth'),
        'max_memory_depth': ('lte', 'memory_depth')
    }
    passes_filters = []

    for filter in filterset:
        if filter_types[filter][0] == 'boolean':
            passes_filters.append(
                passes_boolean_filter(
                    strategy, filter_types[filter][1], filterset[filter]))
        elif filter_types[filter][0] == 'gte':
            passes_filters.append(
                passes_operator_filter(
                    strategy, filter_types[filter][1], filterset[filter], operator.le))
        elif filter_types[filter][0] == 'lte':
            passes_filters.append(
                passes_operator_filter(
                    strategy, filter_types[filter][1], filterset[filter], operator.ge))

    return all(passes_filters)