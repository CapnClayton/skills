# Unused dependency findings: billing-worker

`mvn dependency:analyze` on `worker/pom.xml`, run on main.

Unused declared dependencies:
- com.fasterxml.jackson.dataformat:jackson-dataformat-xml (added for the old XML report format)
- org.glassfish.jaxb:jaxb-runtime
- javax.annotation:javax.annotation-api
- org.apache.commons:commons-text
- com.amazonaws:aws-java-sdk-sqs (AWS SDK v2 migration in PR #212 made it unnecessary)
- config-core (flagged, but loaded reflectively via the YAML config; do not remove)
- bus-client (flagged, but loaded reflectively; do not remove)

Notes:
- The `jaxb.version` property has no other users once the jaxb set goes.
- jersey-client 2.35 still pulls javax.annotation-api 1.3.2 transitively.
- Current version is 3.4.0. Dependency removal is a minor bump per the repo's versioning rule.
- While reviewing, I also noticed `RetryPolicy` swallows `InterruptedException`. That is a behavior bug, not hygiene.
