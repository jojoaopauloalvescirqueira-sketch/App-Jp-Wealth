/* Synthetic scenario field only: no financial state, storage, clock or randomness. */
(function (global) {
  'use strict';
  var ns = global.JPWCapitalCurrents = global.JPWCapitalCurrents || {};
  var DT = 1 / 60;
  var DEFAULTS = Object.freeze({ u: 0.4, tau: 1, kappa: 2, depth: 1, profile: 'uniform' });
  function finite(value, name, min, max) {
    if (typeof value !== 'number' || !Number.isFinite(value) || value < min || value > max) throw new RangeError('Invalid ' + name);
    return value;
  }
  function validateState(s) {
    if (!s || typeof s !== 'object') throw new TypeError('State required');
    finite(s.q, 'q', -1, 1); finite(s.p, 'p', -Infinity, Infinity); finite(s.t, 't', 0, Infinity);
  }
  function validateParams(p) {
    if (!p || typeof p !== 'object') throw new TypeError('Parameters required');
    finite(p.u, 'u', -1, 1); finite(p.tau, 'tau', Number.MIN_VALUE, Infinity); finite(p.kappa, 'kappa', Number.MIN_VALUE, Infinity);
    if ([0.5, 1, 2].indexOf(p.depth) < 0) throw new RangeError('Invalid depth');
    if (p.profile !== 'uniform' && p.profile !== 'band') throw new RangeError('Invalid profile');
  }
  function depthAt(price, p) {
    var z = (price - 1) / 0.8;
    return p.depth * (p.profile === 'band' ? 1 - 0.6 * Math.exp(-z * z) : 1);
  }
  function copy(s) { return { q: s.q, p: s.p, t: s.t }; }
  function fieldAt(s, p) {
    validateState(s); validateParams(p);
    var depth = depthAt(s.p, p);
    var dq = (p.u - s.q) / p.tau, dp = p.kappa * s.q / depth;
    finite(dq, 'pressure derivative', -Infinity, Infinity); finite(dp, 'price derivative', -Infinity, Infinity);
    return { dq: dq, dp: dp, depth: depth };
  }
  function advance(s, p, dt) {
    validateState(s); validateParams(p);
    dt = dt === undefined ? DT : finite(dt, 'dt', 0, 1);
    if (dt === 0) return copy(s);
    function qAt(offset) { return p.u + (s.q - p.u) * Math.exp(-offset / p.tau); }
    function velocity(price, offset) { return p.kappa * qAt(offset) / depthAt(price, p); }
    // Exact pressure at each RK4 stage; only the price coordinate needs integration.
    var k1 = velocity(s.p, 0);
    var k2 = velocity(s.p + dt * k1 / 2, dt / 2);
    var k3 = velocity(s.p + dt * k2 / 2, dt / 2);
    var k4 = velocity(s.p + dt * k3, dt);
    var result = { q: qAt(dt), p: s.p + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6, t: s.t + dt };
    validateState(result); return result;
  }
  function inside(s) { return s.q >= -1 && s.q <= 1 && s.p >= -6 && s.p <= 6; }
  function trace(s, p, options) {
    validateState(s); validateParams(p);
    options = options === undefined ? {} : options;
    if (!options || typeof options !== 'object') throw new TypeError('Trace options required');
    var steps = options.steps === undefined ? 240 : finite(options.steps, 'steps', 0, 10000);
    if (!Number.isInteger(steps)) throw new RangeError('Integer steps required');
    var dt = options.dt === undefined ? DT : finite(options.dt, 'dt', 0, 1);
    var result = [], current = copy(s);
    if (!inside(current)) return result;
    result.push(current);
    for (var i = 0; i < steps; i++) {
      var next = advance(current, p, dt);
      if (!inside(next)) break;
      result.push(next); current = next;
    }
    return result;
  }
  ns.engine = Object.freeze({ DEFAULTS: DEFAULTS, DT: DT, fieldAt: fieldAt, advance: advance, trace: trace });
})(window);
