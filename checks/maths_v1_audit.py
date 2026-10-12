"""Numerical audit of maths-v1.md; no training or external interaction.

Run with Python 3 using only the standard library.
"""

import itertools
import json
import math


STATES = list(itertools.product(range(4), repeat=2))
TRACES = ((0.12, 0.32, 0.21), (0.25, 0.10, 0.45))


def close(x, y, tol=1e-9):
    assert abs(x - y) < tol, (x, y, tol)


def normalize(values):
    total = sum(values)
    assert total > 0
    return [v / total for v in values]


def expectation(p, values):
    return sum(a * b for a, b in zip(p, values))


def features(state, phase, action=1):
    """Equation (8), all listed features for two nodes and two actions."""
    values, jacobian = [], []

    def add(value, i=None, j=None):
        derivative = [0.0, 0.0]
        if i is not None and i != j:
            difference = phase[i] - phase[j]
            derivative[i] = -0.5 * math.sin(difference) * value
            derivative[j] = -derivative[i]
            value *= (1 + math.cos(difference)) / 2
        values.append(value)
        jacobian.append(derivative)

    for b in range(2):
        active = float(action == b)
        for i in range(2):
            for k in range(1, 4):
                add(active * (state[i] == k))
        for j in range(2):
            for i in range(2):
                for kp in range(1, 4):
                    for k in range(1, 4):
                        add(active * TRACES[j][kp - 1] * (state[i] == k), j, i)
        for k in range(1, 4):
            for kp in range(1, 4):
                add(active * (state[0] == k) * (state[1] == kp), 0, 1)
    return values, jacobian


def predict(weights, phase):
    rows = [features(state, phase) for state in STATES]
    log_scores = [
        math.log(1 + 0.1 * sum(state)) + sum(w * x for w, x in zip(weights, row[0]))
        for state, row in zip(STATES, rows)
    ]
    offset = max(log_scores)
    return normalize([math.exp(h - offset) for h in log_scores]), rows


def log_evidence(weights, phase, likelihood):
    p, _ = predict(weights, phase)
    return math.log(expectation(p, likelihood))


def score_audit(weights, phase, likelihood):
    p, rows = predict(weights, phase)
    q = normalize([a * b for a, b in zip(p, likelihood)])
    close(sum(p), 1)
    close(sum(q), 1)
    residual = [a - b for a, b in zip(q, p)]
    score = [
        sum(d * row[0][j] for d, row in zip(residual, rows))
        for j in range(len(weights))
    ]
    phase_score = [
        sum(d * sum(w * jac[i] for w, jac in zip(weights, row[1]))
            for d, row in zip(residual, rows))
        for i in range(2)
    ]
    epsilon = 1e-6
    weight_errors, phase_errors = [], []
    for j, analytic in enumerate(score):
        plus, minus = weights.copy(), weights.copy()
        plus[j] += epsilon
        minus[j] -= epsilon
        numerical = (log_evidence(plus, phase, likelihood)
                     - log_evidence(minus, phase, likelihood)) / (2 * epsilon)
        weight_errors.append(abs(analytic - numerical))
    for i, analytic in enumerate(phase_score):
        plus, minus = phase.copy(), phase.copy()
        plus[i] += epsilon
        minus[i] -= epsilon
        numerical = (log_evidence(weights, plus, likelihood)
                     - log_evidence(weights, minus, likelihood)) / (2 * epsilon)
        phase_errors.append(abs(analytic - numerical))
    assert max(weight_errors + phase_errors) < 1e-7
    return max(weight_errors), max(phase_errors)


def retained_update(value, rho, eta, gradient, gate, bound=8):
    return max(-bound, min(bound, value + gate * ((rho - 1) * value + eta * gradient)))


def main():
    phase = [0.2, 1.1]
    size = len(features(STATES[0], phase)[0])
    weights = [0.35 * math.sin(i + 0.3) for i in range(size)]
    noisy = [0.1 + 0.8 * (state[0] == 1) for state in STATES]
    full = [float(state == (1, 2)) for state in STATES]
    noisy_errors = score_audit(weights, phase, noisy)
    full_errors = score_audit(weights, phase, full)
    missing_errors = score_audit(weights, phase, [1.0] * len(STATES))

    # Bayes and the closed form of anchored settling, not evidence repetition.
    target = normalize([0.5 * 0.8, 0.5 * 0.2])
    close(target[0], 0.8)
    previous_kl = float('inf')
    for time in (0, 0.1, 1, 2, 5, 10, 20):
        a = math.exp(-time)
        q = normalize([0.5 ** a * v ** (1 - a) for v in target])
        kl = sum(x * math.log(x / y) for x, y in zip(q, target))
        assert kl <= previous_kl + 1e-12
        previous_kl = kl
    close(q[0], 0.8, 1e-8)
    wrong_repetition = normalize([0.8 ** 2, 0.2 ** 2])[0]
    assert abs(q[0] - wrong_repetition) > 0.14

    # Directly check the KL dissipation identity in (12).
    q0 = [0.35, 0.65]
    logs = [math.log(a / b) for a, b in zip(q0, target)]
    avg = expectation(q0, logs)
    dq = [-q0[i] * (logs[i] - avg) for i in range(2)]
    close(sum(dq), 0)
    close(sum(d * (l + 1) for d, l in zip(dq, logs)),
          -sum(q0[i] * (logs[i] - avg) ** 2 for i in range(2)))

    # Trace range, and a fully loaded cue followed by two blank ticks.
    for old, beta, lam, alpha, marginal in itertools.product(
            (0, 0.2, 0.7, 1), (0, 0.4, 1), (0, 0.8, 0.99), (0, 0.6, 1), (0, 0.3, 1)):
        new = (1 - beta) * lam * old + beta * alpha * marginal
        assert 0 <= new <= 1
    close(0.8 ** 2, 0.64)

    # Geometric no-feedback retention, frozen gates, and projection.
    fast, slow = 0.8, -0.3
    for _ in range(12):
        fast = retained_update(fast, 0.95, 0.2, 0, 1)
        slow = retained_update(slow, 0.999, 0.02, 0, 1)
    close(fast, 0.8 * 0.95 ** 12)
    close(slow, -0.3 * 0.999 ** 12)
    close(retained_update(0.8, 0.1, 0.2, 1, 0), 0.8)
    close(retained_update(7.9, 1, 1, 1, 1), 8)

    fast = retained_update(0, 0.95, 0.2, 0.5, 1)
    slow = retained_update(0, 0.999, 0.02, 0.5, 1)
    after = 1 / (1 + math.exp(-(fast + slow)))
    close(fast, 0.1)
    close(slow, 0.01)
    close(after, 0.5274723043445937)

    # Gauge invariance of probabilities and the pair potential.
    p, rows = predict(weights, phase)
    rotated, _ = predict(weights, [x + 0.72 for x in phase])
    gauge_error = max(abs(x - y) for x, y in zip(p, rotated))
    assert gauge_error < 1e-12
    potential = lambda ph: -0.1 * math.cos(ph[0] - ph[1] - 0.4)
    close(potential(phase), potential([x + 0.72 for x in phase]))
    epsilon = 1e-6
    expected_dv = 0.1 * math.sin(phase[0] - phase[1] - 0.4)
    numerical_dv = (potential([phase[0] + epsilon, phase[1]])
                    - potential([phase[0] - epsilon, phase[1]])) / (2 * epsilon)
    close(expected_dv, numerical_dv, 1e-8)

    # Pair coupling can encode dependence missed by a product of marginals.
    joint = normalize([math.exp(2 * (s[0] == 1 and s[1] == 1)) for s in STATES])
    m0 = sum(v for v, s in zip(joint, STATES) if s[0] == 1)
    m1 = sum(v for v, s in zip(joint, STATES) if s[1] == 1)
    both = joint[STATES.index((1, 1))]
    covariance = both - m0 * m1
    assert covariance > 0.05

    # Steering: exact log-odds effect of an individual relation edit.
    s, v = STATES.index((1, 1)), STATES.index((0, 0))
    j = next(j for j in range(size) if rows[s][0][j] != rows[v][0][j])
    edited = weights.copy()
    edited[j] += 0.4
    p2, _ = predict(edited, phase)
    observed = math.log(p2[s] / p2[v]) - math.log(p[s] / p[v])
    expected = 0.4 * (rows[s][0][j] - rows[v][0][j])
    close(observed, expected)

    # Local phase stability of the isolated two-node update.
    eta, kappa = 0.05, 0.1
    step = lambda delta: delta - 2 * eta * kappa * math.sin(delta)
    jacobian = (step(epsilon) - step(-epsilon)) / (2 * epsilon)
    close(jacobian, 1 - 2 * eta * kappa, 1e-9)
    assert abs(jacobian) < 1

    print(json.dumps({
        'status': 'passed',
        'scope': 'mathematical identities only; learning experiment not run',
        'joint_configurations': len(STATES),
        'feature_parameters': size,
        'max_gradient_errors': {
            'noisy_observation': noisy_errors,
            'fully_observed': full_errors,
            'missing_observation': missing_errors,
        },
        'common_phase_rotation_error': gauge_error,
        'anchored_posterior': q,
        'worked_next_prediction': after,
        'pair_covariance': covariance,
        'isolated_phase_local_jacobian': jacobian,
    }, indent=2))


if __name__ == '__main__':
    main()
