package edu.berkeley.cs.jqf.fuzz.repro;

import com.influxdb.client.*;
import com.influxdb.client.domain.WritePrecision;
import com.influxdb.client.write.Point;
import com.influxdb.client.write.events.WriteErrorEvent;
import com.influxdb.client.write.events.WriteSuccessEvent;
import edu.berkeley.cs.jqf.fuzz.junit.GuidedFuzzing;

import java.awt.*;
import java.io.File;
import java.io.IOException;
import java.nio.file.*;
import java.sql.Time;
import java.time.Instant;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import static java.nio.file.StandardWatchEventKinds.ENTRY_CREATE;

public class ReproReporter {

    String testClassName;
    String testMethodName;
    String fuzzer;
    String repetition;
    String token;
    String org;
    String bucket;
    String experiment;
    Instant startTime;

    WatchService watcher;
    Map<WatchKey, Path> keys = new HashMap<>();
    Set<String> allBranchCovered = new HashSet<>();

    private void register(String path) throws IOException {
        Path p = Paths.get(path);
        WatchKey key = p.register(watcher, ENTRY_CREATE);
        keys.put(key, p);
        System.out.println("Start monitoring: " + p.normalize());
    }

    public void processEvents() throws IOException, ClassNotFoundException {
        WriteApi writeApi = influxDBClient.makeWriteApi(WriteOptions.builder().flushInterval(1_000).build());
        writeApi.listenEvents(WriteSuccessEvent.class, (value) -> System.out.println("Success"));
        writeApi.listenEvents(WriteErrorEvent.class, (value) -> System.out.println(value.toString()));
//        WriteApiBlocking writeApi = influxDBClient.getWriteApiBlocking();
        for (;;) {
            WatchKey key;
            try {
                key = watcher.take();
            } catch (InterruptedException e) {
                return;
            }
            Path dir = keys.get(key);
            if (dir == null) {
                System.err.println("WatchKey not recognized!!");
                continue;
            }

            for (WatchEvent<?> event : key.pollEvents()) {
                Path name = (Path) event.context();
                Path fullPath = dir.resolve(name);

                ReproGuidance guidance = new ReproGuidance(fullPath.toFile(), null);
                System.out.println("New input found: " + name.getFileName());

                // Run the Junit test
                GuidedFuzzing.run(testClassName, testMethodName, guidance, System.out);
                System.out.println("Run finished!!!");

                Set<String> newCoverage = guidance.getBranchesCovered();
                newCoverage.removeAll(allBranchCovered);
                allBranchCovered.addAll(newCoverage);

                for (String s : newCoverage) {
                    Point point = Point.measurement("coverage")
                            .addTag("testClassName", testClassName)
                            .addTag("testMethodName", testMethodName)
                            .addTag("fuzzer", fuzzer)
                            .addTag("repetition", repetition)
                            .addTag("experiment", experiment)
                            .addField("covered", s)
                            .time(Instant.now().toEpochMilli() - startTime.toEpochMilli(), WritePrecision.MS);
//                            .time(Instant.now(), WritePrecision.MS);
                    writeApi.writePoint(point);
                }
            }
            boolean valid = key.reset();
            if (!valid) {
                break;
            }
        }
    }

    InfluxDBClient influxDBClient;
    public ReproReporter(String args[]) throws IOException {
        testClassName  = args[0];
        testMethodName = args[1];
        fuzzer = args[2];
        repetition = args[3];
        token = System.getenv("INFLUX_API_KEY");
        org = "CMU";
        bucket = "fuzzer";
        experiment = args[4];

        influxDBClient = InfluxDBClientFactory.create("http://localhost:8086", token.toCharArray(), org, bucket);
        watcher = FileSystems.getDefault().newWatchService();
        startTime = Instant.now();

        register(args[5] + "/corpus");

    }

    public static void main(String[] args) throws IOException, ClassNotFoundException {
        if (args.length < 3) {
            System.err.println("Usage: java " + ReproReporter.class + " TEST_CLASS TEST_METHOD FUZZER " +
                    "APPLICATION REPETITION TOKEN ORG BUCKET SEED_FOLDER");
            System.exit(1);
        }
        ReproReporter reporter = new ReproReporter(args);
        System.out.println("Reporter initialized!");
        reporter.processEvents();
    }
}
