"""Contraprovas originais, isoladas: não importa nem altera código do Stoikus.

Executar: python3 contraprovas_matematicas.py
Somente biblioteca padrão; JSON em stdout; não escreve arquivos ou acessa rede.
Não reproduz MQL5/OpenCL nem valida estratégia financeira.
"""
import json
import math
import statistics


def pearson(x, y):
    dx = [v - statistics.mean(x) for v in x]
    dy = [v - statistics.mean(y) for v in y]
    return sum(a*b for a, b in zip(dx, dy)) / math.sqrt(
        sum(a*a for a in dx) * sum(b*b for b in dy))


def main():
    # NN335: comutatividade da soma não torna uma camada densa invariante
    # à permutação SOMENTE das entradas, mantendo pesos diferentes fixos.
    weights, x, permuted = [1, 3], [2, 5], [5, 2]
    dense = sum(a*b for a, b in zip(weights, x))
    dense_permuted = sum(a*b for a, b in zip(weights, permuted))
    assert dense == 17 and dense_permuted == 11 and dense != dense_permuted
    # Controle: permutar simultaneamente pares peso/entrada conserva a soma.
    assert dense == sum(a*b for a, b in zip(weights[::-1], permuted))

    # NN93: correlação linear nula não estabelece independência.
    xs = [-2, -1, 0, 1, 2]
    ys = [v*v for v in xs]
    correlation = pearson(xs, ys)
    assert abs(correlation) < 1e-15
    assert all(b == a*a for a, b in zip(xs, ys))

    # NN225: ajustar escala com futuro muda a representação do treino.
    train, future = [1, 2, 3], [100]
    train_scale, global_scale = max(train), max(train + future)
    only_past = [v/train_scale for v in train]
    leaked = [v/global_scale for v in train]
    assert only_past != leaked and only_past[-1] == 1 and leaked[-1] == .03

    # Gradiente de (w*x-y)^2: controle correto e expressão defeituosa.
    w, feature, target, epsilon = .4, 2., 1., 1e-6
    loss = lambda z: (z*feature-target)**2
    numeric = (loss(w+epsilon)-loss(w-epsilon))/(2*epsilon)
    analytic = 2*(w*feature-target)*feature
    wrong = 2*(w*feature-target)  # omite regra da cadeia
    assert math.isclose(numeric, analytic, rel_tol=1e-7, abs_tol=1e-9)
    assert not math.isclose(numeric, wrong, rel_tol=1e-7, abs_tol=1e-9)
    print(json.dumps({
        'status': 'PASS_LOCAL_MATH_ONLY', 'stdlib_only': True,
        'dense_fixed_weights': [dense, dense_permuted],
        'pearson_zero_but_deterministic_dependence': correlation,
        'normalization_train_only': only_past, 'normalization_with_future': leaked,
        'gradient_numeric': numeric, 'gradient_analytic': analytic,
        'defective_gradient_rejected': wrong,
        'MQL5_compilation': 'NOT_RUN', 'MT5_runtime': 'NOT_RUN',
        'neural_book_reproduction': 'NOT_RUN', 'financial_validation': 'NOT_RUN'
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
