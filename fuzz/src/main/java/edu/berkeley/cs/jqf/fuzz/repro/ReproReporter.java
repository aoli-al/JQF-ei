package edu.berkeley.cs.jqf.fuzz.repro;

import com.influxdb.client.*;
import com.influxdb.client.domain.Bucket;
import com.influxdb.client.domain.Buckets;
import com.influxdb.client.domain.Organization;
import com.influxdb.client.domain.WritePrecision;
import com.influxdb.client.write.Point;
import edu.berkeley.cs.jqf.fuzz.junit.GuidedFuzzing;

import java.io.IOException;
import java.nio.file.*;
import java.time.Instant;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

import static java.nio.file.StandardWatchEventKinds.ENTRY_CREATE;

public class ReproReporter {

    String testClassName;
    String testMethodName;
    String fuzzer;
    String repetition;
    String token;
    String orgId;
    String bucketName;
    String experiment;
    String dbLocation;
    String orgName;
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
        // Run the Junit test
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
                GuidedFuzzing.unsetGuidance();
                GuidedFuzzing.run(testClassName, testMethodName, guidance, null);


                Set<String> newCoverage = guidance.getBranchesCovered();
                System.out.println("New covered: " + newCoverage.size());
                newCoverage.removeAll(allBranchCovered);
                Instant now = Instant.now();
                allBranchCovered.addAll(newCoverage);
                if (newCoverage.size() != 0) {
                    Point p = Point.measurement("coverage")
                            .addTag("testClassName", testClassName)
                            .addTag("testMethodName", testMethodName)
                            .addTag("fuzzer", fuzzer)
                            .addTag("repetition", repetition)
                            .addTag("experiment", experiment)
                            .addField("total", allBranchCovered.size())
                            .time(now.toEpochMilli() - startTime.toEpochMilli(), WritePrecision.MS);
                    writeApi.writePoint(bucketName, orgName, p);
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
        experiment = args[4];


        dbLocation = args[6];
        orgId = args[7];
        bucketName = args[8];
        token = args[9];

        influxDBClient = InfluxDBClientFactory.create(dbLocation, token.toCharArray());
        orgName = influxDBClient.getOrganizationsApi().findOrganizationByID(orgId).getName();
        Bucket bucket = influxDBClient.getBucketsApi().findBucketByName(bucketName);
        if (bucket == null) {
            bucket = influxDBClient.getBucketsApi().createBucket(bucketName, orgId);
        }
        bucketName = bucket.getName();


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
