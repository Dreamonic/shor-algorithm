from src.connection.qi_api import get_api_session
from src.engines.qi_engine import get_engine
from src.quantum.qft import run


wanted = [1, 1, 1, 1]


def pretty_print(ol):
    result = [0] * (int(max(ol, key=int)) + 1)
    for idx, li in ol.items():
        result[int(idx)] = li
    return result


def normalize(wanted):
    return [i / sum(wanted) for i in wanted]


if __name__ == '__main__':
    print("ESTABLISHING SESSION")
    qi = get_api_session()
    print("SESSION ESTABLISHED")

    qi_engine, qi_backend = get_engine(qi)

    result_qi = run(qi_engine)

    print('\nMeasured: {0}'.format([int(q) for q in result_qi]))
    print('Probabilities {0}'.format(qi_backend.get_probabilities(result_qi)))
