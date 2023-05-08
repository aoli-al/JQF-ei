import "date"

sum_result = from(bucket: "fuzzer")
  |> range(start: 0, stop: date.add(d: 1d, to: time(v: 0)))
  |> filter(fn: (r) => r["_measurement"] == "coverage")
  |> filter(fn: (r) => r["_field"] == "covered")
  |> filter(fn: (r) => r["experiment"] == "test1")
  |> filter(fn: (r) => r["fuzzer"] == "zest")
  |> filter(fn: (r) => r["testClassName"] == "edu.berkeley.cs.jqf.examples.closure.CompilerTest")
  |> filter(fn: (r) => r["testMethodName"] == "testWithGenerator")
  |> aggregateWindow(every: 2s, fn: count)
  |> cumulativeSum()

sum_result
  |> aggregateWindow(every: 2s, fn: mean, createEmpty: false)
  |> yield(name: "mean")

sum_result
  |> aggregateWindow(every: 2s, fn: max, createEmpty: false)
  |> yield(name: "max")

sum_result
  |> aggregateWindow(every: 2s, fn: min, createEmpty: false)
  |> yield(name: "min")

from(bucket: "fuzzer")
  |> range(start: 0, stop: date.add(d: 1d, to: time(v: 0)))
  |> filter(fn: (r) => r["_measurement"] == "coverage")
  |> filter(fn: (r) => r["_field"] == "covered")
  |> filter(fn: (r) => r["experiment"] == "test2")
  |> filter(fn: (r) => r["fuzzer"] == "zest")
  |> filter(fn: (r) => r["testClassName"] == "edu.berkeley.cs.jqf.examples.closure.CompilerTest")
  |> filter(fn: (r) => r["testMethodName"] == "testWithGenerator")
  |> aggregateWindow(every: 2s, fn: count)
  |> cumulativeSum()
  |> yield(name: "sum")
