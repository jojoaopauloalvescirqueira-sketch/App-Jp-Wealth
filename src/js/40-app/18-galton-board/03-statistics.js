// ============ GALTON BOARD — ESTATISTICA DESCRITIVA ============
// Os momentos descrevem o conjunto observado completo (divisor N). A curva
// binomial e referencia combinatoria p=0,5; nunca e ajustada aos dados.
(function (global) {
  "use strict";

  var JPWGalton = global.JPWGalton || (global.JPWGalton = {});

  function checkedHistogram(histogram) {
    if (!Array.isArray(histogram)) throw new TypeError("histogram deve ser um array");
    return histogram.map(function (count, index) {
      var value = Number(count);
      if (!Number.isFinite(value) || value < 0 || Math.floor(value) !== value) {
        throw new RangeError("histogram[" + index + "] deve ser um inteiro nao negativo");
      }
      return value;
    });
  }

  function describeHistogram(histogram) {
    var counts = checkedHistogram(histogram);
    var n = counts.reduce(function (sum, count) { return sum + count; }, 0);
    var empty = {
      n: 0,
      mean: null,
      variance: null,
      variancePopulation: null,
      stdDev: null,
      standardDeviation: null,
      mode: null,
      modes: [],
      skewness: null,
      kurtosis: null,
      kurtosisExcess: null,
      kurtosisRaw: null
    };
    if (n === 0) return empty;

    var weightedSum = 0;
    var maxCount = -1;
    counts.forEach(function (count, index) {
      weightedSum += index * count;
      if (count > maxCount) maxCount = count;
    });
    var mean = weightedSum / n;
    var moment2 = 0;
    var moment3 = 0;
    var moment4 = 0;
    counts.forEach(function (count, index) {
      if (count === 0) return;
      var delta = index - mean;
      var delta2 = delta * delta;
      moment2 += count * delta2;
      moment3 += count * delta2 * delta;
      moment4 += count * delta2 * delta2;
    });

    var variance = moment2 / n;
    var stdDev = Math.sqrt(variance);
    var modes = [];
    counts.forEach(function (count, index) {
      if (count === maxCount) modes.push(index);
    });
    var hasDispersion = stdDev > Number.EPSILON;
    var skewness = hasDispersion ? (moment3 / n) / Math.pow(stdDev, 3) : null;
    var kurtosisRaw = hasDispersion ? (moment4 / n) / (variance * variance) : null;
    var kurtosisExcess = kurtosisRaw === null ? null : kurtosisRaw - 3;

    return {
      n: n,
      mean: mean,
      variance: variance,
      variancePopulation: variance,
      stdDev: stdDev,
      standardDeviation: stdDev,
      mode: modes.length ? modes[0] : null,
      modes: modes,
      skewness: skewness,
      kurtosis: kurtosisExcess,
      kurtosisExcess: kurtosisExcess,
      kurtosisRaw: kurtosisRaw
    };
  }

  function checkedRows(rows) {
    var value = Number(rows);
    if (!Number.isFinite(value) || value < 0 || Math.floor(value) !== value || value > 1000) {
      throw new RangeError("rows deve ser inteiro entre 0 e 1000");
    }
    return value;
  }

  function checkedProbability(probability) {
    var value = probability === undefined ? 0.5 : Number(probability);
    if (!Number.isFinite(value) || value < 0 || value > 1) {
      throw new RangeError("probability deve estar entre 0 e 1");
    }
    return value;
  }

  function binomialCoefficient(rows, successes) {
    var n = checkedRows(rows);
    var k = Number(successes);
    if (!Number.isFinite(k) || Math.floor(k) !== k || k < 0 || k > n) return 0;
    k = Math.min(k, n - k);
    var result = 1;
    var index;
    for (index = 1; index <= k; index += 1) {
      result = result * (n - k + index) / index;
    }
    return result;
  }

  function binomialDistribution(rows, probability) {
    var n = checkedRows(rows);
    var p = checkedProbability(probability);
    var distribution = new Array(n + 1).fill(0);
    var index;

    if (p === 0) {
      distribution[0] = 1;
      return distribution;
    }
    if (p === 1) {
      distribution[n] = 1;
      return distribution;
    }

    // Recorrencia evita calcular fatoriais e permanece estavel no intervalo
    // operacional (6-18 linhas; suporta ate 1000 para testes isolados).
    distribution[0] = Math.pow(1 - p, n);
    for (index = 0; index < n; index += 1) {
      distribution[index + 1] = distribution[index] * (n - index) / (index + 1) * p / (1 - p);
    }
    var total = distribution.reduce(function (sum, value) { return sum + value; }, 0);
    if (total > 0) {
      distribution = distribution.map(function (value) { return value / total; });
    }
    return distribution;
  }

  function binomialReference(rows, sampleSize, probability) {
    var n = checkedRows(rows);
    var total = Number(sampleSize);
    if (!Number.isFinite(total) || total < 0) throw new RangeError("sampleSize deve ser nao negativo");
    var p = checkedProbability(probability);
    var probabilities = binomialDistribution(n, p);
    return {
      rows: n,
      probability: p,
      sampleSize: total,
      probabilities: probabilities,
      expectedCounts: probabilities.map(function (value) { return value * total; })
    };
  }

  function compareToBinomial(histogram, probability) {
    var counts = checkedHistogram(histogram);
    var total = counts.reduce(function (sum, value) { return sum + value; }, 0);
    var reference = binomialReference(Math.max(0, counts.length - 1), total, probability);
    if (total === 0) {
      return {
        sampleSize: 0,
        totalVariation: null,
        rmse: null,
        maxAbsoluteDifference: null,
        reference: reference
      };
    }
    var squared = 0;
    var absolute = 0;
    var maximum = 0;
    counts.forEach(function (count, index) {
      var empirical = count / total;
      var delta = Math.abs(empirical - reference.probabilities[index]);
      absolute += delta;
      squared += delta * delta;
      maximum = Math.max(maximum, delta);
    });
    return {
      sampleSize: total,
      totalVariation: absolute * 0.5,
      rmse: Math.sqrt(squared / counts.length),
      maxAbsoluteDifference: maximum,
      reference: reference
    };
  }

  JPWGalton.statistics = Object.freeze({
    describeHistogram: describeHistogram,
    describe: describeHistogram,
    binomialCoefficient: binomialCoefficient,
    binomialDistribution: binomialDistribution,
    binomialReference: binomialReference,
    compareToBinomial: compareToBinomial
  });
})(typeof window !== "undefined" ? window : globalThis);
